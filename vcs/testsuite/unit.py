import os
import os.path
import unittest

import vcs
from helper import remove_test_repo, get_vcs

vcs = get_vcs()

def get_tests():
	return (
		TestCreateProject,
		TestLoadProject,
		TestProject,
		TestPresentation,
		TestSlides,
		TestCheckinCheckout,
		TestRestorePresentation,
		TestConfidentiality)

class TestCreateProject(unittest.TestCase):
	def setUp(self):
		remove_test_repo()
		
	def tearDown(self):
		remove_test_repo()
		
	def test_create_creates_directory(self):
		"Test that the create call succeeded"
		vcs.create_project("testrepo")
		self.assertTrue(os.path.exists("testprojects/testrepo"))

	def test_create_raises_if_exists(self):
		"Projects must have unique names"
		vcs.create_project("testrepo")
		with self.assertRaises(Exception) as ex:
			vcs.create_project("testrepo")
		
class TestLoadProject(unittest.TestCase):
	def setUp(self):
		remove_test_repo()
		vcs.create_project("testrepo")
		
	def tearDown(self):
		remove_test_repo()
		
	def test_load_raises_if_does_not_exist(self):
		remove_test_repo()
		with self.assertRaises(Exception) as ex:
			vcs.load_project("testrepo")
			
	def test_load_succeeds_if_exists(self):
		repo = vcs.load_project("testrepo")
		self.assertIsNotNone(repo)

class TestProject(unittest.TestCase):
	"Test the VCSProject object"

	def setUp(self):
		remove_test_repo() # exceptions may cause tearDown to fail
		self.project = vcs.create_project("testrepo")

	def tearDown(self):
		remove_test_repo()

	def test_get_presentation(self):
		self.project.current_presentation.persist("TESTVAL")
		lastId = self.project.persisted_presentations[-1].id
		self.assertEqual(self.project.get_presentation(lastId).name, "TESTVAL")
		
	def test_get_current_presentation(self):
		"Test that get_current_presentation does return the current presentation"
		presentation = self.project.current_presentation
		self.assertFalse(presentation.is_persisted())

	def test_project_start_with_current_presentation(self):
		self.assertIsNotNone(self.project.current_presentation)

class TestPresentation(unittest.TestCase):
	def setUp(self):
		remove_test_repo()
		self.project = vcs.create_project("testrepo")
		self.presentation = self.project.current_presentation

	def tearDown(self):
		remove_test_repo()

	def test_persisting_adds_a_presentation(self):
		self.presentation.persist()
		self.assertEqual(len(self.project.persisted_presentations), 1)

	def test_persisting_with_name_sets_presentation_name(self):
		self.presentation.persist("testName")
		self.assertEqual(self.project.persisted_presentations[0].name, "testName")

	def test_persist_returns_new_slide_id(self):
		saved_id = self.presentation.persist("testName")
		saved_presentation = self.project.get_presentation(saved_id)		
		self.assertEqual(saved_presentation.name, "testName")

	def test_persisting_keeps_the_same_slides(self):
		self.presentation.add_slide()
		self.presentation.add_slide()
		self.presentation.add_slide()

		saved_id = self.presentation.persist()
		saved_presentation = self.project.get_presentation(saved_id)
		self.assertEqual(len(saved_presentation.slides), 3)

	def test_can_persist_many_presentations(self):
		self.presentation.persist()
		self.presentation.persist()
		self.presentation.persist()
		self.assertEqual(len(self.project.persisted_presentations), 3)

	def test_renaming_presentations(self):
		saved_presentation = self.project.get_presentation(self.presentation.persist())
		saved_presentation.rename("testrename")
		self.assertEqual(saved_presentation.name, "testrename")
		self.assertEqual(self.project.get_presentation(saved_presentation.id).name, "testrename")

	def test_a_presentation_starts_with_zero_slides(self):
		self.assertEqual(len(self.presentation.slides), 0)

	def test_add_slide(self):
		self.presentation.add_slide()
		self.assertEqual(len(self.presentation.slides), 1)

	def test_add_slide_with_data(self):
		self.presentation.add_slide(data="testdata")
		self.assertEqual(self.presentation.slides[0].data, "testdata")

class TestSlides(unittest.TestCase):
	def setUp(self):
		remove_test_repo()
		self.project = vcs.create_project("testrepo")
		self.presentation = self.project.current_presentation
		self.slide1 = self.presentation.add_slide("Slide1", data="slide1")
		self.slide2 = self.presentation.add_slide(data="slide2")
		self.slide1_id = self.slide1.id
		self.slide2_id = self.slide2.id

	def tearDown(self):
		remove_test_repo()

	def test_retrieve_slide_name(self):
		self.assertEqual(self.project.get_slide(self.slide1_id).name, "Slide1")
		self.assertEqual(self.presentation.slides[0].name, "Slide1")

	# Add test for original slide chain soon, once that feature starts to matter

	def test_get_multiple_slide_data(self):
		data = self.presentation.slides.data
		self.assertEqual(len(data), 2)
		self.assertEqual(data[0], "slide1")
		self.assertEqual(data[1], "slide2")

