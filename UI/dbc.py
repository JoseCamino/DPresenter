import psycopg2, os, sys
from werkzeug.security import generate_password_hash, check_password_hash

#Generates a unicode random 16 character length string for the User Interface.
secretkey = os.urandom(16)

#Parameters established for filtering out unwanted characters in a password input and Project Name.
ACCEPTABLE_CHARACTERS = [48,57,65,90,97,122,32]
PASSWORD_MIN_SIZE = 6
PASSWORD_MAX_SIZE = 20

#Required for connecting to the database.  You may edit it using the following parameters:
#Parameters may be passed as the following:
#dbname = the name of the database you're connecting to
#user = the name of the user you want this system to connect to the database to as
#password = the password of the database (please pick a better one other than lol, don't be like me)
#host = address of the host you're trying to connect to (defaults to local machine)
#port = the port you need to connect to (defaults to 5432)
conn = psycopg2.connect("dbname=dynamic user=postgres password = lol")
# necessary after conn to cursor to the database
cur = conn.cursor()

#Result of calling getUserList
#Will push the User Name and the Role
class userRole(object):
	def construct(self, uname, job):
		self.user_ID = uname
		self.role = job

#Result of calling getProjectList
#Will get the Name of the Project and the Role
class project(object):
	def construct(self, projid, job):
		self.project_id = projid
		self.role = job
		self.project_name = None

#Helper Function for the UI to get a Secret Key for Sessions
def giveMetheSecretKey():
	return secretkey


#Checks the Ordinal value of the character given.  Basically, if the character is not alphanumeric, it's not valid.	
def validCharacter(char):
	if(ord(char) >= ACCEPTABLE_CHARACTERS[0] and ord(char) <= ACCEPTABLE_CHARACTERS[1]):
		return True
	if(ord(char) >= ACCEPTABLE_CHARACTERS[2] and ord(char) <= ACCEPTABLE_CHARACTERS[3]):
		return True
	if(ord(char) >= ACCEPTABLE_CHARACTERS[4] and ord(char) <= ACCEPTABLE_CHARACTERS[5]):
		return True
	if(ord(char) == ACCEPTABLE_CHARACTERS[6]):
		return True
	return False

#Uses built in werkzeug security function to compare the password you got with the one in the database.
def checkPassword(username, password):
	sqlcommand = "SELECT password FROM user_list where username = %s;"
	cur.execute(sqlcommand, [username])
	for record in cur:
		return check_password_hash(record[0], password)

#Checks if the user exists in the database.
def userExists(username):
	sqlcommand = "SELECT username From user_list where username = %s;"
	cur.execute(sqlcommand, [username])
	for record in cur:
		if(record[0] == username):
			return True
	return False

#Checks if the user is in the project being checked.
def userInProject(username, project_ID):
	sqlcommand = "SELECT user_id FROM works_on WHERE project_id = %s;"
	cur.execute(sqlcommand, [project_ID])
	for record in cur:
		if(record[0] == username):
			return True
	return False

#REturns a list of all users that can be removed from the project.  Just user IDs, no user objects.
def deletableUserList(project_ID):
	sqlcommand = "SELECT user_id FROM works_on WHERE project_id = %s AND role != 'Project Manager';"
	cur.execute(sqlcommand, [project_ID])
	userList = []
	for record in cur:
		userList.append(record[0])
	return userList
	
#Adds a User to the Database.  Returns a failure message if any inappropriate conditions were met (should provide a better implementation).
#Utilizes werkzeug api to salt and hash the password. Yes, it works.
def addUser(FName, LName, username, password, repeatpass):
	sqlcommand = "SELECT username FROM user_list;"
	cur.execute(sqlcommand)
	result = ""
	for record in cur:
		if(record[0] == username):
			result = "This username already exists.  Please pick another username!"
			return result
	if(password != repeatpass):
		result = "Your passwords do not match.  Please re-input your passwords!"
		return result
	if(len(password) < PASSWORD_MIN_SIZE or len(password) > PASSWORD_MAX_SIZE):
		result = "Your password length is incorrect.  Please input a new password!"
		return result
	for y in range(0, len(password)):
		substring = password[y:y+1]
		if(not validCharacter(substring)):
			result = "Your password has an invalid character in the string.  Please input a new password!"
			return result
	saltedPW = generate_password_hash(password)
	sqlcommand = "INSERT INTO user_list VALUES(%s, %s, %s, %s);"
	cur.execute(sqlcommand, [FName, LName, username, saltedPW])
	conn.commit()
	result = "You are now registered into the Dynamic Presenter system!"
	return result

#Returns the name of the project for that project id, beause displaying project ids is a bit...silly to read.
def getProjectName(project_id):
	sqlcommand = "SELECT project_name FROM project_list WHERE ID = %s;"
	cur.execute(sqlcommand, [project_id])
	result = ""
	for record in cur:
		result = record[0]
	return result
	
#Returns a list of user objects with their name (not username) and their role.
def getUserList(project_ID):
	sqlcommand = "SELECT user_ID, role FROM WORKS_ON WHERE project_ID = %s;"
	cur.execute(sqlcommand, [project_ID])
	userList = []
	for record in cur:
		tempuser = userRole()
		tempuser.construct(record[0], record[1])
		userList.append(tempuser)
	for user in userList:
		sqlcommand = "SELECT FName, LName FROM user_list WHERE username = %s;"
		cur.execute(sqlcommand, [user.user_ID])
		for record in cur:
			name = "%s %s" % (record[0], record[1])
			user.user_ID = name
	return userList

