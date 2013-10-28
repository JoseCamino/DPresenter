import os.path
import shutil

import vcs

vcs = vcs.VCS()

def remove_dir_if_exists(path):
	if os.path.exists(path):
		shutil.rmtree(path)

def remove_test_repo():
	remove_dir_if_exists("testprojects/testrepo")

def get_vcs():
	return vcs