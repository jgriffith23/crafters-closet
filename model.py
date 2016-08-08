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


class Supply(db.Model):
    """A model that represents a craft supply. The supplies table will contain
    a row for each craft supply in all of Crafter's Closet.
    """

    # Set the table name for this model.
    __tablename__ = "supplies"

    # Create the columns in the supplies table.
    supply_id = db.Column(db.Integer, autoincrement=True, primary_key=True)

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

    # WHERE DOES THIS BELONG?? PERHAPS IN PROJECTSUPPLIES INSTEAD???
    purchase_url = db.Column(db.String(256), nullable=True)

    def __repr__(self):
        """Provide a human-readable representation of an instance of the Supply
        class."""

        # Note: Brand and color are nullable, so they may be printed as
        # "None" in output.
        return "<Supply type=%s, brand=%s, color=%s, units=%s>" % \
               (self.supply_type, self.brand, self.color, self.units)


##########################################################
# Helper functions
##########################################################

def init_app():
    from flask import Flask
    app = Flask(__name__)

    connect_to_db(app)
    print "Connected to Crafter's Closet DB."


def connect_to_db(app):
    """Connect to the database for the Crafter's Closet Flask app."""

    # Configure the app to use the database.
    app.config['SQLALCHEMY_DATABASE_URL'] = 'postgres:///crafterscloset'
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
