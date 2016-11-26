class Exchange(object):
    def __init__(self, name):
        self._name = name
        self._tradables = []

    @property
    def name(self):
        return self._name

    def add_tradable(self, tradable):
        self._tradables.append(tradable)

    def get_tradable(self, ticker):
        for tradable in self._tradables:
            if tradable.ticker == ticker:
                return tradable
        raise Exception("Ticker {} not found from {}".format(ticker, self.name))

    def print(self):
        for tradable in self._tradables:
            print(tradable)
