import os
import shutil
from PptxFile import PptxFile
from Image import Image

def relative_path(path):
   return os.path.join(os.path.dirname(__file__), path)

class Parser:
   'A factory class that creates PptxFile and Image objects'

   @staticmethod
   def mergeSlides(slides):
      'Merges any number of slides into a deck. Input is the slides binary data. Returns the path of the deck.'

      temp_folder = relative_path("Files/Temp")
      bin = temp_folder + "/Slide1.bin"
      s1_pptx = temp_folder + "/Slide1.pptx"

      if not (os.path.exists(temp_folder)):
         os.makedirs(temp_folder)

      open(bin,"wb").write(slides[0])
      shutil.move(bin, s1_pptx)

      deck = PptxFile(s1_pptx)
      length = len(slides)

      for i in xrange(1, length):
         n = i + 1
         bin = temp_folder + "/Slide" + str(n) + ".bin"
         pptx = temp_folder + "/Slide" + str(n) + ".pptx"
         open(bin,"wb").write(slides[i])
         shutil.move(bin, pptx)

         slide = PptxFile(pptx)
         deck.addSlide(slide)
         # After adding the slide, delete the folder
         slide.destroy()
         os.remove(pptx)

      temp_file = temp_folder + "/Deck.pptx"

      file_name = deck.buildDeck(temp_file)
      os.remove(s1_pptx)

      return file_name


#############################################################################################

   @staticmethod
   def splitDeck(deck):
      'Splits a deck into individual slides. Returns a list of slides (as binary data).'

      temp_folder = relative_path("Files/Temp")
      bin = temp_folder + "/Deck.bin"
      pptx = temp_folder + "/Deck.pptx"

      if not (os.path.exists(temp_folder)):
         os.makedirs(temp_folder)

      slides_list = []
      deck = PptxFile(deck)
      lenght = len(deck.getSlides())

      for i in xrange(1, lenght):
         slide = deck.removeSlide(temp_folder)
         bin = slide + ".bin"
         shutil.move(slide, bin)
         data = open(bin,"rb").read()
         os.remove(bin)
         slides_list.append(data)

      s1_path = temp_folder + "/Slide1.pptx"
      slide1 = deck.buildDeck(s1_path)
      bin = slide1 + ".bin"
      shutil.move(slide1, bin)
      data = open(bin,"rb").read()
      os.remove(bin)
      slides_list.append(data)
      slides = slides_list[::-1] # Reverse the list

      return slides

######################################################################################

   @staticmethod
   def generateImageFromFile(file_path, output_dir):
      'Generates an image file from each slide. Returns the paths to the images.'

      presentation = PptxFile(file_path)
      no_of_slides = len(presentation.getSlides())
      presentation.destroy() #Delete extracted folder

      image = Image()

      pptx = os.path.abspath(file_path)
      output_folder = os.path.abspath(output_dir)

      image_paths = image.generateFromPpt(pptx, output_folder, no_of_slides)
      return image_paths


   @staticmethod
   def generateImageFromData(data, output_dir):
      'Generates an image file from each slide. Input is the binary data of the slide or deck. Returns the paths to the images.'

      temp_folder = relative_path("Files/Temp")
      bin = temp_folder + "/File.bin"
      pptx = temp_folder + "/File.pptx"

      if not (os.path.exists(temp_folder)):
         os.makedirs(temp_folder)

      open(bin,"wb").write(data)
      shutil.move(bin, pptx)

      presentation = PptxFile(pptx)
      no_of_slides = len(presentation.getSlides())
      presentation.destroy() #Delete extracted folder

      image = Image()

      pptx_dir = os.path.abspath(pptx)
      output_folder = os.path.abspath(output_dir)
      
      image_paths = image.generateFromPpt(pptx_dir, output_folder, no_of_slides)

      os.remove(pptx)

      return image_paths


   @staticmethod
   def generateNewSlide():
      'Generates a blank slide.'
      temp_folder = relative_path("Files/Temp")
      bin = temp_folder + "/NewSlide.bin"
      pptx = "Files/default_slide.pptx"

      if not (os.path.exists(temp_folder)):
         os.makedirs(temp_folder)

      shutil.copy(pptx, bin)

      data = open(bin,"rb").read()
      os.remove(bin)

      return data