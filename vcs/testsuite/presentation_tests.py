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
		TestFragmenter,
		TestMerge)

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

class TestMerge(unittest.TestCase):
	def setUp(self):
		remove_test_repo()
		self.project = vcs.create_project("testrepo")
		self.presentation = self.project.current_presentation

	def tearDown(self):
		remove_test_repo()

	def test_presentation_data_merges_slides(self):
		presentation_location = os.path.join(directory, "test_requests/testpresentation.pptx")
		slides = PresentationFragmenter().fragment_file(presentation_location)
		[self.presentation.add_slide(None, slide) for slide in slides]

		# save the presentation itself to a file
		presentation_data = self.presentation.data
		presentation_save_path = os.path.join(directory, "testdata/testmerge.pptx")
		with open(presentation_save_path, 'wb') as file:
			file.write(presentation_data)

		# Now test if the output presentation has the correct number of slides
		saved_slides = PresentationFragmenter().fragment_file(presentation_save_path)
		self.assertEqual(len(saved_slides), len(slides))

	def test_presentation_write_data_merges_slides(self):
		presentation_location = os.path.join(directory, "test_requests/testpresentation.pptx")
		slides = PresentationFragmenter().fragment_file(presentation_location)
		[self.presentation.add_slide(None, slide) for slide in slides]

		# save the presentation itself to a file
		presentation_save_path = os.path.join(directory, "testdata/testmerge.pptx")
		presentation_data = self.presentation.write_data_to_file(presentation_save_path)

		# Now test if the output presentation has the correct number of slides
		saved_slides = PresentationFragmenter().fragment_file(presentation_save_path)
		self.assertEqual(len(saved_slides), len(slides))