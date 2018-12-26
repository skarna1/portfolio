from collections import defaultdict
from portfolioapp.model.transaction import *
from portfolioapp.model.changesparser import Split,Demerge,SymbolChange
from portfolioapp.model.exchange import Exchange
from portfolioapp.model.quotes import Quotes
from portfolioapp.updater.kauppalehti import KauppalehtiExchangerateFetcher
import copy


class Account(object):
    def __init__(self, broker):
        self._broker = broker
        self._holdings = defaultdict(Holdings)

    @property
    def broker(self):
        return self._broker

    @property
    def holdings(self):
        h = []
        for value in self._holdings.values():
            h.extend(value._holdings)
        return h

    @property
    def holdings_combined(self):
        holdings = []
        for value in self._holdings.values():
            holding = value.combine()
            holdings.append(holding)
        return holdings

    def process(self, tr):
        if tr.NAME == Buy.NAME:
            self._holdings[tr.ticker].process_buy(tr)
        elif tr.NAME == Sell.NAME:
            self._holdings[tr.ticker].process_sell(tr)
            if self._holdings[tr.ticker].is_empty():
                del self._holdings[tr.ticker]
        elif tr.NAME == Dividend.NAME:
            pass
        elif tr.NAME == DividendTax.NAME:
            pass
        elif tr.NAME == CapitalRepayment.NAME:
            pass
        elif tr.NAME == Tax.NAME:
            # Capital gains tax
            pass
        elif tr.NAME == RightsSubscription.NAME:
            self._buy_based_on_rights(tr)
        elif tr.NAME == OptionSubscription.NAME:
            self._buy_based_on_options(tr)
        elif tr.NAME == Transfer.NAME:
            # Transfer capital from the portfolio
            pass
        else:
            raise Exception('Unknown transaction: "{}"'.format(tr.NAME))

    def process_change(self, change):
        if change.ticker not in self._holdings.keys():
            return
        if change.NAME == Split.NAME:
            self._holdings[change.ticker].process_split(change)
        elif change.NAME in SymbolChange.NAMES:
            self._process_ticker_change(change)
        elif change.NAME == Demerge.NAME:
            self._process_demerge(change)
        else:
            raise Exception('Unknown change transaction: {}'.format(change.NAME))

    def transfer(self, account):
        for ticker in account._holdings:
            if ticker in self._holdings:
                self._holdings[ticker].add(account._holdings[ticker])
            else:
                self._holdings[ticker] = account._holdings[ticker]
        account._holdings.clear()

    def _buy_based_on_rights(self, transaction):
        share_holdings = self._holdings[transaction.ticker]
        share_holdings.buy_based_on_rights(transaction)

    def _buy_based_on_options(self, transaction):
        if transaction.option_ticker not in self._holdings:
            raise Exception('Option {} not in holdings'.format(transaction.option_ticker))
        option_holdings = self._holdings[transaction.option_ticker]
        share_holdings = self._holdings[transaction.ticker]

        share_holdings.buy_based_on_options(option_holdings, transaction)
        if option_holdings.is_empty():
            del self._holdings[transaction.option_ticker]

    def _process_ticker_change(self, change):
        if change.newticker in self._holdings.keys():
            self._holdings[change.newticker].add(self._holdings[change.ticker])
        else:
            self._holdings[change.newticker] = self._holdings[change.ticker]
        for holding in self._holdings[change.newticker]._holdings:
            holding._ticker = change.newticker
        del(self._holdings[change.ticker])

    def _process_demerge(self, change):
        parent_holding = self._holdings[change.ticker]
        for d in change.demergees:
            if change.ticker != d.ticker:
                h = Holdings(parent_holding)
                h.spinoff(d.ticker, d.ratio, d.stockratio)
                if d.ticker in self._holdings:
                    self._holdings[d.ticker].add(h)
                else:
                    self._holdings[d.ticker] = h
        if change.parent_not_in_demergees():
            del self._holdings[change.ticker]
        else:
            d = change.get_demergee(change.ticker)
            parent_holding.spinoff(d.ticker, d.ratio, d.stockratio)

    def print(self):
        print("Account: {}".format(self._broker))
        for key, value in self._holdings.items():
            print("{}:".format(key))
            value.print()


