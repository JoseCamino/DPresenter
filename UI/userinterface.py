from datetime import timedelta
from flask import Flask, session, render_template, request, send_from_directory, redirect, url_for, Response
from flask.ext.bootstrap import Bootstrap
import os
from werkzeug import secure_filename
import dbc
from vcs import VCS

app = Flask(__name__)
app.permanent_session_lifetime = timedelta(minutes=15)
app.debug = True
app.config['UPLOAD_FOLDER'] = '/models'
ALLOWED_EXTENSIONS = set(['pptx', 'ppt'])
app.secret_key = dbc.giveMetheSecretKey()
Bootstrap(app)

@app.route("/")
def login():
	if 'username' in session:
		projList = dbc.getProjectList(session['username'])
		return render_template("index.html", stuff = projList)
	return render_template("login.html", warning = "")

@app.route("/login.html")
def logout():
	session.pop('username', None)
	return render_template('login.html', warning = "")

@app.route("/index.html", methods = ['POST','GET'])
def index():
	error = None
	if request.method == 'POST':
		uname = request.form['username']
		if(uname == ""):
			return render_template("login.html", warning = "Username field is required.")
		password = request.form['password']
		if(password == ""):
			return render_template("login.html", warning = "Password field is required.")
		if dbc.checkPassword(uname, password):
			session['username'] = uname
			projList = dbc.getProjectList(uname)
			return render_template('index.html', stuff = projList, warning = "")
		else:
			return render_template("login.html", warning = "Invalid username/password combination.  Please try again.")
	if 'username' in session:
		projList = dbc.getProjectList(session['username'])
		return render_template("index.html", stuff = projList)
	else:
		return render_template("login.html", warning = "Please log-in to the system.")

@app.route("/createProject.html")
def createProject():
	if 'username' in session:
		return render_template("createProject.html")
	return render_template("login.html", warning = "Please log-in to the system.")

@app.route("/buildProject.html", methods = ['POST'])
def buildProject():
	if 'username' not in session:
		return render_template("login.html", warning = "Please log-in to the system.")
	if request.method == 'POST':
		projName = request.form['projname']
		id_name = dbc.addProject(session['username'], projName)
		try:
			float(id_name)  
			VCS().create_project(str(id_name))
			projList = dbc.getProjectList(session['username'])
			return render_template("index.html", stuff = projList, warning = "You have created a new project!")
   		except ValueError:
			projList = dbc.getProjectList(session['username'])
			return render_template("index.html", stuff = projList, warning = id_name)
	return illegal_action("error")

@app.route("/projects/<int:project_id>")
def show_project(project_id):
	if 'username' not in session:
		return render_template("login.html", warning = "Please log-in to the system.")
	project = VCS().load_project(str(project_id))
	status = "Unlocked"
	if(dbc.getProjectStatus(project_id)) == True:
		status = "Frozen"
	if dbc.getRole(project_id, session['username']) == 'Project Manager':
		printMii = dbc.getUserList(project_id)
		printMiiToo = dbc.deletableUserList(project_id)
		return render_template('project1.html', userList = printMii, removeMii = printMiiToo, project = project_id, name = dbc.getProjectName(project_id), warning = "Status of Project: %s" % status)
	if dbc.getRole(project_id, session['username']) == 'Presentation Creator':
		printMii = project.persisted_presentations
		printMiiThree = project.current_presentation
		printMiiToo = project.current_presentation.slides
		printMii4 = dbc.getUserNameList(project_id)		
		return render_template('project3.html', users = printMii4, presentationList = printMii, current = printMiiThree, slideList = printMiiToo, project = project_id, name = dbc.getProjectName(project_id), warning = "Status of Project: %s" % status)
	if dbc.getRole(project_id, session['username']) == 'Slide Creator':
		printMii = project.current_presentation.slides
		return render_template('project2.html', slideList = printMii, project = project_id, name = dbc.getProjectName(project_id), warning = "Status of Project: %s" % status)
	return not_allowed("error")

@app.route("/projects/<int:project_id>/addUserstoProject")
def add_user_to_project(project_id):
	if 'username' not in session:
		return render_template("login.html", warning = "Please log-in to the system.")
	if not dbc.getRole(project_id, session['username']) == "Project Manager":
		return not_allowed("error")
	return render_template("addUsertoProject.html", project_id = project_id)

