import os
import os.path
import unittest

import dbc
from helper import remove_test_result, get_vcs

conn = psycopg2.connect("dbname=testdynamic user=postgres password = lol")
cur = conn.cursor()

def get_tests():
	return (TestAddUser, TestValidCharacters, TestCheckPassword, TestUserExists, TestUserInProject, TestDeletableUserList, TestGetProjectName, TestGetUserList, TestGetUserNameList, TestGetRole, TestGetProjectList, TestSetProjectStatus, TestGetProjectStatus, TestAddUserToProject, TestRemoveUser, TestAddProject)

class TestAddUser(unittest.TestCase):
	def setUp(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()
		remove_test_result()

	def tearDown(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()
		remove_test_result()

	def test_add_user_fail_if_pw_too_short(self):
		result = dbc.addUser("Jimmy", "Tester", "test1", "test", "test")
		self.assertIsEqual(result, "Your password length is incorrect.  Please input a new password!")

	def test_add_user_fail_if_repeat_password_does_not_match(self):
		result = dbc.addUser("Jimmy", "Tester", "test1", "testmiiplz", "test")
		self.assertIsEqual(result, "Your passwords do not match.  Please re-input your passwords!")

	def test_add_user_fail_if_user_exists(self):
		dbc.addUser("Jimmy", "Tester", "test1", "testmiiplz", "testmiiplz")		
		result = dbc.addUser("Jimmy", "Tester", "test1", "testmiiplz", "testmiiplz")
		self.assertIsEqual(result, "This username already exists.  Please pick another username!")

	def test_add_user_fail_if_password_invalid_characters(self):
		result = dbc.addUser("Jimmy", "Tester", "test1", "tesm$$plz", "testm$$plz")
		self.assertIsEqual(result, "Your password has an invalid character in the string.  Please input a new password!")

	def test_add_user_pass_if_successful(self):
		result = dbc.addUser("Jimmy", "Tester", "test1", "testmiiplz", "testmiiplz")
		self.assertIsEqual(result, "You are now registered into the Dynamic Presenter system!")

class TestValidCharacters(unittest.TestCase):
	def test_valid_character_pass_if_valid(self):
		result = dbc.ValidCharacter("a")
		self.assertTrue(result)

	def test_valid_character_fail_if_invalud(self):
		result = dbc.ValidCharacter("^")
		self.assertFalse(result)
		
class TestCheckPassword(unittest.TestCase):
	def setUp(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()
		dbc.addUser("Jimmy", "Tester", "test1", "testthis", "testthis")

	def tearDown(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()

	def check_password_pass_if_true(self):
		result = dbc.checkPassword("test1", "testthis")
		self.assertTrue(result)

	def check_password_pass_if_false(self):
		result = dbc.checkPassword("test1", "failthistest")
		self.assertFalse(result)

class TestUserExists(unittest.TestCase):
	def setUp(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()
		dbc.addUser("Jimmy", "Tester", "test1", "testthis", "testthis")

	def tearDown(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()

	def user_exists_pass_if_true(self):
		result = dbc.userExists("test1")
		self.assertTrue(result)

	def user_exists_pass_if_false(self):
		result = dbc.userExists("test2")
		sef.assertIsEqual(result, False)

class TestUserInProject(unittest.TestCase):
		def setUp(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()
		dbc.addUser("Jimmy", "Tester", "test1", "testthis", "testthis")
		dbc.addProject(1, "TestThisProject")
		dbc.addUserToProject(1, "test1", "Project Manager")

	def tearDown(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()

	def user_in_project_pass_if_exists(self):
		result = dbc.userInProject("test1", 1)
		self.assertTrue(result)

	def user_in_project_pass_if_not_exists(self):
		result = dbc.userInProject("test2", 1)
		self.assertFalse(result)

class TestDeletableUserList(unittest.TestCase):
	def setUp(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()
		dbc.addUser("Jimmy", "Tester", "test1", "testthis", "testthis")
		dbc.addProject(1, "TestThisProject")
		dbc.addUserToProject(1, "test1", "Project Manager")

	def tearDown(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()

	def deletable_user_list_pass_if_empty(self):
		result = dbc.deletableUserList(1)
		self.assertIsEqual(result, [])

	def deletable_user_list_pass_if_not_empty(self):
		dbc.addUser("Jack", "Tester", "test2", "testthis", "testthis")
		dbc.addUserToProject(1, "test2", "Slide Creator")
		result = dbc.deletableUserList(1)		
		dbc.removeUser("test2", 1)
		self.assertIsNotEqual(result, [])

class TestGetProjectName(unittest.TestCase):
	def setUp(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()
		dbc.addProject(1, "TestThisProject")

	def tearDown(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()

	def get_project_name_pass_if_equal(self):
		dbc.getProjectName(1)
		dbc.assertIsEqual(result, "TestThisProject")

class TestGetUserList(unittest.TestCase):
	def setUp(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()
		dbc.addUser("Jimmy", "Tester", "test1", "testthis", "testthis")
		dbc.addProject(1, "TestThisProject")
		dbc.addUserToProject(1, "test1", "Project Manager")

	def tearDown(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()

	def get_user_list_pass_if_not_empty(self):
		result = dbc.getUserList(1)
		self.assertIsNotEqual(result, [])

class TestGetUserNameList(unittest.TestCase):
	def setUp(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()
		dbc.addUser("Jimmy", "Tester", "test1", "testthis", "testthis")
		dbc.addProject(1, "TestThisProject")
		dbc.addUserToProject(1, "test1", "Project Manager")

	def tearDown(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()

	def get_user_name_list_pass_if_not_empty(self):
		result = dbc.getUserNameList(1)
		self.assertIsEqual(result, "test1")

class TestGetRole(unittest.TestCase):
	def setUp(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()
		dbc.addUser("Jimmy", "Tester", "test1", "testthis", "testthis")
		dbc.addProject(1, "TestThisProject")
		dbc.addUserToProject(1, "test1", "Project Manager")

	def tearDown(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()

	def get_role_pass_if_equal(self):
		result = dbc.getRole(1, "test1")
		self.assertIsEqual(result, "Project Manager")

class TestGetProjectList(unittest.TestCase):
	def setUp(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()
		dbc.addUser("Jimmy", "Tester", "test1", "testthis", "testthis")
		dbc.addProject(1, "TestThisProject")
		dbc.addUserToProject(1, "test1", "Project Manager")

	def tearDown(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()

	def get_project_list_pass_if_has_project(self):
		result = dbc.getProjectList("test1")
		self.assertIsNotEqual(result, [])

class TestSetProjectStatus(unittest.TestCase):
	def setUp(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()
		dbc.addProject(1, "TestThisProject")

	def tearDown(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()

	def set_project_status_pass_if_true(self):
		dbc.setProjectStatus(1, True)
		result = dbc.getProjectStatus(1)
		self.assertTrue(result)

	def set_project_status_pass_if_false(self):
		dbc.setProjectStatus(1, False)
		result = dbc.getProjectStatus(1)
		self.assertFalse(result)

class TestGetProjectStatus(unittest.TestCase):
	def setUp(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()
		dbc.addProject(1, "TestThisProject")

	def tearDown(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()

	def get_project_status_pass_if_false(self):
		result = dbc.getProjectStatus(1)
		self.assertFalse(result)

class TestAddUserToProject(unittest.TestCase):
	def setUp(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()
		dbc.addUser("Jimmy", "Tester", "test1", "testthis", "testthis")
		dbc.addProject(1, "TestThisProject")

	def tearDown(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()

	def add_user_to_project_pass_if_not_empty(self):
		dbc.addUserToProject(1, "test1", "Project Manager")
		result = getUserNameList(1)
		self.assertIsEqual(result, "test1")

class TestRemoveUser(unittest.TestCase):
	def setUp(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()
		dbc.addUser("Jimmy", "Tester", "test1", "testthis", "testthis")
		dbc.addProject(1, "TestThisProject")
		dbc.addUserToProject(1, "test1", "Project Manager")

	def tearDown(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()

	def remove_user_pass_if_empty(self):
		dbc.removeUser("test1", 1)
		result = dbc.getUserList
		self.assertIsEqual(result, [])

class TestAddProject(unittest.TestCase):
	def setUp(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()

	def tearDown(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()

	def add_project_pass_if_true(self):
		dbc.addProject(1, "TestThisProject")
		result = dbc.projectExists(1)
		self.assertTrue(result)