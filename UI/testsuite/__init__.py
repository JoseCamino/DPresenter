import os
import os.path
import unittest
import UI.dbc

import unit
from helper import remove_dir_if_exists


def flatten(item_list):
	return [val for sublist in item_list for val in sublist]
		
def test():
	"The main test method"

	tests = flatten([unit.get_tests()])

	loader = unittest.TestLoader()
	test_suites = [loader.loadTestsFromTestCase(case) for case in tests]
	suite = unittest.TestSuite(test_suites)
	unittest.TextTestRunner(verbosity=2).run(suite)
	
