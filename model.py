from flask_sqlalchemy import SQLAlchemy

# Create an object representing the idea of the Crafter's Closet database.
db = SQLAlchemy()


##############################################################
# Primary table models. Users, supplies, and projects.
##############################################################

# The users and supplies tables will have no foreign keys, so create
# those first.

class User(db.Model):
    """A model that represents a user."""

    # Set the table name for this model.
    __tablename__ = "users"

    # Create the columns in the users table.
    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    # Since other users will be able to see which user created a project,
    # emails won't double as usernames, for privacy purposes. A user should
    # be allowed to have multiple usernames attached to one email, if they
    # want.
    email = db.Column(db.String(64), nullable=False)
    username = db.Column(db.String(64), nullable=False, unique=True)
    password = db.Column(db.String(64), nullable=True)

    def get_inventory(self):
        """Get the current user's inventory details as a list of tuples of the
        format: (type, brand, color, units, url, qty)"""
        inventory = db.session.query(SupplyDetail.supply_type,
                                     SupplyDetail.brand,
                                     SupplyDetail.color,
                                     SupplyDetail.units,
                                     SupplyDetail.purchase_url,
                                     Item.qty,
                                     Item.item_id).outerjoin(Item).filter_by(user_id=self.user_id).all()

        inventory = sorted(inventory)
        return inventory

    def get_projects(self):
        """Get all of the user's projects as objects."""
        return Project.query.filter(Project.user_id == self.user_id).all()

    def get_filtered_inventory(self, brand="", supply_type="", color=""):
        """Given a user and filter parameters, fetches inventory table HTML to only
        display supplies matching those parameters. Returns list of tuples."""

        # Craft a query to the db for all needed columns.
        q = db.session.query(SupplyDetail.supply_type,
                             SupplyDetail.brand,
                             SupplyDetail.color,
                             SupplyDetail.units,
                             SupplyDetail.purchase_url,
                             Item.qty,
                             Item.item_id).outerjoin(Item).filter(Item.user_id == self.user_id)

        # If the brand actually came with a filter selected, fetch the inventory
        # filtered by brand.
        if brand != "":

            q = q.filter(SupplyDetail.brand == brand)

        # If we aren't filtering by brand, then check the supply type argument
        # to see if it's not empty.
        if supply_type != "":

            # Craft a query to the db for all needed columns.
            q = q.filter(SupplyDetail.supply_type == supply_type)

        # If we aren't filtering by brand or type, then check the color argument
        # to see if it's not empty.
        if color != "":

            q = q.filter(SupplyDetail.color == color)

        # Fetch the inventory, filtered by the passed parameters. (If the user
        # didn't enter any, then we'll get the whole inventory.)
        inventory = sorted(q.all())

        return inventory

    def get_inventory_by_search(self, search_term):
        """Given a user id and search parameter, get a list of tuples representing
        all items owned by that user with the relevant strings."""

        # Craft a query to the db for all needed columns.
        q = db.session.query(SupplyDetail.supply_type,
                             SupplyDetail.brand,
                             SupplyDetail.color,
                             SupplyDetail.units,
                             SupplyDetail.purchase_url,
                             Item.qty,
                             Item.item_id).outerjoin(Item).filter(Item.user_id == self.user_id)

        # Wrap the user's search term in SQL wildcards and use it as a filter
        # on the existing query.
        sql_like_str = "%" + search_term + "%"
        q = q.filter(SupplyDetail.supply_type.ilike(sql_like_str) |
                     SupplyDetail.brand.ilike(sql_like_str) |
                     SupplyDetail.color.ilike(sql_like_str))

        # Fetch the inventory, filtered by the search parameter.
        inventory = sorted(q.all())

        return inventory

    def get_inventory_search_ac_tags(self, search_term):
        """Given a user ID and the user's search term, return a list of possible
        existing inventory information the user might be trying to type."""

        # Craft a query to the db for all needed columns.
        q = db.session.query(SupplyDetail.supply_type,
                             SupplyDetail.brand,
                             SupplyDetail.color,
                             SupplyDetail.units,
                             SupplyDetail.purchase_url,
                             Item.qty,
                             Item.item_id).outerjoin(Item).filter(Item.user_id == self.user_id)

        inventory = sorted(q.all())

        # We only want to show a given tag once, so create an empty set to contain
        # the tags.
        tags = set()

        # For each item in the user's inventory, check whether the search term
        # is used anywhere in that item's supply details. If so, add it to our set
        # of tags.
        for item in inventory:

            if search_term.lower() in item.supply_type.lower():
                tags.add(item.supply_type)

            if search_term.lower() in item.brand.lower():
                tags.add(item.brand)

            if search_term.lower() in item.color.lower():
                tags.add(item.color)

        # Convert the set of tags to a list for easy jsonification, and sort it
        # for the user's sanity.
        tags = sorted(list(tags))

        return tags

    def __repr__(self):
        """Provide a human-readable representation of an instance of the
        User class."""

        # Perhaps we'll allow users to make their email addresses public, so
        # it's okay to show that as part of the user representation.
        return "<User email=%s, username=%s>" % (self.email, self.username)


