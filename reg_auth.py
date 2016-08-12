from model import User, db
from flask import Flask, render_template, redirect, request, flash, session, url_for

app = Flask(__name__)


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
        flash("Account created.")

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
    