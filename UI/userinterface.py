from datetime import timedelta
from flask import Flask, session, render_template, request, send_from_directory, redirect, url_for, Response
from flask.ext.bootstrap import Bootstrap
import os
from werkzeug import secure_filename
import dbc
from vcs import VCS

app = Flask(__name__)
#Sets the Session Timer.  Removing this defaults the session time to 31 days.
app.permanent_session_lifetime = timedelta(minutes=15)
#Set to false if you want to push this server live.  It's not a good idea to leave debug open when the server is taking outside TCP requets.
app.debug = False
#Unused
app.config['UPLOAD_FOLDER'] = '/models'
#Done to prevent upload of any unwanted files.  Unfortunately, this isn't perfect and people can still damage the system by sending a "fake" .pptx file.
ALLOWED_EXTENSIONS = set(['pptx'])
#Required for sessions
app.secret_key = dbc.giveMetheSecretKey()
#Required for bootstrapping to work properly.
Bootstrap(app)

# Allow a way to determine if the user is logged in
app.jinja_env.globals.update(logged_in=(lambda: 'username' in session))

#Relative Path for sending images for use-case: Preview Slides in Presentation
def relative_path(path):
	return os.path.join(os.path.dirname(__file__), path)

#GLOBAL DOCUMENTATION NOTE
#TO PREVENT SELF-REPEATING, ALL METHODS THAT HAVE if not 'username' in session are checking to see if the user has a valid session.
#ALSO, ALL METHODS WILL HAVE A role check by asking the database controller for your role unless it's the login, register, or index page, for EVERYTHING.

#Default route Directory:  If the user querying the system has an active session, send them to the index page, no need to log in.
#Otherwise, tell him to log in first.
@app.route("/")
def login():
	if 'username' in session:
		projList = dbc.getProjectList(session['username'])
		return render_template("index.html", stuff = projList)
	return render_template("login.html", warning = "")

#Default about page.  May be cropped.
@app.route("/about")
def aboutPage():
	return render_template("about.html")

#This is called when the user logs out.  This will pop their session if it exists, then redirect them to login.
@app.route("/login")
def logout():
	session.pop('username', None)
	return login()

#If routed from a POST request, will check to see if the user made a valid login.  If so, send them to the index, if not then send them to attempt again.
#If routed from a GET request, will check session.
@app.route("/index", methods = ['POST','GET'])
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

#Tries to build a project.  If I get a warning message that I can't parse into a number, it's an exception and push out the error message.
#Otherwise, I create a new projectand tell the Version Control Subsystem to make a new project folder.
@app.route("/buildProject", methods = ['POST'])
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

#Will move to here.  I'll render the appropriate image that you need based on your role.  Redirects will 
#For Cleanup, maybe you only need to query the database server once per call rather than the multiple times I may do here.
#If you don't have a proper role you belong in for the project you're calling, you don't get anything.
@app.route("/projects/<int:project_id>")
def show_project(project_id, warning = None, role = None, alert = None):
	if 'username' not in session:
		return render_template("login.html", warning = "Please log-in to the system.")
	project = VCS().load_project(str(project_id))
	status = "Unlocked"
	if(dbc.getProjectStatus(project_id)) == True:
		status = "Frozen"
	assign = dbc.getRole(project_id, session['username'])
	if assign == 'Project Manager':
		printMii = dbc.getUserList(project_id)
		printMiiToo = dbc.deletableUserList(project_id)		
		printMiiThree = filter(lambda (i, x): x.confidential, enumerate(project.current_presentation.slides))
		return render_template('project1.html', alert = 'info', userList = printMii, removeMii = printMiiToo, project = project_id, name = dbc.getProjectName(project_id), confidential = printMiiThree, warning = "Status of Project: %s" % status)
	if assign == 'Presentation Creator':
		printMii = project.persisted_presentations
		printMiiThree = project.current_presentation
		printMiiToo = project.current_presentation.slides
		printMii4 = dbc.getUserNameList(project_id)		
		return render_template('project3.html', users = printMii4, alert = 'info', presentationList = printMii, current = printMiiThree, slideList = printMiiToo, project = project_id, name = dbc.getProjectName(project_id), warning = "Status of Project: %s" % status)
	if assign == 'Slide Creator':
		printMii = project.current_presentation.slides
		return render_template('project2.html', alert = 'info', slideList = printMii, project = project_id, name = dbc.getProjectName(project_id), warning = "Status of Project: %s" % status, status = status, role = "Slide Creator")
	return not_allowed("error")

