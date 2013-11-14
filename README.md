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