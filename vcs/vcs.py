import json
import os
import os.path
import sqlite3
from os.path import isfile

class VCSProject(object):
	def __init__(self, path):
		self.path = path
		self._repo = FileRepository(self)

	def get_presentation(self, presentation_id):
		return self._repo.load_presentation(presentation_id)

	def get_current_presentation(self):
		return self._repo.load_current_presentation()
		
	def get_presentation_list(self):
		return self._repo.load_presentation_list()

class Presentation(object):
	def get_slides(self):
		return self._repo.load_presentation_slides(self.id)

class CurrentPresentation(Presentation):
	def __init__(self, project, **data):
		self.id = data.get('id', -1)
		self.name = data['name']
		self.project = project
		self._repo = project._repo
		self.slides = []

	def is_persisted(self):
		return False

	def persist(self, new_name="Untitled"):
		return self._repo.persist_presentation(self, new_name)

	def add_slide(self):
		return self._repo.add_slide(self.id, "Untitled")

	def checkout(self, slide_id, user_id):
		self._repo.checkout_slide(slide_id, user_id)

	def checkin(self, slide_id, user_id, newData):
		self._repo.checkin_slide(slide_id, user_id, newData)

class PersistedPresentation(Presentation):
	def __init__(self, project, **data):
		self.id = data.get('id', -1)
		self.name = data['name']
		self.project = project
		self._repo = project._repo
		self.slides = []

	def is_persisted(self):
		return True

	def rename(self, new_name):
		self._repo.rename_presentation(self.id, new_name)
		self.name = new_name

class Slide(object):
	"Encapsulates slide data. TODO: get_original_slide and various history related functions"
	def __init__(self, slide_id, data):
		self.id = slide_id
		self.data = data

class FileRepository(object):
	"""
	Internal class that deals with the actual logic involved in persistence.
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
			# TODO: only load slide ids here, not full slides. This is too slow.
			slides = self.load_presentation_slides(current_presentation.id)
			for (i, slide) in enumerate(slides):
				c.execute("""
					INSERT INTO presentation_slides (presentation_id, slide_id, position)
					VALUES (?, ?, ?)
					""", [new_presentation_id, slide.id, i])

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
				SELECT slide_id
				FROM presentation_slides
				WHERE presentation_id = ?
				ORDER BY position ASC
				""", [pid])

			slides = []
			for row in c.fetchall():
				slide_id = row[0]
				slide_data = self.load_data("slidedata/%d" % slide_id)
				slide = Slide(slide_id, slide_data)
				slides.append(slide)

			return slides

	def add_slide(self, pid, slide_name):
		"Adds an empty slide to the presentation. TODO: perhaps just get the current presentation id instead of retrieving it?"

		with self.connect_to_db() as conn:
			c = conn.cursor()

			# Add the slide to the database
			c.execute("""
				INSERT INTO slides (name, original_slide)
				VALUES (?, NULL)
				""", [slide_name])

			slide_id = c.lastrowid

			# Add the empty slide to the file system
			self.save_data("slidedata/%d" % slide_id, "")

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
				SELECT user_id
				FROM slide_checkout
				WHERE slide_id = ?
				""", [slide_id])

			row = c.fetchone()
			if not row:
				raise Exception("Slide isn't checked out")
			elif row[0] != user_id:
				raise Exception("This slide is checked out by another user")

			c.execute("""
				DELETE FROM slide_checkout
				WHERE slide_id = ?
				""", [slide_id])

			# Update the actual slide data
			self.save_data("slidedata/%d" % slide_id, data)

