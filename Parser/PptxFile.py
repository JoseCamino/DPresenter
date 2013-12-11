import os
import os.path
import re
import zipfile
import shutil

def relative_path(path):
   return os.path.join(os.path.dirname(__file__), path)

class PptxFile:
   """A class that represents a .pptx Microsoft PowerPoint file.

   Attributes:
   	__location		Location of the .pptx file
    __contentTypes    Path to the content types file
    __presentationMain   Path to the presentation main file
   	__slideMaster		Path to the master slide file
   	__slide 		A list with the paths of all slide files
    __media     Path to all the media files
    __extensions   list of available file extensions in xml format
   """

########### Constructor ###############################################

   def __init__(self, path):
      'Constructor'
      ext = path.split("/")
      ext = ext[len(ext)-1].split(".")
      if (ext[1] != "pptx"):
         raise Exception ("Invalid file extension: " + ext[1])

      self.__location = self.__extract(path)
      self.__slide = []
      self.__slideLayout = []
      self.__extensions = []
      self.__contentTypes = self.__location + "/[Content_Types].xml"
      self.__media = self.__getMedia()
      self.__parseContentTypes(self.__contentTypes) # get all other info

#######################################################################

   def __parseContentTypes(self, contents):
      'Parses the content types file to get the location of all the other files'

      f = open(contents, 'r')
      try:
         sections = f.read()
         sections = sections.split('/>')    #split the contents by sections
         first = sections[0].split('">')
         length = len(first)
         sections[0] = first[length - 1]
         length = len(sections)

         for i in xrange(0, length):
            words = sections[i].split()

            if (words[0] == '<Override'):    #the section contains relevant data
               partName = words[1].split('=')
               path = partName[1].replace('"', '')     #get the location of this file
               contentType = words[2].split('=')
               fileType = contentType[1].split('.')     
               fileType = fileType[len(fileType)-1]   #get the type of file

               #determine which attribute to update
               if (fileType == 'main+xml"'):
                  self.__presentationMain = self.__location + path
               elif (fileType == 'slideMaster+xml"'):
                  self.__slideMaster = self.__location + path
               elif (fileType == 'slide+xml"'):
                  self.__slide.append(self.__location + path)

            elif (words[0] == '<Default'):
               ext = ' '.join(words)
               ext = ext + '/>'
               self.__extensions.append(ext)

      finally:
         f.close()


   def __getMedia(self):
      'Get the media files'
      media_folder = self.__location + '/ppt/media'
      if not (os.path.isdir(media_folder)):
         os.mkdir(media_folder)
      path, dirs, files = os.walk(media_folder).next()
      return files
     

   def __extract(self, path):
      'Extracts the contents of the .pptx file into a temporary folder'

      zipOutputDir = path[0:path.rfind(".")]
      if not (os.path.exists(zipOutputDir)):
         os.makedirs(zipOutputDir)

      zp = zipfile.ZipFile(path, "r")
      zp.extractall(zipOutputDir)   # Extract the files
      zp.close()

      return zipOutputDir

#########################################################################

   def addSlide(self, slide):
      'Add a slide to the .pptx file'
      self.__mergePresentationMain(slide.getPresentationMain())
      self.__mergeContentTypes(slide.getContentTypes())
      self.__addRelationship()
      newSlide = self.__moveSlide(slide)
      self.__slide.append(newSlide)


   def removeSlide(self, output_dir):
      'Remove the last slide from the presentation'
      num = len(self.__slide)
      new_slide_folder = output_dir + '/Slide' + str(num)

      if (num > 1):

         if not (os.path.exists(new_slide_folder)):
            os.makedirs(new_slide_folder)

         self.__moveFiles(new_slide_folder)
         self.__splitPresentationMain(new_slide_folder)
         self.__removeRelationships(new_slide_folder)
         self.__removeLastSlide(new_slide_folder)
         self.__parseSlideMaster(new_slide_folder)
         self.__splitContentTypes(new_slide_folder)
         self.__slide.pop()

         new_slide_path = self.__buildSlide(new_slide_folder)
         return new_slide_path

      return None