@app.route("/projects/<int:project_id>/added", methods = ['POST'])
def addUserToProject(project_id):
	if not 'username' in session:
		return render_template("login.html", warning = "Please log-in to the system.")
	if not dbc.getRole(project_id, session['username']) == "Project Manager":
		return not_allowed("error")
	if request.method == 'POST':
		uname_to_add = request.form['username']
		if uname_to_add == "":
			printMii = dbc.getUserList(project_id)
			printMiiToo = dbc.deletableUserList(project_id)
			return render_template('project1.html', userList = printMii, removeMii = printMiiToo, project = project_id, name = dbc.getProjectName(project_id), warning = "Umm...need to add a username cheif.")
		if not dbc.userExists(uname_to_add):
			printMii = dbc.getUserList(project_id)			
			printMiiToo = dbc.deletableUserList(project_id)
			return render_template('project1.html', userList = printMii,  removeMii = printMiiToo, project = project_id, name = dbc.getProjectName(project_id), warning = "User not found in the system!")
		if dbc.userInProject(uname_to_add, project_id):			
			printMiiToo = dbc.deletableUserList(project_id)
			printMii = dbc.getUserList(project_id)
			return render_template('project1.html', userList = printMii,  removeMii = printMiiToo, project = project_id, name = dbc.getProjectName(project_id), warning = "User already exists in the project!")
		role_to_add = request.form['role']
		if not (role_to_add == "Presentation Creator" or "Slide Creator"):
			printMii = dbc.getUserList(project_id)			
			printMiiToo = dbc.deletableUserList(project_id)
			return render_template('project1.html', userList = printMii,  removeMii = printMiiToo, project = project_id, name = dbc.getProjectName(project_id), warning = "INVALID ROLE SELECTION!")
		dbc.addUserToProject(project_id, uname_to_add, role_to_add)
		printMii = dbc.getUserList(project_id)		
		printMiiToo = dbc.deletableUserList(project_id)
		return render_template('project1.html', userList = printMii,  removeMii = printMiiToo, project = project_id, name = dbc.getProjectName(project_id), warning = "User added to project")
	return illegal_action("error")

@app.route("/projects/<int:project_id>/createPresentation", methods = ['POST'])
def createPresentation(project_id):
	if not 'username' in session:
		return render_template("login.html", warning = "Please log-in to the system.")
	if dbc.getRole(project_id, session['username']) != "Presentation Creator" and dbc.getRole(project_id, session['username']) != "Project Manager":
		return not_allowed("error")
	if request.method == "POST":
		project = VCS().load_project(str(project_id))
		nameMii = request.form['presentation_name']
		print nameMii
		project.current_presentation.persist(nameMii)
		printMii = project.persisted_presentations
		printMiiToo = project.current_presentation
		printMiiThree = project.current_presentation.slides
		printMii4 = dbc.getUserNameList(project_id)
		return render_template("project3.html", users = printMii4, slideList = printMiiThree, presentationList = printMii, current = printMiiToo, project = project_id, name = dbc.getProjectName(project_id), warning = "New Presentation Persisted") 
	return illegal_action("error")

@app.route("/projects/<int:project_id>/presentations")
def viewPresentations(project_id):
	if not 'username' in session:
		return render_template("login.html", warning = "Please log-in to the system.")
	if dbc.getRole(project_id, session['username']) != "Project Manager":
		return not_allowed("error") 
	printMii = VCS().load_project(str(project_id)).persisted_presentations
	printMiiThree = VCS().load_project(str(project_id)).current_presentation
	printMiiToo = VCS().load_project(str(project_id)).current_presentation.slides
	printMii4 = dbc.getUserNameList(project_id)
	status = "Unlocked"
	if dbc.getProjectStatus(project_id) == True:
		status = "Frozen"
	return render_template("project3.html", users = printMii4, current = printMiiThree, presentationList = printMii, slideList = printMiiToo, project = project_id, name = dbc.getProjectName(project_id), warning = "Status of Project: %s" % status)

