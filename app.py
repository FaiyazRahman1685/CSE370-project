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
    if session.get("uid") or session.get("role"):
        if session.get("role") == "police":
            return redirect(url_for("dashboard"))
        return redirect(url_for("user_dashboard"))
    return login_page()


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    role = request.form.get("role", "user")
    ## to do: look up USER / POLICE and check password

    session["name"] = username or "Guest"
    session["role"] = role if role in ("user", "police") else "user"
    if session["role"] == "police":
        return redirect(url_for("dashboard"))
    return redirect(url_for("user_dashboard"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# --- Police ---

@app.route("/dashboard")
def dashboard():
    ## to do: counts + recent incidents + recent criminals
    return render_template("dashboard.html")


@app.route("/criminals", methods=["GET", "POST"])
def criminals():
    ## to do: GET list Criminal; POST insert Criminal
    return render_template("criminals.html")


@app.route("/criminals/<int:cid>", methods=["GET", "POST"])
def criminal_detail(cid):
    ## to do: GET one Criminal + arrests + involvement; POST update
    return render_template("criminal_detail.html")


@app.route("/jails", methods=["GET", "POST"])
def jails():
    ## to do: GET Jail + occupancy; POST insert Jail
    return render_template("jails.html")


@app.route("/jails/<int:jid>", methods=["GET", "POST"])
def jail_detail(jid):
    ## to do: GET jail + inmates + jailors; POST update / assign jailor
    return render_template("jail_detail.html")


@app.route("/officers")
def officers():
    ## to do: SELECT police profiles joined with USER
    return render_template("officers.html")


@app.route("/officers/<int:uid>", methods=["GET", "POST"])
def officer_detail(uid):
    ## to do: GET officer + team; POST update POLICE/USER (supervisor)
    return render_template("officer_detail.html")


@app.route("/proceedings")
def proceedings():
    ## to do: list Incident Reports left join Criminal cases
    return render_template("proceedings.html")


@app.route("/proceedings/<int:irid>", methods=["GET", "POST"])
def proceeding_detail(irid):
    ## to do: GET case file; POST update Judge/Evidence, link criminals, assign officers
    return render_template("proceeding_detail.html")


@app.route("/analytics")
def analytics():
    ## to do: GROUP BY Incident Location and by time-of-day
    return render_template("analytics.html")


@app.route("/incidents")
def incidents():
    ## to do: list Incident Reports
    return render_template("incidents.html")


@app.route("/incidents/<int:irid>", methods=["GET", "POST"])
def incident_detail(irid):
    ## to do: GET report + victims + officers; POST assign Works_on
    return render_template("incident_detail.html")


# --- Civilian ---

@app.route("/home")
def user_dashboard():
    ## to do: this user's Incident Reports
    return render_template("user_dashboard.html")


@app.route("/search")
def search_criminals():
    ## to do: filter Criminal by crime / gender / nationality / jail
    return render_template("search.html")


@app.route("/jail-info")
def jail_info():
    ## to do: Jail + occupancy counts
    return render_template("jail_info.html")


@app.route("/jail-info/<int:jid>")
def jail_info_detail(jid):
    ## to do: one Jail + public inmate list
    return render_template("jail_info_detail.html")


@app.route("/my-cases", methods=["GET", "POST"])
def victim_cases():
    ## to do: GET this victim's cases; POST Incident Reports + Targeted + Criminal cases
    return render_template("victim_cases.html")


@app.route("/report", methods=["GET", "POST"])
def report_incident():
    ## to do: POST insert Incident Reports
    return render_template("report_incident.html")


if __name__ == "__main__":
    app.run(debug=True)
