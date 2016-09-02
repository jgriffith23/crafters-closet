"""Before running this file:

1. Drop the database
2. Recreate the database
3. Run model.py to create empty tables

"""


import unittest
from selenium import webdriver
from server import app
from flask import json
from model import db, example_data, connect_to_db


######################################################################
# Tests that don't require the database or an active session.
######################################################################

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


######################################################################
# Tests that require an active session, but no database access.
######################################################################
class CCTestsUsingSessionNoDB(unittest.TestCase):
    """These tests require the session to be active but don't interact with
    the database."""

    # Set up the app for testing and create a client.
    def setUp(self):
        app.config['TESTING'] = True
        app.secret_key = "ABC"
        self.client = app.test_client()

        add_test_user_to_session(self)

    def test_logout(self):
        add_test_user_to_session(self)

        result = self.client.get("/logout", follow_redirects=True)
        self.assertIn("See you later!", result.data)

        with self.client as c:
            with c.session_transaction() as sess:
                self.assertIsNone(sess.get("username"))


######################################################################
# Tests that require database access but not an active session. These
# should not be able to change the database EVER.
######################################################################
class CCTestsDatabaseQueriesNoSession(unittest.TestCase):
    """These are tests that query the database but don't require a session.
    These tests should not change the database."""

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

    def test_get_brands_by_type(self):
        result = self.client.get("/dashboard/brands.json")
        data = json.loads(result.data)
        self.assertEqual(data["Acrylic Paint"][0], "Americana")

    def test_prevent_unauthenticated_dashboard_access(self):
        """Make sure a user can't access the dashboard unless they have an
        active session."""
        result = self.client.get("/dashboard", follow_redirects=True)
        self.assertIn("Please log in.", result.data)
        self.assertNotIn("Your Inventory", result.data)


######################################################################
# Tests that require database access and an active session, but don't
# alter the state of the database.
######################################################################
class CCTestsDatabaseQueriesOnlyWithSession(unittest.TestCase):
    """These tests are for routes that only query the database and require
    a session."""

    def setUp(self):
        """Stuff to do before every test. Create a client, configure the
        app, connect to a test database, create the tables, and seed the testdb."""

        self.client = app.test_client()
        app.config['TESTING'] = True

        connect_to_db(app, "postgresql:///testdb")

        db.create_all()
        example_data()

        add_test_user_to_session(self)

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

    # def test_get_inventory_chart_dict(self):
    #     """Try to get data about supplies in user's inventory for the donut chart. Should
    #     give a dictionary back."""

    #     result = self.client.get("/supply-types")
    #     self.assertIsInstance(result.data, json)



######################################################################
# Tests that require database access, need an active session, and
# can actually change the database.
######################################################################
class CCTestsDatabaseChanges(unittest.TestCase):
    """Flask tests that actually change the database."""

    def setUp(self):
        """Stuff to do before every test. Create a client, configure the
        app, connect to a test database, create the tables, and seed the testdb."""

        self.client = app.test_client()
        app.config['TESTING'] = True

        # We can't change the db without having a user in the session, as all
        # possible changes are associated with users.
        add_test_user_to_session(self)

        connect_to_db(app, "postgresql:///testdb")

        db.create_all()
        example_data()

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

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

    def test_add_completely_new_supply(self):
        """Try to add a supply to user's inventory, where the details are not
        already in the db."""

        data = {"supplytype": "Acrylic Paint",
                "brand": "Americana",
                "color": "Electric Purple",
                "units": "oz",
                "quantity-owned": "42"}

        result = self.client.post("/add-supply",
                                  data=data,
                                  follow_redirects=True)

        self.assertIn("this is new!", result.data)
        self.assertIn("Electric Purple", result.data)

    def test_add_item_where_supply_exists(self):
        """Try to add a supply to user's inventory, where the details are
        already in the db."""

        data = {"supplytype": "Acrylic Paint",
                "brand": "Americana",
                "color": "Bittersweet Chocolate",
                "units": "oz",
                "quantity-owned": "42"}

        result = self.client.post("/add-supply",
                                  data=data,
                                  follow_redirects=True)
        row_str = '42 oz </div>'

        self.assertIn("of Americana Bittersweet Chocolate", result.data)
        self.assertIn("Americana", result.data)
        self.assertIn(row_str, result.data)

    def test_update_inventory_item_on_add(self):
        """Test whether we can successfully update an existing inventory
        item record if the user tries to re-add it."""

        # The authenticated user should already own the item whose data matches
        # the dict below.
        data = {"supplytype": "Oven-Bake Clay",
                "brand": "Sculpey",
                "color": "Terra Cotta",
                "units": "oz",
                "quantity-owned": "3"}

        result = self.client.post("/add-supply",
                                  data=data,
                                  follow_redirects=True)

        # We're expecting a flash message, so let's look for it.
        expected_str = "Amount of Sculpey Terra Cotta Oven-Bake Clay updated."

        self.assertIn(expected_str, result.data)

    def test_overwrite_inventory_item(self):
        """Test whether the we can successfully overwrite an item in the user's
        inventory with a new qty."""

        # The authenticated user should own the item with ID 1.
        data = {"qty": "5", "itemID": "1"}

        result = self.client.post("/update-item",
                                  data=data,
                                  follow_redirects=True)

        # After this call, the resulting string (to be passed to front end) should
        # contain the new qty and units.
        self.assertIn("5 oz", result.data)

    def test_delete_inventory_item(self):
        """Test whether we can successfully delete an item in the user's inventory
        if they explicitly ask to update that item with a qty of 0."""

        # The authenticated user should own the item with ID 1.
        data = {"qty": "0", "itemID": "1"}

        result = self.client.post("/update-item",
                                  data=data,
                                  follow_redirects=True)

        # After this call, the resulting string (to be passed to front end) should
        # be "Deleted!"
        self.assertIn("Deleted!", result.data)


######################################################################
# Helpers/code to run the tests
######################################################################


def add_test_user_to_session(test_class_instance):
    with test_class_instance.client as c:
        with c.session_transaction() as session:
            session['user_id'] = 1
            session['username'] = 'ihaveprojects'

if __name__ == "__main__":
    unittest.main()
