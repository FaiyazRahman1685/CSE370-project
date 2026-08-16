from flask import Flask
from flask import render_template
import sqlite3

app = Flask(__name__)


app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
app.config["DATABASE"] = "database.db"


conn = sqlite3.connect(app.config["DATABASE"])
cursor = conn.cursor()


@app.route("/")
def index():
    return render_template("login.html")  

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    # to do 

    
    return  


if __name__ == "__main__":
    app.run(debug=True)