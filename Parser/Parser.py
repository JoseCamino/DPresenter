import os
from PptxFile import PptxFile
from Image import Image

class Parser:
   'A factory class that creates PptxFile and Image objects'

   @staticmethod
   def mergeSlides(slides, output_path):
      'Merges any number of slides into a deck. Returns True if the deck is created successfully.'
      deck = PptxFile(slides[0])
      length = len(slides)
      for i in xrange(1, length):
         slide = PptxFile(slides[i])
         deck.addSlide(slide)
         # After adding the slide, delete the folder
         slide.destroy()

      name = output_path.split('/')
      n = len(name)
      folder = name[:n-1]
      folder = '/'.join(folder)

      if not (os.path.exists(folder)):
         os.makedirs(folder)

      return deck.buildDeck(output_path)

   @staticmethod
   def splitDeck(deck, output_dir):
      'Splits a deck into individual slides. Returns a list of slide paths.'
      path_list = []
      deck = PptxFile(deck)
      lenght = len(deck.getSlides())

      for i in xrange(1, lenght):
         slide = deck.removeSlide(output_dir)
         path_list.append(slide)

      s1_path = output_dir + "/Slide1.pptx"
      slide1 = deck.buildDeck(s1_path)
      path_list.append(slide1)
      slides = path_list[::-1] # Reverse the list
      return slides

   @staticmethod
   def generateImage(file_path, output_dir):
      'Generates an image file from each slide. Returns the paths to the images.'
      presentation = PptxFile(file_path)
      no_of_slides = len(presentation.getSlides())
      presentation.destroy() #Delete extracted folder

      image = Image()

      pptx = os.path.abspath(file_path)
      output_folder = os.path.abspath(output_dir)

      path = image.generateFromPpt(pptx, output_folder, no_of_slides)
      return path
