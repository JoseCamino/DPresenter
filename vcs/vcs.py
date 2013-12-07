import json
import os
import os.path
import sqlite3
from os.path import isfile

from Parser.ParserFacade import ParserFacade

class VCSProject(object):
	"""
	Represents a single project being persisted by version control.
	"""

	def __init__(self, path):
		self.path = path
		self._repo = FileRepository(self)

	@property
	def type(self):
		return "presentation" # Only presentation projects are supported at this time

	@property
	def current_presentation(self):
		"Returns the current non-persisted presentation"
		return self._repo.load_current_presentation()

	@property
	def presentations(self):
		"Returns a list of every single presentation"
		return self._repo.load_presentation_list()

	def get_presentation(self, presentation_id):
		"Returns the presentation with the given presentation id"
		return self._repo.load_presentation(presentation_id)

	def get_slide(self, slide_id):
		"Retrieves a slide with the given slide id"
		return self._repo.load_slide(slide_id)

class Presentation(object):
	def __init__(self, project, **data):
		self._id = data.get('id', -1)
		self._name = data['name']
		self._project = project
		self._repo = project._repo

	@property
	def id(self):
	    return self._id

	@property
	def name(self):
		return self._name

	@property
	def project(self):
		return self._project

	@property
	def slides(self):
		"""
		Returns a list of slide objects.
		These slides are loaded from the database when this function is called.
		"""
		return self._repo.load_presentation_slides(self.id)

	@property
	def data(self):
		# TODO: Load and merge slide data
		return "this needs to be done"

	def is_persisted(self):
		"Returns true if this slide is persisted. Otherwise returns false."
		# Subclasses need to implement this function
		raise NotImplementedError

class CurrentPresentation(Presentation):
	def __init__(self, *args, **kwargs):
		super(CurrentPresentation, self).__init__(*args, **kwargs)

	def is_persisted(self):
		return False

	def persist(self, new_name="Untitled"):
		"""
		Creates a new presentation that has the same slide data as this one.
		Returns the newly created presentation's id
		"""
		return self._repo.persist_presentation(self, new_name)

	def add_slide(self, name="Untitled", data=None):
		"Adds a new slide to the end of the project"
		return self._repo.add_slide(self.id, name, data)

class PersistedPresentation(Presentation):
	def __init__(self, *args, **kwargs):
		super(PersistedPresentation, self).__init__(*args, **kwargs)

	def is_persisted(self):
		return True

	def rename(self, new_name):
		"Renames this presentation"
		self._repo.rename_presentation(self.id, new_name)
		self._name = new_name

class SlideList(list):
	@property
	def data(self):
		return SlideDataList(self)

# Helper used to implement the proxy pattern. Only load slide data when we need it
class SlideDataList(object):
	def __init__(self, slides):
		self._slides = slides

	def __len__(self):
		return len(self._slides)

	def __getitem__(self, key):
		return self._slides[key].data

class Slide(object):
	"Encapsulates slide data. TODO: get_original_slide and various history related functions"
	def __init__(self, project, slide_id, name, original_slide):
		self._project = project
		self._id = slide_id
		self._name = name
		self._original_slide_id = original_slide

	@property
	def id(self):
		return self._id

	@property
	def name(self):
		return self._name

	@property
	def project(self):
	    return self._project

	@property
	def original(self):
		if not self._original_slide_id:
			return None

		return self._project.get_slide(self._original_slide_id)

	@property
	def data(self):
		"""
		Retrieves the actual data contained in this slide. Slide data is not retrieved
		until this is accessed.
		"""
		return self.project._repo.load_slide_data(self.id)
	
	def checkout(self, user_id):
		"Checks out a slide, preventing checkout by other users"
		self.project._repo.checkout_slide(self.id, user_id)

	def checkin(self, user_id, newData):
		"""
		Checks in a slide, and returns the newly created slide's id.
		Fails if the slide hasn't already been checked out by "user_id"
		"""
		return self.project._repo.checkin_slide(self.id, user_id, newData)

	def save_preview(self, image_path):
		# todo: implement this
		pass

