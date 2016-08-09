from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, url_for
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db
from model import User, SupplyDetail

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route("/")
def index():
    """Homepage."""

    return render_template("homepage.html")


@app.route("/users")
def show_users():
    """Show a list of users."""
    users = User.query.all()

    return render_template("user_list.html", users=users)


@app.route("/all-supply-details")
def show_all_supply_details():
    """Show a list of all general supply info currently in the database."""

    supply_details = SupplyDetail.query.all()

    return render_template("supply_detail_list.html", supply_details=supply_details)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0")