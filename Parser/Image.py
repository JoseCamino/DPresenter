import os
import comtypes.client
import win32com.client as w32c

class Image:
   """A class that represents an image file.

   Attributes:
   	__location		The path to the image file
   """

########### Constructor ###############################################

   def __init__(self):
      'Constructor'
      self.__location = []
      w32c.pythoncom.CoInitialize()

#######################################################################

   def generateFromPpt(self, path, folder, no_of_slides):
      'Generates images from the given pptx file (One per slide)'

      try:
         pptApp = comtypes.client.CreateObject("Powerpoint.Application")
      except:
         raise Exception ("Cannot start MS PowerPoint")

      pptApp.Visible = True 

      try:
         pptApp.Presentations.Open(path)
      except:
         raise Exception ("Cannot open the presentation file")

      pptApp.ActivePresentation.Export(folder, "JPG")
      pptApp.Presentations[1].Close()
      pptApp.Quit()

      for i in xrange (1, no_of_slides + 1):

         self.__location.append(folder + '\Slide' + str(i) + '.JPG')

         if not (os.path.isfile(self.__location[i-1])):
            raise Exception ('Failed to create Slide' + str(i) + '.JPG')

      return self.__location

   """
   def resize(self, width, height):
      'Resizes the image to the given size'
      resized_image = []

      return resized_image
   """

   def getLocation(self):
   	'Returns the location of the image file'
   	return self.location