#Reroute method to save on boilerplate code.
def show_project(project_id, warning, role, alert):
	if 'username' not in session:
		return render_template("login.html", warning = "Please log-in to the system.")
	project = VCS().load_project(str(project_id))
	status = "Unlocked"
	if(dbc.getProjectStatus(project_id)) == True:
		status = "Frozen"
	if role == 'Project Manager':
		printMii = dbc.getUserList(project_id)
		printMiiToo = dbc.deletableUserList(project_id)
		printMiiThree = filter(lambda (i, x): x.confidential, enumerate(project.current_presentation.slides))
		return render_template('project1.html', alert = alert, userList = printMii, removeMii = printMiiToo, project = project_id, name = dbc.getProjectName(project_id), confidential = printMiiThree, warning = warning)
	if role == 'Presentation Creator':
		printMii = project.persisted_presentations
		printMiiThree = project.current_presentation
		printMiiToo = project.current_presentation.slides
		printMii4 = dbc.getUserNameList(project_id)		
		return render_template('project3.html', alert = alert, users = printMii4, presentationList = printMii, current = printMiiThree, slideList = printMiiToo, project = project_id, name = dbc.getProjectName(project_id), warning = warning)
	if role == 'Slide Creator':
		printMii = project.current_presentation.slides
		return render_template('project2.html', alert = alert, slideList = printMii, project = project_id, name = dbc.getProjectName(project_id), warning = warning, status = status, role = dbc.getRole(project_id, session['username']))
	return not_allowed("error")

#Adds the user to the project
#If bad input is given, I'll print the appropriate error message to you (the Database Controller will tell me).
#Otherwise, I'll add him to your project.
@app.route("/projects/<int:project_id>/added", methods = ['POST'])
def addUserToProject(project_id):
	if not 'username' in session:
		return render_template("login.html", warning = "Please log-in to the system.")
	if not dbc.getRole(project_id, session['username']) == "Project Manager":
		return not_allowed("error")
	if request.method == 'POST':
		uname_to_add = request.form['username']
		if uname_to_add == "":
			return show_project(project_id, warning = "Ummm...need to input a username chief.", role = 'Project Manager', alert = "danger")
		if not dbc.userExists(uname_to_add):
			return show_project(project_id, warning = "User not found in the system!", role = 'Project Manager', alert = "danger")
		if dbc.userInProject(uname_to_add, project_id):			
			return show_project(project_id, warning = "User already exists in the project!", role = 'Project Manager', alert = "danger")
		role_to_add = request.form['role']
		if not (role_to_add == "Presentation Creator" or "Slide Creator"):
			return show_project(project_id, warning = "INVALID ROLE SELECTION!", role = 'Project Manager', alert = "danger")
		dbc.addUserToProject(project_id, uname_to_add, role_to_add)
		return show_project(project_id, warning = "User %s added to project!" % uname_to_add, role = 'Project Manager', alert = "success")
	return illegal_action("error")

#If you want to persist a presentation, call this.  I'll ask the Version Control System to do this for me.
@app.route("/projects/<int:project_id>/createPresentation", methods = ['POST'])
def createPresentation(project_id):
	if not 'username' in session:
		return render_template("login.html", warning = "Please log-in to the system.")
	if dbc.getRole(project_id, session['username']) != "Presentation Creator" and dbc.getRole(project_id, session['username']) != "Project Manager":
		return not_allowed("error")
	if request.method == "POST":
		VCS().load_project(str(project_id)).current_presentation.persist(request.form['presentation_name'])
		return show_project(project_id, warning = "New Presentation Persisted", role = "Presentation Creator", alert = "success") 
	return illegal_action("error")