class SupplyDetail(db.Model):
    """A model that represents a set of details about a supply. Table will have
    a row for each craft supply in all of Crafter's Closet.
    """

    # Set the table name for this model.
    __tablename__ = "supply_details"

    # Create the columns in the supplies table.
    sd_id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    # If a user is going to log a craft supply, at least force them to include
    # the supply type.
    supply_type = db.Column(db.String(32), index=True, nullable=False)
    brand = db.Column(db.String(64), index=True, nullable=True)
    color = db.Column(db.String(32), index=True, nullable=True)

    # Units will be a string representation of how a supply is measured. Examples
    # include ft, in, m, mm, square(s), oz, yd, sq in, lb, g, and so on. This
    # field is mandatory for all new supplies created for users to choose from
    # because otherwise, Crafter's Closet won't be able to accurately track
    # a user's inventory.
    units = db.Column(db.String(16), nullable=False)

    # Make the purchase URL nullable, in case a URL for this supply doesn't exist.
    purchase_url = db.Column(db.String(256), nullable=True)

    def __repr__(self):
        """Provide a human-readable representation of an instance of the Supply
        class."""

        # Note: Brand and color are nullable, so they may be printed as
        # "None" in output.
        return "<Supply type=%s, brand=%s, color=%s, units=%s>" % \
               (self.supply_type, self.brand, self.color, self.units)


class Project(db.Model):
    """A model that represents a project created by a user."""

    # Set the table name for this model.
    __tablename__ = "projects"

    # Create the columns in the projects table.
    project_id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    # Enforce titles, for search purposes.
    title = db.Column(db.String(64), index=True, nullable=False)

    # Set foreign key into users table
    user_id = db.Column(db.Integer,
                        db.ForeignKey("users.user_id"),
                        nullable=False)

    # The projects table has a relationship with users: One user can
    # have many projects, but a project can have only one user.
    user = db.relationship("User",
                           backref=db.backref("projects"))

    # If a user doesn't care about logging instructions or a description,
    # then that's on them.
    instr_url = db.Column(db.String(256), nullable=True)
    img_url = db.Column(db.String(256), nullable=True)
    description = db.Column(db.String(500), index=True, nullable=True)

    def __repr__(self):

        return "<Project title=%s, instr_url=%s, description=%s>" % \
            (self.title, self.instr_url, self.description)

    def get_project_supplies_list(self):
        """Get details about the supplies required to make this project instance
        project.

        Format of data: {'color': ???, 'brand': ???, 'qty_to_buy': ???, 'sd_id': ???
                         'units': ???, 'qty_specified': ???, 'supply_type': ???}

        Example:
        [{'color': u'Petal Pink', 'brand': u'Red Heart', 'qty_to_buy': 0, 'sd_id': 1,
          'units': u'yds', 'qty_specified': 4, 'supply_type': u'yarn'},
          {'color': u'blue', 'brand': u'SparkFun', 'qty_to_buy': 0, 'sd_id': 24,
          'units': u'components', 'qty_specified': 6, 'supply_type': u'LED'},
          {'color': u'beige', 'brand': u'Sticks n Stuff', 'qty_to_buy': 45, 'sd_id':
          30, 'units': u'pcs', 'qty_specified': 45, 'supply_type': u'Popsicle Sticks'}]
        """

        # Craft a query to join the tables defined by the SupplyDetail and
        # ProjectSupply models, so we can get information from both.
        q = db.session.query(SupplyDetail.sd_id,
                             SupplyDetail.supply_type,
                             SupplyDetail.brand,
                             SupplyDetail.color,
                             ProjectSupply.supply_qty,
                             SupplyDetail.units).join(ProjectSupply,
                                                      SupplyDetail.sd_id == ProjectSupply.sd_id)

        # Add a filter to the query so that we'll only get details for supplies related
        # to the passed project
        q_filtered = q.filter(ProjectSupply.project_id == self.project_id)

        # Fetch the specified details
        specified_supplies = q_filtered.all()

        # Create an empty list and a list containing the columns for each piece
        # of info for a supply
        supplies_list = []
        columns = ["sd_id", "supply_type", "brand", "color", "qty_specified", "units"]

        # For each set of supply information, create a dictionary using the columns
        # above as keys and the information itself as values.
        for supply in specified_supplies:
            supply_dict = dict(zip(columns, supply))
            supplies_list.append(supply_dict)

        # Return a list of dictionaries
        return supplies_list


