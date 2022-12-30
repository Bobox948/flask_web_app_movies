import os
from cs50 import SQL

from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


db = SQL("sqlite:///imdb.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



@app.route("/")
@login_required #login required to visit this page
def index():
# if user isn't logged in, redirect to login.html, else, index.html
    if session.get("user_id") is None:
        return render_template("login.html")

    return render_template("index.html")


@app.route("/review", methods=["GET", "POST"])
@login_required
def review():

    if request.method == "POST":

        who = session["user_id"]
        title = request.form.get("movie") # the title variable will store the choice of the movie to review by the user and same for the review variable with the html textfield "description"
        review = request.form.get("description")
        title1= title[:-5] # we just get the title, without the year, and for the year bellow the same
        year1 = title[-4:]
        id = db.execute("SELECT id FROM imdb WHERE title = ? and year = ?", title1, year1)
        id = id[0]["id"] # we just take the id of the movie, not the column name or nothing else, because else the SQL request above renders a column and a row 
        db.execute("INSERT INTO reviews (user_id, movie_id, review) VALUES(?, ?, ?)", who, id, review) # insert review to db
        return render_template("review.html")

    else:
        return render_template("review.html")


@app.route("/reviews", methods=["GET", "POST"])
@login_required
def reviews():

 # users reviews
    who = session["user_id"]
    review = db.execute("SELECT imdb.title, reviews.review FROM imdb JOIN reviews on imdb.id = reviews.movie_id WHERE reviews.user_id = ? order by title", who)
    return render_template("reviews.html", review=review)






# user seen movies and choose a movie to review
@app.route("/seen")
@login_required
def seen():
    who = session["user_id"]
    watched = db.execute("SELECT title, genre, year, director FROM imdb JOIN seen on imdb.id = seen.movie_id WHERE seen.user_id = ? ORDER BY title", who)
    review=db.execute("SELECT title, year FROM imdb JOIN seen on imdb.id = seen.movie_id WHERE id NOT IN (SELECT reviews.movie_id from reviews JOIN users on reviews.user_id=users.id where imdb.id=reviews.movie_id and users.id = ?) and seen.user_id = ? order by title", who, who)

    return render_template("seen.html", watched=watched, review=review)



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    if session.get("user_id") is not None:
        flash("You are already logged in !") #check if the user is already logged in so it's redirecting him to home
        return redirect("/")

    # Forget any user_id

    # User reached route via POST (as by submitting a form via POST)
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

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return render_template("/login.html")

@app.route("/suggestion", methods=["GET", "POST"])
@login_required
def suggestion():

    if request.method == "GET":
        return render_template("suggestion.html")
    else:
        if not request.form.getlist("mood"):
            return apology("must choose at least one category", 400) # user must choose at least one category

        mood = request.form.getlist("mood")
        who = session["user_id"]
        year = db.execute("SELECT year FROM users WHERE id = ?", who) # year of birth of the user
        year2 = year[0]["year"] # only get the year, not the column name
        year3 = year2 - 10 # to get a better suggestion of movies, 10 years max before birth and 20 after
        year4 = year2 + 20
        if len(mood) == 1: # according to number of choices of the user, different requests
            suggestions = db.execute("SELECT title, year, director, description FROM imdb WHERE id NOT IN (SELECT seen.movie_id from seen JOIN users on seen.user_id=users.id where imdb.id=seen.movie_id and users.id = ?) and genre like '%'||?||'%' and year > ? and year < ? order by rating DESC limit 5", who, mood[0], year3, year4)
        if len(mood) == 2:
            suggestions = db.execute("SELECT title, year, director, description FROM imdb WHERE id NOT IN (SELECT seen.movie_id from seen JOIN users on seen.user_id=users.id where imdb.id=seen.movie_id and users.id = ?) and genre like '%'||?||'%' and genre like '%'||?||'%' and year > ? and year < ? order by rating DESC limit 5", who, mood[0], mood[1], year3, year4)
        if len(mood) == 3:
            suggestions = db.execute("SELECT title, year, director, description FROM imdb WHERE id NOT IN (SELECT seen.movie_id from seen JOIN users on seen.user_id=users.id where imdb.id=seen.movie_id and users.id = ?) and genre like '%'||?||'%' and genre like '%'||?||'%' and genre like '%'||?||'%' and year > ? and year < ? order by rating DESC limit 5", who, mood[0], mood[1], mood[2], year3, year4)
        if len(suggestions) == 0:
            return render_template("empty.html")
        else:
            return render_template("suggestion.html", suggestions=suggestions)

@app.route("/enjoy", methods=["GET", "POST"])
@login_required
def enjoy():

    if request.method == "GET":
        return render_template("enjoy.html")
    else:

        suggestion = request.form.get("suggestion") 
        suggestion2 = request.form.getlist("suggestion2")
        if suggestion is None and len(suggestion2) != 5: # if the user chooses nothing to watch, or if the seen movies is different from 5 (all choices), error, because the user has to have seen all the movies to be able not to chose a movie to watch
            return apology("You must choose at least one movie to watch", 400)
        if suggestion in suggestion2:
            return apology("You said that you've already seen this one!", 400) # if the "already seen movies" choice is the same as the "choose a movie to watch"; error
        who = session["user_id"]

        if len(suggestion2) == 1:
            suggestion1 = suggestion2[0] # take the first and only value of the array
            suggestion3= suggestion1[:-5] # take name only
            year1 = suggestion1[-4:]# year only
            id = db.execute("SELECT id FROM imdb WHERE title = ? and year = ?", suggestion3, year1)
            id = id[0]["id"]
            db.execute("INSERT INTO seen (user_id, movie_id) VALUES(?, ?)", who, id) 

        if len(suggestion2) == 2: # here , the user said that he already seen one movie and have chosen another one to watch, so at the end we inest to values into the "seen" db
            suggestion1 = suggestion2[0]
            suggestion3= suggestion1[:-5]
            suggestion4 = suggestion2[1]
            suggestion5= suggestion4[:-5]
            year1 = suggestion1[-4:]
            year2 = suggestion4[-4:]
            id = db.execute("SELECT id FROM imdb WHERE title = ? and year = ?", suggestion3, year1)
            id2 = db.execute("SELECT id FROM imdb WHERE title = ? and year = ?", suggestion5, year2)
            id = id[0]["id"]
            id2 = id2[0]["id"]
            db.execute("INSERT INTO seen (user_id, movie_id) VALUES(?, ?)", who, id)
            db.execute("INSERT INTO seen (user_id, movie_id) VALUES(?, ?)", who, id2)


        if len(suggestion2) == 3:
            suggestion1 = suggestion2[0]
            suggestion3= suggestion1[:-5]
            suggestion4 = suggestion2[1]
            suggestion5= suggestion4[:-5]
            suggestion6=suggestion2[2]
            suggestion7= suggestion6[:-5]
            year1 = suggestion1[-4:]
            year2 = suggestion4[-4:]
            year3 = suggestion6[-4:]
            id = db.execute("SELECT id FROM imdb WHERE title = ? and year = ?", suggestion3, year1)
            id2 = db.execute("SELECT id FROM imdb WHERE title = ? and year = ?", suggestion5, year2)
            id3 = db.execute("SELECT id FROM imdb WHERE title = ? and year = ?", suggestion7, year3)
            id = id[0]["id"]
            id2 = id2[0]["id"]
            id3 = id3[0]["id"]
            db.execute("INSERT INTO seen (user_id, movie_id) VALUES(?, ?)", who, id)
            db.execute("INSERT INTO seen (user_id, movie_id) VALUES(?, ?)", who, id2)
            db.execute("INSERT INTO seen (user_id, movie_id) VALUES(?, ?)", who, id3)

        if len(suggestion2) == 4:
            suggestion1 = suggestion2[0]
            suggestion3= suggestion1[:-5]
            suggestion4 = suggestion2[1]
            suggestion5= suggestion4[:-5]
            suggestion6=suggestion2[2]
            suggestion7= suggestion6[:-5]
            suggestion8= suggestion2[3]
            suggestion9 = suggestion8[:-5]
            year1 = suggestion1[-4:]
            year2 = suggestion4[-4:]
            year3 = suggestion6[-4:]
            year4 = suggestion8[-4:]
            id = db.execute("SELECT id FROM imdb WHERE title = ? and year = ?", suggestion3, year1)
            id2 = db.execute("SELECT id FROM imdb WHERE title = ? and year = ?", suggestion5, year2)
            id3 = db.execute("SELECT id FROM imdb WHERE title = ? and year = ?", suggestion7, year3)
            id4 = db.execute("SELECT id FROM imdb WHERE title = ? and year = ?", suggestion9, year4)
            id = id[0]["id"]
            id2 = id2[0]["id"]
            id3 = id3[0]["id"]
            id4= id4[0]["id"]
            db.execute("INSERT INTO seen (user_id, movie_id) VALUES(?, ?)", who, id)
            db.execute("INSERT INTO seen (user_id, movie_id) VALUES(?, ?)", who, id2)
            db.execute("INSERT INTO seen (user_id, movie_id) VALUES(?, ?)", who, id3)
            db.execute("INSERT INTO seen (user_id, movie_id) VALUES(?, ?)", who, id4)

        if len(suggestion2) == 5 and suggestion is None:
            suggestion1 = suggestion2[0]
            suggestion3= suggestion1[:-5]
            suggestion4 = suggestion2[1]
            suggestion5= suggestion4[:-5]
            suggestion6=suggestion2[2]
            suggestion7= suggestion6[:-5]
            suggestion8= suggestion2[3]
            suggestion9 = suggestion8[:-5]
            suggestion10=suggestion2[4]
            suggestion11=suggestion10[:-5]
            year1 = suggestion1[-4:]
            year2 = suggestion4[-4:]
            year3 = suggestion6[-4:]
            year4 = suggestion8[-4:]
            year5 = suggestion10[-4:]
            id = db.execute("SELECT id FROM imdb WHERE title = ? and year = ?", suggestion3, year1)
            id2 = db.execute("SELECT id FROM imdb WHERE title = ? and year = ?", suggestion5, year2)
            id3 = db.execute("SELECT id FROM imdb WHERE title = ? and year = ?", suggestion7, year3)
            id4 = db.execute("SELECT id FROM imdb WHERE title = ? and year = ?", suggestion9, year4)
            id5 = db.execute("SELECT id FROM imdb WHERE title = ? and year = ?", suggestion11, year5)

            id = id[0]["id"]
            id2 = id2[0]["id"]
            id3 = id3[0]["id"]
            id4= id4[0]["id"]
            id5= id5[0]["id"]
            db.execute("INSERT INTO seen (user_id, movie_id) VALUES(?, ?)", who, id)
            db.execute("INSERT INTO seen (user_id, movie_id) VALUES(?, ?)", who, id2)
            db.execute("INSERT INTO seen (user_id, movie_id) VALUES(?, ?)", who, id3)
            db.execute("INSERT INTO seen (user_id, movie_id) VALUES(?, ?)", who, id4)
            db.execute("INSERT INTO seen (user_id, movie_id) VALUES(?, ?)", who, id5)

            return apology("Seems you've seen them all. Go back to homepage to get a better suggestion", 400) # if the user have seen all of the 5 suggestions, he can't chose a movie to watch so he submits anyway and those 5 movies won't be suggested again

        # if len suggestion2 !=5 , this will execute, for instance if the suggestion2 = 4, so the user has a movie to chose for "suggestion"
        suggestion1= suggestion[:-5]
        year1 = suggestion[-4:]
        id = db.execute("SELECT id FROM imdb WHERE title = ? and year = ?", suggestion1, year1)
        id = id[0]["id"]
        print(id)
        db.execute("INSERT INTO seen (user_id, movie_id) VALUES(?, ?)", who, id)

        return render_template("/enjoy.html", suggestion=suggestion)

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if session.get("user_id") is not None:
        flash("You are already registered !")
        return redirect("/")
    if request.method == "POST":

        if not request.form.get("username"):
            return apology("must provide username", 400)
        if not request.form.get("year"):
            return apology("must provide year of birth", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)
        elif not request.form.get("confirmation"):
            return apology("must provide password confirmation", 400)
        username = request.form.get("username")
        year = request.form.get("year")
        usernames = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(usernames) == 1:
            return apology("Username already taken")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if password != confirmation:
            return apology("Passwords doesn't match")

        else:
            hash = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8)
            db.execute("INSERT INTO users (username, hash, year) VALUES(?, ?, ?)", username, hash, year)

            # Confirm registration
            return render_template("/login.html")
    else:
        return render_template("register.html")
