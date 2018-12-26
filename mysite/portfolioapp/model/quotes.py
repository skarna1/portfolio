import datetime
import glob
import os
from portfolioapp.model.constants import Constants
from portfolioapp.model.currency import Currency


class Quote(object):
    def __init__(self, ticker, date, high, low, last, volume=0, rate=1.0):
        self._ticker = ticker
        self._date = date
        self._high = high
        self._low = low
        self._last = last
        self._volume = volume
        self._rate = rate

    def line(self):
        return '{},{},{},{},{},{}\n'.format(self.date_str(), str(self.high),
                                            str(self.low), str(self.last),
                                            str(self.volume), str(self.rate))

    def date_str(self):
        return self.date.strftime('%d%m%Y')

    @property
    def ticker(self):
        return self._ticker

    @property
    def last(self):
        return self._last

    @property
    def date(self):
        return self._date

    @property
    def high(self):
        return self._high

    @property
    def low(self):
        return self._low

    @property
    def volume(self):
        return self._volume

    @property
    def rate(self):
        return self._rate


class Quotes(object):
    _instance = None

    def __init__(self):
        self._quotes = {}
        self._read_quotes()

    @staticmethod
    def instance():
        if not Quotes._instance:
            Quotes._instance = Quotes()
        return Quotes._instance

    def update(self, items):
        today = datetime.datetime.now()
        if today.weekday() == 6:
            today = datetime.date.fromordinal(today.toordinal() - 1)
        if today.weekday() >= 5:
            today = datetime.date.fromordinal(today.toordinal() - 1)

        for (ticker, date, high, low, last, volume, rate) in items:
            if date is None:
                date = today
            self._quotes[ticker] = Quote(ticker, date, high, low, last, volume, rate)
            self._write_quote(ticker, self._quotes[ticker])

    def quote(self, ticker):
        if ticker in self._quotes:
            return self._quotes[ticker]
        return Quote(ticker, datetime.datetime.now(), "N/A",  "N/A", "N/A",0)

    def _read_quotes(self):
        files = glob.glob("{}etc/kurssidata/*".format(Constants.BASEDIR))
        for filename in files:
            with open(filename) as f:
                for line in f:
                    pass

                self._create_quote(filename, line)

    def _write_quote(self, ticker, quote):
        filename = "{}etc/kurssidata/{}.csv".format(Constants.BASEDIR, ticker)
        datestr = '{},'.format(quote.date_str())

        with open(filename, "w+") as f:
            lines = f.readlines()
            if len(lines) == 0:
                lines.append('D8HLCVC\n')
            f.seek(0)
            for line in lines:
                if not line.startswith(datestr):
                    f.write(line)
            f.write(quote.line())
            #print('Writing to {} line {}'.format(filename, quote.line()))

    def _create_quote(self, filename, line):
        fields = line.split(',')

        date = datetime.datetime.strptime(fields[0], '%d%m%Y')
        high = float(fields[1])
        low = float(fields[2])
        last = float(fields[3])
        volume = int(fields[4])
        if len(fields) > 5:
            rate = float(fields[5])
        else:
            rate = 1.0
        ticker = os.path.basename(filename.replace('.csv', ''))
        self._quotes[ticker] = Quote(ticker, date, high, low, last, volume, rate)