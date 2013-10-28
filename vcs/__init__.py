import io
import os
import os.path
from vcs import VCSProject

class VCS(object):
    def __init__(self):
        self.projects_location = "projects"

    def set_project_directory(self, location):
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