from flask import Flask
from flask import render_template, request, redirect, url_for, g, session
import sqlite3
import random

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

def check_login():
    if session.get("loggedin_UID") is None:
        return False
    return True
    

def generate_uid():
    while True:
        uid = random.randint(1000, 9999)
        db = get_db()
        user = db.execute("SELECT * FROM USER WHERE UID = ?", (uid,)).fetchone()
        if user is None:
            return uid

@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()




# --- Person 1: login, dashboards, incidents, analytics ---
# docs/person-1-login-incidents.md

@app.route("/")
def index():
    if session.get("loggedin_UID"):
        return redirect("/dashboard")
    return redirect("/login")


@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        role = request.form.get("role")
        age = request.form.get("age")
        gender = request.form.get("gender")
        phone = request.form.get("phone")
        uid = generate_uid()
        db = get_db()
        db.execute("insert into user (UID, name, password, age, gender, phone, role) values (?, ?, ?, ?, ?, ?, ?)", (uid, username, password, age, gender, phone, role))
        
        if role == "police":
            rank = request.form.get("rank")
            supervisor = request.form.get("supervisor")
            department = request.form.get("department")
            patrol_area = request.form.get("patrol_area")
            badge_no = request.form.get("badge_no")
            db.execute("insert into police (UID, rank, supervisor, department, patrol_area, badge_no) values (?, ?, ?, ?, ?, ?)", (uid, rank, supervisor, department, patrol_area, badge_no))

        db.commit()
        return redirect("/login")
        
@app.route("/login", methods=["POST","GET"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        ## to do: look up USER / POLICE and check password
        db = get_db()
        user = db.execute("SELECT * FROM USER WHERE name = ?", (username,)).fetchone()
        if user:
            real_password = user["password"]
            if password == real_password:
                session["loggedin_UID"] = user["UID"]
                session["role"] = user["role"]
                return redirect("/dashboard")
            else:
                return render_template("login.html", error="Invalid password")
        else: 
            return render_template("login.html", error="User not found ")



@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/dashboard")
def dashboard():
    ## to do: counts + recent incidents + recent criminals
    if not check_login():
        return redirect("/login")
    role = session.get("role")
    user_id = session.get("loggedin_UID")
    db = get_db()
    user = db.execute("SELECT * FROM USER WHERE UID = ?", (user_id,)).fetchone()
    if role == "police":
        return render_template("dashboard.html", user=user)
    else:
        return render_template("user_dashboard.html", user=user)



@app.route("/incidents")
def incidents():
    ## to do: list Incident Reports
    return render_template("incidents.html")


@app.route("/incidents/<int:irid>", methods=["GET", "POST"])
def incident_detail(irid):
    ## to do: GET report + victims + officers; POST assign Works_on
    return render_template("incident_detail.html")


@app.route("/report", methods=["GET", "POST"])
def report_incident():
    ## to do: POST insert Incident Reports
    return render_template("report_incident.html")


@app.route("/analytics")
def analytics():
    ## to do: GROUP BY Incident Location and by time-of-day
    return render_template("analytics.html")


# --- Person 2: criminals, search, court cases ---
# docs/person-2-criminals-cases.md

@app.route("/criminals", methods=["GET", "POST"])
def criminals():
    ## to do: GET list Criminal; POST insert Criminal
    if request.method == "GET":
        db = get_db()
        criminal = db.execute("SELECT * FROM CRIMINAL").fetchall()
        jail = db.execute("SELECT * FROM JAIL").fetchall()
        return render_template("criminals.html", criminals=criminal)

    if request.method == "POST":
        db = get_db()
        name = request.form.get("Name").strip()
        age = request.form.get("Age")
        gender = request.form.get("Gender")
        nationality = request.form.get("Nationality")
        crime = request.form.get("Crime")
        jail_id = request.form.get("JID")
        time_sentenced = request.form.get("time_sentenced")
        db.execute("INSERT INTO CRIMINAL (Name, Age, Gender, Nationality, Crime, JID, time_sentenced) VALUES (?, ?, ?, ?, ?, ?, ?)", (name, age, gender, nationality, crime, jail_id, time_sentenced))
        db.commit()
        return redirect("/criminals")



@app.route("/criminals/<int:cid>", methods=["GET", "POST"])
def criminal_detail(cid):
    db = get_db()
    return render_template("criminal_detail.html")


@app.route("/search")
def search_criminals():
    ## to do: filter Criminal by crime / gender / nationality / jail
    return render_template("search.html")


@app.route("/proceedings")
def proceedings():
    ## to do: list Incident Reports left join Criminal cases
    return render_template("proceedings.html")


@app.route("/proceedings/<int:irid>", methods=["GET", "POST"])
def proceeding_detail(irid):
    ## to do: GET case file; POST update Judge/Evidence, link criminals, assign officers
    return render_template("proceeding_detail.html")


# --- Person 3: jails, officers, victim cases ---
# docs/person-3-jails-officers.md

@app.route("/jails", methods=["GET", "POST"])
def jails():
    ## to do: GET Jail + occupancy; POST insert Jail
    if request.method == "GET":
        db = get_db()
        jail = db.execute("SELECT * FROM Jail").fetchall()
        return render_template("jails.html", jails=jail)
        
    if request.method == "POST":
        db = get_db()
        name = request.form.get("Name").strip()
        location = request.form.get("Location").strip()
        capacity = request.form.get("Capacity")
        db.execute("INSERT INTO JAIL (Name, Location, Capacity) VALUES (?, ?, ?)", (name, location, capacity))
        db.commit()
        return redirect("/jails")


@app.route("/jails/<int:jid>", methods=["GET", "POST"])
def jail_detail(jid):
    ## to do: GET jail + inmates + jailors; POST update / assign jailor
    if request.method == "GET":
        db = get_db()
        jail = db.execute("SELECT * FROM Jail").fetchall()
        inmates = db.execute("SELECT * FROM Criminal WHERE JID = ?", (jid,)).fetchall()
        jailers = db.execute("SELECT * FROM Police WHERE UID IN (SELECT UID FROM Jailor WHERE JID = ?)", (jid,)).fetchall()
        return render_template("jail_detail.html", jail=jail, inmates=inmates, jailors=jailers)


@app.route("/jail-info")
def jail_info():
    ## to do: Jail + occupancy counts
    return render_template("jail_info.html")


@app.route("/jail-info/<int:jid>")
def jail_info_detail(jid):
    ## to do: one Jail + public inmate list
    return render_template("jail_info_detail.html")


@app.route("/officers")
def officers():
    ## to do: SELECT police profiles joined with USER
    return render_template("officers.html")


@app.route("/officers/<int:uid>", methods=["GET", "POST"])
def officer_detail(uid):
    ## to do: GET officer + team; POST update POLICE/USER (supervisor)
    return render_template("officer_detail.html")


@app.route("/my-cases", methods=["GET", "POST"])
def victim_cases():
    ## to do: GET this victim's cases; POST Incident Reports + Targeted + Criminal cases
    return render_template("victim_cases.html")


if __name__ == "__main__":
    app.run(debug=True)
