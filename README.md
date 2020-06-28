# Project 1

Web Programming with Python, JavaScript, SQL, and Flask!


This is a Flask application for a book review site that uses a Heroku PostgreSQL db on the backend.

The application.py file contains the server-side logic for page routing. This contains the logic
for register, login, logout, search, books, reviews, and the book api.

The books.csv is the library of books that is imported into the Heroku PostrgreSQL db.

The configdatabase.py contains the logic for creating the table of books in the db.

The helpers.py contains the protocol for error handling routing and login.

The impoort.py is a copy of the configdatabase.py file for troubleshooting.

The requirements.txt contains the packages necessary to run the application.

The settings.py contains particular settings for dotenv.

The setup.py is another troubleshooting script for the db.

The templates folder contains the user-facing HTML pages. These HTML pages are organized
with Jinja, a templating engine. The index.html file dynamically changes upon the session to
display useful buttons for the user. The books.html serves the library of books contained in the db.
Each book is displayed with book.html. The login.html contains the form for login. The register.html contains
the form for register. The search.html contains the search feature. The thankyou.html is the "thank you" for
submitting a book review. The book review form is contained in review.html. The apology.html contains
the routing error page.

The static folder contains the styles.css file for styling. This file is currently not used on the site. The current styling is contained in the layouts.html file which uses Bootstrap and Font Awesome Icons.



Thanks!
JT Williams
