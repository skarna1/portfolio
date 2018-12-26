from datetime import datetime


class ChangeTransaction(object):
    def __init__(self, ticker, date):
        self._ticker = ticker
        self._date = date

    @property
    def ticker(self):
        return self._ticker

    @property
    def date(self):
        return self._date


class Split(ChangeTransaction):
    NAME = 'SPLIT'

    def __init__(self, ticker, date, a, b):
        super(Split, self).__init__(ticker, date)
        self.a = a
        self.b = b

    def get_ratio(self):
        return self.b / self.a


class SymbolChange(ChangeTransaction):
    NAMES = ['TUNNUS', 'TUNNUSNIMI']
    NAME = 'TUNNUS'

    def __init__(self, ticker, date, newticker):
        super(SymbolChange, self).__init__(ticker, date)
        self.newticker = newticker


class Demergee(object):
    def __init__(self, ticker, ratio):
	    self.ticker = ticker
	    self.ratio = ratio
	    self.stockratio = 1.0;


class Demerge(ChangeTransaction):
    NAME = 'JAKAUTUMINEN'

    def __init__(self, ticker, date):
        super(Demerge, self).__init__(ticker, date)
        self.demergees = []

    def parent_not_in_demergees(self):
        return self.get_demergee(self.ticker) is None

    def get_demergee(self, ticker):
        for d in self.demergees:
            if ticker == d.ticker:
                return d

class ChangesParser(object):

    def __init__(self, filename):
        self.filename = filename

    def parse(self):
        transactions = []
        with open(self.filename) as f:
            for line in f:
                change_transaction = self._parseline(line)
                if change_transaction:
                    transactions.append(change_transaction)
        return transactions

    def _parseline(self, line):
        items = [x.strip() for x in line.split(';')]
        date = datetime.strptime(items[0], '%d.%m.%Y')
        ticker = items[1]
        eventtype = items[2].upper()
        if eventtype == Split.NAME:
            a = float(items[3])
            b = float(items[4])
            tr = Split(ticker, date, a, b)
            return tr
        elif eventtype in SymbolChange.NAMES:
            newticker = items[3]
            tr = SymbolChange(ticker, date, newticker)
            return tr
        elif eventtype == Demerge.NAME:
            tr = Demerge(ticker, date)
            demergees = int(items[3])
            fieldsindemergee = 3
            if len(items) > (4 + 3 * demergees):
                fieldsindemergee = 4
            for i in range(demergees):
                d = Demergee(items[4 + i * fieldsindemergee], float(items[6 + i * fieldsindemergee]))
                if (fieldsindemergee == 4):
                    d.stockratio = float(items[7 + i * fieldsindemergee])
                tr.demergees.append(d)
            return tr

