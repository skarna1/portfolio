from model.currency import Currency


class Tradable(object):
    DEFAULT_COUNTRY = "Suomi"

    def __init__(self, name):
        self._name = name
        self._isin = None
        self._ticker = None
        self._exchange = "OMX"
        self._sector = None
        self._currency = Currency.EUR
        self._country = Tradable.DEFAULT_COUNTRY

    def __str__(self):
        return type(self).__name__ + ": " + self._name + " " + self._ticker

    @property
    def name(self):
        return self._name

    @property
    def isin(self):
        return self._isin

    @isin.setter
    def isin(self, value):
        self._isin = value

    @property
    def ticker(self):
        return self._ticker

    @ticker.setter
    def ticker(self, value):
        self._ticker = value

    @property
    def exchange(self):
        return self._exchange

    @exchange.setter
    def exchange(self, value):
        self._exchange = value

    @property
    def sector(self):
        return self._sector

    @sector.setter
    def sector(self, value):
        self._sector = value

    @property
    def currency(self):
        return self._currency

    @currency.setter
    def currency(self, value):
        self._currency = value

    @property
    def country(self):
        return self._country

    @country.setter
    def country(self, value):
        self._country = value


class Stock(Tradable):
    def __init__(self, name):
        super().__init__(name)


class Option(Tradable):
    def __init__(self, name):
        super().__init__(name)


class Fund(Tradable):
    def __init__(self, name):
        super().__init__(name)
        self._pricedivider = 1

    @property
    def pricedivider(self):
        return self._pricedivider


class OldStock(Tradable):
    def __init__(self, name):
        super().__init__(name)


class OldFund(Tradable):
    def __init__(self, name):
        super().__init__(name)


class OldOption(Tradable):
    def __init__(self, name):
        super().__init__(name)
