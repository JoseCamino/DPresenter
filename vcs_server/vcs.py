import json
import os
import os.path
from os.path import isfile

def extract_args(request, *args):
	return map(lambda x: request[x], args)

class VCS(object):
	def __init__(self):
		self.projects_location = "projects"

	def handle_request(self, request):
		"Handles a request given as a dict object"
		# TODO: Implement these commands with a decorator

		command = request["command"]
		project_name = request["projectName"]

		if command == "create project":
			create_project(project_name)
		else:
			# A project already exists. Load it and parse further
			project = load_project(project_name)

			if command == "list presentations":
				pass 
			if command == "get slide data":
				pass
			if command == "persist":
				pass
			if command == "add slide":
				pass
			if command == "move slide":
				pass
			if command == "remove slide":
				pass
			if command == "checkout":
				pass
			if command == "checkin":
				pass
			# HISTORY OF A SLIDE
			# SET PREVIOUS VERSION OF A SLIDE

	def set_projects_location(self, location):
		self.projects_location = location

	def load_project(self, name):
		"Loads a new project if it exists. Otherwise throws an exception."
		path = os.path.join(self.projects_location, name)
		if not os.path.exists(path):
			raise Exception("Project doesn't exist")
		
		return VCSProject(path)
		
	def create_project(self, name):
		"Creates a new project if it doesn't exists. Otherwise throws an exception."
		path = os.path.join(self.projects_location, name)
		if os.path.exists(path):
			raise Exception("Directory already exists")
			
		# TODO: Move to the repository or some sort of abstract storage mechanism
		vcs = VCSProject(path)
		vcs._repo.create_repository() # NOTE: Should we really get into internals like that here?
		return vcs

class VCSProject(object):
	def __init__(self, path):
		self.path = path
		self._repo = FileRepository(self)

	def get_presentation(self, presentation_id="current"):
		return self._repo.load_presentation(presentation_id)

	def get_current_presentation(self):
		return self._repo.load_current_presentation()
		
	def get_presentation_list(self):
		return self._repo.load_presentation_list()

class PersistedPresentation(object):
	def __init__(self, project, presentation_id, **data):
		self.id = presentation_id
		self.name = data['name']
		self.project = project
		self._repo = project._repo
		self.slides = []

	def is_persisted(self):
		return True

	def rename(self, new_name):
		pass

class CurrentPresentation(object):
	def __init__(self, project, presentation_id, **data):
		self.id = presentation_id
		self.name = data['name']
		self.project = project
		self._repo = project._repo
		self.slides = []

	def is_persisted(self):
		return False

	def persist(self, new_name="Untitled"):
		self._repo.persist_presentation(self, new_name)

	def add_slide(self):
		pass

	def checkout(self, slide):
		pass

	def checkin(self, slide, newData):
		pass

class FileRepository(object):
	"Internal class that deals with the actual logic involved in persistence"

	def __init__(self, project):
		self.project = project

	def create_repository(self):
		# TODO: Raise if already initialized
		repository_path = self.project.path
		os.mkdir(repository_path)
		os.mkdir(os.path.join(repository_path, "presentations"))
		os.mkdir(os.path.join(repository_path, "slides"))
		self.save_presentation(CurrentPresentation(self.project, "current", name="current"))

	def make_path(self, path):
		return os.path.join(self.project.path, path)

	def load_data(self, path):
		path = self.make_path(path)
		with open(path, 'r') as file:
			return json.load(file)

	def save_data(self, path, data):
		path = self.make_path(path)
		with open(path, 'w') as file:
			json.dump(data, file)

	def persist_presentation(self, current_presentation, new_name):
		"Used to add non-current presentations to the project"
		new_id = "AHH"

		# first copy the presentation
		new_presentation = PersistedPresentation(self.project, new_id, 
			name = new_name
		)

		self.save_presentation(new_presentation)

	def save_presentation(self, presentation):
		"Saves a presentation to the correct place in the repository. If new_id is non null, "
		self.save_data("presentations/%s" % presentation.id, {
			"name": presentation.name,
			"slides": presentation.slides
		})

	def load_current_presentation(self):
		return self.load_presentation("current")

	def load_presentation_list(self):
		path = self.make_path("presentations")
		presentations = [None]
		current = None
		for filename in os.listdir(path):
			filepath = os.path.join(path, filename)
			if not isfile(filepath): continue

			data = self.load_data("presentations/%s" % filename)
			if filename == "current":
				current = CurrentPresentation(self.project, filename, **data)
			else:
				presentation = PersistedPresentation(self.project, filename, **data)
				presentations.append(presentation)

		# TODO: Sort presentations by created_at
		presentations[0] = current
		return presentations

	def load_presentation(self, pid):
		if pid == "current":
			return CurrentPresentation(self.project, pid, **self.load_data("presentations/%s" % pid))
		else:
			return PersistedPresentation(self.project, pid, **self.load_data("presentations/%s" % pid)) 
