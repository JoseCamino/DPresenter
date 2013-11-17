from Parser import Parser

class ParserFacade:
   'A facade class for accessing the Parser subsystem'

   @staticmethod
   def mergeSlides(slides):
      'Merges any number of slides into a deck. Input is the slides binary data. '
      'Returns the path of a temporary deck that can be deleted after it is downloaded.'
      return Parser.mergeSlides(slides)

   @staticmethod
   def splitDeck(deck):
   	'Splits a deck into individual slides. Returns a list of slides (as binary data).'
   	return Parser.splitDeck(deck)

   @staticmethod
   def generateImageFromFile(file_path, output_dir):
      'Generates an image file from each slide. Returns the paths to the images as '
      '[.../Slide1.JPG, .../Slide2.JPG, ...].'
      return Parser.generateImageFromFile(file_path, output_dir)

   @staticmethod
   def generateImageFromData(data, output_dir):
      'Generates an image file from each slide. Input is the binary data of the slide or deck.'
      'Returns the paths to the images as [.../Slide1.JPG, .../Slide2.JPG, ...].'
      return Parser.generateImageFromData(data, output_dir)

   @staticmethod
   def generateNewSlide():
      'Generates a blank slide and returns its binary data.'
      return Parser.generateNewSlide()  


