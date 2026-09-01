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
    ## done
    if session.get("loggedin_UID"):
        return redirect("/dashboard")
    return redirect("/login")


@app.route("/signup", methods=["GET","POST"])
## done
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
        ## done
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
    ##done
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
    ## done
    if not check_login():
            return redirect("/login")
    if request.method == "GET":
        db = get_db()
        criminal = db.execute("SELECT * FROM CRIMINAL").fetchall()
        jail = db.execute("SELECT * FROM JAIL").fetchall()
        return render_template("criminals.html", criminals=criminal, jails=jail)

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
    if not check_login():
            return redirect("/login")
    db = get_db()
    if request.method == "GET":
        criminal = db.execute("SELECT * FROM CRIMINAL WHERE CID = ?", (cid,)).fetchone()
        jail = db.execute("SELECT * FROM JAIL WHERE JID = ?", (criminal["JID"],)).fetchone()
        arrest = db.execute("SELECT * FROM 'Arrested By' WHERE CID = ?", (cid,)).fetchall()
        case = db.execute("SELECT * FROM 'Criminal Involvement' WHERE CID = ?", (cid,)).fetchall()
        return render_template("criminal_detail.html", criminal=criminal, jail=jail, arrest=arrest, case=case)

    if request.method == "POST":
        name = request.form.get("Name").strip()
        age = request.form.get("Age")
        gender = request.form.get("Gender")
        nationality = request.form.get("Nationality")
        crime = request.form.get("Crime")
        jail_id = request.form.get("JID")
        time_sentenced = request.form.get("time_sentenced")
        db.execute("UPDATE CRIMINAL SET Name = ?, Age = ?, Gender = ?, Nationality = ?, Crime = ?, JID = ?, time_sentenced = ? WHERE CID = ?", (name, age, gender, nationality, crime, jail_id, time_sentenced, cid))
        db.commit()
        return redirect("/criminals/{cid}".format(cid=cid))


@app.route("/search" , methods=["GET"])
def search_criminals():
    ## done kindof
    if not check_login():
                return redirect("/login")

    db = get_db()
    #drop down filters
    crimes = db.execute("SELECT DISTINCT Crime FROM CRIMINAL").fetchall()
    genders = db.execute("SELECT DISTINCT Gender FROM CRIMINAL").fetchall()
    nationalities = db.execute("SELECT DISTINCT Nationality FROM CRIMINAL").fetchall()
    jail = db.execute("SELECT * FROM JAIL").fetchall()
    
    #Filtered values
    crime = request.args.get("crime") or ""
    gender = request.args.get("gender") or ""
    nationality = request.args.get("nationality") or ""
    jail_id = request.args.get("jail_id") or ""

    query = "SELECT c.*, j.Name as jail_name FROM CRIMINAL c LEFT JOIN JAIL j ON c.JID = j.JID where 1=1"

    params = []
    if crime:   
        query += " AND c.Crime = ?"
        params.append(crime)

    if gender:
        query += " AND c.Gender = ?"
        params.append(gender)

    if nationality:
        query += " AND c.Nationality = ?"
        params.append(nationality)

    if jail_id:
        query += " AND c.JID = ?"
        params.append(jail_id)

    criminals = db.execute(query, params).fetchall()
    filters = {
            "crime": crimes,
            "gender": genders,
            "nationality": nationalities,
            "jail_id": jail_id
        }
    
    return render_template("search.html", results=criminals, jails=jail, crimes=crimes, genders=genders, nationalities=nationalities, filters=filters)
        


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
    ## done
    if not check_login():
            return redirect("/login")
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
    ## done
    if not check_login():
            return redirect("/login")
    if request.method == "GET":
        db = get_db()
        jail = db.execute("SELECT j.*, Count(c.CID) as Occupancy FROM Jail j LEFT JOIN Criminal c ON j.JID = c.JID WHERE j.JID = ?", (jid,)).fetchone()
        inmates = db.execute("SELECT * FROM Criminal WHERE JID = ?", (jid,)).fetchall()
        jailers = db.execute("SELECT j.UID, u.Name, p.badge_no, p.rank FROM Jailor j JOIN User u ON j.UID = u.UID JOIN Police p ON j.UID = p.UID WHERE j.JID = ?", (jid,)).fetchall()
        officers = db.execute("SELECT p.UID, u.Name FROM Police p JOIN User u ON p.UID = u.UID").fetchall()
        return render_template("jail_detail.html", jail=jail, inmates=inmates, jailors=jailers, officers=officers)
    
    if request.method == "POST":
        db = get_db()
        jailor_id = request.form.get("UID")
        db.execute("INSERT INTO Jailor (UID, JID) VALUES (?, ?)", (jailor_id, jid))
        db.commit()
        return redirect(f"/jails/{jid}")
        
@app.route("/updatejail", methods=["POST"])
def update_jail():
    if not check_login():
            return redirect("/login")
    if request.method == "POST":
        db = get_db()
        jid = request.form.get("JID")
        name = request.form.get("Name").strip()
        location = request.form.get("Location").strip()
        capacity = request.form.get("Capacity")
        db.execute("UPDATE JAIL SET Name = ?, Location = ?, Capacity = ? WHERE JID = ?", (name, location, capacity, jid))
        db.commit()
        return redirect(f"/jails/{jid}")    
    

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
