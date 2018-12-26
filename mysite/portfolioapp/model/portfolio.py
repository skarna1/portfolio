import os
from glob import glob
import codecs
import datetime
from portfolioapp.model.account import Account
from portfolioapp.model.transaction import TransferAccount, TransactionFactory
from portfolioapp.model.changesparser import ChangesParser
from portfolioapp.model.constants import Constants


class Portfolios(object):

    portfolio_path = Constants.BASEDIR + 'etc/salkut/'

    def __init__(self):
        self.portfolios = []
        dirs =  glob("{}*/".format(self.portfolio_path))
        dirs.sort()
        for path in dirs:
            portfolio = Portfolio(path)
            portfolio.read()
            self.portfolios.append(portfolio)

    def get(self, name):
        for portfolio in self.portfolios:
            if portfolio.name == name:
                return portfolio


class Portfolio(object):
    KAIKKI = "Kaikki"

    def __init__(self, path):
        self.name = os.path.basename(path.rstrip('/'))
        self.path = path
        self.display_name = ''
        self.accounts = []

    def read(self):
        self.read_info()
        transactions = self.read_transactions()
        changesparser = ChangesParser(Constants.BASEDIR+'etc/muutokset.csv')
        changes = changesparser.parse()

        for tr in transactions:
            self.process_changes(changes, tr.date)
            account = self._get_account(tr.broker)
            if tr.NAME == TransferAccount.NAME:
                old_account = self._get_account(tr.old_broker)
                account.transfer(old_account)
                self.accounts.remove(old_account)
            else:
                account.process(tr)
        self.process_changes(changes, datetime.datetime.now())

    def process_changes(self, changes, date):
        while True:
            try:
                change = changes.pop(0)
                if change.date <= date:
                    for account in self.accounts:
                        account.process_change(change)
                else:
                    changes.insert(0, change)
                    break
            except IndexError as ex:
                break

    def read_info(self):
        path = self.path + '/info.txt'
        with codecs.open(path, encoding='iso8859-1') as f:
            self.display_name = f.readline()

    def read_transactions(self):
        transactions = []
        path = self.path + '/tapahtumat.csv'
        with codecs.open(path, encoding='iso8859-1') as f:
            for line in f:
                tr = TransactionFactory.process_transaction_line(line)
                if tr:
                    transactions.append(tr)
        return transactions

    def get_accounts(self, broker):
        accounts = []
        for account in self.accounts:
            if broker == self.KAIKKI or broker == account.broker:
                if account.broker != "SRT":
                    accounts.append(account)
        return accounts

    def get_holdings(self, broker, lots):
        holdings = []
        for account in self.accounts:
            if broker == self.KAIKKI or broker == account.broker:
                if account.broker != "SRT":
                    if lots == 'erat':
                        account_holdings = account.holdings
                    else:
                        account_holdings = account.holdings_combined
                    for holding in account_holdings:
                        holdings.append({'name': holding.name,
                                         'price_per_share':holding.price_per_share,
                                         'price_date': holding.price_date,
                                         'amount': holding.amount,
                                         'buy_price_per_share' : holding.buy_pricepershare_display,
                                         'buy_price': holding.buy_price_display,
                                         'buy_date': holding.buy_date,
                                         'value': holding.value_display,
                                         })

        return holdings

    def get_broker_tuple(self):
        brokers = {}
        for account in self.accounts:
            if account.broker != "SRT":
                if len(account._holdings.keys()) > 0:
                    brokers[account.broker] = account.broker
        items_list = list(brokers.items())
        items_list.insert(0, (self.KAIKKI, self.KAIKKI))
        return tuple(items_list)

    def _get_account(self, broker):
        for account in self.accounts:
            if account.broker == broker:
                return account
        account = Account(broker)
        self.accounts.append(account)
        return account

    def calculate_value(self, broker):
        value = 0.0
        for account in self.get_accounts(broker):
            for holding in account.holdings_combined:
                value += float(holding.value)
                print(holding.name, holding.value, holding.value_display,value)
        return value