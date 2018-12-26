from django.conf.urls import url

from . import views

app_name = 'portfolio'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^portfolios/$', views.portfolios, name='portfolios'),
    url(r'^portfolios/(?P<portfolio_name>salkku[0-9]+)/$', views.holdings),
    url(r'^portfolios/(?P<portfolio_name>salkku[0-9]+)/(?P<broker>\w+)/$', views.holdings),
    url(r'^portfolios/(?P<portfolio_name>salkku[0-9]+)/(?P<broker>\w+)/(?P<lots>\w+)/$', views.holdings, name='holdings'),

]