#If you want to see the list of presentations or view the Presentation Creator's Page, you may do so through this route.  I'll check what you
#can do based on role using the Database Controller.
@app.route("/projects/<int:project_id>/presentations")
def viewPresentations(project_id):
	if not 'username' in session:
		return render_template("login.html", warning = "Please log-in to the system.")
	status = "Unlocked"
	if dbc.getProjectStatus(project_id):
		status = "Frozen"
	role = dbc.getRole(project_id, session['username']) 
	if role == "Project Manager" or role == 'Presentation Creator':
		return show_project(project_id, warning = "Status of Project: %s" % status, role = 'Presentation Creator', alert = "info")
	if role == 'Slide Creator':
		return slideCreatorViewPresentation(project_id)
	return not_allowed("error")

#Render this instead if the slide creator is the one who's working on it.
def slideCreatorViewPresentation(project_id):
	printMii = VCS().load_project(str(project_id)).persisted_presentations
	printMiiToo = VCS().load_project(str(project_id)).current_presentation
	return render_template("presentationList.html", project_id = project_id, presentationList = printMii, current = printMiiToo)

#Ask me for the actual Presentation.  Based on Role, I'll determine what you'll be able to download.
#When I figure that out, I'll tell the Version Control System to either give me a completely unfiltered presentation, or if
#not a project manager, fetch one with confidentiality rules enforced.
@app.route("/projects/<int:project_id>/<int:presentation_id>/download")
def downloadPresentation(project_id, presentation_id):
	if not 'username' in session:
		return render_template("login.html", warning = "Please log-in to the system.")
	role = dbc.getRole(project_id, session['username'])
	if role != "Project Manager" and role != 'Presentation Creator' and role != 'Slide Creator':
		return not_allowed("error")
	presentation = VCS().load_project(str(project_id)).get_presentation(presentation_id)
	if role == "Project Manager":
		presentationObject = presentation.data
		return Response(presentationObject, mimetype="pptx", headers={"Content-Disposition":"attachment;filename=%s.pptx" % presentation.name})
	else:
		presentationObject = presentation.data_obfuscated
		return Response(presentationObject, mimetype="pptx", headers={"Content-Disposition":"attachment;filename=%s.pptx" % presentation.name})
	return not_allowed("error")

#I'll do this to revert the current presentation to a previous one.  Version Control System takes care of the hard work for me.
@app.route("/projects/<int:project_id>/revertPresentation", methods = ['POST'])
def revertPresentation(project_id):
	if not 'username' in session:
		return render_template("login.html", warning = "Please log-in to the system.")
	if dbc.getRole(project_id, session['username']) != "Project Manager" and dbc.getRole(project_id, session['username']) != 'Presentation Creator':
		return not allwed("error")
	if request.method == 'POST':
		VCS().load_project(str(project_id)).get_presentation(request.form['presentation_id']).restore()
		return show_project(project_id, warning = "Current Presentation has been reverted", role = 'Presentation Creator', alert = "success")
	return illegal_action("error")

#If you want to see the slide previews for the presentation, I'll call this.  I'll ask the Version Control System to send a set of images to the static directiory.
#Using the appropriate rules, I'll make directory files for the slides, you put them there, and on the template, I'll render the images based on their location (img source info is on the template).
@app.route("/projects/<int:project_id>/presentations/<int:presentation_id>")
def viewSlides(project_id, presentation_id):
	if not 'username' in session:
		return render_template("login.html", warning = "Please log-in to the system.")
	role = dbc.getRole(project_id, session['username'])
	if role != "Presentation Creator" and role != "Project Manager" and role != 'Slide Creator':
		return not_allowed("error")
	presentation = VCS().load_project(str(project_id)).get_presentation(presentation_id)
	path = relative_path("static/%s" % project_id)
	if not os.path.exists(path):
		os.makedirs(path)
	presentation.export_images(path, hide_confidential = True)
	printMii = presentation.slides
	return render_template("viewPresentation.html", project_id = project_id, presentation_id = presentation_id, name = presentation.name, slideList = printMii)

