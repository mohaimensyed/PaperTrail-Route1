import os
import requests
from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

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


@app.route("/")
def index():

	users = db.execute("SELECT * FROM users").fetchall()

	headline = "PaperTrail - Route 1"
	return render_template("index.html", users=users, headline=headline)

@app.route("/home", methods=["POST"])
def home():

	username = request.form.get("username")
	password = request.form.get("password")

	user = db.execute("SELECT * FROM users WHERE username = :username AND password = :password", {"username": username, "password": password}).fetchone()
	if user is None:
		return render_template("error.html", message="Wrong username or password")


	users = db.execute("SELECT lastname FROM users WHERE username = :username", {"username": username}).fetchone()

	return render_template("home.html", users=users)

@app.route("/register", methods=["GET", "POST"])
def register():

	return render_template("register.html", message="Sign Up Now")

@app.route("/welcome", methods=["POST"])
def welcome():

	username = request.form.get("username")
	firstname = request.form.get("firstname")
	lastname = request.form.get("lastname")
	password = request.form.get("password")
	email = request.form.get("email")

	#check if username exists
	user = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
	if user is not None:
		return render_template("error.html", message="Username already exists.")

	db.execute("INSERT INTO users (username, password, email, firstname, lastname) VALUES (:username, :password, :email, :firstname, :lastname)",
                  {"username": username, "password": password, "email": email, "firstname": firstname, "lastname": lastname})
	db.commit()

	return render_template("welcome.html", firstname=firstname)


@app.route("/search", methods=["POST"])
def search():

	book = request.form.get("book")
	book = '%' + book + '%'


	books = db.execute(" SELECT * FROM books WHERE (author || title || isbn || year) LIKE :book", {"book": book}).fetchall()

	return render_template("search.html", books=books)

@app.route("/search/<book_isbn>")
def bookpage(book_isbn):

	books = db.execute(" SELECT * FROM books WHERE isbn = :book_isbn", {"book_isbn": book_isbn}).fetchone()

	res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "vVSdlHAWDb9gtC332fJ9Hg", "isbns": book_isbn})
	data = res.json()
	ratings = data["books"][0]["average_rating"]

	return render_template("bookpage.html", books=books, ratings=ratings)

