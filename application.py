import os
import requests

from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Create the table called users and name each column
# db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT NOT NULL, hash TEXT NOT NULL)")

@app.route("/", methods=["GET"])
def index():
    """ Show the index page for the Book Review Website """

    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """ Allow users to register for the Book Review Website """

    # Forget any user_id
    session.clear()

    # User reached by submitting a post request
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Missing username!", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Missing password!", 400)

        # Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("Must input password twice!", 400)

        # Ensure confirmation matches password
        elif not request.form.get("password") == request.form.get("confirmation"):
            return apology("Passwords must match!", 400)

        # Store the username in the database
        result = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)",
                            {"username": request.form.get("username"),
                            "hash": generate_password_hash(request.form.get("password"))})
        db.commit()

        if not result:
            return apology("Username currently in use", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          {"username": request.form.get("username")}).fetchall()

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:

        return render_template("register.html")

    # If for some reason we get to this point
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """ Allow users to login to the Book Review Website """

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          {"username": request.form.get("username")}).fetchall()

        # Ensure username exists and password is correct
        print(request.form.get("username"))
        print(rows[0]["username"])
        print(len(rows))
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
    return redirect("/")

@app.route("/search", methods=["GET", "POST"])
def search():
    """Search for Books"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # User reaches route by filling out the search
        try:
            book = request.form.get("search")
        except ValueError:
            return render_template("search.html")

        # Make sure the database can find the book(s)
        # books = db.execute("SELECT * FROM books WHERE to_tsvector('english', body) @@ to_tsquery('english', :search)",
        #                         {"search": request.form.get("search")}).fetchall()

        # Queu the database for ISBN number - expand later
        books = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": request.form.get("search")}).fetchall()

        if not books:
            return render_template("search.html")
        else:
            return render_template("search.html", books=books)

    return render_template("search.html")

@app.route("/books", methods=["GET"])
def books():
    """Create a List of All Books"""

    books = db.execute("SELECT * FROM books").fetchall()
    return render_template("books.html", books=books)

@app.route("/books/<string:isbn>")
def book(isbn):
    """Show Book Details"""
    # Make sure the book exists.
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    if book is None:
        return apology("No such book", 400)

    # Get all reviews.
    reviews = db.execute("SELECT * FROM reviews WHERE isbn = :isbn", {"isbn": isbn}).fetchall()

    # Get the Goodreads data
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "oGrroC73zVBU3rZZyUXxBw", "isbns": isbn})
    goodreads_data = res.json()

    #Get the username
    username = db.execute("SELECT username FROM users WHERE id = :id", {"id": session["user_id"]}).fetchone()

    # User review exists?
    review_exists = False

    # Calculate the average rating
    average_rating = None
    if reviews is None:
        return render_template("book.html", book=book, reviews=reviews, average_rating=average_rating, review_exists=review_exists)
    else:
        review_count = 0
        ratings_sum = 0
        for i in reviews:
            if i.username == username[0]:
                review_exists = True
            ratings_sum += i.rating
            review_count += 1
            average_rating = round(ratings_sum / review_count, 2)
        return render_template("book.html", book=book, reviews=reviews, goodreads_data=goodreads_data, average_rating=average_rating, review_exists=review_exists)

@app.route("/review/<string:isbn>", methods=["GET", "POST"])
def review(isbn):
    """Let User Make a Review"""

    # Make sure the book exists
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    if book is None:
        return apology("No such book", 400)

    # User got to the review for the book via a GET request
    if request.method == "GET":

        # Get the username from the database
        username = db.execute("SELECT username FROM users WHERE id = :id", {"id": session["user_id"]}).fetchone()

        review = db.execute("SELECT * FROM reviews WHERE username = :username AND isbn = :isbn", {"username": username[0], "isbn": isbn}).fetchone()

        return render_template("review.html", book=book, review=review)

    if request.method == "POST":

        # Query the database for the Username
        username = db.execute("SELECT username FROM users WHERE id = :id", {"id": session["user_id"]}).fetchone()
        # Commit the review to the database
        result = db.execute("INSERT INTO reviews (username, isbn, content, rating) VALUES(:username, :isbn, :content, :rating)",
                            {"username": username[0], "isbn": isbn, "content": request.form.get("review_content"), "rating": request.form.get("rating")})
        db.commit()

        return render_template("thankyou.html", book=book)

@app.route("/delete/<string:isbn>", methods=["POST"])
def delete_review(isbn):
    """Delete Review"""

    # Query the database for the Username
    username = db.execute("SELECT username FROM users WHERE id = :id", {"id": session["user_id"]}).fetchone()

    # Delete the rview from the database
    result = db.execute("DELETE FROM reviews WHERE username = :username AND isbn = :isbn", {"username": username[0], "isbn": isbn})
    db.commit()

    # Gather book info
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()

    # Review info
    review = None

    return render_template("review.html", book=book, review=review)


@app.route("/api/<string:isbn>")
def book_api(isbn):
    """Return details about a single book"""

    # Make sure the book exists
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    if book is None:
        return jsonify({"error": "Invalid ISBN"}), 404

    # Get all reviews
    reviews = db.execute("SELECT * FROM reviews WHERE ibsn = :isbn", {"isbn": isbn}).fetchall()
    ratings_sum = 0
    if reviews is None:
        review_count = 0
        review_avg_score = None
    else:
        for review in reviews:
            review_count += 1
            ratings_sum += reviews.rating
        review_avg_score = round(ratings_sum / review_count, 2)

    return jsonify({
        "title": book.title,
        "author": book.author,
        "year": int(book.year),
        "isbn": book.isbn,
        "review_count": reviews_count,
        "average_score": reviews_avg_score
    })
