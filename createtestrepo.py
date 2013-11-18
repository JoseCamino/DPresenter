import os.path
import shutil

from vcs import VCS

def remove_dir_if_exists(path):
	if os.path.exists(path):
		shutil.rmtree(path)

if __name__ == '__main__':
    remove_dir_if_exists("testprojects/testcreatingprojects")

    vcs = VCS()
    vcs.set_project_directory("testprojects")
    
    # Create project
    project = vcs.create_project("testcreatingprojects")
    presentation = project.current_presentation

    # Add slides
    slide1 = presentation.add_slide("Slide 1")
    slide2 = presentation.add_slide("Slide 2")
    slide3 = presentation.add_slide("Slide 3")

    # Update slide 1
    presentation.checkout(slide1, "testuser")
    slide1 = presentation.checkin(slide1, "testuser", "This is slide 1")

    # Update slide 2
    presentation.checkout(slide2, "testuser")
    slide2 = presentation.checkin(slide2, "testuser", "This is slide 2")

    # Update slide 3
    presentation.checkout(slide3, "testuser")
    slide3 = presentation.checkin(slide3, "testuser", "This is slide 3")

    # Update slide 3 again
    presentation.checkout(slide3, "testuser")
    slide3 = presentation.checkin(slide3, "testuser", "This is slide 3 (updated)")

    # Leave slide 1 checked out
    presentation.checkout(slide1, "testuser")

    print("Created slides: ")
    for slide in presentation.slides:
        print("%s: %s" % (slide.name, slide.data))