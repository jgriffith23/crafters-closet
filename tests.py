"""Before running this file:

1. Drop the database
2. Recreate the database
3. Run model.py to create empty tables

"""


import unittest

from server import app
from model import db, example_data, connect_to_db


class CCTestsBasic(unittest.TestCase):
    """Tests for Crafter's Closet website."""

    def setUp(self):
        app.config['TESTING'] = True
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


class CCTestsDatabase(unittest.TestCase):
    """Flask tests that use the database."""

    def setUp(self):
        """Stuff to do before every test."""

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
        result = self.client.post("/login",
                                  data={"username": "ihaveprojects", "password": "tobehashed"},
                                  follow_redirects=True)
        self.assertIn("Hi, ihaveprojects!", result.data)

    def test_register_user_good_data(self):
        result = self.client.post("/register",
                                  data={"email": "joe@schmo.com",
                                        "username": "joe",
                                        "password": "abc124",
                                        "repeat_pw": "abc124"},
                                  follow_redirects=True)
        self.assertIn("Hi, joe!", result.data)

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
