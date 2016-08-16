"""Helper functions specific to Crafter's Closet project."""

from model import SupplyDetail, ProjectSupply, Item, Project, db


def get_all_supply_types():
    """Returns all existing types of supplies from the db."""

    all_supply_types = set(db.session.query(SupplyDetail.supply_type).all())
    all_supply_types = sorted(list(all_supply_types))

    return all_supply_types


def get_all_supply_units():
    """Returns all existing units of measurement from the db."""

    all_units = set(db.session.query(SupplyDetail.units).all())
    all_units = sorted(list(all_units))

    return all_units


def get_matching_sd(supply_type, brand, color, units):
    """Gets an existing supply detail record from the database whose columns match
    those of the passed supply detail."""

    # Use ilike() to check columns despite typos
    sd_from_db = SupplyDetail.query.filter(SupplyDetail.supply_type.ilike("%" + supply_type + "%"),
                                           SupplyDetail.brand.ilike("%" + brand + "%"),
                                           SupplyDetail.color.ilike("%" + color + "%"),
                                           SupplyDetail.units.ilike("%" + units + "%")).first()
    return sd_from_db


def get_brand_color_url(supply_type):
    """Given a supply type, get all relevant supply detail info
    for supplies of that type."""

    query = db.session.query(SupplyDetail.brand,
                             SupplyDetail.color,
                             SupplyDetail.purchase_url).filter(SupplyDetail.supply_type == supply_type)

    result = query.all()

    return result


def get_supply_units(supply_type):
    """Given a supply type, return the possible units."""

    query = db.session.query(SupplyDetail.units).filter(SupplyDetail.supply_type == supply_type)

    result = query.all()

    return set(result)


def check_supply_quantities(project_supplies, project_id, user_id):
    """Given a list of project supplies, the project's ID, and a user
    ID, check whether the user has enough of each supply in the list, and
    return how many of each supply the user has to buy."""

    # Gives the supply id, quantity required for the project,
    # and the quantity the current user owns. Format: (sd_id, project_supply qty, item qty)
    # where project_supply qty ==> required for project, item qty ==> number user owns.
    join_ps_items = db.session.query(ProjectSupply.sd_id,
                                     ProjectSupply.supply_qty,
                                     Item.qty).join(Item, ProjectSupply.sd_id == Item.sd_id)

    supply_comparison = join_ps_items.filter(ProjectSupply.project_id == project_id,
                                             Item.user_id == user_id).all()

    # for supply in project_supplies:


def get_project_supplies_list(project_id):
    """Given a project id, get details about the supplies required to make that
    project. These details are NOT user-specific.

    Format of data: [(sd_id, supply_type, color, brand, qty for project, units), ...]

    Example:
    [(1, u'yarn', u'Red Heart', u'Petal Pink', 4, u'yds'),
     (24, u'LED', u'SparkFun', u'blue', 6, u'components'),
     (30, u'Popsicle Sticks', u'Sticks n Stuff', u'beige', 45, u'pcs')]

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
    q_filtered = q.filter(ProjectSupply.project_id == project_id)

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


def calc_amt_to_buy(sd_id, user_id, qty_specified):
    """Given a supply that is in a project and a user, figure out how much of
    that supply a user would need to buy to build the project that supply
    belongs to."""

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

    return amt_to_buy

def craft_project_supplies_info(project, user_id):
    """Given a project and a user_id, craft a dictionary containing
    all necessary info to display on a project page, including the amount of 
    required supplies a user owns and how  much they'd need to buy."""

    # Get the project's id.
    project_id = project.project_id

    # Get a list of dictionaries representing the supplies needed for the
    # project.
    project_supplies_info = get_project_supplies_list(project_id)

    # For each supply in the list of dictionaries, calculate how many
    # of that supply the user must buy, and add that amount to the dictionary.
    for supply in project_supplies_info:
        amt_to_buy = calc_amt_to_buy(supply["sd_id"],
                                     user_id,
                                     supply["qty_specified"])

        supply["qty_to_buy"] = amt_to_buy

    return project_supplies_info


# FIXME: FINISH IMPLEMENTING THE DUPLICATE CHECK FEATURE
def check_for_dup_sd(sd):
    """Check whether the passed supply detail exists in the db. Different
    purchase url is okay."""

    possible_dupe = get_matching_sd(sd)

    return is_duplicate
