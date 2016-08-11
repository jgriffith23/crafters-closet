from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, url_for
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db
from model import User, SupplyDetail, Project, ProjectSupply, Item

from reg_auth import register_form, handle_register, login_form, handle_login, logout
from helpers import get_all_supply_types, get_all_supply_units, get_matching_sd

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

        # Get the user's projects.
        projects = Project.query.filter(Project.user_id == user_id).all()

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
                               projects=projects,
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

    # Get all supplies related to that project
    project_supplies = ProjectSupply.query.filter(ProjectSupply.project_id == project.project_id).all()

    # Render the project page
    return render_template("project.html",
                           project=project,
                           project_supplies=project_supplies,
                           user=user)


@app.route('/create-project', methods=['GET'])
def show_project_creation_form():
    """Displays the project creation form."""

    # Get the user info from the session.
    # FIXME: Refactor to pass a user object into the session?????
    # Most of the time, all I want is the user_id, so maybe not???

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

    # Get supply info from form
    supply_type = request.form.get("supplytype")
    brand = request.form.get("brand")
    color = request.form.get("color")
    units = request.form.get("units")
    qty = request.form.get("qty-required")

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


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0")