class TestCheckinCheckout(unittest.TestCase):
	def setUp(self):
		remove_test_repo()
		self.project = vcs.create_project("testrepo")
		self.presentation = self.project.current_presentation
		self.slide = self.presentation.add_slide()
		self.slide_id = self.slide.id

	def tearDown(self):
		remove_test_repo()

	def test_checkout_checkin(self):
		self.slide.checkout("testuser")
		newSlide = self.slide.checkin("testuser", "TEST DATA")
		# TODO: Check that the slide isn't checked out
		self.assertEqual(newSlide.data, "TEST DATA")

	def test_cannot_checkout_twice(self):
		self.slide.checkout("testuser1")
		with self.assertRaises(Exception):
			self.slide.checkout("testuser2")

	def test_checkin_requires_same_user(self):
		self.slide.checkout("testuser1")
		with self.assertRaises(Exception):
			self.slide.checkin("testuser2", "TEST DATA")

	def test_checkin_fails_before_checkout(self):
		with self.assertRaises(Exception):
			self.slide.checkin("testuser", "TEST DATA")

	def test_checkout_user(self):
		self.assertIsNone(self.slide.checkout_user)
		self.slide.checkout("testuser")
		self.assertEqual(self.slide.checkout_user, "testuser")

	def test_cancel_checkout(self):
		self.slide.checkout("testuser")
		self.assertIsNotNone(self.slide.checkout_user)
		self.slide.cancel_checkout()
		self.assertIsNone(self.slide.checkout_user)

class TestRestorePresentation(unittest.TestCase):
	def setUp(self):
		remove_test_repo()
		self.project = vcs.create_project("testrepo")
		self.current_presentation = self.project.current_presentation
		self.slide_id1 = self.current_presentation.add_slide().id
		self.slide_id2 = self.current_presentation.add_slide().id
		self.presentation = self.project.get_presentation(self.current_presentation.persist())

	def tearDown(self):
		remove_test_repo()

	def test_restored_presentation_have_same_slides_as_persisted(self):
		# todo: remove slides from current presentation
		self.current_presentation.add_slide()
		self.current_presentation.add_slide()
		self.presentation.restore()

		new_current_slides = self.project.current_presentation.slides
		self.assertEqual(len(new_current_slides), 2)
		self.assertEqual(new_current_slides[0].id, self.slide_id1)
		self.assertEqual(new_current_slides[1].id, self.slide_id2)

class TestConfidentiality(unittest.TestCase):
	def setUp(self):
		remove_test_repo()
		self.project = vcs.create_project("testrepo")
		self.slide1 = self.project.current_presentation.add_slide()
		self.slide2 = self.project.current_presentation.add_slide()
		self.slide3= self.project.current_presentation.add_slide()

	def tearDown(self):
		remove_test_repo()

	def test_setting_confidential_saves(self):
		self.slide1.confidential = True
		self.assertTrue(self.slide1.confidential)
		self.assertTrue(self.project.get_slide(self.slide1.id).confidential)

	def test_previous_versions_are_also_confidential(self):
		previous_slide_id = self.slide1.id
		self.slide1.checkout("me")
		self.slide1 = self.slide1.checkin("me", "test")
		self.slide1.confidential = True
		self.assertTrue(self.project.get_slide(previous_slide_id).confidential)
		self.assertTrue(self.project.get_slide(self.slide1.id).confidential)

	def test_updated_slides_of_confidential_slides_are_confidential(self):
		self.slide1.confidential = True
		self.slide1.checkout("me")
		new_slide = self.slide1.checkin("me", "test")
		self.assertTrue(new_slide.confidential)
		self.assertTrue(self.project.get_slide(new_slide.id).confidential)

	def test_other_slides_are_not_affected(self):
		self.slide1.confidential = True
		self.slide1.checkout("me")
		new_slide = self.slide1.checkin("me", "test")
		new_slide.confidential = True

		self.assertFalse(self.project.get_slide(self.slide2.id).confidential)

	def test_slide_list_confidential_returns_only_confidential(self):
		self.slide1.confidential = True
		confidential_slides = self.project.current_presentation.slides.confidential
		self.assertEqual(len(confidential_slides), 1)
		for slide in confidential_slides:
			self.assertTrue(slide.confidential)

	def test_slide_list_public_returns_only_not_confidential(self):
		self.slide1.confidential = True
		public_slides = self.project.current_presentation.slides.public
		self.assertEqual(len(public_slides), 2)
		for slide in public_slides:
			self.assertFalse(slide.confidential)