#########################################################################


   def buildDeck(self, output_path):
      'Compress the presentation folder into .pptx format and return its path'
      name = self.__location.split('/')
      n = len(name)
      name[n-1] = 'Temp'
      loc = '/'.join(name)
      name = self.__location

      shutil.move(name, loc)
      zp = shutil.make_archive(loc, 'zip', loc) # Archive the folder into a .zip file
      shutil.move(loc, name)

      self.destroy()

      path = loc + '.pptx'
      shutil.move(zp, path)

      shutil.move(path, output_path)

      return output_path

   def __buildSlide(self, new_slide_folder):

      new_slide_name = new_slide_folder + ".pptx"

      zp = shutil.make_archive(new_slide_folder, 'zip', new_slide_folder) # Archive the folder into a .zip file
      shutil.move(zp, new_slide_name)

      shutil.rmtree(new_slide_folder, ignore_errors=True)

      return new_slide_name


   def destroy(self):
      'Remove the temporary folder'
      shutil.rmtree(self.__location, ignore_errors=True)


########### Helper Methods for AddSlide() ###############################################

   def __mergePresentationMain(self, presentationMain):
      'A helper method for addSlide(). Merges two presentation.xml files'
      string = []

      # Read the new slide's info
      f = open(presentationMain, 'r')
      try:
         out = False
         while (out == False):
            if (f.read(1) == '<'):
               if (f.read(11) == 'p:sldIdLst>'):
                  while True:
                     char = f.read(1)
                     if (char != '/'):
                        string.append(char)
                     else: break                 
                  out = True
      finally:
         f.close()

      slideInfo = ''.join(string)

      info = slideInfo.split(' ')
      slide = info[1].split('=')
      slide = slide[1].split('"')
      slide = slide[1]
      number = int(slide)

      # Write the new slide's info to the current presentation.xml file
      f = open(self.__presentationMain, 'r+')
      try:
         contents = f.read()

         existingId = []

         existing_slides = contents.split('p:sldIdLst>')
         existing_slides = existing_slides[1].split('/>')

         n = len(existing_slides)

         for i in xrange(0, n - 1):
            existing_info = existing_slides[i].split(' ')
            s = existing_info[1].split('=')
            s = s[1].split('"')
            s = s[1]
            num = int(s)

            if (number <= num):
               number = num + 1

         # Change the new slide's Id and rId 
         slideRID = str(len(self.__slide)+2)
         slideInfo = '<p:sldId id="' + str(number) + '" r:id="rId' + slideRID + '"'
         contents = contents.split('</p:sldIdLst>')
         f.seek(0)
         f.write(contents[0])
         f.write(slideInfo + '/></p:sldIdLst>')
         f.write(contents[1])
         f.truncate()
      finally:
         f.close()


   def __mergeContentTypes(self, contentTypes):
      'Parses the content types file to get the location of all the other files'

      string = ''

      # Get the slide's information from its [Content_Types].xml
      f = open(contentTypes, 'r')
      try:
         sections = f.read()
         sections = sections.split('/>')    #split the contents by sections
         length = len(sections)
         done = False

         for i in xrange(1, length):
            words = sections[i].split()

            if (words[0] == '<Override'):    #the section may contain the slide info
               partName = words[1].split('=')
               path = partName[1].replace('"', '') #get the location of this file
               contentType = words[2].split('=')
               fileType = contentType[1].split('.')     
               fileType = fileType[len(fileType)-1] #get the type of file

               # Get the slide info
               if (fileType == 'slide+xml"'):
                  string = sections[i] + '/>'
                  done = True

            if (done == True): break

      finally:
         f.close()

      # Change the new slide's number
      slideN = str(len(self.__slide)+1)
      sp = string.split('1')
      string = sp[0] + slideN + sp[1]

      # Write the new slide's info to the current file's [Content_Types].xml
      f = open(self.__contentTypes, 'r+')
      try:
         contents = f.read()
         contents = contents.split('</Types>')
         f.seek(0)
         f.write(contents[0])
         f.write(string + '</Types>')
         f.write(contents[1])
         f.truncate()
      finally:
         f.close()


   def __addRelationship(self):
      'A helper method for addSlide(). Uses the location of presentation.xml.rels file'
      'and adds the corresponding relationship for the new slide.'

      relationships = self.__location + '/ppt/_rels/presentation.xml.rels'
      slideN = str(len(self.__slide)+1) #The new slide's number

      f = open(relationships, 'r+')
      try:
         # Split the content into sections
         content = f.read()
         sections = content.split('/>')
         n = len(sections) - 1

         # Determine the last 4 relationship id's
         n1 = 'rId' + str(n + 1)
         n2 = 'rId' + str(n)
         n3 = 'rId' + str(n - 1)
         n4 = 'rId' + str(n - 2)
         n5 = 'rId' + str(n - 3)

         # Replace all words in one pass using a regular expression
         rep = {n2: n1, n3: n2, n4: n3, n5: n4} 
         rep = dict((re.escape(k), v) for k, v in rep.iteritems())
         pattern = re.compile("|".join(rep.keys()))
         content = pattern.sub(lambda m: rep[re.escape(m.group(0))], content)

         # Write the new slide's info to the file
         newInfo = ''

         for i in xrange(1, n+1):
            if 'rId2' in sections[i]:
               newInfo = sections[i] + '/>'
               break

         newSlide = 'slide' + slideN
         newInfo = newInfo.replace('slide1', newSlide)
         newInfo = newInfo.replace('rId2', n5)
         content = content.split('</Relationships>')
         f.seek(0)
         f.write(content[0])
         f.write(newInfo + '</Relationships>')
         f.truncate()

      finally:
         f.close()


   def __moveSlide(self, slide):
      'A helper method for addSlide(). Adds the new slide xml files to the deck'
      slide_path = slide.getSlides()

      # Move slide.xml from the slide folder to the current deck's folder
      slideN = len(self.__slide)
      dst = self.__slide[slideN-1].split('/')
      dstLen = len(dst)
      dst[dstLen-1] = 'slide' + str(slideN+1) + '.xml'
      destination = '/'.join(dst)

      shutil.move(slide_path[0], destination)

      # Move slide.xml.rels to the current deck's folder
      src = slide_path[0].split('/')
      srcLen = len(src)
      src[srcLen-1] = '_rels/slide1.xml.rels'
      src = '/'.join(src)
      dst[dstLen-1] = '_rels/slide' + str(slideN+1) + '.xml.rels'
      dst = '/'.join(dst)

      shutil.move(src, dst)

      # Move media

      n = len(slide.getMedia())
      m = len(self.__media)
      # Check if there are media files in the slide
      if (n > 0):
         media = slide.getMedia()
         m += 1

         f = open(dst, 'r+')
         content = f.read()
         sections = content.split('/>')
         first = sections[0].split('<Relationship ')
         first = '<Relationship ' + first[1]
         sections[0] = first

         x = len(sections) - 1         

         try:
            for i in xrange(0, x):

               line = sections[i].split()
               media_type = line[2].split('/')
               length = len(media_type)
               media_type = media_type[length - 1]
               media_type = media_type.split('"')
               media_type = media_type[0]

               if (media_type == "image"):
                  target = line[3].split("=")
                  target = target[1].split('/')
                  length = len(target)
                  target = target[length - 1]
                  target = target.replace('"', "")

                  src = slide.getLocation() + '/ppt/media/' + target
                  new_file_name = target.split('.')
                  new_file_name[0] = "image" + str(m)
                  new_file_name = '.'.join(new_file_name)
                  dst = self.__location + '/ppt/media/' + new_file_name

                  if (os.path.exists(src)):
                     shutil.move(src, dst)

                  # Change the image names on the slide.xml.rels file
                  content = content.replace(target, new_file_name)

                  # Update the media list
                  self.__media.append(new_file_name)
                  m += 1

               if (media_type == "video"):
                  target = line[3].split("=")
                  target = target[1].split('/')
                  length = len(target)
                  target = target[length - 1]
                  target = target.replace('"', "")

                  src = slide.getLocation() + '/ppt/media/' + target
                  new_file_name = target.split('.')
                  new_file_name[0] = "media" + str(m)
                  new_file_name = '.'.join(new_file_name)
                  dst = self.__location + '/ppt/media/' + new_file_name

                  if (os.path.exists(src)):
                     shutil.move(src, dst)

                  # Update the names of the videos on the slide.xml.rels file
                  content = content.replace(target, new_file_name)

                  # Update the media list
                  self.__media.append(new_file_name)
                  m += 1

            f.seek(0)
            f.write(content)
            f.truncate()

         finally:
            f.close()

         # Check for new extensions
         slide_ext = slide.getExtensions()
         n = len(self.__extensions)
         m = len(slide_ext)

         string = []

         for j in range(0, m):

            extExists = False
            for i in range(0, n):
               if (self.__extensions[i] == slide_ext[j]):
                  extExists = True
                  break
               else:
                  extExists = False

            if (extExists == False):
               string.append(slide_ext[j])
               self.__extensions.append(slide_ext[j])

         # If any new extensions are found, write them to [Content_Types].xml
         if (len(string) > 0):

            string = ''.join(string)
            f = open(self.__contentTypes, 'r+')
            try:
               content = f.read()
               content = content.split('</Types>')
               f.seek(0)
               f.write(content[0])
               f.write(string + '</Types>')
               f.truncate()

            finally:
               f.close()

      return destination


