import datetime


class Transaction(object):
    def __init__(self, ticker, amount, broker, pricepershare, comission, cost, rate, datestr):
        self._ticker = ticker
        self._amount = amount
        self._pricepershare = pricepershare
        self._comission = comission
        self._date = datetime.datetime.strptime(datestr, '%d.%m.%Y')
        self._rate = rate
        self._broker = broker
        self._cost = cost

    @property
    def ticker(self):
        return self._ticker

    @property
    def amount(self):
        return self._amount

    @property
    def pricepershare(self):
        return self._pricepershare

    @property
    def rate(self):
        return self._rate

    @property
    def comission(self):
        return self._comission

    @property
    def date(self):
        return self._date

    @property
    def broker(self):
        return self._broker

    @property
    def cost(self):
        return self._cost


class Buy(Transaction):
    NAME = 'OSTO'
    ALIAS = 'MERKINTÄ'

    def __init__(self, ticker, amount, broker, pricepershare, comission, cost, rate, date):
        super().__init__(ticker, amount, broker, pricepershare, comission, cost, rate, date)


class Sell(Transaction):
    NAME = 'MYYNTI'

    def __init__(self, ticker, amount, broker, pricepershare, comission, cost, rate, date):
        super().__init__(ticker, amount, broker, pricepershare, comission, cost, rate, date)


class Tax(Transaction):
    NAME = 'VERO'

    def __init__(self, ticker, amount, broker, pricepershare, comission, cost, rate, date):
        super().__init__(ticker, amount, broker, pricepershare, comission, cost, rate, date)


class Dividend(Transaction):
    NAME = 'OSINKO'

    def __init__(self, ticker, amount, broker, pricepershare, comission, cost, rate, date):
        super().__init__(ticker, amount, broker, pricepershare, comission, cost, rate, date)


class DividendTax(Transaction):
    NAME = 'OSINKOVERO'

    def __init__(self, ticker, amount, broker, pricepershare, comission, cost, rate, date):
        super().__init__(ticker, amount, broker, pricepershare, comission, cost, rate, date)


class CapitalRepayment(Transaction):
    NAME = 'PÄÄOMAN PALAUTUS'

    def __init__(self, ticker, amount, broker, pricepershare, comission, cost, rate, date):
        super().__init__(ticker, amount, broker, pricepershare, comission, cost, rate, date)


class RightsSubscription(Transaction):
    NAME = 'MERKINTÄ_OIKEUKSILLA'

    def __init__(self, ticker, amount, broker, pricepershare, comission, cost, rate, date, old_ownership, ratio):
        super().__init__(ticker, amount, broker, pricepershare, comission, cost, rate, date)
        self.amount_of_old_ownership = old_ownership
        self.ratio = ratio
        self._tax_change_date = datetime.date(2005, 1, 1)

    def is_cost_shared(self):
        return self.date.date() > self._tax_change_date


class OptionSubscription(Transaction):
    NAME = 'MERK.OIKEUS'

    def __init__(self, ticker, amount, broker, pricepershare, comission, cost, rate, date, option_ticker, subscription_ratio):
        super().__init__(ticker, amount, broker, pricepershare, comission, cost, rate, date)
        self.option_ticker = option_ticker
        self.subscription_ratio = subscription_ratio #one share requires x options, subscriptionRatio = x


class Transfer(Transaction):
    NAME = 'SIIRTO'

    def __init__(self, ticker, amount, broker, pricepershare, comission, cost, rate, date):
        super().__init__(ticker, amount, broker, pricepershare, comission, cost, rate, date)


class TransferAccount(Transaction):
    NAME = 'TILISIIRTO'

    def __init__(self, ticker, amount, broker, pricepershare, comission, cost, rate, date, old_broker):
        super().__init__(ticker, amount, broker, pricepershare, comission, cost, rate, date)
        self.old_broker = old_broker