class Holdings(object):
    def __init__(self, holdings=None):
        if holdings is None:
            self._holdings = []
        else:
            self._holdings = copy.deepcopy(holdings._holdings)

    def process_buy(self, transaction):
        holding = Holding(transaction.ticker)
        holding._date = transaction.date
        holding._tax_date = transaction.date
        holding._amount = transaction.amount
        holding._comission = transaction.comission
        holding._rate = transaction.rate
        holding._pricepershare = transaction.pricepershare
        holding._cost = transaction.cost
        self._holdings.append(holding)

    def process_sell(self, transaction):
        amount_to_sell = transaction.amount
        #print(amount_to_sell)
        for holding in reversed(self._holdings[:]):
            if holding._amount >= amount_to_sell:
                #print (amount_to_sell)
                holding.reduce(amount_to_sell)
                break
            else:
                self._holdings.remove(holding)
            amount_to_sell -= holding.amount
        self._holdings = [ x for x in self._holdings if x._amount > 0.00 ]

    def process_split(self, change):
        ratio = change.get_ratio()
        fractions = 0.0
        for holding in self._holdings:
            new_amount = holding._amount * ratio
            holding._amount = int(new_amount)
            fractions += new_amount - holding._amount

        if fractions >= 1.0:
            self._holdings[0]._amount += int(fractions)

        for holding in self._holdings:
            holding._pricepershare = - holding._cost / float(holding._amount)

    def spinoff(self, new_ticker, ratio, stockratio):
        fractions = 0.0
        for holding in self._holdings:
            holding._ticker = new_ticker
            fractions += holding.scale_after_spinoff(ratio, stockratio)
        self._holdings[0]._amount += int(fractions)

    def add(self, holdings):
        self._holdings.extend(holdings._holdings)

    def is_empty(self):
        return len(self._holdings) == 0

    def combine(self):
        h = None
        for holding in self._holdings:
            if h is None:
                h = copy.deepcopy(holding)
            else:
                h.add(holding)
        return h

    def buy_based_on_rights(self, transaction):
        if transaction.is_cost_shared():
            self._buy_based_on_rights_shared(transaction)
        else:
            self._buy_based_on_rights_non_shared(transaction)

    def _buy_based_on_rights_shared(self, transaction):
        for holding in self._holdings:
            pass

    def buy_based_on_options(self, option_holdings, transaction):
        option_amount = transaction.subscription_ratio * transaction.amount
        unused_options = 0
        for holding in option_holdings._holdings:
            amount_of_options_in_holding = holding.amount + unused_options
            if amount_of_options_in_holding <= option_amount:
                share_amount = int(amount_of_options_in_holding / transaction.subscription_ratio)
                used_options = share_amount * transaction.subscription_ratio
                unused_options += amount_of_options_in_holding - used_options
                option_amount -= used_options
                if share_amount > 0:
                    share_holding = self._create_holding_based_on_option(holding, transaction, share_amount)
                    self._holdings.append(share_holding)
                holding._amount = 0
            else:
                # use options only partially
                share_amount = int(option_amount / transaction.subscription_ratio)

                if share_amount > 0:
                    share_holding = self._create_holding_based_on_option(holding, transaction, share_amount)
                    self._holdings.append(share_holding)

                option_amount = 0

        # Remove used option holdings
        option_holdings._holdings = [x for x in option_holdings._holdings if x._amount > 0]

    def _create_holding_based_on_option(self, holding, transaction, share_amount):
        share_holding = Holding(transaction.ticker)
        share_holding._date = transaction.date
        share_holding._tax_date = holding._tax_date
        share_holding._amount = share_amount
        share_holding._comission = holding.comission
        share_holding._pricepershare = holding.buy_pricepershare * transaction.subscription_ratio + transaction.pricepershare
        share_holding._cost = holding._cost - share_amount * transaction.pricepershare
        return share_holding

    def print_holdings(self):
        for holding in self._holdings:
            holding.print()


class Holding(object):
    def __init__(self, ticker):
        self._ticker = ticker
        self._date = None
        self._tax_date = None
        self._amount = None
        self._comission = None
        self._currency = None
        self._rate = 1.0
        self._pricepershare = None
        self._cost = None

    def reduce(self, amount):
        new_amount = self._amount - amount
        if new_amount < 0.00001:
            new_amount = 0.0
        new_comission = (new_amount/self._amount) * self._comission

        self._comission = new_comission
        self._amount = new_amount

    def add(self, holding):
        self._amount += holding._amount
        self._cost += holding._cost
        self._comission += holding._comission
        self._pricepershare = -self._cost / self._amount

    def scale_after_spinoff(self, ratio, stockratio):
        self._comission *= ratio
        self._pricepershare *= ratio
        self._cost *= ratio
        new_amount = stockratio * self._amount
        self._amount = int(new_amount)
        return new_amount - self._amount

    def print(self):
        print (self._ticker, self._amount)

    @property
    def ticker(self):
        return self._ticker

    @property
    def name(self):
        tradable = Exchange.instance('Helsinki').get_tradable(self._ticker)
        if tradable is None:
            raise Exception('Could not find tradable for ticker {}'.format(self._ticker))
        return tradable.name

    @property
    def amount(self):
        return self._amount

    @property
    def amount_display(self):
        return int(self._amount * 1000) / 1000.0

    @property
    def comission(self):
        return self._comission

    @property
    def buy_pricepershare(self):
        return self._pricepershare

    @property
    def buy_pricepershare_display(self):
        return int(self.buy_pricepershare * 100) / 100.0

    @property
    def buy_date(self):
        return self._date.strftime('%d.%m.%Y')

    @property
    def buy_price_display(self):
        return int(self.buy_pricepershare * self.amount * 100) /100.0

    @property
    def buy_price(self):
        return self.buy_pricepershare * self.amount

    @property
    def tax_date(self):
        return self._tax_date.strftime('%d.%m.%Y')

    @property
    def price_per_share(self):
        tradable = Exchange.instance('Helsinki').get_tradable(self._ticker)
        try:
            quote = Quotes.instance().quote(self._ticker)
            return quote.last / tradable.price_divider / quote.rate
        except TypeError as ex:
            return "N/A"

    @property
    def price_date(self):
        return Quotes.instance().quote(self._ticker).date.strftime('%d.%m.%Y')

    @property
    def value(self):
        try:
            return int(self.price_per_share * self.amount * 100.0) / 100.0
        except TypeError:
            return 0.0

    @property
    def value_display(self):
        try:
            return int(self.price_per_share * self.amount * 100.0) / 100.0
        except (TypeError):
            return "N/A"