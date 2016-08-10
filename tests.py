"""Before running this file:

1. Drop the database
2. Recreate the database
3. Run model.py to create empty tables

"""


import unittest

from server import app
from model import db, example_data, connect_to_db


class CCTests(unittest.TestCase):
    """Tests for Crafter's Closet website."""

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_homepage(self):
        result = self.client.get("/")
        self.assertIn("Welcome to Crafter's Closet!", result.data)


class CCTestsDatabase(unittest.TestCase):
    """Flask tests that use the database."""

    def setUp(self):
        """Stuff to do before every test."""

        self.client = app.test_client()
        app.config['TESTING'] = True

        # Connect to test database (uncomment when testing database)
        connect_to_db(app, "postgresql:///testdb")

        # Create tables and add sample data (uncomment when testing database)
        db.create_all()
        example_data()

        with self.client as c:
            with c.session_transaction() as session:
                session['user_id'] = 3

    def tearDown(self):
        """Do at end of every test."""

        # (uncomment when testing database)
        db.session.close()
        db.drop_all()


if __name__ == "__main__":
    unittest.main()