class TransactionFactory(object):

    @staticmethod
    def process_transaction_line(line):
        fields = line.split(';')
        if len(fields) < 4:
            return
        fields = [x.strip().replace(',', '.') for x in fields]

        tr = None
        transaction_type = fields[1]
        if transaction_type == Buy.NAME or transaction_type == Buy.ALIAS:
            tr = TransactionFactory.create_buy(fields)
        elif transaction_type == Sell.NAME:
            tr = TransactionFactory.create_sell(fields)
        elif transaction_type == Tax.NAME:
            tr = TransactionFactory.create_tax(fields)
        elif transaction_type == Dividend.NAME:
            tr = TransactionFactory.create_dividend(fields)
        elif transaction_type == DividendTax.NAME:
            tr = TransactionFactory.create_dividend_tax(fields)
        elif transaction_type == CapitalRepayment.NAME:
            tr = TransactionFactory.create_capital_repayment(fields)
        elif transaction_type == RightsSubscription.NAME:
            tr = TransactionFactory.create_rights_subscription(fields)
        elif transaction_type == OptionSubscription.NAME:
            tr = TransactionFactory.create_option_subscription(fields)
        elif transaction_type == Transfer.NAME:
            tr = TransactionFactory.create_transfer(fields)
        elif transaction_type == TransferAccount.NAME:
            tr = TransactionFactory.create_transfer_account(fields)
        else:
            raise Exception('Unknown transaction: {}'.format(transaction_type))

        return tr

    @staticmethod
    def create_buy(fields):
        tr = Buy(fields[2], float(fields[4]), fields[6], float(fields[5]), float(fields[7]),
                 float(fields[8]), TransactionFactory._get_rate(fields, 9), fields[0])
        return tr

    @staticmethod
    def create_sell(fields):
        tr = Sell(fields[2], float(fields[4]), fields[6], float(fields[5]), float(fields[7]),
                  float(fields[8]), TransactionFactory._get_rate(fields, 9), fields[0])
        return tr

    @staticmethod
    def create_tax(fields):
        tr = Tax(fields[2], float(fields[4]), fields[6], float(fields[5]), float(fields[7]),
                 float(fields[8]), TransactionFactory._get_rate(fields, 9), fields[0])
        return tr

    @staticmethod
    def create_dividend(fields):
        tr = Dividend(fields[2], float(fields[4]), fields[6], float(fields[5]), float(fields[7]),
                      float(fields[8]), TransactionFactory._get_rate(fields, 9), fields[0])
        return tr

    @staticmethod
    def create_dividend_tax(fields):
        tr = DividendTax(fields[2], float(fields[4]), fields[6], float(fields[5]), float(fields[7]),
                         float(fields[8]), TransactionFactory._get_rate(fields, 9), fields[0])
        return tr

    @staticmethod
    def create_capital_repayment(fields):
        tr = CapitalRepayment(fields[2], float(fields[4]), fields[6], float(fields[5]), float(fields[7]),
                              float(fields[8]), TransactionFactory._get_rate(fields, 9), fields[0])
        return tr

    @staticmethod
    def create_rights_subscription(fields):
        old_ownership = float(fields[10])
        ratio = float(fields[11])
        tr = RightsSubscription(fields[2], float(fields[4]), fields[6], float(fields[5]), float(fields[7]),
                                float(fields[8]), TransactionFactory._get_rate(fields, 9), fields[0], old_ownership, ratio)
        return tr

    @staticmethod
    def create_option_subscription(fields):
        if len(fields) > 11:
            optionTicker = fields[10]
            ratio = float(fields[11])

            tr = OptionSubscription(fields[2], float(fields[4]), fields[6], float(fields[5]), float(fields[7]),
                                    float(fields[8]), TransactionFactory._get_rate(fields, 9), fields[0], optionTicker, ratio)
            return tr
        raise Exception('Invalid Option subscription')

    @staticmethod
    def create_transfer(fields):
        tr = Transfer(fields[2], float(fields[4]), fields[6], float(fields[5]), float(fields[7]),
                      float(fields[8]), TransactionFactory._get_rate(fields, 9), fields[0])
        return tr

    @staticmethod
    def create_transfer_account(fields):
        if len(fields) > 10:
            new_broker = fields[10]

            tr = TransferAccount(fields[2], float(fields[4]), fields[6], float(fields[5]), float(fields[7]),
                                 float(fields[8]), TransactionFactory._get_rate(fields, 9), fields[0], new_broker)
            return tr
        raise Exception('Invalid account transfer')

    @staticmethod
    def _get_rate(fields, n):
        rate = 1.0
        if len(fields) > n:
            if fields[n]:
                rate = float(fields[n])
        return rate
