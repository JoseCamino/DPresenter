import os.path
import shutil

import vcs

vcs = vcs.VCS()
file_dir = os.path.dirname(__file__)

def remove_dir_if_exists(path):
	if os.path.exists(path):
		shutil.rmtree(path)

def remove_data_inside_test_dir():
	path = os.path.join(file_dir, "testdata")
	for filepath in os.listdir(path):
		os.remove(filepath)

def remove_test_repo():
	remove_dir_if_exists("testprojects/testrepo")

def get_vcs():
	return vcs