#If I want to manage the slides in the current presentation as someone who's not a slide creator, I'll need this route to do that.
@app.route("/projects/<int:project_id>/presentations/current")
def presentation(project_id):
	if not 'username' in session:
		return render_template("login.html", warning = "Please Log-in to the system.")
	if dbc.getRole(project_id, session['username']) != "Project Manager" and dbc.getRole(project_id, session['username']) != "Presentation Creator":
		return not_allowed("error")
	status = "Unlocked"
	if dbc.getProjectStatus(project_id):
		status = "Frozen"
	return show_project(project_id, warning = "Status of Project: %s" % status, role = 'Slide Creator', alert = "info") 

#If I want to revoke a check-out.  I'll need this method to do that.  I'll get the slide info that I need from the VCS in the template call, then 
#tell the VCS to deauthroize it.
@app.route("/project/<int:project_id>/deauthorized", methods = ['POST'])
def deauthorizeCheckOut(project_id):
	if not 'username' in session:
		return render_template("login.html", warning = "Please log-in to the system.")
	if dbc.getRole(project_id, session['username']) != 'Project Manager' and dbc.getRole(project_id, session['username']) != 'Presentation Creator':
		return not_allowed("error")
	if request.method == 'POST':
		slide_id = request.form['slide_ID']
		slide = VCS().load_project(str(project_id)).get_slide(slide_id)
		slide.cancel_checkout()
		return show_project(project_id, warning = "Slide %s checkout has been removed" % slide.name, role = 'Presentation Creator', alert = 'warning')
	return illegal_action("error")

#Checkout routine for Project Managers and Slide Creators.  Get the user id I want from the post request and the slide Id and tell the VCS to check out the slide.
#Of course, I ask the VCS first if I can do that.
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
		if project.get_slide(slide).confidential:
			return show_project(project_id, warning = "Slide %s checkout failed. It's protected by confidentiality." % project.get_slide(slide).name, role = 'Presentation Creator', alert = 'danger')
		if project.get_slide(slide).checkout_user != None:
			return show_project(project_id, warning = "Slide %s checkout failed. It's already been checked out." % project.get_slide(slide).name, role = 'Presentation Creator', alert = 'danger')
		project.get_slide(slide).checkout(user)
		return show_project(project_id, warning = "Slide %s has been checked out." % project.get_slide(slide).name, role = 'Presentation Creator', alert = 'success')
	return illegal_action("error")

#Similar to checkout, but this is compatible with Slide Creators.
@app.route("/projects/<int:project_id>/slideCreatorCheckedOut", methods = ['POST'])
def slideCheckOut(project_id):	
	if not 'username' in session:
		return render_template("login.html", warning = "Please Log-in to the system.")
		role = dbc.getRole(project_id, session['username'])
	if role != 'Project Manager' and role != 'Presentation Creator' and role != 'Slide Creator':
		return not_allowed("error")
	if request.method == 'POST':
		project = VCS().load_project(str(project_id))
		slide = request.form['slide_ID']
		if project.get_slide(slide).confidential:
			return show_project(project_id, warning = "Slide %s checkout failed. It's protected by confidentiality." % slide, role = 'Slide Creator', alert = 'danger')
		if(project.get_slide(slide).checkout_user != None):
			return show_project(project_id, warning = "Slide %s checkout failed. It's already checked out." % slide, role = 'Slide Creator', alert = 'danger')
		project.get_slide(slide).checkout(session['username'])
		return show_project(project_id, warning = "Slide %s has been checked out." % slide, role = 'Slide Creator', alert = 'success')
	return illegal_action("error")

#Had enough of a user in your project?  Call this method and as long as the proper form is given, I'll remove them from the system.
#only project manager can remove users from the project.
@app.route("/projects/<int:project_id>/removed", methods = ['POST'])
def removeUserFromProject(project_id):
	if request.method == 'POST':
		if not 'username' in session:
			return render_template("login.html", warning = "Please log-in to the system.")
		if not dbc.getRole(project_id, session['username']) == "Project Manager":
			return not_allowed("error")
		userToBeRemoved = request.form['username']
		if dbc.getRole(project_id, userToBeRemoved) == 'Project Manager':
			return not_allowed("error")
		dbc.removeUser(userToBeRemoved, project_id)
		return show_project(project_id, warning = "%s has been removed from the project." % userToBeRemoved, role = 'Project Manager', alert = 'warning')
	return illegal_action("error")

