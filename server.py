from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, url_for, jsonify, Markup
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db
from model import User, SupplyDetail, Project, ProjectSupply, Item

#from reg_auth import register_form, handle_register, login_form, handle_login, logout
from helpers import get_all_supply_types, get_all_supply_units, get_all_brands, get_all_colors, get_matching_sd
from helpers import get_all_brands_by_supply_type, get_all_units_by_supply_type
from helpers import craft_project_supplies_info, get_filtered_inventory

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
                                     Item.qty,
                                     Item.item_id).outerjoin(Item).filter_by(user_id=user_id).all()

        inventory = sorted(inventory)

        # Get the user's projects.
        projects = Project.query.filter(Project.user_id == user_id).all()

        # Prepare data for the "Add a Supply", "Filter Inventory View", and
        # "Search Your Inventory" features.
        all_supply_types = get_all_supply_types()
        all_brands = get_all_brands()
        all_colors = get_all_colors()

        table_body = Markup(render_template("supply_table.html", inventory=inventory))

        print "So I'm in show_dashboard, and here's your inventory: ", inventory

        # Render a dashboard showing the user's inventory.
        return render_template("dashboard.html",
                               user=user,
                               projects=projects,
                               all_supply_types=all_supply_types,
                               all_brands=all_brands,
                               all_colors=all_colors,
                               table_body=table_body)

    else:
        flash("You can't go there! Please log in.")
        return redirect("/")


# The following routes are dashboard routes because the "add supply" window
# appears as part of the dashboard template, and we need this data before
# we can submit a new supply.
@app.route("/dashboard/brands.json")
def get_brands():
    """Fetch all brands in the db by supply type, and return as JSON."""
    brands = get_all_brands_by_supply_type()
    brands = jsonify(brands)
    return(brands)


@app.route("/dashboard/units.json")
def get_units():
    """Fetch all units in the db by supply type, and return as JSON."""
    units = get_all_units_by_supply_type()
    units = jsonify(units)
    return(units)


####################################################
# Inventory routes (add supply, search, filter)
####################################################
@app.route('/add-supply', methods=['POST'])
def add_supply():
    """Add a supply to the user's inventory.

    This route responds to a POST request by adding a new record
    to the items table with the current authenticated user's id, the supply_detail's
    id, and the quantity given. If the supply_detail doesn't exist, we create one
    and add it to the database.
    """

    supply_type = request.form.get("supplytype")
    brand = request.form.get("brand")
    color = request.form.get("color")
    purchase_url = request.form.get("purchase-url")
    units = request.form.get("units")
    qty = request.form.get("quantity-owned")

    # Instantiate a new supply detail record.
    supply_detail = SupplyDetail(supply_type=supply_type,
                                 brand=brand,
                                 color=color,
                                 units=units,
                                 purchase_url=purchase_url)

    # Add that record to the database.
    db.session.add(supply_detail)
    db.session.commit()

    # Instantiate a new item record, using the current user's id and the
    # newly created supply detail's sd_id
    item = Item(user_id=session.get("user_id"),
                sd_id=supply_detail.sd_id,
                qty=qty)

    # Add the new item to the database
    db.session.add(item)
    db.session.commit()

    flash("%s %s of %s %s have been added to your inventory." %
         (item.qty, supply_detail.units, supply_detail.brand, supply_detail.supply_type))

    return redirect(url_for('.show_dashboard', user_id=session.get("user_id")))


@app.route("/inventory/filter.html")
def filter_inventory():
    """Gives AJAX a filtered version of the HTML for the user's inventory, based on
    brand, supply type, or color."""

    # Get the brand, supply_type, and color from the GET request arguments.
    # Alse get the user_id from the session.
    brand = request.args.get("brand")
    supply_type = request.args.get("supplytype")
    color = request.args.get("color")
    user_id = session.get("user_id")

    # Fetch the filtered inventory as a list of tuples.
    inventory = get_filtered_inventory(user_id, brand, supply_type, color)

    # Render the HTML for the filtered inventory as a safe-to-use Markup object.
    table_body = Markup(render_template("supply_table.html", inventory=inventory))

    # Return the HTML to the AJAX request as a response.
    return table_body


########################################################################
# Project routes (show project, show project creation form, handle form)
########################################################################