@app.route("/projects/<int:project_id>/<int:presentation_id>/download")
def downloadPresentation(project_id, presentation_id):
	if not 'username' in session:
		return render_template("login.html", warning = "Please log-in to the system.")
	if dbc.getRole(project_id, session['username']) != "Project Manager" and dbc.getRole(project_id, session['username']) != 'Presentation Creator' and dbc.getRole(project_id, session['username']) != 'Slide Creator':
		return not_allowed("error") 
	return "This is still not implemented...holy shit how hard chan this be?!"

@app.route("/projects/<int:project_id>/revertPresentation", methods = ['POST'])
def revertPresentation(project_id):
	if not 'username' in session:
		return render_template("login.html", warning = "Please log-in to the system.")
	if dbc.getRole(project_id, session['username']) != "Project Manager" and dbc.getRole(project_id, session['username']) != 'Presentation Creator':
		return not allwed("error")
	if request.method == 'POST':
		project = VCS().load_project(str(project_id))	
		presentation = project.get_presentation(request.form['presentation_id'])
		presentation.restore()
		printMii = project.persisted_presentations		
		printMiiThree = project.current_presentation
		printMiiToo = project.current_presentation.slides
		printMii4 = dbc.getUserNameList(project_id)
		return render_template('project3.html', users = printMii4, current = printMiiThree, presentationList = printMii, slideList = printMiiToo, project = project_id, name = dbc.getProjectName(project_id), warning = "Current Presentation has been reverted")
	return illegal_action("error")

@app.route("/projects/<int:project_id>/<int:presentation_id>")
def viewSlides(project_id, presentation_id):
	if not 'username' in session:
		return render_template("login.html", warning = "Please log-in to the system.")
	if dbc.getRole(project_id, session['username']) != "Presentation Creator" and dbc.getRole(project_id, session['username']) != "Project Manager":
		return not_allowed("error")
	presentation = VCS().load_project(str(project_id)).get_presentation(presentation_id)
	printMii = presentation.slides
	return render_template("viewPresentation.html", project_id = project_id, presentation_id = presentation_id, name = presentation.name, slideList = printMii)

@app.route("/projects/<int:project_id>/presentations/current")
def presentation(project_id):
	if not 'username' in session:
		return render_template("login.html", warning = "Please Log-in to the system.")
	if dbc.getRole(project_id, session['username']) != "Project Manager" and dbc.getRole(project_id, session['username']) != "Presentation Creator":
		return not_allowed("error")
	slidesInPresentation = VCS().load_project(str(project_id)).current_presentation.slides
	status = "Unlocked"
	if dbc.getProjectStatus == True:
		status = "Frozen"
	return render_template("project2.html", slideList = slidesInPresentation, project = project_id, name = dbc.getProjectName(project_id), warning = "Status of Project: %s" % status)

@app.route("/projects/<int:project_id>/deauthorizeCheckOut")
def revokeCheckOut(project_id):
	if not 'username' in session:
		return render_template("login.html", warning = "Please log-in to the system.")
	if dbc.getRole(project_id, session['username']) != 'Project Manager' and dbc.getRole(project_id, session['username']) != 'Presentation Creator':
		return not_allowed("error")
	currentPresentation = VCS().load_project(str(project_id)).current_presentation
	userList = dbc.getUserNameList(project_id)
	#This should never realistically happen, but just in case.
	if len(userList) == 0:
		printMii = VCS().load_project(str(project_id)).persisted_presentations		
		printMiiThree = VCS().load_project(str(project_id)).current_presentation
		printMii4 = dbc.getUserNameList(project_id)
		return render_template('project3.html', users = printMii4, current = printMiiThree, presentationList = printMii, project = project_id, name = dbc.getProjectName(project_id), warning = "Project Manager needs to add users first to the project.")
	#End unrealisitc occurrence
	slideList = currentPresentation.slides
	if len(slideList) == 0:
		printMii = VCS().load_project(str(project_id)).persisted_presentations		
		printMiiThree = VCS().load_project(str(project_id)).current_presentation
		printMiiToo = VCS.load_project(str(project_id)).current_presentation.slides
		printMii4 = dbc.getUserNameList(project_id)
		return render_template('project3.html', users = printMii4, current = printMiiThree, presentationList = printMii, slideList = printMiiToo, project = project_id, name = dbc.getProjectName(project_id), warning = "You need to make some slides for the project first.")
	return render_template("deauthorizeCheckOut.html", slides = slideList, users = userList, project_id = project_id)

