from Parser import Parser

class ParserFacade:
   'A facade class for accessing the Parser subsystem'

   @staticmethod
   def mergeSlides(slides):
      'Calls the mergeSlides() static method from the Parser class'
      return Parser.mergeSlides(slides)

   @staticmethod
   def splitDeck(deck):
   	'Calls the splitDeck() static method from the Parser class'
   	return Parser.splitDeck(deck)

   @staticmethod
   def generateImageFromFile(file_path, output_dir):
   	'Calls the generateImage() static method from the Parser class'
   	return Parser.generateImageFromFile(file_path, output_dir)

   @staticmethod
   def generateImageFromData(data, output_dir):
      'Calls the generateImageFromData() static method from the Parser class'
      return Parser.generateImageFromData(data, output_dir)  


