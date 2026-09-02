from flask import Flask
from flask import render_template, request, redirect, url_for, g, session
from datetime import date
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


@app.context_processor
def inject_current_user():
    uid = session.get("loggedin_UID")
    if not uid:
        return {"user_name": "Guest"}
    name = session.get("name")
    if not name:
        db = get_db()
        row = db.execute("SELECT name FROM USER WHERE UID = ?", (uid,)).fetchone()
        name = row["name"] if row else "Guest"
        session["name"] = name
    return {"user_name": name}


@app.after_request
def disable_cache(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route("/session-check")
def session_check():
    if not check_login():
        return ("", 401)
    return ("", 204)




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
            issupervisor = request.form.get("issupervisor")
            db.execute("insert into police (UID, rank, supervisor, department, patrol_area, badge_no, issupervisor) values (?, ?, ?, ?, ?, ?, ?)", (uid, rank, supervisor, department, patrol_area, badge_no, issupervisor))

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
                session["name"] = user["name"]
                if session["role"] == "police":
                    police = db.execute("SELECT issupervisor FROM POLICE WHERE UID = ?", (session["loggedin_UID"],)).fetchone()
                    session["issupervisor"] = police["issupervisor"]
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
    
    if not check_login():
        return redirect("/login")
    role = session.get("role")
    user_id = session.get("loggedin_UID")
    db = get_db()
    user = db.execute("SELECT * FROM USER WHERE UID = ?", (user_id,)).fetchone()
    if role == "police":
        officers_count = db.execute("select count(*) as officers from Police").fetchone()
        incidents_count = db.execute("select count(*) as incidents from 'Incident Reports'").fetchone()
        criminals_count = db.execute("select count(*) as criminals from Criminal").fetchone()
        jails_count = db.execute("select count(*) as jails from Jail").fetchone()
        stats = {
            "officers": officers_count[0],
            "incidents": incidents_count[0],
            "criminals": criminals_count[0],
            "jails": jails_count[0]
        }
        own_incidents = db.execute("select i.IRID, i.Date, i.incident_location as location, i.AccusedName from 'Incident Reports' i join Works_on w on i.IRID = w.IRID where w.UID = ? order by i.Date desc", (session.get("loggedin_UID"),)).fetchall()
        criminals = db.execute("select CID, Name, Crime, Age from Criminal").fetchall()
        return render_template("dashboard.html", user=user, stats=stats, own_incidents=own_incidents, criminals=criminals)

    else:
        reports = db.execute("select IRID, Date, incident_location as location, AccusedName from 'Incident Reports' where ReportedUID = ? order by Date desc", (session.get("loggedin_UID"),)).fetchall()
        return render_template("user_dashboard.html", user=user, reports=reports)



@app.route("/incidents")
def incidents():
    ## to do: list Incident Reports
    if not check_login():
        return redirect("/login")
    if session.get("role") != "police":
        return redirect("/dashboard")
    db = get_db()
    incidents = db.execute("select i.IRID, i.Date, i.incident_location as location, i.AccusedName, u.Name as reporter_name, count(w.UID) as officer_count from 'Incident Reports' i join User u on i.ReportedUID = u.UID left join Works_on w on i.IRID = w.IRID group by i.IRID").fetchall()
    return render_template("incidents.html", incidents=incidents)



@app.route("/incidents/<int:irid>", methods=["GET", "POST"])
def incident_detail(irid):
    ## to do: GET report + victims + officers + Judge/Evidence; POST assign Works_on (police only)
    if not check_login():
        return redirect("/login")
    db = get_db()
    if request.method == "GET":
        incident = db.execute("select i.IRID, i.Description, i.Date, i.incident_location as location, i.AccusedName, u.Name as reporter_name, c.Judge, c.Evidence from 'Incident Reports' i join User u on i.ReportedUID = u.UID left join 'Criminal cases' c on i.IRID = c.IRID where i.IRID = ?", (irid,)).fetchone()
        victims = db.execute("select u.Name from Targeted t join User u on t.UID = u.UID where t.IRID = ?", (irid,)).fetchall()
        officers = db.execute("select u.Name from Works_on w join User u on w.UID = u.UID where w.IRID = ?", (irid,)).fetchall()
        cases = db.execute("select c.Judge, c.Evidence from 'Criminal cases' c where c.IRID = ?", (irid,)).fetchone()
        involved_criminals = db.execute("select c.CID, c.Name from 'Criminal Involvement' ci join Criminal c on ci.CID = c.CID where ci.IRID = ?", (irid,)).fetchall()
        if session.get("role") == "police":
            all_officers = db.execute("select p.UID, u.Name from Police p join User u on p.UID = u.UID where p.UID not in (select w.UID from Works_on w where w.IRID = ?)", (irid,)).fetchall()
            all_criminal = db.execute("select * from Criminal").fetchall()
            return render_template("incident_detail.html", incident=incident, victims=victims, officers=officers, all_officers=all_officers, cases=cases, involved_criminals=involved_criminals, all_criminal=all_criminal)
        else:
            return render_template("incident_detail.html", incident=incident, victims=victims, officers=officers, cases=cases, involved_criminals=involved_criminals)
        
    if request.method == "POST" and session.get("role") == "police":
        db = get_db()
        action = request.form.get("action")
        if action == "assign_officer":
            officer = request.form.get("officer")
            db.execute("INSERT INTO Works_on (UID, IRID) VALUES (?, ?)", (officer, irid))
            db.commit()
            return redirect(f"/incidents/{irid}")
        if action == "update_judge":
            judge = request.form.get("judge")
            evidence = request.form.get("evidence")
            db.execute("UPDATE 'Criminal cases' SET Judge = ?, Evidence = ? WHERE IRID = ?", (judge, evidence, irid))
            db.commit()
            return redirect(f"/incidents/{irid}")
        if action == "update_criminal":
            criminal = request.form.get("criminal")
            db.execute("INSERT INTO 'Criminal Involvement' (CID, IRID) VALUES (?, ?)", (criminal, irid))
            db.commit()
            return redirect(f"/incidents/{irid}")
        if action == "promote_case":
            judge = request.form.get("judge")
            evidence = request.form.get("evidence")
            db.execute("insert into 'Criminal cases' (IRID, Judge, Evidence) values (?, ?, ?)", (irid, judge, evidence))
            db.commit()
            return redirect(f"/incidents/{irid}")


@app.route("/report", methods=["GET", "POST"])
def report_incident():
    ## to do: POST insert Incident Reports
    if not check_login():
        return redirect("/login")
    if request.method == "GET":
        return render_template("report_incident.html", today=date.today().isoformat())
    if request.method == "POST":
        db = get_db()
        incident_date = request.form.get("Date")
        incident_location = request.form.get("incident_location")
        accused_name = request.form.get("AccusedName")
        description = request.form.get("Description")
        victims = request.form.getlist("victims")
        db.execute("INSERT INTO 'Incident Reports' (Date, incident_location, AccusedName, Description, ReportedUID) VALUES (?, ?, ?, ?, ?)", (incident_date, incident_location, accused_name, description, session.get("loggedin_UID")))
        irid = db.execute("SELECT last_insert_rowid()").fetchone()[0]
        for victim_uid in victims:
            if not victim_uid:
                continue
            db.execute("INSERT INTO Targeted (UID, IRID) VALUES (?, ?)", (victim_uid, irid))
        db.commit()
        return redirect("/incidents")


@app.route("/analytics")
def analytics():
    ## to do: GROUP BY Incident Location and by time-of-day
    if not check_login():
        return redirect("/login")
    db = get_db()
    hot_zones = db.execute("select incident_location as location, count(*) as count, count(*) * 100.0 / (select count(*) from 'Incident Reports') as pct from 'Incident Reports' group by incident_location").fetchall()
    crimes_by_day = db.execute("select strftime('%Y-%m-%d', Date) as label, count(*) as count, count(*) * 100.0 / (select count(*) from 'Incident Reports') as pct from 'Incident Reports' group by label").fetchall()
    crimes_by_month = db.execute("select strftime('%Y-%m', Date) as label, count(*) as count, count(*) * 100.0 / (select count(*) from 'Incident Reports') as pct from 'Incident Reports' group by label").fetchall()
    crimes_by_year = db.execute("select strftime('%Y', Date) as label, count(*) as count, count(*) * 100.0 / (select count(*) from 'Incident Reports') as pct from 'Incident Reports' group by label").fetchall()
    totals = db.execute("select count(*) as incidents, count(distinct incident_location) as locations from 'Incident Reports'").fetchone()
    peak_day = db.execute("select strftime('%Y-%m-%d', Date) as label, count(*) as count from 'Incident Reports' group by label order by count desc limit 1").fetchone()
    peak_month = db.execute("select strftime('%Y-%m', Date) as label, count(*) as count from 'Incident Reports' group by label order by count desc limit 1").fetchone()
    peak_year = db.execute("select strftime('%Y', Date) as label, count(*) as count from 'Incident Reports' group by label order by count desc limit 1").fetchone()
    return render_template("analytics.html", hot_zones=hot_zones, crimes_by_day=crimes_by_day, crimes_by_month=crimes_by_month, crimes_by_year=crimes_by_year, totals=totals, peak_day=peak_day, peak_month=peak_month, peak_year=peak_year)


# --- Person 2: criminals, search, court cases ---
# docs/person-2-criminals-cases.md

@app.route("/criminals", methods=["GET", "POST"])
def criminals():
    ## done
    if not check_login():
            return redirect("/login")
    if session.get("role") != "police":
        return redirect("/search")
    if request.method == "GET":
        db = get_db()
        criminal = db.execute("SELECT c.CID, c.Name, c.Age, c.Crime, c.Gender, c.Nationality, j.Name as jail_name, c.time_sentenced FROM CRIMINAL c LEFT JOIN JAIL j ON c.JID = j.JID").fetchall()
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
        height = request.form.get("Height")
        time_sentenced = request.form.get("time_sentenced")
        db.execute("INSERT INTO CRIMINAL (Name, Age, Gender, Nationality, Crime, JID, Height, time_sentenced) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (name, age, gender, nationality, crime, jail_id, height, time_sentenced))
        db.commit()
        return redirect("/criminals")



@app.route("/criminals/<int:cid>", methods=["GET", "POST"])
def criminal_detail(cid):
    # done
    if not check_login():
            return redirect("/login")
    db = get_db()
    if request.method == "GET":
        criminal = db.execute("SELECT * FROM CRIMINAL WHERE CID = ?", (cid,)).fetchone()
        jail = db.execute("SELECT * FROM JAIL WHERE JID = ?", (criminal["JID"],)).fetchone()
        arrest = db.execute("SELECT a.UID, u.Name, p.badge_no, p.rank FROM 'Arrested By' a JOIN User u ON a.UID = u.UID JOIN Police p ON a.UID = p.UID WHERE a.CID = ?", (cid,)).fetchall()
        officers = db.execute("SELECT p.UID, u.Name FROM Police p JOIN User u ON p.UID = u.UID where p.UID not in (SELECT distinct UID FROM 'Arrested By')").fetchall()
        case = db.execute("SELECT * FROM 'Criminal Involvement' WHERE CID = ?", (cid,)).fetchall()
        jails = db.execute("SELECT * FROM JAIL").fetchall()
        return render_template("criminal_detail.html", criminal=criminal, jail=jail, arrest=arrest, allofficers=officers, case=case, jails=jails)

    if request.method == "POST":
        if session.get("role") != "police":
            return redirect("/criminals/{cid}".format(cid=cid))
        name = request.form.get("Name").strip()
        age = request.form.get("Age")
        gender = request.form.get("Gender")
        nationality = request.form.get("Nationality")
        crime = request.form.get("Crime")
        jail_id = request.form.get("JID")
        height = request.form.get("Height")
        time_sentenced = request.form.get("time_sentenced")
        db.execute("UPDATE CRIMINAL SET Name = ?, Age = ?, Gender = ?, Nationality = ?, Crime = ?, JID = ?, Height = ?, time_sentenced = ? WHERE CID = ?", (name, age, gender, nationality, crime, jail_id, height, time_sentenced, cid))
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


# --- Person 3: jails, officers, victim cases ---
# docs/person-3-jails-officers.md

@app.route("/jails", methods=["GET", "POST"])
def jails():
    ## done
    if not check_login():
            return redirect("/login")
    if session.get("role") != "police":
        return redirect("/dashboard")
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
    if session.get("role") != "police":
        return redirect("/dashboard")
    if request.method == "GET":
        db = get_db()
        jail = db.execute("SELECT j.*, Count(c.CID) as Occupancy FROM Jail j LEFT JOIN Criminal c ON j.JID = c.JID WHERE j.JID = ?", (jid,)).fetchone()
        inmates = db.execute("SELECT * FROM Criminal WHERE JID = ?", (jid,)).fetchall()
        jailers = db.execute("SELECT j.UID, u.Name, p.badge_no, p.rank FROM Jailor j JOIN User u ON j.UID = u.UID JOIN Police p ON j.UID = p.UID WHERE j.JID = ?", (jid,)).fetchall()
        officers = db.execute("SELECT p.UID, u.Name FROM Police p JOIN User u ON p.UID = u.UID where p.UID not in (SELECT distinct UID FROM Jailor)").fetchall()
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
    if session.get("role") != "police":
        return redirect("/dashboard")
    if request.method == "POST":
        db = get_db()
        jid = request.form.get("JID")
        name = request.form.get("Name").strip()
        location = request.form.get("Location").strip()
        capacity = request.form.get("Capacity")
        db.execute("UPDATE JAIL SET Name = ?, Location = ?, Capacity = ? WHERE JID = ?", (name, location, capacity, jid))
        db.commit()
        return redirect(f"/jails/{jid}")    
    

@app.route("/officers")
def officers():
    # done
    ## to do: SELECT police profiles joined with USER
    if not check_login():
        return redirect("/login")
    if session.get("role") != "police" or session.get("issupervisor") == False:
        return redirect("/dashboard")
    db = get_db()
    officers = db.execute("SELECT p.UID, u.Name, p.rank, p.department, p.patrol_area, p.badge_no FROM Police p JOIN User u ON p.UID = u.UID where p.supervisor = ?", (session.get("loggedin_UID"),)).fetchall()
    return render_template("officers.html", officers=officers)


@app.route("/officers/<int:uid>", methods=["GET", "POST"])
def officer_detail(uid):
    ## to do: GET officer + team; POST update POLICE/USER (supervisor)
    if not check_login():
        return redirect("/login")
    if session.get("role") != "police" or session.get("issupervisor") == False:
        return redirect("/dashboard")
    db = get_db()
    officer = db.execute("SELECT p.UID, u.phone, u.age, u.gender, u.Name, p.rank, p.department, p.patrol_area, p.badge_no, p.number_of_arrests FROM Police p JOIN User u ON p.UID = u.UID WHERE p.UID = ?", (uid,)).fetchone()
    return render_template("officer_detail.html", officer=officer)


@app.route("/my-cases", methods=["GET", "POST"])
def victim_cases():
    if not check_login():
        return redirect("/login")
    if session.get("role") == "police":
        return redirect("/incidents")
    if request.method == "POST":
        return redirect("/report")
    db = get_db()
    cases = db.execute("select i.IRID, i.Date, i.incident_location as location, i.AccusedName, c.Judge, c.Evidence from 'Incident Reports' i left join 'Criminal cases' c on i.IRID = c.IRID where i.ReportedUID = ? order by i.Date desc", (session.get("loggedin_UID"),)).fetchall()
    return render_template("victim_cases.html", cases=cases)


if __name__ == "__main__":
    app.run(debug=True)
