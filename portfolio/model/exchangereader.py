from model.stock import Stock, OldFund, OldStock, Option, Fund


class ExchangeReader(object):
    def __init__(self, filename):
        self._filename = filename

    def populate_exchange(self, exchange):
        with open(self._filename, "r", encoding="iso8859-1") as f:
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
            tradable.divider = fields[position].strip()
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