######################################################################
# Models for middle tables relating projects/users, projects/supplies
######################################################################


class ProjectSupply(db.Model):
    """ A model that represents the relationship between a project and a
    set of supply information. A project can have many supplies, and a supply
    may be in many projects."""

    # Set the table name for this model.
    __tablename__ = "project_supplies"

    # Create the columns in the project_supplies table.
    ps_id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    # Set foreign key into projects table
    project_id = db.Column(db.Integer,
                           db.ForeignKey("projects.project_id"),
                           nullable=False)

    # Set foreign key into supply_details table
    sd_id = db.Column(db.Integer,
                      db.ForeignKey("supply_details.sd_id"),
                      nullable=False)

    # Quantity column, to store how much of a supply is needed for a project
    supply_qty = db.Column(db.Integer,
                           nullable=False)

    # Define relationships between projects, supply details, and the supplies
    # in a project. A supply detail describes the nature of the supply in a
    # project, and the project supply table says how many supplies of that nature
    # are owned.
    project = db.relationship("Project",
                              backref="project_supplies")

    supply_details = db.relationship("SupplyDetail",
                                     backref="project_supplies")

    def __repr__(self):
        return "<ProjectSupply project_id=%s, sd_id=%s, supply_qty=%s>" % \
            (self.project_id, self.sd_id, self.supply_qty)


class Item(db.Model):
    """A model that represents a supply owned by a user, including
    the quantity of that supply the user owns."""

    # Set the table name for this model.
    __tablename__ = "items"

    # Create the columns in the items table.
    item_id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    # Set foreign key into users table
    user_id = db.Column(db.Integer,
                        db.ForeignKey("users.user_id"),
                        nullable=False)

    # Set foreign key into supply_details table
    sd_id = db.Column(db.Integer,
                      db.ForeignKey("supply_details.sd_id"),
                      nullable=False)

    # Quantity column, to store how much of a supply a user owns.
    qty = db.Column(db.Integer, nullable=False)

    # Define relationship between users, supply details, and the items a user
    # owns.  A supply detail describes the nature of the item owned, and the items
    # table says how many supplies of that nature are owned.
    user = db.relationship("User",
                           backref="items")

    supply_details = db.relationship("SupplyDetail",
                                     backref="items")

    def update_item_record(self, qty, overwrite=False):
        """Given an item, change the quantity in the user's inventory. Returns
        a string to be sent back to the server, based on the action taken."""

        # If there's no qty, the user probably didn't mean to change anything. To
        # be save, just return the old values, and make no changes.
        if qty == "":
            success_string = str(self.qty) + " " + str(self.supply_details.units)

        # If overwrite is true, then check qty. If the qty is 0, just delete
        # the record; otherwise, change the old item qty to reflect the new one.
        elif overwrite:
            if qty == "0":
                db.session.delete(self)
                db.session.commit()
                success_string = "Deleted!"

            else:
                self.qty = qty
                db.session.commit()
                success_string = str(self.qty) + " " + str(self.supply_details.units)

        # If we're changing but not overwriting, then we must be trying to add
        # a supply that exists. Just increase the qty in the db.
        else:
            self.qty = self.qty + qty
            db.session.commit()
            success_string = "Amount of " + self.supply_details.brand + " " + \
                             self.supply_details.color + " " + \
                             self.supply_details.supply_type + " updated."

        return success_string

    def __repr__(self):
        return "<Item user_id=%s, sd_id=%s, qty=%s>" % \
            (self.user_id, self.sd_id, self.qty)


