from flask import Flask
from flask import render_template, request, redirect, url_for, g, session
import sqlite3

app = Flask(__name__)


app.secret_key = "sentinel-dev-key"
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
app.config["DATABASE"] = "database.db"


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def login_page(error=None, username="", role="user"):
    return render_template("login.html", error=error, username=username, role=role)


@app.route("/")
def index():
    if session.get("uid"):
        if session.get("role") == "police":
            return redirect(url_for("dashboard"))
        return redirect(url_for("user_dashboard"))
    return login_page()


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    role = request.form.get("role", "user")
    ## to do 
    
    return redirect(url_for("user_dashboard"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/dashboard")
def dashboard():
    ## to do 



@app.route("/home")
def user_dashboard():
    ## to do 


if __name__ == "__main__":
    app.run(debug=True)