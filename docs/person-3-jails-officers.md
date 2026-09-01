# Person 3 — Jails, police officers, victim cases

You write the **SQL** in `app.py`. Do **not** change the HTML files.

Find your functions by searching `app.py` for names like `jails`, `jail_info`, `officers`, `victim_cases`.

Wait until Person 1 finishes login, so `session["uid"]` exists.

If an inmate name links to a criminal page, that page is Person 2’s job. You only make the list.

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
return render_template("jails.html", jails=rows)
```

The **names** on the right must match what the page expects.

If you forget to send them, the page shows fake sample data.

To **save** something:

```python
db.execute("INSERT INTO Jail (Name, Location, Capacity) VALUES (?, ?, ?)", (name, location, capacity))
db.commit()
```

To **read a form box**:

```python
request.form["Name"]
```

Some pages have two forms. Check:

```python
action = request.form.get("action")
```

Table/column names with spaces need quotes: `"Badge No"`, `"patrol area"`, `"number of arrests"`, `"Incident Location"`, `"Criminal cases"`.

---

## List of jails + add one (police)

**Function:** `jails`  
**When:** police click **Jails**.

**Opening the page:**

- all rows in `Jail`
- `occupancy` = how many criminals have that `JID`
- `jailor_count` = how many rows in `Jailor` for that jail

**Give the page:** `jails` = `JID`, `Name`, `Location`, `Capacity`, `occupancy`, `jailor_count`

**Clicking Save jail:**

Form boxes: `Name`, `Location`, `Capacity`.  
`INSERT` into `Jail`, then:

```python
return redirect(url_for("jails"))
```

---

## One jail (police)

**Function:** `jail_detail`  
**When:** police click **Manage** on a jail.

The number in the URL is `jid`.

**Opening the page:**

- that jail
- criminals in it
- jailors (`Jailor` + officer name + badge + rank)
- all officers (dropdown)

**Give the page:**

- `jail` = `JID`, `Name`, `Location`, `Capacity`, `occupancy`
- `inmates` = `CID`, `Name`, `Crime`, `time_sentenced`
- `jailors` = `UID`, `name`, `badge_no`, `rank`
- `officers` = `UID`, `name`

**Clicking Update jail** (`action` is `update_jail`):

- form: `Name`, `Location`, `Capacity`
- `UPDATE Jail ... WHERE JID = ?`

**Clicking Add** next to jailors (`action` is `assign_jailor`):

- form: `UID`
- `INSERT` into `Jailor` (`UID`, this `jid`)

Then `db.commit()` and show this page again.

---

## Jail info list (not public)

Civilians do **not** get jail info. Do not send them to `jail_info`. If `/jail-info` is opened, send them home.

Police use **Jails** (`jails` / `jail_detail`) instead.

---

## One jail, public view (not used)

**Function:** `jail_info_detail`  
Same as above: civilians do not see facility details. Redirect home.

---

## List of officers (police)

**Function:** `officers`  
**When:** police click **Officers**.

**SQL:** `POLICE` joined with `USER` (name comes from `USER`). Also get the supervisor’s name (another join to `USER`).

**Give the page:** `officers` = `UID`, `name`, `badge_no`, `rank`, `department`, `patrol_area`, `arrests`, `supervisor_name`

Remember:

- `badge_no` = `"Badge No"`
- `patrol_area` = `"patrol area"`
- `arrests` = `"number of arrests"`

---

## One officer (police)

**Function:** `officer_detail`  
**When:** police click **View** next to an officer.

The number in the URL is `uid`.

**Opening the page:**

- that person (`USER` + `POLICE`)
- officers whose `supervisor` is this `uid` (their team)
- list of officers who could be a supervisor (dropdown)

**Give the page:**

- `officer` = `UID`, `name`, `phone`, `age`, `gender`, `badge_no`, `patrol_area`, `arrests`, `department`, `rank`, `supervisor`
- `supervisors` = `UID`, `name`
- `team` = `UID`, `name`, `badge_no`, `rank`

**Clicking Save officer:**

Form boxes: `name`, `phone`, `badge_no`, `rank`, `department`, `patrol_area`, `arrests`, `supervisor`.

- `UPDATE USER` (name, phone)
- `UPDATE POLICE` (badge, rank, department, patrol area, arrests, supervisor)

Then show this page again.

---

## Victim reports (civilian)

**Function:** `victim_cases`  
**When:** someone opens `/my-cases`. This is **not** in the public nav.

Civilians **cannot** create criminal cases. They only file incident reports (`report_incident`).

**Opening the page:** list this person’s incident reports (`ReportedUID` = signed-in user), and show judge/evidence if police later promoted the report (`"Criminal cases"`).

**Give the page:** `cases` = `IRID`, `Date`, `location`, `AccusedName`, `Judge`, `Evidence`

**If they POST:** do **not** insert into `"Criminal cases"`. Send them to file an incident instead:

```python
return redirect(url_for("report_incident"))
```
