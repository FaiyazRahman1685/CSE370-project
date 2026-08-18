# Person 2 — Criminals, search, court cases

You write the **SQL** in `app.py`. Do **not** change the HTML files.

Find your functions by searching `app.py` for names like `criminals`, `search_criminals`, `proceedings`.

Wait until Person 1 finishes login, so `session["uid"]` exists.

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
return render_template("criminals.html", criminals=rows, jails=jails)
```

The **names** on the right must match what the page expects.

If you forget to send them, the page shows fake sample data.

To **save** something:

```python
db.execute("INSERT INTO Criminal (Name, Age) VALUES (?, ?)", (name, age))
db.commit()
```

To **read a form box**:

```python
request.form["Name"]
```

Some functions handle two things:

```python
if request.method == "POST":
    # they clicked Save — INSERT or UPDATE, then redirect
    return redirect(url_for("criminals"))

# they just opened the page — SELECT and show it
return render_template("criminals.html", criminals=rows, jails=jails)
```

Table/column names with spaces need quotes: `"Time sentenced"`, `"Criminal cases"`, `"Incident Location"`.

---

## List of criminals + add one (police)

**Function:** `criminals`  
**When:** police click **Criminals**.

**Opening the page:**

- `SELECT` all criminals. Also get the jail name (`JOIN Jail`).
- `SELECT` all jails (for the dropdown).

**Give the page:**

- `criminals` = `CID`, `Name`, `Age`, `Crime`, `Gender`, `Nationality`, `jail_name`, `time_sentenced`
- `jails` = `JID`, `Name`

**Clicking Save profile:**

Form boxes: `Name`, `Age`, `Height`, `Crime`, `Gender`, `Nationality`, `JID`, `time_sentenced`.

`INSERT` into `Criminal`. The sentence column is `"Time sentenced"`.

Then go back to the same list:

```python
return redirect(url_for("criminals"))
```

---

## One criminal (police)

**Function:** `criminal_detail`  
**When:** police click **Open** next to a name.

The number in the URL is `cid`.

**Opening the page:**

- that one criminal + jail name
- who arrested them (`"Arrested by"` + officer name + badge)
- which incidents they are in (`"Criminal involvement"`)

**Give the page:**

- `criminal` = `CID`, `Name`, `Age`, `Crime`, `Height`, `Gender`, `Nationality`, `JID`, `jail_name`, `time_sentenced`
- `jails` = `JID`, `Name` (dropdown)
- `arrests` = `Date`, `officer_name`, `badge_no`
- `cases` = `IRID`, `Date`, `location`

**Clicking Update profile:**

Same form boxes as add. `UPDATE Criminal ... WHERE CID = ?`

Then show this page again.

---

## Search (civilian)

**Function:** `search_criminals`  
**When:** civilian clicks **Search**, or clicks **Search** on the filter form.

This page does **not** save anything. It only reads.

The filters come from:

```python
crime = request.args.get("crime") or ""
gender = request.args.get("gender") or ""
nationality = request.args.get("nationality") or ""
jail_id = request.args.get("jail_id") or ""
```

**SQL:** `SELECT` criminals (+ jail name). If a filter is not empty, add `AND Crime = ?` (same idea for the others).

Also load the dropdown lists: distinct crimes, distinct nationalities, all jails.

**Give the page:**

- `filters` = those four values (so the boxes stay filled)
- `crimes` = a list of crime names
- `nationalities` = a list of nationalities
- `jails` = `JID`, `Name`
- `results` = `CID`, `Name`, `Age`, `Crime`, `Gender`, `Nationality`, `jail_name`

---

## List of court cases (police)

**Function:** `proceedings`  
**When:** police click **Cases**.

**SQL:** list incident reports, and join `"Criminal cases"` to get the judge (it can be empty).

**Give the page:** `cases` = `IRID`, `Judge`, `Evidence`, `Date`, `location`, `AccusedName`, `criminal_count`

(`criminal_count` = how many people in `"Criminal involvement"` for that report.)

---

## One court case (police)

**Function:** `proceeding_detail`  
**When:** police click **Open** on a case.

The number in the URL is `irid`.

This page has **three** forms. Check which one was submitted:

```python
action = request.form.get("action")
```

**Opening the page:**

- the incident + judge + evidence
- criminals already linked
- officers already assigned
- full lists for the two dropdowns

**Give the page:**

- `case` = `IRID`, `Judge`, `Evidence`, `Date`, `Description`, `location`, `AccusedName`
- `criminals` = `CID`, `Name`, `Crime`
- `officers` = `UID`, `name`, `badge_no`
- `all_criminals` = `CID`, `Name`
- `all_officers` = `UID`, `name`

**If they click Save proceeding** (`action` is `update_case`):

- form: `Judge`, `Evidence`
- if this `IRID` is not in `"Criminal cases"` yet, `INSERT`; else `UPDATE`

**If they click Add under criminals** (`action` is `link_criminal`):

- form: `CID`
- `INSERT` into `"Criminal involvement"` (`CID`, this `irid`)

**If they click Add under officers** (`action` is `assign_officer`):

- form: `UID`
- `INSERT` into `Works_on` (`UID`, this `irid`)

After any save: `db.commit()` and show this page again.
