import datetime
from portfolioapp.model.exchange import Exchange, ExchangeReader
from portfolioapp.model.account import Account
from portfolioapp.model.transaction import Buy,Sell
from portfolioapp.model.currency import Currency
from portfolioapp.model.changesparser import ChangesParser
from portfolioapp.model.portfolio import Portfolio, Portfolios


BASEDIR = "/home/sami/workspace/javaportfolio"

exchange = Exchange("OMX Helsinki")
reader = ExchangeReader("{}/etc/tunnukset.csv".format(BASEDIR))

reader.populate_exchange(exchange)

exchange.print()

account = Account("Nordnet")
buy = Buy("NOK", 100, 'EVL', 4.00, 8.00, -392.0, 1.0, '05.12.2007')
account.process(buy)
account.print()
sell=Sell("NOK", 50, 'EVL', 4.2, 8, 202.0, 1.0, '05.12.2008')
account.process(sell)
account.print()
sell=Sell("NOK", 50, 'EVL', 4.2, 8, 202.0, 1.0, '05.12.2009')
account.process(sell)
account.print()

changesparser = ChangesParser(BASEDIR + '/etc/muutokset.csv')
changes = changesparser.parse()

portfolio = Portfolios().get('salkku0')
portfolio.read_transactions()