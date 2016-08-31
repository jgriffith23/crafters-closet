"""Before running this file:

1. Drop the database
2. Recreate the database
3. Run model.py to create empty tables

"""


import unittest

from server import app
from model import db, example_data, connect_to_db


class CCTestsBasic(unittest.TestCase):
    """Tests for Crafter's Closet pages that don't require the db."""

    # Set up the app for testing and create a client.
    def setUp(self):
        app.config['TESTING'] = True
        app.secret_key = "ABC"
        self.client = app.test_client()

    def test_login_page(self):
        result = self.client.get("/login")
        self.assertIn("Sign In", result.data)

    def test_register_page(self):
        result = self.client.get("/register")
        self.assertIn("Repeat Password:", result.data)

    def test_homepage(self):
        result = self.client.get("/")
        self.assertIn("Welcome to Crafter's Closet!", result.data)

    def test_logout(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = 1
                sess['username'] = 'ihaveprojects'

        result = self.client.get("/logout", follow_redirects=True)
        self.assertIn("See you later!", result.data)

        with self.client as c:
            with c.session_transaction() as sess:
                self.assertIsNone(sess.get("username"))


class CCTestsDatabase(unittest.TestCase):
    """Flask tests that use the database."""

    def setUp(self):
        """Stuff to do before every test. Create a client, configure the
        app, connect to a test database, create the tables, and seed the testdb."""

        self.client = app.test_client()
        app.config['TESTING'] = True

        connect_to_db(app, "postgresql:///testdb")

        db.create_all()
        example_data()

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

    def test_login(self):
        # /login redirects to /dashboard on success, so need to follow
        # redirects.
        result = self.client.post("/login",
                                  data={"username": "ihaveprojects",
                                        "password": "tobehashed"},
                                  follow_redirects=True)

        self.assertIn("Hi, ihaveprojects!", result.data)

    def test_project_search_projects_exist(self):
        """Search for a term where matching projects should be in db."""
        result = self.client.get("/projects/search-results.html?search=clay")
        self.assertIn("clay", result.data)
        self.assertNotIn("sorry", result.data)

    def test_project_search_no_projects(self):
        """Search for a term where matching projects should NOT be in db."""
        result = self.client.get("/projects/search-results.html?search=foobar")
        self.assertNotIn("<td>", result.data)

    def test_register_user_all_data_okay(self):
        """Test a good registration."""
        result = self.client.post("/register",
                                  data={"email": "joe@schmo.com",
                                        "username": "joe",
                                        "password": "abc124",
                                        "repeat-pw": "abc124"})

        # For some reason, post parameters don't carry over to the redirect
        # in a testing environment. Known problem in Flask testing. Instead,
        # let's make sure we got the correct status code for the redirect.
        self.assertEqual(result.status_code, 307)

    def test_register_user_unmatched_pws(self):
        """Test a bad registration, where pws don't match."""
        result = self.client.post("/register",
                                  data={"email": "joe@schmo.com",
                                        "username": "joe",
                                        "password": "abc124",
                                        "repeat-pw": "abc123"},
                                  follow_redirects=True)

        self.assertIn("Entered passwords do not match.", result.data)
        self.assertNotEqual(result.status_code, 307)

    def test_register_user_username_in_db(self):
        """Test a bad registration, where the username is taken."""
        result = self.client.post("/register",
                                  data={"email": "joe@schmo.com",
                                        "username": "ihaveprojects",
                                        "password": "abc123",
                                        "repeat-pw": "abc123"},
                                  follow_redirects=True)

        self.assertIn("That username has already been registered.", result.data)
        self.assertNotEqual(result.status_code, 307)

    def test_dashboard(self):
        """Test whether user can view dashboard while logged in."""

        with self.client as c:
            with c.session_transaction() as session:
                session['user_id'] = 1
                session['username'] = 'ihaveprojects'
        result = self.client.get("/dashboard")
        self.assertIn("Your Inventory", result.data)


if __name__ == "__main__":
    unittest.main()