class FileRepository(object):
	"""
	Internal class that deals with the actual persistence logic.
	TODO: Perhaps split this into a facade for actual plumbing, so that we don't have to
	keep reopening sqlite instances
	"""

	def __init__(self, project):
		self.project = project

	def make_path(self, path):
		return os.path.join(self.project.path, path)

	def load_data(self, path):
		path = self.make_path(path)
		with open(path, 'rb') as file:
			return file.read()

	def save_data(self, path, data):
		path = self.make_path(path)
		with open(path, 'wb') as file:
			file.write(data)

	def connect_to_db(self):
		return sqlite3.connect(self.make_path('data.db'))

	def create_repository(self):
		# TODO: Raise if already initialized
		repository_path = self.project.path
		os.mkdir(repository_path)
		os.mkdir(os.path.join(repository_path, "slidedata"))

		with self.connect_to_db() as conn:
			c = conn.cursor()

			c.execute("""
				CREATE TABLE presentations
				(id integer primary key autoincrement, name text)
				""")

			c.execute("""
				CREATE TABLE slides
				(id integer primary key autoincrement, name text, original_slide integer)
				""")

			c.execute("""
				CREATE TABLE presentation_slides
				(presentation_id integer, slide_id integer, position integer)
				""")

			c.execute("""
				CREATE TABLE slide_checkout
				(slide_id integer, user_id text, checkout_at integer)
				""")


		self.create_presentation(CurrentPresentation(self.project, name="current"))

	def persist_presentation(self, current_presentation, new_name):
		"Used to add non-current presentations to the project"

		with self.connect_to_db() as conn:
			c = conn.cursor()

			c.execute("""
				INSERT INTO presentations (name)
				VALUES (?)
				""", [new_name])
			new_presentation_id = c.lastrowid

			# Copy slides
			c.execute("""
				INSERT INTO presentation_slides (presentation_id, slide_id, position)
				SELECT ?, slide_id, position
				FROM presentation_slides
				WHERE presentation_id = ?
				""", [new_presentation_id, current_presentation.id])

			return new_presentation_id

	def rename_presentation(self, pid, new_name):
		with self.connect_to_db() as conn:
			c = conn.cursor()

			c.execute("""
				UPDATE presentations
				SET name = ?
				WHERE id = ?
				""", [new_name, pid])

	def create_presentation(self, presentation):
		"Creates a new presentation."
		with self.connect_to_db() as conn:
			c = conn.cursor()

			c.execute("""
				INSERT INTO presentations (name)
				VALUES (?)
				""", [presentation.name])

	def save_presentation(self, presentation):
		"Saves a presentation."

		with self.connect_to_db() as conn:
			c = conn.cursor()

			c.execute("""
				UPDATE presentations
				SET name = ?
				WHERE id = ?
				""", [presentation.id])

	def load_current_presentation(self):
		# Todo: make more efficient
		return self.load_presentation_list()[0]

	def load_presentation_list(self):
		presentations = []

		with self.connect_to_db() as conn:
			c = conn.cursor()

			c.execute("""
				SELECT id, name
				FROM presentations
				ORDER BY id ASC
				""")

			for row in c.fetchall():
				pid = row[0]
				name = row[1]

				presentation_data = {
					'id': pid,
					'name': name
				}

				if not presentations:
					presentations.append(CurrentPresentation(self.project, **presentation_data))
				else:
					presentations.append(PersistedPresentation(self.project, **presentation_data))

		return presentations

	def load_presentation(self, pid):
		with self.connect_to_db() as conn:
			c = conn.cursor()

			c.execute("""
				SELECT name
				FROM presentations
				WHERE id = ?
				""", [pid])

			data = c.fetchone()
			name = data[0]
			presentation_data = {
				'id': pid,
				'name': name
			}

			if pid == 1: # TODO: Use a non-hardcoded value that doesn't depend on sqlite implementation
				return CurrentPresentation(self.project, **presentation_data)
			else:
				return PersistedPresentation(self.project, **presentation_data) 

	def load_presentation_slides(self, pid):
		with self.connect_to_db() as conn:
			c = conn.cursor()

			c.execute("""
				SELECT ps.slide_id, s.name, s.original_slide
				FROM presentation_slides ps 
					JOIN slides s
						ON ps.slide_id = s.id
				WHERE presentation_id = ?
				ORDER BY position ASC
				""", [pid])

			slides = SlideList()
			for row in c.fetchall():
				slide_id = row[0]
				name = row[1]
				original_slide = row[2]
				slide = Slide(self.project, slide_id, name, original_slide)
				slides.append(slide)

			return slides

	def load_slide(self, slide_id):
		with self.connect_to_db() as conn:
			c = conn.cursor()

			# todo: load more data
			c.execute("""
				SELECT id, name, original_slide
				FROM slides
				WHERE id = ?
				""", [slide_id])

			row = c.fetchone()
			if row:
				slide_id = row[0]
				name = row[1]
				original_slide = row[2]
				return Slide(self.project, slide_id, name, original_slide)

			raise Exception("Slide with id %s doesn't exist" % slide_id)

	def load_slide_data(self, slide_id):
		return self.load_data("slidedata/%d" % slide_id)

	def add_slide(self, pid, slide_name, data):
		"Adds an empty slide to the presentation."
		# TODO: perhaps just get the current presentation id instead of getting it as a parameter?

		# TODO: Make this information change depending by project type
		if data is None:
			data = ParserFacade.generateNewSlide()

		with self.connect_to_db() as conn:
			c = conn.cursor()

			# Add the slide to the database
			c.execute("""
				INSERT INTO slides (name, original_slide)
				VALUES (?, NULL)
				""", [slide_name])

			slide_id = c.lastrowid

			# Add the empty slide to the file system
			self.save_data("slidedata/%d" % slide_id, data)

			# Register this slide as part of the presentation.
			# TODO: new slide should be at the end. Make sure to update position
			c.execute("""
				INSERT INTO presentation_slides (presentation_id, slide_id)
				VALUES (?, ?)
				""", [pid, slide_id])

			return slide_id

	def checkout_slide(self, slide_id, user_id):
		with self.connect_to_db() as conn:
			c = conn.cursor()

			# TODO: Check if the slide exists
			# TODO: Check if the slide is part of the current presentation

			# Check if the slide has been checked out
			c.execute("""
				SELECT COUNT(*)
				FROM slide_checkout
				WHERE slide_id = ?
				""", [slide_id])

			if c.fetchone()[0] > 0:
				raise Exception("Slide has already been checked out")

			c.execute("""
				INSERT INTO slide_checkout(slide_id, user_id, checkout_at)
				VALUES (?, ?, datetime('now'))
				""", [slide_id, user_id])

	def checkin_slide(self, slide_id, user_id, data):
		with self.connect_to_db() as conn:
			c = conn.cursor()
		
			# Check if the slide has been checked out
			c.execute("""
				SELECT s.original_slide, c.user_id
				FROM slide_checkout c
					JOIN slides s
						ON s.id = c.slide_id
				WHERE slide_id = ?
				""", [slide_id])

			row = c.fetchone()
			if not row:
				raise Exception("Slide isn't checked out")
			elif row[1] != user_id:
				raise Exception("This slide is checked out by another user")

			original_slide = row[0] if row[0] else slide_id

			# Add the new slide to the database
			c.execute("""
				INSERT INTO slides (name, original_slide)
				VALUES ((SELECT name FROM slides WHERE id = ?), ?)
				""", [slide_id, original_slide])
			new_slide_id = c.lastrowid

			# Update the current presentation to point to the new slide
			c.execute("""
				UPDATE presentation_slides
				SET slide_id = ?
				WHERE slide_id = ?
				  AND presentation_id = (SELECT id
				  	                     FROM presentations
				  	                     ORDER BY id ASC
				  	                     LIMIT 1)
				""", [new_slide_id, slide_id])

			# Add the new slide data
			self.save_data("slidedata/%d" % new_slide_id, data)

			# Remove the slide from the checkout list
			c.execute("""
				DELETE FROM slide_checkout
				WHERE slide_id = ?
				""", [slide_id])

			return new_slide_id