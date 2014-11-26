<<<<<<< HEAD
DynamicPresenter
================

Parser Subsystem
----------------
Import the ParserFacade class and call the following methods:

Splitting a deck:
```
ParserFacade.splitDeck(deck)	#Splits a deck into individual slides. Returns a list of slides (as binary data).
```

Merging slides:
```
ParserFacade.mergeSlides(slides)	#Merges any number of slides into a deck. Input is the slides binary data. Returns the path of a temporary deck that can be deleted after it is downloaded.
```

Generating images:
```
ParserFacade.generateImageFromData(data, image_paths)	#Generates an image file from each slide. Input is the binary data of the slide or deck and the list of paths of the images to be generated.
```

Generating blank slide:
```
ParserFacade.generateNewSlide()	#Generates a blank slide and returns its binary data.
```
Generating "default" confidential slide:
```
ParserFacade.generateConfidentialSlide()	#Generates a slide with a message warning the user that the contents of the slide are confidential. Returns the binary data of the slide.
```

VCS Subsystem
-------------
Some sample code to use the VCS subsystem can be found in createtestrepo.py, but here is a reduced version of that sample code

```python
import os.path
import shutil

from vcs import VCS

vcs = VCS()
vcs.set_project_directory("testprojects") # Make sure this directory exists

# Create project
project = vcs.create_project("testcreatingprojects")
presentation = project.get_current_presentation()

# Add slides
slide1 = presentation.add_slide("Slide 1")
slide2 = presentation.add_slide("Slide 2")

# Update slide 1
presentation.checkout(slide1, "testuser")
slide1 = presentation.checkin(slide1, "testuser", "This is slide 1")

# Update slide 2
presentation.checkout(slide2, "testuser")
slide2 = presentation.checkin(slide2, "testuser", "This is slide 2")

# Update slide 2 again
presentation.checkout(slide2, "testuser")
slide2 = presentation.checkin(slide2, "testuser", "This is slide 2 (updated)")

# Leave slide 1 checked out
presentation.checkout(slide1, "testuser")

print("Created slides: ")
for (i, slide) in enumerate(presentation.slides):
	print("Slide #%d: %s" % (i, slide.data))
```
=======
DPresenter
==========

Senior Project
>>>>>>> origin/master
