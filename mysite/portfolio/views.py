from django.shortcuts import render
from django.http import HttpResponse
from django_tables2 import RequestConfig
from django.http import HttpResponseRedirect
#from django.core.urlresolvers import reverse
from django.urls import reverse
from portfolioapp.model.portfolio import Portfolios, Portfolio
from portfolioapp.updater.kauppalehti import KauppalehtiQuoteFetcher
from portfolioapp.model.quotes import Quotes
from .forms import SelectBrokerForm
from .tables import HoldingsTable


def index(request):
    return HttpResponse("Hello, world. You're at the portfolio.")


def portfolios(request):
    context = {
        'portfolios': Portfolios().portfolios
    }
    return render(request, 'portfolio/index.html', context)


def holdings(request, portfolio_name, broker=Portfolio.KAIKKI, lots='combined'):
    portfolio = Portfolios().get(portfolio_name)

    custom_choices = portfolio.get_broker_tuple()
    if request.method == 'POST':
        if 'update' in request.POST:
            quotes = KauppalehtiQuoteFetcher().get_quotes()
            Quotes.instance().update(quotes)

        form = SelectBrokerForm(request.POST, prefix='select_broker')
        form.set_custom_choices(custom_choices)
        if form.is_valid():
            broker = form.cleaned_data['broker']
            return HttpResponseRedirect(reverse('portfolio:holdings', args=(portfolio_name, broker, lots)))
    else:
        form = SelectBrokerForm(prefix='select_broker')
        form.set_custom_choices(custom_choices)
        form.set_initial(broker)

    table = HoldingsTable(portfolio.get_holdings(broker, lots))
    RequestConfig(request, paginate={'per_page': 50}).configure(table)

    if lots == "combined":
        is_lots_active = False
    else:
        is_lots_active = True
    context = {
        'portfolio': portfolio,
        'portfolio_value' : portfolio.calculate_value(broker),
        'lots': lots,
        'broker': broker,
        'form': form,
        'portfolio_table' : table,
        'is_lots_active' : is_lots_active,
    }

    return render(request, 'portfolio/broker/holdings/index.html', context)
