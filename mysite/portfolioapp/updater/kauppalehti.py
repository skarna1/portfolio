from lxml import html
import requests
from portfolioapp.model.constants import Constants


class KauppalehtiQuoteFetcher(object):
    def __init__(self, uri='http://www.kauppalehti.fi/5/i/porssi/porssikurssit/lista.jsp'):
        self._tickers = {}
        self.uri = uri
        self._read_tickers('{}etc/KauppalehtiStockQuoteFetcher.txt'.format(Constants.BASEDIR))

    def get_quotes(self):
        items = []
        page = requests.get(self.uri)
        tree = html.fromstring(page.content)
        names = tree.xpath('(//table[@class="table_stockexchange"])[2]//tr[@class="odd" or @class=""]/td/a/text()')[0::4]
        lasts = tree.xpath('(//table[@class="table_stockexchange"])[2]//tr[@class="odd" or @class=""]/td/text()')[0::6]
        highs = tree.xpath('(//table[@class="table_stockexchange"])[2]//tr[@class="odd" or @class=""]/td/text()')[3::6]
        lows = tree.xpath('(//table[@class="table_stockexchange"])[2]//tr[@class="odd" or @class=""]/td/text()')[4::6]

        for (name, price, high, low) in zip(names, lasts, highs, lows):
            try:
                items.append((self._tickers[name], None, float(high), float(low), float(price), 0))
            except ValueError:
                pass
            except KeyError as ex:
                print (ex)
        return items

    def _read_tickers(self, path):
        with open(path) as f:
            for line in f:
                fields = line.split(maxsplit=1)
                if len(fields) >= 2:
                    self._tickers[fields[1].rstrip('\n')] = fields[0]


class KauppalehtiExchangerateFetcher(object):

    URI = 'http://www.kauppalehti.fi/5/i/porssi/valuutat/valuutta.jsp?curid='

    def __init__(self):
        self._rates = { 'EUR': 1.0 }

    def get_rate(self, currency):
        if currency not in self._rates:
            self._rates[currency] = self._fetch_rate(currency)

        return self._rates[currency]

    def _fetch_rate(self, currency):
        page = requests.get(self.URI + currency)
        tree = html.fromstring(page.content)
        values = tree.xpath("//table[@class='table_stockexchange']/tr[position()=2]/td/text()")
        if values[0] != currency:
            raise Exception('Fetching {} failed'.format(currency))

        return float(values[1])