#Check in a slide.  I'll ask the VCS if I can check in the slide in the post request.  If i can, great.  If not, throw a warning.
@app.route("/projects/<int:project_id>/checkedIn", methods = ['POST'])
def checkInSlide(project_id):
	if not 'username' in session:
		return render_template("login.html", warning = "Please log-in to the system.")
	if dbc.getRole(project_id, session['username']) != "Slide Creator" and dbc.getRole(project_id, session['username']) != "Project Manager" and dbc.getRole(project_id, session['username']) != "Presentation Creator":
		return not_allowed("error")
	if request.method == 'POST':
		user = session['username']
		slideObject = VCS().load_project(str(project_id)).get_slide(request.form['slide_id'])
		if slideObject.checkout_user != user:			
			return show_project(project_id, warning = "Check In %s failed.  You don't have that checked out." % slideObject.name, role = 'Slide Creator', alert = 'danger')
		stuff = request.files['slide_file']
		if stuff and isFileAllowed(stuff.filename):
			slideObject.checkin(user, stuff.read())	
			return show_project(project_id, warning = "Slide %s has been checked in." % slideObject.name, role = "Slide Creator", alert = "success")
		return show_project(project_id, warning = "Only use powerpoint files to check in please.", role = 'Slide Creator', alert = 'warning')
	return illegal_action("error")

#If i want to freeze the project, use this method to do so.  This will swap the boolean values appropriately.
@app.route("/projects/<int:project_id>/changeProjectStatus")
def changeProjectStatus(project_id):
	if not 'username' in session:
		return render_template("login.html", warning = "Please log-in to the system.")
	role = dbc.getRole(project_id, session['username'])
	if role != 'Presentation Creator' and role != 'Project Manager':
		return not_allowed("error")
	if dbc.getProjectStatus(project_id):
		dbc.setProjectStatus(project_id, False)
	else:
		dbc.setProjectStatus(project_id, True)
	value = dbc.getProjectStatus(project_id)
	if value == True:
		value = "Frozen"
	else:
		value = "Released"
	if role == 'Presentation Creator':
		return show_project(project_id, warning = "Project is now %s." % value, role = 'Presentation Creator', alert = 'info')
	return show_project(project_id, warning = "Project is now %s." % value, role = 'Project Manager', alert = 'info')

#If I want to add a slide, use this call to do so.  I also have to tell the VCS we have a new slide to make.
@app.route("/projects/<int:project_id>/addSlide", methods = ['POST'])
def addSlide(project_id):	
	if not 'username' in session:		
		return render_template("login.html", warning = "Please log-in to the system.")
	role = dbc.getRole(project_id, session['username'])
	if role != "Project Manager" and role != "Presentation Creator" and role != "Slide Creator":
		return not_allowed("error")
	if request.method == 'POST':
		slideName = request.form['name']
		project = VCS().load_project(str(project_id))
		project.current_presentation.add_slide(slideName)
		return show_project(project_id, warning = "Slide %s has been added." % slideName, role = 'Slide Creator', alert = 'success')
	return illegal_action("error")

#I'll check authorization rules.  IF a slide is confidential (VCS) and you're not a project manager, you don't get to download it.
#If I am a project manager for that slide, then doesn't matter, give me the slide.
#Otherwise, as long as you're part of the project, I just tell the VCS to give me the slide.
@app.route("/projects/<int:project_id>/<int:presentation_id>/<int:slide_id>")
def downloadSlide(project_id, presentation_id, slide_id):
	if not 'username' in session:		
		return render_template("login.html", warning = "Please log-in to the system.")
	role = dbc.getRole(project_id, session['username'])
	if role != "Project Manager" and role != "Presentation Creator" and role != "Slide Creator":
		return not_allowed("error")
	slide = VCS().load_project(str(project_id)).get_slide(slide_id)
	if role != "Project Manager" and slide.confidential:
		return show_project(project_id, warning = "Slide %s is confidential!  Cannot download it." % slide_id, role = role, alert = 'success')
	slideFile = slide.data
	return Response(slideFile, mimetype="pptx", headers={"Content-Disposition":"attachment;filename=%s.pptx" % slide.name})

