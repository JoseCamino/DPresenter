from flask import Flask, session, render_template, request, send_from_directory
import os
from werkzeug import secure_filename
import dbc
from vcs import VCS

app = Flask(__name__)
app.debug = True
app.config['UPLOAD_FOLDER'] = '/models'
ALLOWED_EXTENSIONS = ['pptx', 'ppt']
app.secret_key = dbc.giveMetheSecretKey()

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
			return render_template('index.html', stuff = projList)
		else:
			return render_template("login.html", warning = "Invalid username/password combination.  Please try again.")
	if 'username' in session:
		projList = dbc.getProjectList(session['username'])
		return render_template("/index.html", stuff = projList)
	else:
		return render_template("/login.html", warning = "Please log-in to the system.")

@app.route("/createProject.html")
def createProject():
	if 'username' in session:
		return render_template("createProject.html")
	return render_template("login.html")

@app.route("/buildProject.html", methods = ['POST'])
def buildProject():
	if 'username' not in session:
		return render_template("login.html", warning = "Please log-in to the system.")
	if request.method == 'POST':
		projName = request.form['projname']
		id_name = dbc.addProject(session['username'], projName)
		if(id_name == "Your project name has too few characters.  Please make project names at least 5 characters or more."):
			return id_name
		if(id_name == "Your project name has too many characters.  Please make project names no more than 32 characters long."):
			return id_name
		if(id_name == "Your Project Name has invalid characters.  Please don't anything other than numbers or characters."):
			return id_name
		VCS().create_project(str(id_name))
		return "Success!  //Todo: Redirect."
	return "This shouldn't happen...ever"

@app.route("/projects/<int:project_id>")
def show_project(project_id):
	if 'username' not in session:
		return render_template("login.html", warning = "Please log-in to the system.")

	project = VCS().load_project(str(project_id)) # todo: catch exception
	if dbc.getRole(project_id, session['username']) == 'Project Manager':
		printMii = dbc.getUserList(project_id)
		return render_template('project1.html', userList = printMii, project = project_id, name = dbc.getProjectName(project_id))
	if dbc.getRole(project_id, session['username']) == 'Slide Creator':
		printMii = project.presentations
		return render_template('project3.html', presentationList = printMii, project = project_id, name = dbc.getProjectName(project_id))
	if dbc.getRole(project_id, session['username']) == 'Presentation Creator':
		return render_template('project2.html')
	return "You are viewing project with id %s" % project_id

@app.route("/projects/<int:project_id>/addUserstoProject")
def add_user_to_project(project_id):
	if 'username' not in session:
		return render_template("login.html", warning = "Please log-in to the system.")
	if not dbc.getRole(project_id, session['username']) == "Project Manager":
		return not_allowed()
	return render_template("addUsertoProject.html", project_id = project_id)

@app.route("/projects/<int:project_id>/added", methods = ['POST'])
def added(project_id):
	if request.method == 'POST':
		if not 'username' in session:
			return render_template("login.html", warning = "PLease log-in to the system.")
		if not dbc.getRole(project_id, session['username']) == "Project Manager":
			return not_allowed()
		uname_to_add = request.form['username']
		if uname_to_add == "":
			return "Um...need to add a username chief."
		if not dbc.userExists(uname_to_add):
			return "User doesn't exist in the system.  Please try again."
		if dbc.userInProject(uname_to_add, project_id):
			return "User already exists in the project.  Can't add him again."
		role_to_add = request.form['role']
		if not (role_to_add == "Presentation Creator" or "Slide Creator"):
			return "Invalid role selection.  Please assign as either a Presentation Creator or Slide Creator."
		dbc.addUserToProject(project_id, uname_to_add, role_to_add)
		return "Success!"
	return "This should never happen"

@app.route("/projects/<int:project_id>/presentations/<int:presentation_id>")
def presentation(project_id, presentation_id):
	return "Testing"

@app.route("/projects/<int:project_id>/removeUser")
def remove_users_from_project(project_id):
	if not 'username' in session:
		return render_template("login.html", warning = "Please log-in to the system.")
	if not dbc.getRole(project_id, session['username']) == "Project Manager":
		return not_allowed()
	printMii = dbc.deletableUserList(project_id)
	if printMii == []:
		return "You don't have any users in this project.  Care to add some?"
	return render_template("removeUserFromProject.html", uList = printMii, project = project_id)

@app.route("/projects/<int:project_id>/removed", methods = ['POST'])
def removed(project_id):
	if request.method == 'POST':
		if not 'username' in session:
			return render_template("login.html", warning = "Please log-in to the system.")
		if not dbc.getRole(project_id, session['username']) == "Project Manager":
			return not_allowed()
		userToBeRemoved = request.form['username']
		print userToBeRemoved
		if dbc.getRole(project_id, userToBeRemoved) == 'Project Manager':
			return not_allowed()
		dbc.removeUser(userToBeRemoved, project_id)
		return "USER REMOVED!"
	return not_allowed()

@app.route("/projects/<int:project_id>/downloadPrimary")
def download_current_presentation(project_id):
	filename = "%s" % project_id
	return send_from_directory(app.config['UPLOAD_FOLDER'], '3')

@app.route("/createpresentation.html")
def createpresentation():
    return testlogin('createpresentation.html')

@app.route("/setprimary.html")
def setprimary():
	return testlogin('setprimary.html')

@app.route("/register.html")
def register():
	return render_template('register.html', warning = "")

@app.route("/registered.html", methods = ['POST'])
def registered():
	if request.method == 'POST':
		result = dbc.addUser(request.form['FName'], request.form['LName'], request.form['UName'], request.form['password'], request.form['repeatpass'])
		if not result == "You are now registered into the Dynamic Presenter system!":
			return render_template("register.html", warning = result)
		return render_template("login.html", warning = result)		
	return "This shouldn't happen.  Error 405 handles this."

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

def run_app():
	app.run(port=80)

if __name__ == "__main__":
    run_app()