@app.route("/project/<int:project_id>/deauthorized", methods = ['POST'])
def deauthorized(project_id):
	if not 'username' in session:
		return render_template("login.html", warning = "Please log-in to the system.")
	if dbc.getRole(project_id, session['username']) != 'Project Manager' and dbc.getRole(project_id, session['username']) != 'Presentation Creator':
		return not_allowed("error")
	if request.method == 'POST':
		slide_id = request.form['slide_ID']
		slide = VCS().load_project(str(project_id)).get_slide(slide_id)
		slide.cancel_checkout()
		printMii = VCS().load_project(str(project_id)).persisted_presentations		
		printMiiThree = VCS().load_project(str(project_id)).current_presentation
		printMiiToo = VCS().load_project(str(project_id)).current_presentation.slides
		printMii4 = dbc.getUserNameList(project_id)
		return render_template('project3.html', users = printMii4, current = printMiiThree, presentationList = printMii, slideList = printMiiToo, project = project_id, name = dbc.getProjectName(project_id), warning = "Slide %s checkout has been removed" % VCS().load_project(str(project_id)).get_slide(slide_id).name)
	return illegal_action("error")

@app.route("/projects/<int:project_id>/checkedOut", methods = ['POST'])
def checkOut(project_id):
	if not 'username' in session:
		return render_template("login.html", warning = "Please Log-in to the system.")
	if dbc.getRole(project_id, session['username']) != 'Project Manager' and dbc.getRole(project_id, session['username']) != 'Presentation Creator':
		return not_allowed("error")
	if request.method == 'POST':
		project = VCS().load_project(str(project_id))
		user = request.form['username']
		slide = request.form['slide_ID']
		if project.get_slide(slide).checkout_user != None:
			printMii = VCS().load_project(str(project_id)).persisted_presentations		
			printMiiThree = VCS().load_project(str(project_id)).current_presentation
			printMiiToo = project.current_presentation.slides
			printMii4 = dbc.getUserNameList(project_id)
			return render_template('project3.html', users = printMii4, current = printMiiThree, presentationList = printMii, project = project_id, slideList = printMiiToo, name = dbc.getProjectName(project_id), warning = "Slide %s checkout failed. It's already been checked out." % VCS().load_project(str(project_id)).get_slide(slide).name)
		project.get_slide(slide).checkout(user)
		printMii = project.persisted_presentations
		printMiiThree = project.current_presentation
		printMiiToo = project.current_presentation.slides
		printMii4 = dbc.getUserNameList(project_id)
		return render_template('project3.html', users = printMii4, current = printMiiThree, presentationList = printMii, project = project_id, slideList = printMiiToo, name = dbc.getProjectName(project_id), warning = "Slide %s has been checked out." % VCS().load_project(str(project_id)).get_slide(slide).name)
	return illegal_action("error")

@app.route("/projects/<int:project_id>/slideCreatorCheckedOut", methods = ['POST'])
def slideCheckedOut(project_id):	
	if not 'username' in session:
		return render_template("login.html", warning = "Please Log-in to the system.")
	if dbc.getRole(project_id, session['username']) != 'Project Manager' and dbc.getRole(project_id, session['username']) != 'Presentation Creator' and dbc.getRole(project_id, session['username']) != 'Slide Creator':
		return not_allowed("error")
	if request.method == 'POST':
		project = VCS().load_project(str(project_id))
		slide = request.form['slide_ID']
		if(project.get_slide(slide).checkout_user != None):
			printMii = project.current_presentation.slides
			return render_template('project2.html', slideList = printMii, project = project_id, name = dbc.getProjectName(project_id), warning = "Slide %s checkout failed. It's already checkd out." % slide)
		project.get_slide(slide).checkout(session['username'])
		printMii = project.current_presentation.slides
		return render_template('project2.html', slideList = printMii, project = project_id, name = dbc.getProjectName(project_id), warning = "Slide %s has been checked out." % slide)
	return illegal_action("error")

