import os
import os.path
import unittest

from UI import dbc
import psycopg2

dbc.conn = psycopg2.connect("dbname=testdynamic user=postgres password = lol")
dbc.cur = dbc.conn.cursor()

def get_tests():
	return (TestAddUser, TestvalidCharacters, TestCheckPassword, TestUserExists, TestUserInProject, TestDeletableUserList, TestGetProjectName, TestGetUserList, TestGetUserNameList, TestGetRole, TestGetProjectList, TestSetProjectStatus, TestGetProjectStatus, TestAddUserToProject, TestRemoveUser, TestAddProject)

class TestAddUser(unittest.TestCase):
	def setUp(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()
		

	def tearDown(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()
		

	def test_add_user_fail_if_pw_too_short(self):
		result = dbc.addUser("Jimmy", "Tester", "test1", "test", "test")
		self.assertEqual(result, "Your password length is incorrect.  Please input a new password!")

	def test_add_user_fail_if_repeat_password_does_not_match(self):
		result = dbc.addUser("Jimmy", "Tester", "test1", "testmiiplz", "test")
		self.assertEqual(result, "Your passwords do not match.  Please re-input your passwords!")

	def test_add_user_fail_if_user_exists(self):
		dbc.addUser("Jimmy", "Tester", "test1", "testmiiplz", "testmiiplz")		
		result = dbc.addUser("Jimmy", "Tester", "test1", "testmiiplz", "testmiiplz")
		self.assertEqual(result, "This username already exists.  Please pick another username!")

	def test_add_user_fail_if_password_invalid_characters(self):
		result = dbc.addUser("Jimmy", "Tester", "test1", "testm$$plz", "testm$$plz")
		self.assertEqual(result, "Your password has an invalid character in the string.  Please input a new password!")

	def test_add_user_pass_if_successful(self):
		result = dbc.addUser("Jimmy", "Tester", "test1", "testmiiplz", "testmiiplz")
		self.assertEqual(result, "You are now registered into the Dynamic Presenter system!")

class TestvalidCharacters(unittest.TestCase):
	def test_valid_character_pass_if_valid(self):
		result = dbc.validCharacter("a")
		self.assertTrue(result)

	def test_valid_character_fail_if_invalid(self):
		result = dbc.validCharacter("@")
		self.assertFalse(result)
		
class TestCheckPassword(unittest.TestCase):
	def setUp(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()
		dbc.addUser("Jimmy", "Tester", "test1", "testthis", "testthis")
		

	def tearDown(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()
		

	def test_check_password_pass_if_true(self):
		result = dbc.checkPassword("test1", "testthis")
		self.assertTrue(result)

	def test_check_password_pass_if_false(self):
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
		

	def test_user_exists_pass_if_true(self):
		result = dbc.userExists("test1")
		self.assertTrue(result)

	def test_user_exists_pass_if_false(self):
		result = dbc.userExists("test2")
		self.assertFalse(result)

class TestUserInProject(unittest.TestCase):
	def setUp(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()
		dbc.addUser("Jimmy", "Tester", "test1", "testthis", "testthis")
		dbc.addProject("test1", "TestThisProject")
		dbc.addUserToProject(1, "test1", "Project Manager")		

	def tearDown(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()		

	def test_user_in_project_pass_if_exists(self):
		result = dbc.userInProject("test1", 1)
		self.assertTrue(result)

	def test_user_in_project_pass_if_not_exists(self):
		result = dbc.userInProject("test2", 1)
		self.assertFalse(result)

class TestDeletableUserList(unittest.TestCase):
	def setUp(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()
		dbc.addUser("Jimmy", "Tester", "test1", "testthis", "testthis")
		dbc.addProject("test1", "TestThisProject")
		dbc.addUserToProject(1, "test1", "Project Manager")
		

	def tearDown(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()
		

	def test_deletable_user_list_pass_if_empty(self):
		result = dbc.deletableUserList(1)
		self.assertEqual(result, [])

	def test_deletable_user_list_pass_if_not_empty(self):
		dbc.addUser("Jack", "Tester", "test2", "testthis", "testthis")
		dbc.addUserToProject(1, "test2", "Slide Creator")
		result = dbc.deletableUserList(1)		
		dbc.removeUser("test2", 1)
		self.assertNotEqual(result, [])

class TestGetProjectName(unittest.TestCase):
	def setUp(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()
		dbc.addUser("Junk", "Junk", "junk", "junkuser", "junkuser")
		dbc.addProject("junk", "TestThisProject")
		

	def tearDown(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()
		

	def test_get_project_name_pass_if_equal(self):
		result = dbc.getProjectName(1)
		self.assertEqual(result, "TestThisProject")

class TestGetUserList(unittest.TestCase):
	def setUp(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()
		dbc.addUser("Jimmy", "Tester", "test1", "testthis", "testthis")
		dbc.addProject("test1", "TestThisProject")
		dbc.addUserToProject(1, "test1", "Project Manager")
		

	def tearDown(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()
		

	def test_get_user_list_pass_if_not_empty(self):
		result = dbc.getUserList(1)
		self.assertNotEqual(result, [])

class TestGetUserNameList(unittest.TestCase):
	def setUp(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()
		dbc.addUser("Jimmy", "Tester", "test1", "testthis", "testthis")
		dbc.addProject("test1", "TestThisProject")		

	def tearDown(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()
		

	def test_get_user_name_list_pass_if_not_empty(self):
		result = dbc.getUserNameList(1)
		self.assertEqual(result, ["test1"])

class TestGetRole(unittest.TestCase):
	def setUp(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()
		dbc.addUser("Jimmy", "Tester", "test1", "testthis", "testthis")
		dbc.addProject("test1", "TestThisProject")
		dbc.addUserToProject(1, "test1", "Project Manager")
		

	def tearDown(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()
		

	def test_get_role_pass_if_equal(self):
		result = dbc.getRole(1, "test1")
		self.assertEqual(result, "Project Manager")

class TestGetProjectList(unittest.TestCase):
	def setUp(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()
		dbc.addUser("Jimmy", "Tester", "test1", "testthis", "testthis")
		dbc.addProject("test1", "TestThisProject")
		dbc.addUserToProject(1, "test1", "Project Manager")
		

	def tearDown(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()
		

	def test_get_project_list_pass_if_has_project(self):
		result = dbc.getProjectList("test1")
		self.assertNotEqual(result, [])

class TestSetProjectStatus(unittest.TestCase):
	def setUp(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()
		dbc.addUser("Junk", "Input", "junk", "junktest", "junktest")
		dbc.addProject("junk", "TestThisProject")
		

	def tearDown(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()
		

	def test_set_project_status_pass_if_true(self):
		dbc.setProjectStatus(1, True)
		result = dbc.getProjectStatus(1)
		self.assertTrue(result)

	def test_set_project_status_pass_if_false(self):
		dbc.setProjectStatus(1, False)
		result = dbc.getProjectStatus(1)
		self.assertFalse(result)

class TestGetProjectStatus(unittest.TestCase):
	def setUp(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()
		dbc.addUser("Junk", "Input", "junk", "junktest", "junktest")
		dbc.addProject("junk", "TestThisProject")
		

	def tearDown(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()		

	def test_get_project_status_pass_if_false(self):
		result = dbc.getProjectStatus(1)
		self.assertFalse(result)

class TestAddUserToProject(unittest.TestCase):
	def setUp(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()
		dbc.addUser("Junk", "Input", "junk", "junktest", "junktest")
		dbc.addProject("junk", "TestThisProject")
		dbc.addUser("Jimmy", "Tester", "test1", "testthis", "testthis")
		

	def tearDown(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()
		

	def test_add_user_to_project_pass_if_not_empty(self):
		dbc.addUserToProject(1, "test1", "Slide Creator")
		result = dbc.deletableUserList(1)
		self.assertEqual(result[0], "test1")

class TestRemoveUser(unittest.TestCase):
	def setUp(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()
		dbc.addUser("Jimmy", "Tester", "test1", "testthis", "testthis")
		dbc.addProject("test1", "TestThisProject")		

	def tearDown(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()		

	def test_remove_user_pass_if_empty(self):
		dbc.removeUser("test1", 1)
		result = dbc.getUserList(1)
		self.assertEqual(len(result), 0)

class TestAddProject(unittest.TestCase):
	def setUp(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()
		dbc.addUser("Junk", "User", "junk", "junktest", "junktest")
		dbc.addProject("junk", "junktest")		

	def tearDown(self):
		dbc.wipeDatabase()
		dbc.initializeDatabase()		

	def test_add_project_pass_if_true(self):
		dbc.addProject("junk", "TestThisProject")
		result = dbc.projectExists(1)
		self.assertTrue(result)
