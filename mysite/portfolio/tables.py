import django_tables2 as tables


class HoldingsTable(tables.Table):
    name = tables.Column()
    price_per_share = tables.Column()
    price_date = tables.Column()
    amount = tables.Column()
    buy_price_per_share = tables.Column()
    buy_date = tables.Column()
    buy_price = tables.Column()
    value = tables.Column()


    class Meta:
        attrs = {'class': 'paleblue'}