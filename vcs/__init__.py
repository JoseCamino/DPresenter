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
        """
        Loads a new project if it exists and returbns a VCSProject. 
        Otherwise throws an exception.
        """
        
        path = os.path.join(self.projects_location, name)
        if not os.path.exists(path):
            raise Exception("Project doesn't exist")
        
        return VCSProject(path)
        
    def create_project(self, name, project_type="presentation"):
        """
        Creates a new project if it doesn't exists and returns a VCSProject. 
        Otherwise throws an exception.
        """

        if project_type != "presentation":
            raise Exception("ERROR: Only project type presentation is supported at this time")

        path = os.path.join(self.projects_location, name)
        if os.path.exists(path):
            raise Exception("Project already exists")
            
        # Create the project directory if it doesn't exist
        try:
            os.makedirs(self.projects_location)
        except:
            pass # Most likely the project directory already exists

        # TODO: Move to the repository or some sort of abstract storage mechanism
        vcs = VCSProject(path)
        vcs._repo.create_repository() # NOTE: Should we really get into internals like that here?
        return vcs