@app.route("/projects/<int:project_id>/removed", methods = ['POST'])
def removeUserFromProject(project_id):
	if request.method == 'POST':
		if not 'username' in session:
			return render_template("login.html", warning = "Please log-in to the system.")
		if not dbc.getRole(project_id, session['username']) == "Project Manager":
			return not_allowed("error")
		userToBeRemoved = request.form['username']
		print userToBeRemoved
		if dbc.getRole(project_id, userToBeRemoved) == 'Project Manager':
			return not_allowed("error")
		dbc.removeUser(userToBeRemoved, project_id)
		printMii = dbc.getUserList(project_id)	
		printMiiToo = dbc.deletableUserList(project_id)
		return render_template('project1.html', userList = printMii, removeMii = printMiiToo, project = project_id, name = dbc.getProjectName(project_id), warning = "%s has been removed from the project." % userToBeRemoved)
	return illegal_action("error")

@app.route("/projects/<int:project_id>/checkIn")
def checkInSlide(project_id):
	if not 'username' in session:
		return render_template("login.html", warning = "Please log-in to the system.")
	if dbc.getRole(project_id, session['username']) != "Slide Creator" and dbc.getRole(project_id, session['username']) != "Project Manager" and dbc.getRole(project_id, session['username']) != "Presentation Creator":
		return not_allowed("error")
	if dbc.getProjectStatus(project_id) == True:
		printMii = VCS().load_project(str(project_id)).current_presentation.slides
		return render_template('project2.html', slideList = printMii, project = project_id, name = dbc.getProjectName(project_id), warning = "Project is FROZEN.  No Check-ins Allowed.")
	slides = VCS().load_project(str(project_id)).current_presentation.slides
	return render_template("checkIn.html", project_id = project_id, slideList = slides)

@app.route("/projects/<int:project_id>/checkedIn", methods = ['POST'])
def checkedIn(project_id):
	if not 'username' in session:
		return render_template("login.html", warning = "Please log-in to the system.")
	if dbc.getRole(project_id, session['username']) != "Slide Creator" and dbc.getRole(project_id, session['username']) != "Project Manager" and dbc.getRole(project_id, session['username']) != "Presentation Creator":
		return not_allowed("error")
	if request.method == 'POST':
		user = session['username']
		slideObject = VCS().load_project(str(project_id)).get_slide(request.form['slide_id'])
		if slideObject.checkout_user != user:			
			printMii = VCS().load_project(str(project_id)).current_presentation.slides
			return render_template('project2.html', slideList = printMii, project = project_id, name = dbc.getProjectName(project_id), warning = "Check In %s failed.  You don't have that checked out." % slideObject.name)
		stuff = request.files['slide_file']
		if stuff and isFileAllowed(stuff.filename):
			slideObject.checkin(user, stuff.read())			
			printMii = VCS().load_project(str(project_id)).current_presentation.slides
			return render_template('project2.html', slideList = printMii, project = project_id, name = dbc.getProjectName(project_id), warning = "Slide %s has been checked in." % slideObject.name)
		printMii = VCS().load_project(str(project_id)).current_presentation.slides
		return render_template('project2.html', slideList = printMii, project = project_id, name = dbc.getProjectName(project_id), warning = "Only use powerpoint files to check in please.")
	return illegal_action("error")

@app.route("/projects/<int:project_id>/projectStatus")
def changeProjectStatus(project_id):
	if not 'username' in session:
		return render_template("login.html", warning = "Please log-in to the system.")
	if dbc.getRole(project_id, session['username']) != 'Presentation Creator' and dbc.getRole(project_id, session['username']) != 'Project Manager':
		return not_allowed("error")
	return render_template("changeStatus.html", project_id = project_id)

