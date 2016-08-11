"""Helper functions specific to Crafter's Closet project."""

from model import SupplyDetail, db


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


# FIXME: FINISH IMPLEMENTING THE DUPLICATE CHECK FEATURE
# def check_for_dup_sd(sd):
#     """Check whether the passed supply detail exists in the db. Different
#     purchase url is okay."""

#     sd_from_db = SupplyDetail.query.filter(SupplyDetail.supply_type.ilike("%" + sd.supply_type + "%"),
#                                            SupplyDetail.brand.ilike("%" + sd.brand + "%"),
#                                            SupplyDetail.color.ilike("%" + sd.color + "%"),
#                                            SupplyDetail.units.ilike("%" + sd.units + "%")).first()

#     possible_dupe = []

#     return is_duplicate
