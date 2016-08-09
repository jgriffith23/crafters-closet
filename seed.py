"""Write code to seed database here."""
"""Utility file to seed ratings database from MovieLens data in seed_data/"""

from sqlalchemy import func
from model import User, SupplyDetail, Project, ProjectSupplyDetail, Item

from model import connect_to_db, db
from server import app

#########################################################
# Functions related to loading users.
#########################################################


def load_users():
    """Load users from u.user into database."""

    print "\n****Loading Users****\n"

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    User.query.delete()

    # Read u.user file and insert data
    for row in open("seed_data/u.user"):
        row = row.rstrip()
        user_id, email, username, password = row.split(",")

        user = User(user_id=user_id,
                    email=email,
                    username=username,
                    password=password)

        # We need to add to the session or it won't ever be stored
        db.session.add(user)

    # Once we're done, we should commit our work
    db.session.commit()


def set_val_user_id():
    """Set value for the next user_id after seeding database. Otherwise,
    we'll always start over at id 1!=
    """

    # Get the Max user_id in the database
    result = db.session.query(func.max(User.user_id)).one()
    max_id = int(result[0])

    # Set the value for the next user_id to be max_id + 1
    query = "SELECT setval('users_user_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()

#########################################################
# Functions related to loading supply details.
#########################################################

def load_supplydetails():
    """Load supply details from u.supplydetail into database."""

    print "\n****Loading SupplyDetails****\n"

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate supply information.
    SupplyDetail.query.delete()

    # Read u.supplydetail file and insert data
    for row in open("seed_data/u.supplydetail"):
        row = row.rstrip()
        sd_id, supply_type, brand, color, units, url = row.split(",")

        supplydetail = SupplyDetail(sd_id=sd_id,
                                    supply_type=supply_type,
                                    brand=brand,
                                    color=color,
                                    units=units,
                                    purchase_url=url)

        # We need to add to the session or it won't ever be stored
        db.session.add(supplydetail)

    # Once we're done, we should commit our work
    db.session.commit()


def set_val_sd_id():
    """Set value for the next sd_id after seeding database. Otherwise,
    we'll always start over at id 1!
    """

    # Get the Max user_id in the database
    result = db.session.query(func.max(SupplyDetail.sd_id)).one()
    max_id = int(result[0])

    # Set the value for the next user_id to be max_id + 1
    query = "SELECT setval('supply_details_sd_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()

#########################################################
# Functions related to loading projects owned by users.
#########################################################

def load_projects():
    """Load items from u.project into database."""

    print "\n****Loading Projects****\n"

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate items owned.
    Project.query.delete()

    # Read u.project file and insert data
    for row in open("seed_data/u.project"):
        row = row.rstrip()
        project_id, title, user_id, instr_url, description = row.split(",")
        print row

        project = Project(project_id=project_id,
                          title=title,
                          user_id=user_id,
                          instr_url=instr_url,
                          description=description)

        # We need to add to the session or it won't ever be stored
        db.session.add(project)

    # Once we're done, we should commit our work
    db.session.commit()


def set_val_project_id():
    """Set value for the next project_id after seeding database. Otherwise,
    we'll always start over at id 1!
    """

    # Get the Max user_id in the database
    result = db.session.query(func.max(Project.project_id)).one()
    max_id = int(result[0])

    # Set the value for the next user_id to be max_id + 1
    query = "SELECT setval('projects_project_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()

################################################################################
# Functions related to loading information about supplies contained in projects.
################################################################################

def load_projectsupplydetails():
    """Load items from u.projectsupplydetail into database."""

    print "\n****Loading Details About Supplies in Projects****\n"

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate items owned.
    ProjectSupplyDetail.query.delete()

    # Read u.projectsupplydetail file and insert data
    for row in open("seed_data/u.projectsupplydetail"):
        row = row.rstrip()
        ps_id, project_id, sd_id = row.split(",")

        projectsupplydetail = ProjectSupplyDetail(ps_id=ps_id,
                                                  project_id=project_id,
                                                  sd_id=sd_id)

        # We need to add to the session or it won't ever be stored
        db.session.add(projectsupplydetail)

    # Once we're done, we should commit our work
    db.session.commit()


def set_val_ps_id():
    """Set value for the next item_id after seeding database. Otherwise,
    we'll always start over at id 1!
    """

    # Get the Max user_id in the database
    result = db.session.query(func.max(ProjectSupplyDetail.ps_id)).one()
    max_id = int(result[0])

    # Set the value for the next user_id to be max_id + 1
    query = "SELECT setval('project_supply_details_ps_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()


#########################################################
# Functions related to loading items owned by users.
#########################################################

def load_items():
    """Load items from u.item into database."""

    print "\n****Loading Items****\n"

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate items owned.
    Item.query.delete()

    # Read u.supplydetail file and insert data
    for row in open("seed_data/u.item"):
        row = row.rstrip()
        item_id, user_id, sd_id, qty = row.split(",")

        item = Item(item_id=item_id,
                    user_id=user_id,
                    sd_id=sd_id,
                    qty=qty)

        # We need to add to the session or it won't ever be stored
        db.session.add(item)

    # Once we're done, we should commit our work
    db.session.commit()


def set_val_item_id():
    """Set value for the next item_id after seeding database. Otherwise,
    we'll always start over at id 1!
    """

    # Get the Max user_id in the database
    result = db.session.query(func.max(Item.item_id)).one()
    max_id = int(result[0])

    # Set the value for the next user_id to be max_id + 1
    query = "SELECT setval('items_item_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()

if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    load_users()
    load_supplydetails()
    load_projects()
    load_projectsupplydetails()
    load_items()

    # Set the value of the autoincrementing primary key in each table to
    # the number immediately following the greatest existing id, so we don't
    # start overwriting data.
    set_val_user_id()
    set_val_sd_id()
    set_val_item_id()
    set_val_project_id()
    set_val_ps_id()