#Handles registration post requests.
@app.route("/registered", methods = ['POST'])
def register():
	if request.method == 'POST':
		result = dbc.addUser(request.form['FName'], request.form['LName'], request.form['UName'], request.form['password'], request.form['repeatpass'])
		if not result == "You are now registered into the Dynamic Presenter system!":
			return render_template("login.html", warning = result)
		return render_template("login.html", warning = result)		
	return illegal_action("error")

#Tagging a Slide as confidential.  IF you're not a project manager, you won't get to do it.  (Have some unnecessary code sadly, former functionality stuff.
#Tell the VCS if the slide was checked out, to revoke it immediately and also to flag the project as confidential.
@app.route("/projects/<int:project_id>/tagConfidential", methods = ['POST'])
def tagSlideAsConfidential(project_id):
	if not 'username' in session:		
		return render_template("login.html", warning = "Please log-in to the system.")
	role = dbc.getRole(project_id, session['username'])
	if role != "Project Manager":
		return not_allowed("error")
	if request.method == 'POST':
		slide = request.form['slide_id']
		print slide
		currentSlide = VCS().load_project(str(project_id)).get_slide(slide)
		if currentSlide.confidential:		
			return show_project(project_id, warning = "Slide is already flagged as confidential.", role = 'Slide Creator', alert = 'warning')
		if currentSlide.checkout_user != session['username'] and role == 'Slide Creator':
			return show_project(project_id, warning = "You can't mark a slide as confidential if you're a Slide Creator and haven't checked it out.", role = 'Slide Creator', alert = 'danger')
		currentSlide.cancel_checkout()
		currentSlide.confidential = True
		return show_project(project_id, warning = "Slide has been tagged as confidential.", role = 'Slide Creator', alert = 'danger')
	return illegal_action("error")

#Release confidential slide tags on the slide.  I'll let the VCS know to do that for me.
@app.route("/projects/<int:project_id>/untagConfidential", methods = ['POST'])
def removeConfidentialTag(project_id):
	if not 'username' in session:
		return render_template("login.html", warning = "Please log-in to the system.")
	if dbc.getRole(project_id, session['username']) != 'Project Manager':
		return not_allowed("error")
	if request.method == 'POST':
		slide = request.form['slide_id']
		print slide
		VCS().load_project(str(project_id)).get_slide(slide).confidential = False
		return show_project(project_id, warning = "Slide confidentiality tag has been removed.", role = 'Project Manager', alert = 'warning')
	return illegal_action("error")

@app.errorhandler(404)
def page_not_found(error):
	return "<h1>Sorry chief, we don't have what you're looking for.  You might wanna try again.  Error 404: Can't Find It</h1>"

@app.errorhandler(405)
def illegal_action(error):
	return "<h1>Please do not attempt to break the system.  Don't attempt GET requests on a required POST (etc).  Error 405: Illegal action.</h1>"

@app.errorhandler(400)
def bad_request(error):
	return "<h1>Something went wrong.  Probably submitted a bad form request.  Error 400: Bad form requests.</h1>"

@app.errorhandler(403)
def not_allowed(error):
	return "<h1>This is a protected area and you are not allowed to access whatever is in here.  Need super admin priveleges.  Error 403: Access Denied</h1>"

#checks to see if the file name is acceptable
def isFileAllowed(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

#Runs the app function with the parameters set
#Port: Listening Port the System will Check
#Host: add the parameter host='0.0.0.0' to get the server to listen to outside requests.
def run_app():
	app.run(port=80, host='0.0.0.0')

if __name__ == "__main__":
    run_app()