##########################################################
# Function to add controlled sample data
##########################################################
def example_data():
    """Create example data for the test database."""

    # Two test users. IDs should be 1 and 2.

    # This user will own the terra cotta bowl project, but won't have the brown paint
    # to make it. Password: tobehashed
    tu1 = User(email="ihave@projects.net",
               username="ihaveprojects",
               password='$2b$12$w/6gclJwoAH5NzqBpYOWj.eruNZUsE.5jU2vtAhN5W0jxVysyewXS')

    # This user will own the blue clay bowl project and will have all needed supplies.
    # Password: notsogood
    tu2 = User(email="ihave@suppliesandprojects.com",
               username="ihaveprojectsnsupplies",
               password='$2b$12$3Y3wb0qkhkiuN9dKBp5ihOUFoN3SzITPouwiyX7pJfOVDr2c2wZGW')

    # Some test supply details. IDs should be 1, 2, 3, 4.
    sd1 = SupplyDetail(supply_type="Oven-Bake Clay",
                       brand="Sculpey",
                       color="Terra Cotta",
                       units="oz",
                       purchase_url="http://www.michaels.com/original-sculpey-oven-bake-clay-1.75lb/M10083451.html")

    sd2 = SupplyDetail(supply_type="Oven-Bake Clay",
                       brand="Sculpey",
                       color="White",
                       units="oz",
                       purchase_url="http://www.michaels.com/original-sculpey-oven-bake-clay-1.75lb/M10083451.html")

    sd3 = SupplyDetail(supply_type="Acrylic Paint",
                       brand="Americana",
                       color="Bittersweet Chocolate",
                       units="oz",
                       purchase_url="http://www.michaels.com/americana-acrylic-paint-2-oz/M10132000.html")

    sd4 = SupplyDetail(supply_type="Acrylic Paint",
                       brand="Americana",
                       color="Calypso Blue",
                       units="oz",
                       purchase_url="http://www.michaels.com/americana-acrylic-paint-2-oz/M10132000.html")

    # Some test projects. IDs should be 1 and 2
    p1 = Project(title="Terra Cotta Bowl",
                 user_id=1,
                 description="An oven-baked clay bowl. I'll give it dark brown accents!")

    p2 = Project(title="Blue Clay Bowl",
                 user_id=2,
                 description="Shape some white Sculpey clay into a bowl, bake it, and paint it blue.")

    # Some test entries for project_supply_details. IDs should be 1, 2, 3, 4
    psd1 = ProjectSupply(project_id=1,
                               sd_id=1,
                               supply_qty=5)

    psd2 = ProjectSupply(project_id=1,
                               sd_id=3,
                               supply_qty=2)

    psd3 = ProjectSupply(project_id=2,
                               sd_id=2,
                               supply_qty=10)

    psd4 = ProjectSupply(project_id=2,
                               sd_id=4,
                               supply_qty=1)

    # Some test items.
    # ihaveprojects has terra cotta clay
    i1 = Item(user_id=1,
              sd_id=1,
              qty=10)

    # ihaveprojectsnsupplies has white clay and blue paint
    i2 = Item(user_id=2,
              sd_id=2,
              qty=10)

    i3 = Item(user_id=1,
              sd_id=4,
              qty=5)

    db.session.add_all([tu1, tu2,
                       sd1, sd2, sd3, sd4,
                       p1, p2,
                       psd1, psd2, psd3, psd4,
                       i1, i2, i3])

    db.session.commit()


##########################################################
# Helper functions
##########################################################

def connect_to_db(app, uri='postgresql:///crafterscloset'):
    """Connect to the database for the Crafter's Closet Flask app."""

    # Configure the app to use the database.
    app.config['SQLALCHEMY_DATABASE_URI'] = uri
    # app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)

if __name__ == "__main__":
    # Have the module drop us into the Python console after running, if
    # it is run interactively.

    from server import app

    connect_to_db(app)
    print "Connected to Crafter's Closet DB."
