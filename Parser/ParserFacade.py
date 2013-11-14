from Parser import Parser

class ParserFacade:
   'A facade class for accessing the Parser subsystem'

   @staticmethod
   def mergeSlides(slides, output_path):
      'Calls the mergeSlides() static method from the Parser class'
      return Parser.mergeSlides(slides, output_path)

   @staticmethod
   def splitDeck(deck, output_dir):
   	'Calls the splitDeck() static method from the Parser class'
   	return Parser.splitDeck(deck, output_dir)

   @staticmethod
   def generateImage(file_path, output_dir):
   	'Calls the generateImage() static method from the Parser class'
   	return Parser.generateImage(file_path, output_dir)