#Returns a list of User Names, done for form handling.
def getUserNameList(project_ID):
	sqlcommand = "SELECT user_ID from WORKS_ON WHERE project_ID = %s;"
	cur.execute(sqlcommand, [project_ID])
	userList = []
	for record in cur:
		userList.append(record[0])
	return userList

#Returns the role of the target user in that project.  This is done for authorization checks.
def getRole(project_ID, username):
	sqlcommand = "SELECT role from WORKS_ON where project_ID = %s AND user_ID = %s;"
	cur.execute(sqlcommand, [project_ID, username])
	result = None
	for record in cur:
		result = record[0]
	return result

#Returns the Object List of projects with their ID, Name and Role.  Done for printing your list of projects.
def getProjectList(username):
	sqlcommand = "SELECT project_id, role FROM WORKS_ON WHERE user_ID = %s;"
	cur.execute(sqlcommand, [username])
	projectList = []
	for record in cur:
		tempproject = project()
		tempproject.construct(record[0], record[1])
		projectList.append(tempproject)
	for x in range (0, len(projectList)):
		sqlcommand = "SELECT project_name from project_List where id = %s;"
		value = projectList[x].project_id
		cur.execute(sqlcommand, [value])
		for record in cur:
			projectList[x].project_name = record[0]
	return projectList

#Sets the project Status of the project in status (Frozen or Released (True/False)).  This is for freezing and releasing the project.
def setProjectStatus(project_id, status):
	sqlcommand = "UPDATE project_list SET frozen = %s WHERE id = %s;"
	cur.execute(sqlcommand, [status, project_id])
	conn.commit()

#REturns the status of the project (True for Frozen, False for Released), returns None if project doesn't exist.
def getProjectStatus(project_id):
	sqlcommand = "SELECT frozen FROM project_list where id = %s;"
	cur.execute(sqlcommand, [project_id])
	for record in cur:
		return record[0]
	return None

#Adds the user to the target project
def addUserToProject(project, user, role):
	sqlcommand = "INSERT INTO works_on VALUES(%s, %s, %s);"
	entry = [project, user, role]
	cur.execute(sqlcommand, entry)	
	conn.commit()

#Removes the user from the target project
def removeUser(username, project_ID):
	sqlcommand = "DELETE FROM works_on WHERE user_ID = %s AND project_id = %s;"
	cur.execute(sqlcommand, [username, project_ID])
	conn.commit()

#Creates a Project.  Returns a warning message if it fails to do so.  Otherwise, returns the id.  Need to have a better way to implement this.
def addProject(user_ID, project_name):
	if len(project_name) < 5:
		return "Your project name has too few characters.  Please make project names at least 5 characters or more."
	if len(project_name) > 32:
		return "Your project name has too many characters.  Please make project names no more than 32 characters long."
	for x in range(0, len(project_name)):
		substring = project_name[x:x+1]
		if not validCharacter(substring):
			return "Your Project Name has invalid characters.  Please don't anything other than numbers or characters."
	sqlcommand = "INSERT INTO project_list VALUES((SELECT MAX(id) from project_list) + 1, %s, false);"
	cur.execute(sqlcommand, [project_name])
	conn.commit()
	sqlcommand = "INSERT INTO works_on VALUES((SELECT MAX(id) from project_list), %s, 'Project Manager');"
	cur.execute(sqlcommand, [user_ID])
	conn.commit()
	sqlcommand = "SELECT MAX(id) from project_list;"
	cur.execute(sqlcommand)
	id_of_proj = ""
	for record in cur:
		id_of_proj = record[0]
	return id_of_proj

# ONLY RUN THIS IF YOU ARE MAKING A NEW DATABASE FROM SCRATCH!  THIS IS HERE FOR INITIALIZATION AND TESTING PURPOSES!		
def initializeDatabase():
	sqlcommand = "CREATE TABLE IF NOT EXISTS user_list(FName text, LName text, username text PRIMARY KEY, password text);"
	cur.execute(sqlcommand)
	conn.commit()
	sqlcommand = "CREATE TABLE IF NOT EXISTS project_list(ID serial PRIMARY KEY, project_name text, frozen boolean);"
	cur.execute(sqlcommand)
	conn.commit()
	sqlcommand = "CREATE TABLE IF NOT EXISTS works_on(project_ID integer, user_id text, FOREIGN KEY (project_ID) references project_list(ID), FOREIGN KEY (user_ID) references user_list(username), role text);"
	cur.execute(sqlcommand)
	conn.commit()
	sqlcommand = "INSERT INTO project_list VALUES(0, 'Do Not Delete Mii', true);"
	cur.execute(sqlcommand)
	conn.commit()

# ONLY RUN THIS IF YOU ARE PLANNING TO RUN TESTS ON THE DATABASE!  DO NOT RUN THIS METHOD OTHERWISE!
def wipeDatabase():
	sqlcommand = "DROP TABLE IF EXISTS works_on;"
	cur.execute(sqlcommand)
	conn.commit()
	sqlcommand = "DROP TABLE IF EXISTS project_list;"
	cur.execute(sqlcommand)
	conn.commit()
	sqlcommand = "Drop TABLE IF EXISTS user_list;"
	cur.execute(sqlcommand)
	conn.commit()

#TEST FUNCTION ONLY! NOT USED!
def projectExists(project_id):
	sqlcommand = "SELECT id FROM project_list where id = %s;"
	cur.execute(sqlcommand, [project_id])
	inputvalue = []
	for record in cur:
		if record[0] == project_id:
			return True
	return False

#Unused Method
def disconnect():
    conn.close()
    cur.close()

