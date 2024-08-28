"""
Emilio Lim
8/10/24
This module will be the test suite for the flower shop module
"""
import unittest
from flower_database_backend.flowershop import *


class FlowerShopTest(unittest.TestCase):
    def setUp(self):
        """
        A test fixture that creates an instance of FlowerShopTest
        """
        self.file = FlowerDataBase(
            'flowershopdata.csv')

    def test_import_file_raises_exception_with_invalid_file(self):
        failed_file = FlowerDataBase(filename='test.csv')
        self.assertFalse(failed_file.import_file())

    def test_convert_file_raises_exception_with_invalid_file(self):
        failed_file = FlowerDataBase()
        error = FileNotFoundError
        self.assertRaises(error, failed_file.convert_file)

    def test_visualize_report_raises_exception_when_len_zero(self):
        error = DataNotFound
        self.assertRaises(error, self.file._visualize_report, sales={},
                          specify_year=2016,
                          interval="monthly"
                          )

    def tearDown(self):
        self.file.close_file()


if __name__ == '__main__':
    unittest.main()
