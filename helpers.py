"""Helper functions specific to Crafter's Closet project."""

from model import SupplyDetail, ProjectSupply, Item, Project, User, db
from flask import jsonify, request
import math

CHART_COLORS = ["#b366ff", "#0059b3", "#00cc99", "#ffd480",
                "#ff99cc", "#b3e6ff", "#bfff80", "#ffccb3"]


####################################################################
# Get all non-duplicate, non-null fields in a column from the
# supply_details table.
####################################################################

def get_all_supply_types():
    """Returns all existing types of supplies from the db."""

    all_supply_types = set(db.session.query(SupplyDetail.supply_type).all())
    all_supply_types = sorted(list(all_supply_types))

    return all_supply_types


def get_all_brands():
    """Returns all existing brands in db."""

    all_brands = set(db.session.query(SupplyDetail.brand).filter(SupplyDetail.brand != None).all())
    all_brands = sorted(list(all_brands))

    return all_brands


def get_all_colors():
    """Returns all existing colors in db."""

    all_colors = set(db.session.query(SupplyDetail.color).filter(SupplyDetail.color != None).all())
    all_colors = sorted(list(all_colors))

    return all_colors


def get_all_supply_units():
    """Returns all existing units of measurement from the db."""

    all_units = set(db.session.query(SupplyDetail.units).all())
    all_units = sorted(list(all_units))

    return all_units


###################################################
# Fetch individual, complete existing records
###################################################

def get_matching_sd(supply_type, brand, color):
    """Gets an existing supply detail record from the database whose columns match
    those of the passed supply detail."""

    # Use ilike() to check columns despite typos
    sd_from_db = SupplyDetail.query.filter(SupplyDetail.supply_type.ilike("%" + supply_type + "%"),
                                           SupplyDetail.brand.ilike("%" + brand + "%"),
                                           SupplyDetail.color.ilike("%" + color + "%")).first()
    return sd_from_db


def get_matching_item(user_id, sd_id):
    """Given a user and a supply id, find an existing item record."""

    q = Item.query.filter(Item.user_id == user_id, Item.sd_id == sd_id)

    item_from_db = q.first()

    return item_from_db


#################################################
# Add records to database
#################################################

def add_item_to_inventory(user_id, sd_id, qty):
    """Add an item to the user's inventory.
    Creates a new record for the items table and adds it."""

    # Instantiate a new item record, using the current user's id and the
    # newly created supply detail's sd_id
    item = Item(user_id=user_id,
                sd_id=sd_id,
                qty=qty)

    # Add the new item to the database
    db.session.add(item)
    db.session.commit()

    # Return the id of the item just created.
    return item


def add_supply_to_db(supply_type, brand, color, units):
    """Add details about a supply to the database.
    Creates a new record for the supply_details table and adds it."""

    # Instantiate a new supply detail record.
    supply_detail = SupplyDetail(supply_type=supply_type,
                                 brand=brand,
                                 color=color,
                                 units=units)

    # Add that record to the database.
    db.session.add(supply_detail)
    db.session.commit()

    # Return the id of the supply_detail just created.
    return supply_detail


def add_user_to_db(email, username, password_hash):
    """Add a new user record to the users table, with the passed attributes."""

    # Create a user object and add it to the database.
    user = User(email=email, username=username, password=password_hash)
    db.session.add(user)
    db.session.commit()


def add_project_supply_to_db(project, sd, qty):

        # Get the entered supply's id
        sd_id = sd.sd_id

        # Create and commit project supply record to db, so the entered
        # supply is associated with this project.

        project_supply = ProjectSupply(project_id=project.project_id,
                                       sd_id=sd_id,
                                       supply_qty=qty)

        db.session.add(project_supply)
        db.session.commit()


def add_project_to_db(user_id, title, description, instr_url, img_url):
    #Create and commit project record
    project = Project(user_id=user_id,
                      title=title.title(),
                      description=description,
                      instr_url=instr_url,
                      img_url=img_url)

    db.session.add(project)
    db.session.commit()

    return project


###################################################################
# Get groups of data from the database in dictionary format
# for easy jsonification.
###################################################################

