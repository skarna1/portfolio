import unittest
import datetime
from model.account import Account
from model.transaction import Buy, Sell
from model.currency import Currency


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.account = Account("broker")

    def test_get_broker(self):
        self.assertEqual(self.account.broker, "broker")

    def test_process_buy_sell(self):
        buy = Buy("DNA", 100, 10.00, 5.00, Currency.EUR, datetime.date(2009, 12, 5))
        self.account.process(buy)
        holdings = self.account._holdings["DNA"]
        self.assertEqual(len(holdings._holdings), 1)
        holding = holdings._holdings[0]
        self.assertEqual(holding._amount, 100)
        self.assertEqual(holding._pricepershare, 10.00)
        self.assertEqual(holding._comission, 5)
        self.assertEqual(holding._currency, Currency.EUR)
        self.assertEqual(holding._date, datetime.date(2009, 12, 5))

        sell=Sell("DNA", 100, 10.00, 5.00, Currency.EUR, datetime.date(2009, 12, 5))
        self.account.process(sell)
        self.assertEqual(len(holdings._holdings), 0)

    def test_process_buy_two_sell(self):
        buy = Buy("DNA", 100, 10.00, 5.00, Currency.EUR, datetime.date(2009, 12, 5))
        self.account.process(buy)
        holdings = self.account._holdings["DNA"]
        self.assertEqual(len(holdings._holdings), 1)
        holding = holdings._holdings[0]

        sell=Sell("DNA", 40, 10.00, 5.00, Currency.EUR, datetime.date(2009, 12, 5))
        self.account.process(sell)
        self.assertEqual(len(holdings._holdings), 1)
        holding = holdings._holdings[0]
        self.assertEqual(holding._amount, 60)

        sell = Sell("DNA", 60, 10.00, 5.00, Currency.EUR, datetime.date(2009, 12, 5))
        self.account.process(sell)
        self.assertEqual(len(holdings._holdings), 0)


    def test_process_unknown_transaction(self):
        self.assertRaisesRegex(Exception, "Unknown transaction:.*", self.account.process, object())


if __name__ == '__main__':
    unittest.main()
