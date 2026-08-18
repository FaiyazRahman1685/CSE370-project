# Person 1 — Login, home pages, incident reports, analytics

You write the **SQL** in `app.py`. Do **not** change the HTML files.

Find your functions by searching `app.py` for names like `login`, `dashboard`, `incidents`.

---

## How this works (read once)

1. Someone opens a page or clicks a button.
2. Python runs one function.
3. You run SQL with:

```python
db = get_db()
rows = db.execute("SELECT ...").fetchall()   # many rows
row  = db.execute("SELECT ...").fetchone()   # one row
```

4. You send the result to the page:

```python
return render_template("dashboard.html", stats=stats, incidents=incidents, criminals=criminals)
```

The **names** on the right (`incidents`, `criminals`, …) must match what the page expects.

If you forget to send them, the page shows fake sample data.

To **save** something:

```python
db.execute("INSERT INTO ... VALUES (?, ?)", (value1, value2))
db.commit()
```

To **read a form box** the user filled in:

```python
request.form["username"]
```

After a successful login, store:

```python
session["uid"] = user["UID"]
session["name"] = user["name"]
session["role"] = "police"   # or "user"
```

Other people need `session["uid"]`. Please do login first.

Table/column names with spaces need quotes, for example `"Incident Reports"` and `"Incident Location"`.

---

## Login

**Function:** `login`  
**When:** user fills the login page and clicks **Sign in**.

**SQL:** find a person in `USER` whose `name` and `password` match.

- If they picked **Police**, they must also be in the `POLICE` table.
- If they picked **Civilian**, they must **not** be in `POLICE`.

Wrong login → show the login page again with an error:

```python
return login_page("Invalid username or password", username, role)
```

Correct login → save `uid`, `name`, `role` in `session`, then:

- police go to the police dashboard
- civilians go to home

(`index` and `logout` are already done. Leave them.)

---

## Police dashboard

**Function:** `dashboard`  
**When:** a police officer logs in, or clicks **Dashboard**.

**SQL:**

- count rows in `POLICE`, `"Incident Reports"`, `Criminal`, `Jail`
- last few incident reports
- last few criminals

**Give the page:**

- `stats` = officers count, incidents count, criminals count, jails count
- `incidents` = `IRID`, `Date`, `location`, `AccusedName`  
  (`location` means column `"Incident Location"`)
- `criminals` = `CID`, `Name`, `Crime`, `Age`

---

## Civilian home

**Function:** `user_dashboard`  
**When:** a civilian logs in, or clicks **Home**.

**SQL:** incident reports where `ReportedUID` is this person (`session["uid"]`).

**Give the page:** `reports` = `IRID`, `Date`, `location`, `AccusedName`

---

## All incident reports (police)

**Function:** `incidents`  
**When:** police click **Incidents**.

**SQL:** list every row in `"Incident Reports"`. Also get the reporter’s name from `USER`, and how many officers are on it (`Works_on`).

**Give the page:** `incidents` = `IRID`, `Date`, `location`, `AccusedName`, `reporter_name`, `officer_count`

---

## One incident (police)

**Function:** `incident_detail`  
**When:** police click **Open** on a report.

The number in the URL is `irid` (the report id).

**If they are just opening the page:**

- one report
- victims of this report (`Targeted` + `USER`)
- officers already assigned (`Works_on` + `USER` + `POLICE`)
- list of all officers (for the dropdown)

**Give the page:**

- `incident` = `IRID`, `Date`, `Description`, `location`, `AccusedName`, `reporter_name`
- `victims` = `UID`, `name`
- `officers` = `UID`, `name`, `badge_no`  
  (`badge_no` means column `"Badge No"`)
- `all_officers` = `UID`, `name`

**If they click Add** (assign an officer):

- form sends `UID`
- `INSERT` into `Works_on` (`UID`, this `irid`)
- `db.commit()`
- show the same page again

---

## File a report (civilian)

**Function:** `report_incident`  
**When:** civilian clicks **Report**.

**If they are just opening the page:** show the form (already there). Do not pass extra data.

**If they click File report:**

Form boxes: `Date`, `incident_location`, `AccusedName`, `Description`.

`INSERT` into `"Incident Reports"`. Set `ReportedUID` to `session["uid"]`.  
Column name for the place is `"Incident Location"`.

Then send them to home:

```python
return redirect(url_for("user_dashboard"))
```

---

## Analytics (police)

**Function:** `analytics`  
**When:** police click **Analytics**.

**SQL:**

1. How many reports per place (`GROUP BY "Incident Location"`) → hot zones
2. How many reports per time of day → busy hours

For the bars, `pct` = that count ÷ the biggest count × 100.

**Give the page:**

- `totals` = `incidents` (total reports), `locations` (how many different places), `peak_label` (busiest time, e.g. `"6–9 PM"`)
- `hot_zones` = `location`, `count`, `pct`
- `busy_hours` = `label`, `count`, `pct`
