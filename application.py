"""
--- WELLNESS TRACKER --- HELEN YAP --- CS50 --- DECEMBER 2020 ---
This application allows unique user accounts and for each user to record particular wellness items:
    1. Journal entries
    2. Exercise time
    3. Sleep time.
This app also takes each user's entry upon submission and conducts blunt sentiment analysis. The results
across all user entries are displayed to the user in a plot designed using Chart.js.
"""

import os
import json
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, vader


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///journal.db")

@app.route("/")
@login_required
def index():
    """Show homepage"""
    user_id = session.get("user_id")
    return render_template("index.html")

@app.route("/history")
@login_required
def history():
    """Show history of sentiment from entries, exercise log, and sleep log"""
    user_id = session.get("user_id")
    # Select all the rows of entries, exercise, and sleep from SQL database for user logged
    entries = db.execute("SELECT timestamp, negative, neutral, positive, compound FROM entries WHERE user_id = :id", id=user_id)
    exercises = db.execute("SELECT date, minutes, intensity FROM exercise WHERE user_id = :id", id=user_id)
    sleep = db.execute("SELECT date, hours FROM sleep WHERE user_id = :id", id=user_id)
    return render_template("history.html", entries=entries, exercises=exercises, sleep=sleep)

@app.route("/journal", methods=["GET", "POST"])
@login_required
def journal():
    """Enter journal entries, calculate sentiment values from vader function, and store new values in SQL database
    For full user flexibility, this text box allows users to enter whatever content they wish. Of course, without
    text content, the sentiment analysis will return scores of 0.
    """
    if request.method == "POST":
        form_entry = request.form.get("entry")
        if not form_entry:
            return apology("please provide entry", 400)
        elif len(form_entry) > 524288:
            return apology("your exceeded the character limit of 524288", 400)
        else:
            user_id = session.get("user_id")
            #  vader function is imported from the helper.py file and more details are available there. The function returns a dictionary of valence and compound scores.
            sentiment = vader(form_entry)
            neg = sentiment["neg"]
            neu = sentiment["neu"]
            pos = sentiment["pos"]
            compound = sentiment["compound"]
            db.execute(
                """
                INSERT INTO entries
                (user_id, text, negative, neutral, positive, compound)
                VALUES (:userid, :entry, :negative, :neutral, :positive, :compound)
                """,
                userid=user_id,
                entry=form_entry,
                negative=neg,
                neutral=neu,
                positive=pos,
                compound=compound)
        entry = db.execute("SELECT * FROM entries WHERE user_id = :id AND entry_id = (SELECT MAX(entry_id) FROM entries)", id=user_id)

        return render_template("sentiment.html", entry=entry)
    else:
        return render_template("journal.html")

@app.route("/selectpastentries", methods=["GET", "POST"])
@login_required
def pastentries():
    """Select and see old text entires"""
    user_id = session.get("user_id")

    if request.method == "POST":
        form_timestamp = request.form.get("options")

        if not form_timestamp:
            return apology("please select a date from the dropdown menu", 400)
        else:
            old = db.execute("SELECT * FROM entries WHERE user_id = :id AND timestamp= :timestamp", id=user_id, timestamp=form_timestamp)
            return render_template("past.html", old=old)

    # The GET method will display the available entries for the user to select
    else:
        timestamps = db.execute("SELECT timestamp FROM entries WHERE user_id = :id", id=user_id)
        return render_template("pastentries.html", timestamps=timestamps)


@app.route("/exercise", methods=["GET", "POST"])
@login_required
def exercise():
    """Log exercise"""
    user_id = session.get("user_id")
    if request.method == "POST":
        form_date = request.form.get("date")
        form_minutes = request.form.get("minutes")
        form_intensity = request.form.get("intensity")
        # standard error handling for missing exercise fields or for attempt to enter data for the duplicate dates
        if not form_date:
            return apology("must provide date", 400)
        elif not form_minutes:
            return apology("must provide minutes exercised", 400)
        elif not form_intensity:
            return apology("must select level of exercise intensity", 400)
        elif not form_minutes.isdigit():
            return apology("integer of at least 1 is required", 400)
        rows = db.execute("SELECT * FROM exercise WHERE date = ?", form_date)
        if len(rows) > 0:
            return apology("you have already logged exercise for this date", 400)
        db.execute(
            """
            INSERT INTO exercise
            (user_id, date, minutes, intensity)
            VALUES (:user_id, :date, :minutes, :intensity)
            """,
            user_id=user_id,
            date=form_date,
            minutes=form_minutes,
            intensity=form_intensity)

        return redirect("/history")

    else:
        return render_template("exercise.html")


@app.route("/sleep", methods=["GET", "POST"])
@login_required
def sleep():
    """Log sleep"""
    user_id = session.get("user_id")
    if request.method == "POST":
        form_date = request.form.get("date")
        form_hours = request.form.get("hours")
        # standard error handling for missing sleep form fields or for attempt to enter data for the duplicate dates
        if not form_date:
            return apology("must provide date", 400)
        elif not form_hours:
            return apology("must provide hours slept", 400)
        elif not form_hours.isdigit():
            return apology("integer of at least 1 is required", 400)
        rows = db.execute("SELECT * FROM sleep WHERE date = ?", form_date)
        if len(rows) > 0:
            return apology("you have already logged exercise for this date", 400)
        db.execute(
            """
            INSERT INTO sleep
            (user_id, date, hours)
            VALUES (:user_id, :date, :hours)
            """,
            user_id=user_id,
            date=form_date,
            hours=form_hours)

        return redirect("/history")

    else:
        return render_template("sleep.html")


@app.route("/plot", methods=["GET"])
@login_required
def plot():
    """Show graph of the sentiment history"""
    user_id = session.get("user_id")
    data = db.execute("SELECT timestamp AS x, compound AS y FROM entries WHERE user_id = :id", id=user_id)

    return render_template("plot.html", data=data)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # Check that user provided correct login details and make sure user account exists
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)
        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)
        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        # Redirect user to home page
        return redirect("/")
    # User reached route via GET
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # error handling for username and password
        if not request.form.get("username"):
            return apology("must provide username", 400)
        # error handling for no password
        elif not request.form.get("password"):
            return apology("must provide password", 400)
        # error handling for no password in confirmation line
        elif not request.form.get("confirmation"):
            return apology("must provide password confirmation", 400)
        # error handling for mismatched passwords
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 400)
        # error handling if user bypasses html password requirement of 6 character minimum and unique pw from username:
        elif len(request.form.get("password")) < 6:
            return apology("password must have minimum of 6 characters", 400)
        elif (request.form.get("password")) == (request.form.get("username")):
            return apology("password cannot be identical to username", 400)

        # check if username already exists in users table and only insert new registrant if it's new
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if len(rows) == 0:
            hashed = generate_password_hash(request.form.get("password"))
            db.execute(
                """
                INSERT INTO users (username, hash)
                VALUES (:username, :hash)
                """,
                username=request.form.get("username"), hash=hashed)
        else:
            return apology("username is already taken", 400)

        # store session
        new = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        session["user_id"] = new[0]["id"]
        return redirect("/")

    else:
        return render_template("register.html")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)