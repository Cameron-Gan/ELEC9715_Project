from unittest import TestCase
from aCAT import Predispatch

class Test(TestCase):

    def test_free_pass(self):
        assert True


class MyTestCase(TestCase):

    def test_predispatch_package(self):
        predispatch_package = Predispatch()
        region_solution = predispatch_package.get_table('REGION_SOLUTION')
        self.assertFalse(region_solution.empty)
        """"REGION_SOLUTION SHOULD HAVE 165 ROWS 109 COLUMNS"""
        self.assertEqual(region_solution.shape[1], 109)
