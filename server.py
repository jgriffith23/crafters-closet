from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, url_for
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db
from model import User, SupplyDetail, Project, ProjectSupply, Item

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route("/")
def index():
    """Homepage."""

    # Check whether the user is logged in. If so, get the user, so we can
    # display user-specific info on the homepage.
    user_id = session.get("user_id")

    if user_id:
        user = User.query.get(user_id)
    else:
        user = None

    return render_template("homepage.html", user=user)


####################################################
# Dashboard routes
####################################################

@app.route('/dashboard/<int:user_id>')
def show_dashboard(user_id):
    """Show a user's dashboard."""

    print "---------------------------------------"
    print "\n\nSession:", session, "\n\n"
    print "---------------------------------------"

    # Get the user's id from the session, if possible.
    user_id = session.get("user_id")

    if user_id:
        # Get the current user
        user = User.query.get(user_id)

        # Get the current user's inventory details as a list of tuples of the
        # format: (type, brand, color, units, url, qty)
        inventory = db.session.query(SupplyDetail.supply_type,
                                     SupplyDetail.brand,
                                     SupplyDetail.color,
                                     SupplyDetail.units,
                                     SupplyDetail.purchase_url,
                                     Item.qty).outerjoin(Item).filter_by(user_id=user_id).all()

#----------------------------------------------------------------------------------------------
        # Prepare data for the "Add a Supply", "Filter Inventory View", and
        # "Search Your Inventory" features.

        # TODO: Ask an adviser whether it makes sense to do all of this here
        all_supply_types = get_all_supply_types()
        all_units = get_all_supply_units()
#----------------------------------------------------------------------------------------------

        # Render a dashboard showing the user's inventory.
        return render_template("dashboard.html",
                               user=user,
                               inventory=inventory,
                               all_supply_types=all_supply_types,
                               all_units=all_units)

    else:
        flash("You can't go there! Please log in.")
        return redirect("/")


####################################################
# Inventory routes (add supply, search, filter)
####################################################
@app.route('/add-supply', methods=['POST'])
def add_supply():
    """Add a supply to the user's inventory.

    This route responds to a POST request from Ajax by adding a new record
    to the items table with the current authenticated user's id, the supply_detail's
    id, and the quantity given. If the supply_detail doesn't exist, we create one
    and add it to the database.

    TODO: Write function so that it actually works as described.
    """

    supply_type = request.form.get("supplytype")
    brand = request.form.get("brand")
    color = request.form.get("color")
    purchase_url = request.form.get("purchase-url")
    units = request.form.get("units")
    qty = request.form.get("quantity-owned")

# TODO: Add a helper function to check whether this supply duplicates an exising
# supply in the database, and just apply the correct supply_detali ID. Right now,
# just add the supply to supply_details anyway.

    # Create a new supply detail record.
    supply_detail = SupplyDetail(supply_type=supply_type,
                                 brand=brand,
                                 color=color,
                                 units=units,
                                 purchase_url=purchase_url)

    # Add that record to the database.
    db.session.add(supply_detail)
    db.session.commit()

    # Fun fact: Once you commit a new record to the db, you can fetch its
    # autoincrementing id as you would if the record had existed all along!
    # Let's do that.

    item = Item(user_id=session.get("user_id"),
                sd_id=supply_detail.sd_id,
                qty=qty)

    db.session.add(item)
    db.session.commit()

    flash("OMGWTFBBQ")

    return redirect('/')

####################################################
# Registration routes
####################################################

@app.route('/register', methods=['GET'])
def register_form():
    """Displays the registration form."""

    return render_template("register_form.html")


@app.route('/register', methods=['POST'])
def handle_register():
    """Handles input from registration form."""

    # Get the user's email, username, and password from the form.

    #FIXME: Have user enter pw twice?
    email = request.form.get("email")
    username = request.form.get("username")
    password = request.form.get("password")

    # Check whether the user exists.
    user = User.query.filter(User.username == username).first()

    # If that user exists, tell the user they can't have that username.
    if user:
        flash("That username has already been registered.")
        return redirect("/register")

    #FIXME: Check whether they entered a pw

    else:
        # If the user doesn't exist, create one.
        user = User(email=email, username=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash("Account created. Happy crafting!")

        #Code 307 preserves the POST request, including form data.
        return redirect("/login", code=307)


####################################################
# Authentication/Deauthentication routes
####################################################

@app.route('/login', methods=['GET'])
def login_form():
    """Displays the login form."""

    return render_template("login_form.html")


@app.route('/login', methods=['POST'])
def handle_login():
    """Handles input from login/registration form."""

    username = request.form.get("username")
    password = request.form.get("password")

    user = User.query.filter(User.username == username).first()

    if user:
        if password != user.password:
            flash("Incorrect username or password.")
            return redirect("/login")
        else:
            #add their user_id to session
            session["user_id"] = user.user_id

            print "---------------------------------------"
            print "\n\nSession:", session, "\n\n"
            print "---------------------------------------"

            flash("Welcome back!")
            return redirect(url_for('.show_dashboard', user_id=user.user_id))

    else:
        flash("Incorrect username or password.")
        return redirect("/login")


@app.route('/logout')
def logout():

    # FIXME: How would we delete the entire session?

    if "user_id" in session:
        del session["user_id"]
        flash("See you later!")
    print "\n\n\n\nSession", session, "\n\n\n\n"

    return redirect("/")


############################################################
# Helper functions
############################################################

def get_all_supply_types():

    all_supply_types = set(db.session.query(SupplyDetail.supply_type).all())
    all_supply_types = sorted(list(all_supply_types))

    return all_supply_types


def get_all_supply_units():

    all_units = set(db.session.query(SupplyDetail.units).all())
    all_units = sorted(list(all_units))

    return all_units


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0")
