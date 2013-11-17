import os
import os.path
import unittest

import vcs
from helper import remove_test_repo, get_vcs

from vcs.fragmenter import PresentationFragmenter

vcs = get_vcs()
directory = os.path.dirname(__file__)

def get_tests():
	return (
		TestFragmenter,)

class PresentationTest(unittest.TestCase):
	def setUp(self):
		remove_test_repo()
		self.project = vcs.create_project(self, "testrepo")

	def tearDown(self):
		remove_test_repo()

class TestFragmenter(unittest.TestCase):
	def test_fragmenter(self):
		presentation_location = os.path.join(directory, "test_requests/testpresentation.pptx")
		slides = PresentationFragmenter().fragment_file(presentation_location)
		self.assertEqual(len(slides), 3)