def get_inventory_chart_dict(user_id):
    """Build a JSON object representing the total numbers of each type of item
    in a user's inventory."""

    weights = {
        "Fabric": 10, "Felt": 10, "Yarn": 10, "Acrylic Paint": 1,
        "Oven-Bake Clay": 1, "Conductive Thread": 1, "LEDs": .1,
        "Color Sensor": 1, "Arduino Board": 1
    }

    # Get all of the passed user's items
    items = Item.query.filter(Item.user_id == user_id)

    # Create an empty dict for counting supply quantities and an empty set
    # to contain non-repeating supply types, to be used as chart labels.
    type_quantities = {}
    labels = set([])

    # For each item in the user's inventory, get the type and quantity.
    # If the supply type isn't in the dict, add it. Either way, add the
    # current quantity to that type's total value. Add the supply type
    # to the labels set.
    for item in items:

        supply_type = str(item.supply_details.supply_type)
        qty_owned = item.qty

        wtd_qty_owned = math.floor(qty_owned * weights[supply_type])

        type_quantities[supply_type] = type_quantities.get(supply_type, 0)
        type_quantities[supply_type] += wtd_qty_owned
        labels.add(supply_type)

    # Put the quantity counts we just made in a list, in the same order as
    # the labels array.
    data = [type_quantities[label] for label in labels]

    # Get enough colors from the global colors list to fill out the chart.
    backgroundColors = CHART_COLORS[:len(labels)]

    # Create the data dictionary in a format Chart.js can understand, and
    # return it as JSON.
    supply_data_dict = {"labels": list(labels),
                        "datasets": [{"data": data,
                                      "backgroundColor": backgroundColors}]
                       }

    return jsonify(supply_data_dict)


def get_all_brands_by_supply_type():
    """Fetch all brands in the database by supply type.

    Returns a dictionary of the following format:

    {"supplytype1": ["brand1", "brand2", ...],
     "supplytype2": ["brand3", ...], ...}
    """

    # Fetch all supply types from the db. Cast the list returned by the
    # db query into a set to remove dupes.
    supply_types = set(db.session.query(SupplyDetail.supply_type).all())

    # Create a dictionary of empty lists, where each key is a supply in the db.
    # Uses dictionary comprehension!
    brands_by_type = {supply_type: [] for (supply_type,) in supply_types}

    # For each supply type, fetch the brands associated with that type. Then, use
    # a list comprehension to create a list of brands & set the value of the key for
    # that supply type equal to the list.
    for key in brands_by_type.iterkeys():
        brands = set(db.session.query(SupplyDetail.brand).filter(SupplyDetail.supply_type == key).all())
        brands_by_type[key] = [brand for (brand,) in brands if brand is not None]

    return brands_by_type


def get_all_units_by_supply_type():
    """Fetch all units in the database by supply type.

    Returns a dictionary of the following format:

    {"supplytype1": "units",
     "supplytype2": "units"}
    """

    # Fetch all supply types from the db. Cast the list returned by the
    # db query into a set to remove dupes.
    raw_supply_types = set(db.session.query(SupplyDetail.supply_type).all())
    supply_types = [raw_type for (raw_type,) in raw_supply_types]

    # Create a dictionary of empty lists, where each key is a supply in the db.
    # Uses dictionary comprehension!
    units_by_type = {}

    # For each supply type, fetch the unit of measure associated with that type
    # and create a key/value pair with the type as the key and the unit as the value.
    for supply_type in supply_types:
        unit_q = db.session.query(SupplyDetail.units).filter(SupplyDetail.supply_type == supply_type)
        unit = unit_q.first()
        units_by_type[supply_type] = units_by_type.get(supply_type, unit[0])

    return units_by_type


def get_all_colors_by_supply_type():
    """Fetch all brands in the database by supply type.

    Returns a dictionary of the following format:
    """

    # Fetch all supply types from the db. Cast the list returned by the
    # db query into a set to remove dupes.
    supply_types = set(db.session.query(SupplyDetail.supply_type).all())

    # Create a dictionary of empty lists, where each key is a supply in the db.
    # Uses dictionary comprehension!
    colors_by_type = {supply_type: [] for (supply_type,) in supply_types}

    # For each supply type, fetch the brands associated with that type. Then, use
    # a list comprehension to create a list of brands & set the value of the key for
    # that supply type equal to the list.
    for key in colors_by_type.iterkeys():
        colors = set(db.session.query(SupplyDetail.color).filter(SupplyDetail.supply_type == key).all())
        colors_by_type[key] = [color for (color,) in colors if color is not None]

    return colors_by_type