@app.route("/projects/<int:project_id>/changeProjectStatus", methods = ['POST'])
def statusChange(project_id):
	if not 'username' in session:
		return render_template("login.html", warning = "Please log-in to the system.")
	if dbc.getRole(project_id, session['username']) != 'Presentation Creator' and dbc.getRole(project_id, session['username']) != 'Project Manager':
		return not_allowed("error")
	if request.method == 'POST':
		value = request.form['status']
		dbc.setProjectStatus(project_id, value)
		if value == True:
			value = "Frozen"
		else:
			value = "Released"
		if dbc.getRole(project_id, session['username']) == 'Presentation Creator':
			printMii = VCS().load_project(str(project_id)).persisted_presentations		
			printMiiThree = VCS().load_project(str(project_id)).current_presentation
			printMiiToo = VCS().load_project(str(project_id)).current_presentation.slides
			printMii4 = dbc.getUserNameList(project_id)
			return render_template('project3.html', slideList = printMiiToo, users = printMii4, current = printMiiThree, presentationList = printMii, project = project_id, name = dbc.getProjectName(project_id), warning = "Project is now %s." % value)
		printMii = dbc.getUserList(project_id)		
		printMiiToo = dbc.deletableUserList(project_id)
		return render_template('project1.html', userList = printMii, removeMii = printMiiToo, project = project_id, name = dbc.getProjectName(project_id), warning = "Project is now %s." % value)
	return illegal_action("error")

@app.route("/projects/<int:project_id>/addASlide")
def addASlide(project_id):
	if not 'username' in session:		
		return render_template("login.html", warning = "Please log-in to the system.")
	if dbc.getRole(project_id, session['username']) != "Project Manager" and dbc.getRole(project_id, session['username']) != "Presentation Creator" and dbc.getRole(project_id, session['username']) != "Slide Creator":
		return not_allowed("error")
	return render_template('addASlide.html', project_id = project_id)

@app.route("/projects/<int:project_id>/addSlide", methods = ['POST'])
def addSlide(project_id):	
	if not 'username' in session:		
		return render_template("login.html", warning = "Please log-in to the system.")
	if dbc.getRole(project_id, session['username']) != "Project Manager" and dbc.getRole(project_id, session['username']) != "Presentation Creator" and dbc.getRole(project_id, session['username']) != "Slide Creator":
		return not_allowed("error")
	if request.method == 'POST':
		slideName = request.form['name']
		project = VCS().load_project(str(project_id))
		project.current_presentation.add_slide(slideName)
		printMii = project.current_presentation.slides
		return render_template('project2.html', slideList = printMii, project = project_id, name = dbc.getProjectName(project_id), warning = "Slide %s has been added." % slideName)
	return illegal_action("error")

@app.route("/projects/<int:project_id>/<int:presentation_id>/<int:slide_id>")
def downloadSlide(project_id, presentation_id, slide_id):
	if not 'username' in session:		
		return render_template("login.html", warning = "Please log-in to the system.")
	if dbc.getRole(project_id, session['username']) != "Project Manager" and dbc.getRole(project_id, session['username']) != "Presentation Creator" and dbc.getRole(project_id, session['username']) != "Slide Creator":
		return not_allowed("error")
	slide = VCS().load_project(str(project_id)).get_slide(slide_id)
	slideFile = slide.data
	return Response(slideFile, mimetype="pptx", headers={"Content-Disposition":"attachment;filename=%s.ppt" % slide.name})

@app.route("/projects/<int:project_id>/downloadCurrentPresentation")
def downloadCurrentPresentation(project_id):
	return "testing"

@app.route("/registered", methods = ['POST'])
def register():
	if request.method == 'POST':
		result = dbc.addUser(request.form['FName'], request.form['LName'], request.form['UName'], request.form['password'], request.form['repeatpass'])
		if not result == "You are now registered into the Dynamic Presenter system!":
			return render_template("login.html", warning = result)
		return render_template("login.html", warning = result)		
	return illegal_action("error")

@app.errorhandler(404)
def page_not_found(error):
	return "<h1>Sorry chief, we don't have what you're looking for.  You might wanna try again.  Error 404: Can't Find It</h1>"

@app.errorhandler(405)
def illegal_action(error):
	return "<h1>Please do not attempt to break the system.  Error 405: Illegal action.</h1>"

@app.errorhandler(400)
def bad_request(error):
	return "<h1>Something went wrong.  Probably bad form requests.  Error 400: Bad form requests.</h1>"

@app.errorhandler(403)
def not_allowed(error):
	return "<h1>This is a protected area and you are not allowed to access whatever is in here.  Need super admin priveleges.  Error 403: Access Denied</h1>"

def isFileAllowed(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def run_app():
	app.run(port=80)

if __name__ == "__main__":
    run_app()
