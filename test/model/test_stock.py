import unittest
from model.stock import Stock


class MyTestCase(unittest.TestCase):
    def test_stock(self):
        stock = Stock("Nokia")
        self.assertEqual("Nokia", stock.name)


if __name__ == '__main__':
    unittest.main()