def get_all_colors_dict_by_brand():
    """Fetch all colors in the database by brand."""

    # Query the database to get all colors associated with the brand, as a
    # list of tuples
    brands = get_all_brands()

    # Create a dictionary of empty lists, where each key is a brand in the db.
    colors_by_brand = {brand: [] for (brand,) in brands}

    # For each brand, fetch the colors associated with that brand. Then, use
    # a list comprehension to create a list of colors & set the value of the key for
    # that brand equal to the list.
    for key in colors_by_brand.iterkeys():
        colors = set(db.session.query(SupplyDetail.color).filter(SupplyDetail.brand == key).all())
        colors_by_brand[key] = [color for (color,) in colors if color is not None]

    return colors_by_brand


def get_colors_from_brand(brand):
    colors = set(db.session.query(SupplyDetail.color).filter(SupplyDetail.brand.ilike("%"+brand+"%")).all())
    colors = [color for (color,) in colors if color is not None]
    return colors


###########################################################
# Generate supply info table in project.html
###########################################################

def calc_amt_to_buy(sd_id, qty_specified, user_id=None):
    """Given a supply id from a project, a user id, and the qty of the supply
    needed for a project, calculate how much of that supply a user needs to buy
    to build the project that supply belongs to."""

    if user_id is not None:
        # Get the item in the user's inventory with the sd_id passed
        item = Item.query.filter(Item.sd_id == sd_id, Item.user_id == user_id).first()

        # If the user doesn't own that item, they have to buy the amount of supplies
        # specified in the project.
        if item is None:
            amt_to_buy = qty_specified

        # If the user does have that item in their inventory, subtract the qty owned
        # from the qty specified to see how much the user needs to buy.
        else:
            qty_owned = item.qty
            amt_to_buy = qty_specified - qty_owned

            if amt_to_buy < 0:
                amt_to_buy = 0

    # If the user doesn't exist, assume they need to buy all the supplies
    # specified.
    else:
        amt_to_buy = qty_specified

    return amt_to_buy


def get_craft_project_supplies_info(project, user_id):
    """Given a project and a user_id, craft a dictionary containing
    all necessary info to display on a project page, including the amount of
    required supplies a user owns and how  much they'd need to buy."""

    # # Get the project's id.
    # project_id = project.project_id

    # Get a list of dictionaries representing the supplies needed for the
    # project.
    project_supplies_info = project.get_project_supplies_list()

    # For each supply in the list of dictionaries, calculate how many
    # of that supply the user must buy, and add that amount to the dictionary.
    for supply in project_supplies_info:
        amt_to_buy = calc_amt_to_buy(supply["sd_id"],
                                     supply["qty_specified"], user_id)

        item = Item.query.filter(Item.sd_id == supply["sd_id"],
                                 Item.user_id == user_id).first()

        supply["qty_to_buy"] = amt_to_buy

        if item is None:
            supply["qty_owned"] = 0
        else:
            supply["qty_owned"] = item.qty

    return project_supplies_info


############################################################
# Data processing functions for project search table.
############################################################
def get_projects_by_search(search_term):
    """Given a search term, return a list of tuples containing
    relevant project data."""

    sqlfied_st = "%" + search_term + "%"

    # Craft query to db for all needed columns.
    q = db.session.query(Project.title, Project.description, Project.project_id)

    # Join the projects table with the supply_detalis and project_supply tables,
    # so we can search both project info and supply info. Join on sd_id so that
    # we'll only get supplies that are actually in projects.
    q = q.join(ProjectSupply).join(SupplyDetail,
                                   ProjectSupply.sd_id == SupplyDetail.sd_id)

    # Filter on our search term.
    q = q.filter(Project.title.ilike(sqlfied_st) |
                 Project.description.ilike(sqlfied_st) |
                 SupplyDetail.supply_type.ilike(sqlfied_st) |
                 SupplyDetail.brand.ilike(sqlfied_st) |
                 SupplyDetail.color.ilike(sqlfied_st))

    # Get the resulting tuples and clean them up (remove dupes & sort).
    search_results = q.all()
    search_results = sorted(set(search_results))

    return search_results
