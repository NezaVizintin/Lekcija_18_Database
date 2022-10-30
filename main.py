import os
from flask import Flask, render_template, request, redirect, url_for
from sqla_wrapper import SQLAlchemy
from sqlalchemy_pagination import paginate

app = Flask(__name__)

# To deploy on Heroku, a different db system is needed.
# Your Postgress database URL on Heroku will be stored under the DATABASE_URL environment variable.
# If your Python code will not find this variable, it will default to the "sqlite:///db.sqlite" URL (if DATABASE_URL is not found, it means you're running your web app on localhost).
# The replace() method in db_url is needed due to this issue: https://help.heroku.com/ZKNTJQSK/why-is-sqlalchemy-1-4-x-not-connecting-to-heroku-postgres.

db_url = os.getenv("DATABASE_URL", "sqlite:///db.sqlite").replace("postgres://", "postgresql://", 1)  # the database name name: db.sqlite could be something else, like database.sqlite or localhost.sqlite
db = SQLAlchemy(db_url) # creates a new SQLite database
# db = SQLAlchemy("sqlite:///db.sqlite") - code appropriate for local work, can not be deployed to Heroku

class Message(db.Model): # inherits features from the db.Model class, that's why it doesn't have to use the __init__ method
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String, unique=False)
    text = db.Column(db.String, unique=False)

db.create_all() # calls the database (db) and tells it to create new tables based on the classes defined

@app.route("/", methods=["GET"])
def index():
    page = request.args.get("page") # tries to get the "page" variable from request.args (request arguments)

    if not page:
        page = 1

    # messages_query = db.query(Message).all  gets all messages at once, not corrects for paginating
    messages_query = db.query(Message) # creates variebale with query to get messages from database
                                        # .all() is not included, we don't actually want to execute this query
    messages = paginate(query=messages_query, page=int(page), page_size=5) # executes specified query based on the two parameters that we specify:
                                                                            # The page (results from the page that we want to receive)
                                                                            # The page size (how many chat messages are on one page)

    return render_template("index.html", messages=messages)

@app.route("/add-message", methods=["POST"])
def add_message():
    username = request.form.get("username")
    text = request.form.get("text")

    message = Message(author=username, text=text)
    message.save()

    print("{0}: {1}".format(username, text))

    return redirect("/") # rederects to home address (reloads page)

if __name__ == '__main__':
    app.run()