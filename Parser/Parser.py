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

      bin = file_name.replace('.pptx', '.bin')
      shutil.move(file_name, bin)
      data = open(bin,"rb").read()
      os.remove(bin)

      return data


#############################################################################################

   @staticmethod
   def splitDeck(deck):
      'Splits a deck into individual slides. Returns a list of slides (as binary data).'

      temp_folder = relative_path("Files/Temp")
      bin = temp_folder + "/Deck.bin"
      pptx = temp_folder + "/Deck.pptx"

      if not (os.path.exists(temp_folder)):
         os.makedirs(temp_folder)

      if not (deck[-4:] == 'pptx'):
         open(bin,"wb").write(deck)
         shutil.move(bin, pptx)
         deck = pptx

      slides_list = []

      try:
         deck = PptxFile(deck)
      except:
         "Delete invalid file"
         os.remove(deck)
         folder = deck.replace('.pptx', '')
         if (os.path.exists(folder)):
            shutil.rmtree(folder)
         raise Exception ("Invalid presentation data")

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
      if(os.path.exists(pptx)):
         os.remove(pptx)

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
   def generateImageFromData(data, image_names):
      'Generates an image file from each slide. Input is the binary data of the slide or deck'
      'and a list of names. Renames the images and returns a list of paths.'

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
      
      temp_paths = image.generateFromPpt(pptx_dir, temp_folder, no_of_slides)

      n = len(temp_paths)

      if (len(image_names) != n):
         for i in xrange (0, n):
            os.remove(temp_paths[i])
         raise Exception ("Amount of generated slides differs from lenght of input parameter") 

      for i in xrange (0, n):
         shutil.move(temp_paths[i], image_names[i])

      os.remove(pptx)

      return image_names


   @staticmethod
   def generateNewSlide():
      'Generates a blank slide.'
      temp_folder = relative_path("Files/Temp")
      bin = temp_folder + "/NewSlide.bin"
      pptx = relative_path("Files/default_slide.pptx")

      if not (os.path.exists(temp_folder)):
         os.makedirs(temp_folder)

      shutil.copy(pptx, bin)

      data = open(bin,"rb").read()
      os.remove(bin)

      return data


   @staticmethod
   def generateConfidentialSlide():
      'Generates a default confidential slide.'
      temp_folder = relative_path("Files/Temp")
      bin = temp_folder + "/ConfidentialSlide.bin"
      pptx = relative_path("Files/confidential_slide.pptx")

      if not (os.path.exists(temp_folder)):
         os.makedirs(temp_folder)

      shutil.copy(pptx, bin)

      data = open(bin,"rb").read()
      os.remove(bin)

      return data