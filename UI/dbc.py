import psycopg2
import sys

conn = psycopg2.connect("dbname=dynamic user=postgres password = lol")
cur = conn.cursor()

secretkey = 'erhhsdabuohewwerlqwnruqewrouir'

ACCEPTABLE_CHARACTERS = [48,57,65,90,97,122,32]
PASSWORD_MIN_SIZE = 6
PASSWORD_MAX_SIZE = 20

class userRole(object):
	def construct(self, uname, job):
		self.user_ID = uname
		self.role = job

class project(object):
	def construct(self, projid, job):
		self.project_id = projid
		self.role = job
		self.project_name = None

class presentation(object):
	def construct(self, pres_id, vers, primary):
		self.presentation_ID = pres_id
		self.version = vers
		self.is_primary = primary

class slideInPresentation(object):
	def construct(self, sli_ID, page_num):
		self.slide_ID = sli_ID
		self.page_number = page_num

def giveMetheSecretKey():
	return secretkey
	
def validCharacter(char):
	if(ord(char) >= ACCEPTABLE_CHARACTERS[0] and ord(char) > ACCEPTABLE_CHARACTERS[1]):
		return True
	if(ord(char) >= ACCEPTABLE_CHARACTERS[2] and ord(char) <= ACCEPTABLE_CHARACTERS[3]):
		return True
	if(ord(char) >= ACCEPTABLE_CHARACTERS[4] and ord(char) <= ACCEPTABLE_CHARACTERS[5]):
		return True
	if(ord(char) == ACCEPTABLE_CHARACTERS[6]):
		return True
	return False

def checkPassword(username, password):
	sqlcommand = "SELECT password FROM user_list where username = %s;"
	cur.execute(sqlcommand, [username])
	for record in cur:
		if(record[0] == password):
			return True
	return False

def userExists(username):
	sqlcommand = "SELECT username From user_list where username = %s;"
	cur.execute(sqlcommand, [username])
	for record in cur:
		if(record[0] == username):
			return True
	return False

def userInProject(username, project_ID):
	sqlcommand = "SELECT user_id FROM works_on WHERE project_id = %s;"
	cur.execute(sqlcommand, [project_ID])
	for record in cur:
		if(record[0] == username):
			return True
	return False
	
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
	sqlcommand = "INSERT INTO user_list VALUES(%s, %s, %s, %s);"
	cur.execute(sqlcommand, [FName, LName, username, password])
	conn.commit()
	result = "You are now registered into the Dynamic Presenter system!"
	return result

def getProjectName(project_id):
	sqlcommand = "SELECT project_name FROM project_list WHERE ID = %s;"
	cur.execute(sqlcommand, [project_id])
	result = ""
	for record in cur:
		result = record[0]
	return result
	
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

def getRole(project_ID, username):
	sqlcommand = "SELECT role from WORKS_ON where project_ID = %s AND user_ID = %s;"
	cur.execute(sqlcommand, [project_ID, username])
	result = None
	for record in cur:
		result = record[0]
	return result

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

def getPrimaryPresentation(project_ID):
	sqlcommand = "SELECT ID, version from presentation WHERE project_ID = %s AND primary_status = true"
	cur.execute(sqlcommand, [project_ID])
	result = []
	for record in cur:
		result.append(record[0])
		result.append(record[1])
	return result

def getPresentationList(project_ID):
	sqlcommand = "SELECT ID, version, primary_status FROM presentation WHERE project_ID = %s;"
	cur.execute(sqlcommand, [project_ID])
	presentationList = []
	for record in cur:
		temppresentation = presentation()
		temppresentation.construct(record[0], record[1], record[2])
		presentationList.append(temppresentation)
	return presentationList

def getSlideList(presentation):
	sqlcommand = "SELECT slide_ID, page_number FROM presentation where presentation_ID = %s;"
	cur.execute(sqlcommand, [presentation])
	slideList = []
	for record in cur:
		tempslide = slideInPresentation(r)
		tempslide.construct(record[0], record[1])
		slideList.append(tempslide)
	return slideList

def addUserToProject(project, user, role):
	sqlcommand = "INSERT INTO works_on VALUES(%s, %s, %s);"
	entry = [project, user, role]
	cur.execute(sqlcommand, entry)	
	conn.commit()
	
def removeUser(username):
	sqlcommand = "DELETE FROM works_on WHERE user_ID = %s;"
	cur.execute(sqlcommand, [username])
	conn.commit()
	
def addSlide(id, project_ID, version, creation_date, original_ID, previous_ID, approval_required, approval_status, confidentiality, mandatory_status, checkout_ID):
	sqlcommand = "INSERT INTO slide_list VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
	entry = [id, project_ID, version, creation_date, original_ID, previous_ID, approval_required, approval_status, confidentiality, mandatory_status, checkout_ID]
	cur.execute(sqlcommand, entry)
	conn.commit()
	
def addPresentation(id, project_ID, version, primary_status):
	sqlcommand = "INSERT INTO presentation VALUES(%s, %s, %s)"
	entry = [id, project_ID, version, primary_status]
	cur.execute(sqlcommand, entry)
	conn.commit()

def addPresentationContains(presentation_ID, slide_ID, page_number):
	sqlcommand = "INSERT INTO presentation_contains VALUES(%s, %s, %s);"
	entry = [presentation_ID, slide_ID, page_number]
	cur.execute(sqlcommand, entry)
	conn.commit()
	
def addOptOut(slide_ID, user_ID, opt_out_status):
	sqlcommand = "INSERT INTO opt_out_list VALUES(%s, %s, %s);"
	entry = [slide_ID, user_ID, opt_out_status]
	cur.execute(sqlcommand, entry)
	conn.commit()

def addProject(user_ID, project_name):
	if len(project_name) < 5:
		return "Your project name has too few characters.  Please make project names at least 5 characters or more."
	if len(project_name) > 32:
		return "Your project name has too many characters.  Please make project names no more than 32 characters long."
	for x in range(0, len(project_name)):
		substring = project_name[x:x+1]
		if not validCharacter(substring):
			return "Your Project Name has invalid characters.  Please don't anything other than numbers or characters."
	sqlcommand = "INSERT INTO project_list VALUES((SELECT MAX(id) from project_list) + 1, %s);"
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
	
def optOut(slide_ID, user_ID):
	sqlcommand = "SELECT * FROM opt_out_list WHERE slide_ID = %s AND user_ID = %s);"
	cur.execute(sqlcommand, [slide_ID, user_ID])
	for record in cur:
		if(record[2] == 'Optional'):
			sqlcommand = "UPDATE TABLE opt_out_list SET opt_out_status = true WHERE (slide_ID = %s) AND (user_ID = %s);"
			cur.execute(sqlcommand, [slide_ID, user_ID])
			conn.commit()
			
def updatePrimary(presentation_ID, project_ID):
	sqlcommand = "UPDATE TABLE presentation SET primary_status = false WHERE (project_ID = %s) AND (primary_status = true);"
	cur.execute(sqlcommand, [project_ID])
	conn.commit()
	sqlcommand = "UPDATE TABLE presentation SET primary_status = true WHERE (presentation_ID = %s);"
	cur.execute(sqlcommand, [presentation_ID])
	conn.commit()
		
def disconnect():
        conn.close()
        cur.close()