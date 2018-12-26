from portfolioapp.model.stock import Stock, OldFund, OldStock, Option, Fund
from portfolioapp.model.constants import Constants


class Exchange(object):
    _instance = None


    def __init__(self, name):
        self._name = name
        self._tradables = []
        self._tradable_dict = {}
        reader = ExchangeReader("{}etc/tunnukset.csv".format(Constants.BASEDIR))
        reader.populate_exchange(self)


    @staticmethod
    def instance(name):
        if not Exchange._instance:
            Exchange._instance = Exchange(name)
        return Exchange._instance

    @property
    def name(self):
        return self._name

    def add_tradable(self, tradable):
        self._tradables.append(tradable)
        self._tradable_dict[tradable.ticker] = tradable

    def get_tradable(self, ticker):
        if ticker in self._tradable_dict:
            return self._tradable_dict[ticker]
        raise Exception("Ticker {} not found from {}".format(ticker, self.name))

    def print(self):
        for tradable in self._tradables:
            print(tradable)




class ExchangeReader(object):
    def __init__(self, filename):
        self._filename = filename

    def populate_exchange(self, exchange):
        with open(self._filename, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith('#'):
                    continue
                tradable = self._create_tradable(line)
                if tradable is not None:
                    exchange.add_tradable(tradable)
        return exchange

    def _create_tradable(self, line):
        tradable = None
        fields = line.split(';')
        length = len(fields)
        position = 4
        if length >= position:
            tradable = self._create_tradable_based_on_type(fields)
            tradable.sector = fields[0].strip()
            tradable.ticker = fields[2].strip()
        if length > position:
            tradable.price_divider = float(fields[position].strip())
        position += 1
        if length > position:
            tradable.currency = fields[position].strip()
        position += 1
        if length > position:
            tradable.country = fields[position].strip()

        return tradable

    @staticmethod
    def _create_tradable_based_on_type(fields):
        tradabletype = fields[1].strip()
        name = fields[3].strip()
        if tradabletype == 'S':
            return Stock(name)
        if tradabletype == 'X':
            return OldStock(name)
        if tradabletype == 'F':
            return Fund(name)
        if tradabletype == 'Y':
            return OldFund(name)
        if tradabletype == 'O':
            return Option(name)
        return None

