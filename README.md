DynamicPresenter
================

Parser Subsystem
----------------
Import the ParserFacade class and call the following methods:

Splitting a deck:
```
ParserFacade.splitDeck(presentation_path, output_folder)   # returns a list with the location of all slides
```

Merging slides:
```
ParserFacade.mergeSlides(list_of_slide_locations, deck_path)   # returns the deck_path
```

Generating images:
```
ParserFacade.generateImage(presentation_path,  output_folder)   # returns a list with the location of all the images
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
for (i, slide) in enumerate(presentation.get_slides()):
	print("Slide #%d: %s" % (i, slide.data))
```