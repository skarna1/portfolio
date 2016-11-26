from model.exchange import Exchange
from model.exchangereader import ExchangeReader

BASEDIR = "/home/sami/workspace/portfolio"

exchange = Exchange("OMX Helsinki")
reader = ExchangeReader("{}/etc/tunnukset.csv".format(BASEDIR))

reader.populate_exchange(exchange)

exchange.print()
