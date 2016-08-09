from flask_sqlalchemy import SQLAlchemy

# Create an object representing the idea of the Crafter's Closet database.
db = SQLAlchemy()

#######################################################
# Table Model Classes
#######################################################

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
    # only be able to have one username per email address.
    email = db.Column(db.String(64), nullable=False, unique=True)
    username = db.Column(db.String(64), nullable=False, unique=True)
    password = db.Column(db.String(64), nullable=False)

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
    supply_type = db.Column(db.String(32), nullable=False)
    brand = db.Column(db.String(64), nullable=True)
    color = db.Column(db.String(32), nullable=True)

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
    title = db.Column(db.String(64), nullable=False)

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
    description = db.Column(db.String(500), nullable=True)

    # Define relationship between project_supply_details table
    # and supply_details table. Can't define this on ProjectSupplyDetail
    # because that table doesn't represent "real" data!

    # Supplies don't care about projects, but projects do care about supplies.
    supply_detail = db.relationship("SupplyDetail",
                                    secondary="project_supply_details",
                                    backref=db.backref("projects"))

    def __repr__(self):

        return "<Project title=%s, instr_url=%s, description=%s>" % \
            (self.title, self.instr_url, self.description)


class ProjectSupplyDetail(db.Model):
    """ A model that represents the relationship between a project and a
    set of supply information. A project can have many supplies, and a supply
    may be in many projects."""

    # Set the table name for this model.
    __tablename__ = "project_supply_details"

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

    def __repr__(self):
        return "<ProjectSupplyDetail project_id=%s, sd_id=%s>" % \
            (self.project_id, self.sd_id)


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

    qty = db.Column(db.String(8), nullable=False)

    # There's no relationship between users and supply details, but there is a
    # relationship between both of those things and the items a user owns.
    # Define those relationships here, because this is a middle table.
    user = db.relationship("User",
                           backref="items")

    supply_detail = db.relationship("SupplyDetail",
                                    backref="items")

    def __repr__(self):
        return "<Item user_id=%s, sd_id=%s, qty=%s>" % \
            (self.user_id, self.sd_id, self.qty)


##########################################################
# Helper functions
##########################################################

def connect_to_db(app):
    """Connect to the database for the Crafter's Closet Flask app."""

    # Configure the app to use the database.
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///crafterscloset'
    app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)

if __name__ == "__main__":
    # Have the module drop us into the Python console after running, if
    # it is run interactively.

    from flask import Flask

    app = Flask(__name__)

    connect_to_db(app)
    print "Connected to Crafter's Closet DB."
