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
	return render_template("login.html")

@app.route("/login.html")
def logout():
	session.pop('username', None)
	return render_template('login.html')

@app.route("/index.html", methods = ['POST','GET'])
def index():
	error = None
	if request.method == 'POST':
		uname = request.form['username']
		print uname
		password = request.form['password']
		print password
		if dbc.checkPassword(uname, password):
			session['username'] = uname
			projList = dbc.getProjectList(uname)
			return render_template('index.html', stuff = projList)
		else:
			return 'Thou Hath Chosen...poorly...by giving me an invalid username and/or password combination!!!'
	if 'username' in session:
		projList = dbc.getProjectList(session['username'])
		return render_template("index.html", stuff = projList)
	else:
		return render_template("login.html")

@app.route("/createProject.html")
def createProject():
	if 'username' in session:
		return render_template("createProject.html")
	return render_template("login.html")

@app.route("/buildProject.html", methods = ['POST'])
def buildProject():
	if 'username' not in session:
		return render_template("login.html")
	if request.method == 'POST':
		projName = request.form['projname']
		return dbc.addProject(session['username'], projName)
	return "This shouldn't happen...ever"

@app.route("/projects/<int:project_id>")
def show_project(project_id):
	if 'username' not in session:
		return render_template("/login.html")
	printMii = []
	if dbc.getRole(project_id, session['username']) == 'Project Manager':
		printMii = dbc.getUserList(project_id)
		return render_template('project1.html', userList = printMii, project = project_id, name = dbc.getProjectName(project_id))
	return "You are viewing project with id %s" % project_id

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
	
@app.route("/created.html", methods = ['POST'])
def createNewPresentation():
	stuff = Presentation()
	global latestversion
	latestversion += 1
	global latestpresentation
	latestpresentation += 1
	stuff.id = latestpresentation
	stuff.version = latestversion
	stuff.primary = True
	presentationList[len(presentationList)-1].primary = False
	presentationList.insert(len(presentationList), stuff)
	if request.method == 'POST':
		return render_template('created.html')
	return "Done!"

@app.route("/register.html")
def register():
	return render_template('register.html')

@app.route("/registered.html", methods = ['POST'])
def registered():
	if request.method == 'POST':
		return dbc.addUser(request.form['FName'], request.form['LName'], request.form['UName'], request.form['password'], request.form['repeatpass'])
	return "YOU HATH CHOSEN TO ILLEGALLY DO SHITS!  YOU FAIL GOOD SIR"

@app.errorhandler(404)
def page_not_found(error):
	return "<h1>THOU HATH FAILED TO FIND WHAT YOU ARE LOOKING FOR!  YOU ARE NOW DOOMED TO DIE!</h1>"

@app.errorhandler(405)
def illegal_action(error):
	return "<h1>THOU HATH CHOSEN TO DO SHITS ILLEGALLY!  YOU SHALL DIE NOW!</h1>"

@app.errorhandler(400)
def bad_request(error):
	return "<h1>THOU HATH CHOSEN TO BE EVIL AND MAKE BAD REQUESTS!  YOU SHALL BE PURGED BY FIRE!</h1>"

def run_app():
	app.run(port=80)

if __name__ == "__main__":
    run_app()
