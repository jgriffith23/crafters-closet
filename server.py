"""Fill in Flask server here!"""

from jinja2 import StrictUndefined

from flask import Flask, render_template

from model import User, SupplyDetail, Project, ProjectSupplyDetail, Item
from model import connect_to_db, db

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar

app.secret_key = "FIXME"

# Have Jinja2 raise errors when variables are undefined
app.jinja_env.undefined = StrictUndefined


@app.route("/")
def homepage():
    """Show the homepage."""

    return render_template("homepage.html")


if __name__ == "__main__":

    connect_to_db(app)
    app.run()
