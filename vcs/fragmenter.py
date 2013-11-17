from Parser.ParserFacade import ParserFacade

class PresentationFragmenter(object):
	"""
	A fragmenter used for powerpoint presentations which takes a presentations
	and splits it into multiple slides. This is used if the data given by the user
	consists of multiple slides.
	"""

	def fragment(self, presentation_data):
		slide_data_list = ParserFacade.splitDeck(presentation_data)
		return slide_data_list

	def fragment_file(self, path):
		# NOTE: This is temporary until the parser supports file data
		return self.fragment(path)
		
		# TODO: Support file objects
		with open(path, "r") as file:
			return self.fragment(file.read())