#################### Helper methods for removeSlide() #######################################################

   def __moveFiles(self, output_dir):
      'A helper method for removeSlide(). Copy all the folders and the files that dont'
      'need to be modified into a new Slide folder.'

      shutil.copytree(self.__location + '/_rels', output_dir + '/_rels')
      shutil.copytree(self.__location + '/ppt/slideLayouts', output_dir + '/ppt/slideLayouts')
      shutil.copytree(self.__location + '/ppt/slideMasters', output_dir + '/ppt/slideMasters')
      shutil.copy(self.__location + '/ppt/presProps.xml', output_dir + '/ppt/presProps.xml')
      shutil.copy(self.__location + '/ppt/tableStyles.xml', output_dir + '/ppt/tableStyles.xml')
      shutil.copy(self.__location + '/ppt/viewProps.xml', output_dir + '/ppt/viewProps.xml')

      directory = output_dir + '/docProps'
      if not os.path.isdir(directory):
         os.mkdir(directory)  
      shutil.copy(self.__location + '/docProps/app.xml', output_dir + '/docProps/app.xml')
      shutil.copy(self.__location + '/docProps/core.xml', output_dir + '/docProps/core.xml')
      shutil.copy(relative_path('Files/default_thumbnail.jpeg'), output_dir + '/docProps/thumbnail.jpeg') # Temporary

      shutil.copytree(self.__location + '/ppt/theme', output_dir + '/ppt/theme')
      self.__parseThemeRels(output_dir)


   def __parseThemeRels(self, output_dir):
      'Parse theme.xml.rels files to find any other files that need to be moved'

      directory = output_dir + '/ppt/media'
      # Create the media directory if it doesn't exist
      if not os.path.isdir(directory):
         os.mkdir(directory)

      rels_folder = self.__location + '/ppt/theme/_rels'

      if (os.path.exists(rels_folder)):
         path, dirs, files = os.walk(rels_folder).next()
         
         n = len(files)
         for i in xrange (0, n):
            file_path = rels_folder + '/' + files[i]

            f = open(file_path, 'r')
            try:
               content = f.read()
               sections = content.split('/>')
               first = sections[0].split('<Relationship ')
               first = '<Relationship ' + first[1]
               sections[0] = first

               n = len(sections) - 1

               for i in xrange (0, n):
                  line = sections[i].split()
                  media_type = line[2].split('/')
                  length = len(media_type)
                  media_type = media_type[length - 1]
                  media_type = media_type.split('"')
                  media_type = media_type[0]

                  if (media_type == "image"):
                     target = line[3].split('/')
                     length = len(target)
                     target = target[length - 1]
                     target = target.split('"')
                     target = target[0]

                     src = self.__location + '/ppt/media/' + target
                     dst = directory + "/" + target

                     shutil.copy(src, dst)

            finally:
               f.close()            

   def __parseSlideMaster(self, output_dir):
      'Parse slideMaster.xml.rels to find if there are files that need to be copied'

      masters_folder = self.__location + '/ppt/slideMasters/_rels'

      if (os.path.exists(masters_folder)):
         path, dirs, files = os.walk(masters_folder).next()

         n = len(files)
         for i in xrange (0, n):
            file_path = masters_folder + '/' + files[i]

            f = open(file_path, 'r')
            try:
               content = f.read()
               sections = content.split('/>')
               first = sections[0].split('<Relationship ')
               first = '<Relationship ' + first[1]
               sections[0] = first

               n = len(sections) - 1

               for i in xrange (0, n):
                  line = sections[i].split()
                  file_type = line[2].split('/')
                  length = len(file_type)
                  file_type = file_type[length - 1]
                  file_type = file_type.split('"')
                  file_type = file_type[0]

                  if (file_type == "image"):
                     target = line[3].split('/')
                     length = len(target)
                     target = target[length - 1]
                     target = target.replace('"', '')

                     src = self.__location + '/ppt/media/' + target
                     dst = output_dir + "/ppt/media/" + target

                     if not (os.path.exists(dst)):
                        shutil.copy(src, dst)

            finally:
               f.close()            

   def __splitPresentationMain(self, output_dir):
      'A helper method for removeSlide(). Split the presentation.xml file'

      pres_main = self.__presentationMain
      slide_pres_main = output_dir + '/ppt/presentation.xml'

      shutil.copy(pres_main, slide_pres_main)

      # Delete last slide's info from Deck
      f = open(pres_main, 'r+')
      try:
         data = f.read()
         data = data.split('p:sldIdLst>')
         string = data[1]
         string = string.split('/>')
         string[len(string)-2] = string[len(string)-1]
         string.pop()
         string = '/>'.join(string)
         string = 'p:sldIdLst>' + string + 'p:sldIdLst>'
         data[1] = string
         data = ''.join(data)

         f.seek(0)
         f.write(data)
         f.truncate()

      finally:
         f.close()

      # Delete all other slides' info from Slide
      f = open(slide_pres_main, 'r+')
      try:
         data = f.read()
         data = data.split('p:sldIdLst>')
         string = data[1]
         string = string.split('/>')
         slide1 = string[0]
         string = slide1 + '/>'
         string = 'p:sldIdLst>' + string + '</p:sldIdLst>'
         data[1] = string
         data = ''.join(data)

         f.seek(0)
         f.write(data)
         f.truncate()

      finally:
         f.close()


   def __splitContentTypes(self, output_dir):
      'A helper method for removeSlide(). Split the [Content_Types].xml file'

      content_types = self.__contentTypes
      slide_content_types = output_dir + '/[Content_Types].xml'

      shutil.copy(content_types, slide_content_types)

      # Find out if there are extenssions that need updating on the deck
      media_folder = self.__location + '/ppt/media'
      if not (os.path.isdir(media_folder)):
         os.mkdir(media_folder)
      path, dirs, files = os.walk(media_folder).next()

      file_n = len(files)

      f = open(content_types, 'r+')
      try:
         content = f.read()
         sections = content.split('/>')    #split the contents by sections
         length = len(sections)
         done = False

         for i in xrange(0, length):

            if (i == 0):
               relevant_info = sections[i].split('>')
               sections[i] = relevant_info[len(relevant_info)-1]

            words = sections[i].split()

            # Delete last slide's info from the Deck's content types file
            if (words[0] == '<Override' and done == False):    #the section may contain the slide info
               partName = words[1].split('=')
               path = partName[1].replace('"', '') #get the location of this file
               contentType = words[2].split('=')
               fileType = contentType[1].split('.')     
               fileType = fileType[len(fileType)-1] #get the type of file

               # Delete the last slide's info
               if (fileType == 'slide+xml"'):
                  slide_name = "slide" + str(len(self.__slide))

                  if slide_name in sections[i]:
                     string = sections[i] + '/>'
                     content = content.replace(string, "")
                     done = True
            
            # Delete unused extensions
            elif (words[0] == '<Default'):
               ext = words[1].split("=")

               if (ext[0] == 'Extension'):
                  ext = ext[1].replace('"', "")
                  ext_exists = False

                  for j in xrange (0, file_n):
                     file_name = files[j].split('.')
                     if (ext == file_name[1]):
                        ext_exists = True
                        break

                  if (ext_exists == False and ext != "xml" and ext != "rels" and ext != "jpeg"):
                     string = sections[i] + '/>'
                     content = content.replace(string, "")
            

         f.seek(0)
         f.write(content)
         f.truncate()

      finally:
         f.close()


      # Find out if there are extensions that need updating on the slide
      media_folder = output_dir + '/ppt/media'
      if not (os.path.isdir(media_folder)):
         os.mkdir(media_folder)
      path, dirs, files = os.walk(media_folder).next()

      file_n = len(files)

      f = open(slide_content_types, 'r+')
      try:
         content = f.read()
         sections = content.split('/>')    #split the contents by sections
         length = len(sections)
         counter = 0
         num = len(self.__slide) - 1

         for i in xrange(0, length):

            if (i == 0):
               relevant_info = sections[i].split('>')
               sections[i] = relevant_info[len(relevant_info)-1]

            words = sections[i].split()

            # Delete all other slides' info from the Slide's content types file
            if (words[0] == '<Override' and counter != num):    #the section may contain the slide info

               partName = words[1].split('=')
               path = partName[1].replace('"', '') #get the location of this file
               contentType = words[2].split('=')
               fileType = contentType[1].split('.')     
               fileType = fileType[len(fileType)-1] #get the type of file

               # Delete the other slides' info
               if (fileType == 'slide+xml"'):
                  
                  if "slide1" not in sections[i]:
                     string = sections[i] + '/>'
                     content = content.replace(string, "")
                     counter = counter + 1
            
            # Delete unused extensions
            elif (words[0] == '<Default'):
               ext = words[1].split("=")

               if (ext[0] == 'Extension'):
                  ext = ext[1].replace('"', "")
                  ext_exists = False

                  for j in xrange (0, file_n):
                     file_name = files[j].split('.')
                     if (ext == file_name[1]):
                        ext_exists = True
                        break

                  if (ext_exists == False and ext != "jpeg" and ext != "xml" and ext != "rels"):
                     string = sections[i] + '/>'
                     content = content.replace(string, "") 
                    

         f.seek(0)
         f.write(content)
         f.truncate()

      finally:
         f.close()


   def __removeRelationships(self, output_dir):
      'A helper method for removeSlide(). Remove unnecessary relationships from presentation.xml.rels'

      rels = self.__location + '/ppt/_rels/presentation.xml.rels'
      slide_rels = output_dir + '/ppt/_rels/presentation.xml.rels'

      directory = output_dir + '/ppt/_rels'
      # Create the _rels directory if it doesn't exist
      if not os.path.isdir(directory):
         os.mkdir(directory)  

      shutil.copy(rels, slide_rels)

      # Remove the last slide's rId from the Deck's presentation.xml.rels file
      last_slide_num = len(self.__slide)+1
      slide_rid = 'rId' + str(last_slide_num)

      f = open(rels, 'r+')
      try:
         # Split the content into sections
         content = f.read()
         sections = content.split('/>')
         n = len(sections) - 1

         # Delete the last slide's info
         for i in xrange (0, n):
            if slide_rid in sections[i]:
               if (i > 0):
                  string = sections[i] + '/>'
                  content = content.replace(string, "")
               else:
                  string = sections[i].split('>')
                  string = string[len(string)-1] + '/>'
                  content = content.replace(string, "")
               break

         # Determine the last 4 relationship id's
         n1 = 'rId' + str(last_slide_num + 1)
         n2 = 'rId' + str(last_slide_num + 2)
         n3 = 'rId' + str(last_slide_num + 3)
         n4 = 'rId' + str(last_slide_num + 4)

         # Replace all words in one pass using a regular expression
         rep = {n1: slide_rid, n2: n1, n3: n2, n4: n3} 
         rep = dict((re.escape(k), v) for k, v in rep.iteritems())
         pattern = re.compile("|".join(rep.keys()))
         content = pattern.sub(lambda m: rep[re.escape(m.group(0))], content)

         # Write to the file
         f.seek(0)
         f.write(content)
         f.truncate()

      finally:
         f.close()      


      # Remove the all other slide's rIds from the Slide's presentation.xml.rels file
      slide_rid = 'rId2'

      f = open(slide_rels, 'r+')
      try:
         # Split the content into sections
         content = f.read()
         sections = content.split('/>')
         n = len(sections) - 1

         # Delete the all other slides' info
         for i in xrange (0, n):

            if (i > 0):
               string = sections[i] + '/>'
               # Get the rid number
               slide_num = string.split()
               slide_num = slide_num[1].split('=')
               slide_num = slide_num[1].split('"')
               slide_num = slide_num[1]
               slide_num = slide_num[3:]
            
               num = 0
               if slide_num.isdigit():
                  num = int(slide_num)

                  if ((num > 2) and (num <= last_slide_num)):
                     content = content.replace(string, "")

            else:
               string = sections[i].split('>')
               string = string[len(string)-1] + '/>'
               # Get the rid number
               slide_num = string.split()
               slide_num = slide_num[1].split('=')
               slide_num = slide_num[1].split('"')
               slide_num = slide_num[1]
               slide_num = slide_num[3:]
            
               num = 0
               if slide_num.isdigit():
                  num = int(slide_num)

                  if ((num > 2) and (num <= last_slide_num)):
                     content = content.replace(string, "")

         # Determine the last 4 relationship id's
         n1 = 'rId' + str(last_slide_num + 1)
         n2 = 'rId' + str(last_slide_num + 2)
         n3 = 'rId' + str(last_slide_num + 3)
         n4 = 'rId' + str(last_slide_num + 4)

         # Replace all words in one pass using a regular expression
         rep = {n1: 'rId3', n2: 'rId4', n3: 'rId5', n4: 'rId6'} 
         rep = dict((re.escape(k), v) for k, v in rep.iteritems())
         pattern = re.compile("|".join(rep.keys()))
         content = pattern.sub(lambda m: rep[re.escape(m.group(0))], content)

         # Write to the file
         f.seek(0)
         f.write(content)
         f.truncate()

      finally:
         f.close()


   def __removeLastSlide(self, output_dir):
      'A helper method for removeSlide(). Move corresponding slide.xml and media files to Slide folder'

      directory = output_dir + '/ppt/slides'
      # Create the slides directory if it doesn't exist
      if not os.path.isdir(directory):
         os.mkdir(directory)

      directory = output_dir + '/ppt/slides/_rels'
      # Create the slides/_rels directory if it doesn't exist
      if not os.path.isdir(directory):
         os.mkdir(directory) 

      directory = output_dir + '/ppt/media'
      # Create the media directory if it doesn't exist
      if not os.path.isdir(directory):
         os.mkdir(directory)  

      last_slide = 'slide' + str(len(self.__slide)) + '.xml'

      xml = self.__location + '/ppt/slides/' + last_slide
      slide_xml = output_dir + '/ppt/slides/slide1.xml'

      rel = self.__location + '/ppt/slides/_rels/' + last_slide + '.rels'
      slide_rel = output_dir + '/ppt/slides/_rels/slide1.xml.rels'

      # Move the files
      shutil.move(xml, slide_xml)
      shutil.move(rel, slide_rel)
      
      n = len(self.__media)

      # Find which media files belong to the slide and move them
      if (n > 0):
         f = open(slide_rel, 'r')
         try:
            content = f.read()
            sections = content.split('/>')
            first = sections[0].split('<Relationship ')
            first = '<Relationship ' + first[1]
            sections[0] = first

            n = len(sections) - 1

            for i in xrange (0, n):
               line = sections[i].split()
               media_type = line[2].split('/')
               length = len(media_type)
               media_type = media_type[length - 1]
               media_type = media_type.split('"')
               media_type = media_type[0]

               if media_type in ("image", "video"):
                  target = line[3].split("=")
                  target = target[1].split('/')
                  length = len(target)
                  target = target[length - 1]
                  target = target.replace('"', "")

                  src = self.__location + '/ppt/media/' + target
                  dst = directory + "/" + target

                  if (os.path.exists(src)):
                     shutil.move(src, dst)               
               
         finally:
            f.close()

########### Accessor Methods ###############################################

   def getLocation(self):
   	'Returns location'
   	return self.__location

   def getContentTypes(self):
      'Returns location of the content types file'
      return self.__contentTypes     

   def getPresentationMain(self):
      'Returns location of the presentation main file'
      return self.__presentationMain    

   def getSlideMaster(self):
   	'Returns location of slide master file'
   	return self.__slideMaster

   def getSlides(self):
   	'Returns location of the individual slides XML files'
   	return self.__slide

   def getMedia(self):
      'Returns a list with the location of all media files'
      return self.__media

   def getExtensions(self):
      'Returns a list with all the extensions used in the presentation'
      return self.__extensions