@app.route("/project/<int:project_id>")
def show_project(project_id):
    """Displays a page with all information about a project."""

    user_id = session.get("user_id")
    user = User.query.get(user_id)

    # Get an object representing the project whose id was passed
    project = Project.query.get(project_id)

    # Get a dictionary representing all supply info for this project,
    # including the amount of any supplies a user must buy.
    project_supplies_info = craft_project_supplies_info(project, user_id)

    # Render the project page
    return render_template("project.html",
                           project=project,
                           project_supplies_info=project_supplies_info,
                           user=user)


@app.route('/create-project', methods=['GET'])
def show_project_creation_form():
    """Displays the project creation form."""

    # Get the user info from the session.
    user_id = session.get("user_id")
    user = User.query.get(user_id)

    # Get the available supply types and units from db
    all_supply_types = get_all_supply_types()
    all_units = get_all_supply_units()

    return render_template("project_form.html",
                           user=user,
                           all_supply_types=all_supply_types,
                           all_units=all_units)


@app.route("/create-project", methods=["POST"])
def handle_project_creation():
    """Handles input from project creation form and adds project to database."""

    # Get the user info from the session.
    user_id = session.get("user_id")

    # Fetch basic project data from form
    title = request.form.get("title")
    description = request.form.get("description")
    instr_url = request.form.get("instr-url")

    #Create and commit project record
    project = Project(user_id=user_id,
                      title=title.title(),
                      description=description,
                      instr_url=instr_url)

    db.session.add(project)
    db.session.commit()

    # Get supply info from form. First, we need the number of supplies from
    # the hidden field num-supplies.
    num_supplies = request.form.get("num-supplies")

    # Given num-supplies, we can iterate over the number of supplies to add
    # records to the db.

    # Need to take the range of num_supplies + 1 or we won't get all supplies.
    for supply_num in range(int(num_supplies)+1):
        fieldname_num = str(supply_num)
        supply_type = request.form.get("supplytype"+fieldname_num)
        brand = request.form.get("brand"+fieldname_num)
        color = request.form.get("color"+fieldname_num)
        units = request.form.get("units"+fieldname_num)
        qty = request.form.get("qty-required"+fieldname_num)

        # Get a supply from the db that matches the entered supply
        sd = get_matching_sd(supply_type, brand, color, units)

        # Get the entered supply's id
        sd_id = sd.sd_id

        # Create and commit project supply record to db, so the entered
        # supply is associated with this project.

        project_supply = ProjectSupply(project_id=project.project_id,
                                       sd_id=sd_id,
                                       supply_qty=qty)

        db.session.add(project_supply)
        db.session.commit()

    flash("%s added to your projects. Hooray!" % (title))
    return redirect(url_for('.show_project', project_id=project.project_id))


####################################################
# Registration routes
#
# These are based on code created in collaboration
# with rayramsay (https://github.com/rayramsay/).
####################################################

@app.route('/register', methods=['GET'])
def register_form():
    """Displays the registration form."""

    return render_template("register_form.html")


@app.route('/register', methods=['POST'])
def handle_register():
    """Handles input from registration form."""

    # Get the user's email, username, and password from the form.
    email = request.form.get("email")
    username = request.form.get("username")
    password = request.form.get("password")
    repeat_pw = request.form.get("repeat-pw")

    # Check whether the user exists.
    user = User.query.filter(User.username == username).first()

    # If that user exists, tell the user they can't have that username.
    if user:
        flash("That username has already been registered.")
        return redirect("/register")

    # Check whether the password and repeated passwords match.
    elif password != repeat_pw:
        flash("Entered passwords do not match.")
        return redirect("/register")

    else:
        # If the user doesn't exist, create one.
        user = User(email=email, username=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash("Account created.")

        #Code 307 preserves the POST request, including form data.
        return redirect("/login", code=307)


####################################################
# Authentication/Deauthentication routes
#
# These are based on code created in collaboration
# with rayramsay (https://github.com/rayramsay/).
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
            # Add their user_id to session
            session["user_id"] = user.user_id
            session["username"] = user.username

            flash("Welcome to Crafter's Closet!")
            return redirect(url_for('.show_dashboard', user_id=user.user_id))

    else:
        flash("Incorrect username or password.")
        return redirect("/login")


@app.route('/logout')
def logout():

    # Clear the session to log the user out and clear their cookie.
    session.clear()
    flash("See you later!")

    return redirect("/")


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0")
