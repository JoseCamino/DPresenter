import os
import shutil
import unittest

from Parser.ParserFacade import ParserFacade

def get_tests():
	return (
		TestMergeSlides,
		TestSplitDeck,
		TestGenerateImage,
		TestGenerateSlide
		)

def relative_path(path):
   return os.path.join(os.path.dirname(__file__), path)

class TestMergeSlides(unittest.TestCase):
	def setUp(self):
		temp_folder = relative_path("../Files/Temp")
		if os.path.exists(temp_folder):
			shutil.rmtree(temp_folder)
		
	def tearDown(self):
		temp_folder = relative_path("../Files/Temp")
		if os.path.exists(temp_folder):
			shutil.rmtree(temp_folder)
		
	def test_merge_slides(self):
		"Test that mergeSlides() returns the path of the deck"
		folder = relative_path("test_files")
		paths = [folder + "/slide1.pptx", folder + "/slide2.pptx"]
		slides = [open(path,"rb").read() for path in paths]

		deck = ParserFacade.mergeSlides(slides)	
		self.assertTrue(deck[-4:] == 'pptx')

	def test_merge_slides_invalid_input(self):
		"Test that mergeSlides() only accepts binary data"
		folder = relative_path("test_files")
		slides = [folder + "/slide1.pptx", folder + "/slide2.pptx"]

		with self.assertRaises(Exception) as ex:
			ParserFacade.mergeSlides(slides)
	

class TestSplitDeck(unittest.TestCase):
	def setUp(self):
		temp_folder = relative_path("../Files/Temp")
		if os.path.exists(temp_folder):
			shutil.rmtree(temp_folder)
		
	def tearDown(self):
		temp_folder = relative_path("../Files/Temp")
		if os.path.exists(temp_folder):
			shutil.rmtree(temp_folder)

	def test_split_deck_bin(self):
		"Test that splitDeck() succeeds splitting a presentation with binary format"
		folder = relative_path("test_files")
		pptx = os.path.join(folder, "testpresentation.pptx")

		deck = open(pptx,"rb").read()
		slides = ParserFacade.splitDeck(deck)

		self.assertEqual(len(slides), 4)

	def test_split_deck_pptx(self):
		"Test that splitDeck() succeeds splitting a presentation with .pptx format"
		folder = relative_path("test_files")
		deck = folder + "/testpresentation.pptx"
		slides = ParserFacade.splitDeck(deck)

		self.assertEqual(len(slides), 4)

	def test_split_deck_invalid_input(self):
		"Test that splitDeck() does not accept other type of files"
		folder = relative_path("test_files")
		invalid_file = folder + "/invalidfile.pptx"
		deck = folder + 'temp_inv_deck.pptx'

		shutil.copy(invalid_file, deck)

		with self.assertRaises(Exception) as ex:
			slides = ParserFacade.splitDeck(deck)


class TestGenerateImage(unittest.TestCase):
	def setUp(self):
		temp_folder = relative_path("../Files/Temp")
		image = relative_path("test_files") + "/Slide1.JPG"
		if os.path.exists(temp_folder):
			shutil.rmtree(temp_folder)
		if os.path.exists(image):
			os.remove(image)			
		
	def tearDown(self):
		temp_folder = relative_path("../Files/Temp")
		image = relative_path("test_files") + "/Slide1.JPG"
		if os.path.exists(temp_folder):
			shutil.rmtree(temp_folder)
		if os.path.exists(image):
			os.remove(image)	

	def test_generate_image_from_file(self):
		"Test that generateImageFromFile() returns images when the input is a pptx file"
		folder = relative_path("test_files")
		deck = folder + "/slide1.pptx"
		image_path = ParserFacade.generateImageFromFile(deck, folder)

		if os.path.exists(folder + "/Slide1.JPG"):
			os.remove(folder + "/Slide1.JPG")

		self.assertEqual(image_path[0][-3:], "JPG")

	def test_generate_image_from_data(self):
		"Test that generateImageFromFile() returns images when the input is binary data"
		folder = relative_path("test_files")
		pptx = folder + "/slide1.pptx"
		bin = pptx.replace(".pptx", ".bin")
		shutil.copy(pptx, bin)

		deck = open(bin,"rb").read()
		os.remove(bin)
		image_names = [folder+'/0001.JPG']
		image_path = ParserFacade.generateImageFromData(deck, image_names)

		os.remove(image_names[0])

		self.assertEqual(image_path[0][-3:], "JPG")

	def test_invalid_path(self):
		"Test that an invalid input path causes an exception"
		folder = relative_path("test_files")
		deck = folder + "/invalid_slide.pptx"
		
		with self.assertRaises(Exception) as ex:
			image_path = ParserFacade.generateImageFromFile(deck, folder)


class TestGenerateSlide(unittest.TestCase):
	def setUp(self):
		temp_folder = relative_path("../Files/Temp")
		if os.path.exists(temp_folder):
			shutil.rmtree(temp_folder)
		
	def tearDown(self):
		temp_folder = relative_path("../Files/Temp")
		if os.path.exists(temp_folder):
			shutil.rmtree(temp_folder)

	def test_generate_new_slide(self):
		"Test that generateNewSlide() works"
		slide = ParserFacade.generateNewSlide()
		self.assertTrue(slide != None)

	def test_generate_confidential_slide(self):
		"Test that generateConfidentialSlide() works"
		slide = ParserFacade.generateConfidentialSlide()
		self.assertTrue(slide != None)