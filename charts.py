from server import app
from flask import Flask

@app.route("/supply-types.json")
def supply_types_data():
    """Return data about supplies in a user's inventory."""
    return "supply_types_data"
