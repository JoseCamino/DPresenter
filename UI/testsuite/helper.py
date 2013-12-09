import os.path
import shutil

def remove_dir_if_exists(path):
	if os.path.exists(path):
		shutil.rmtree(path)