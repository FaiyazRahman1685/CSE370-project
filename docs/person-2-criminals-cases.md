# Person 2 — Criminals, public search, legal proceedings

**Features:** manage criminal profiles, public criminal search by category, legal proceedings for a case.

**File:** `app.py` — only the routes listed below. Use `get_db()`. Pass the named variables into `render_template(...)` so the sample data goes away.

**Needs from Person 1:** `session["uid"]` and `session["role"]` after login. Police-only routes should bounce civilians to `/home`.

---

### `GET|POST /criminals` — `criminals` (police)
- **Called from:** nav “Criminals”; dashboard card. Add-profile form POSTs here. Rows link to `/criminals/<cid>`.
- **GET:** list `Criminal` joined to `Jail.Name` as `jail_name`. Also load jails for the dropdown.
- **POST:** insert `Criminal` from form: `Name`, `Age`, `Height`, `Crime`, `Gender`, `Nationality`, `JID`, `time_sentenced` (column `"Time sentenced"`). Redirect back to `/criminals`.
- **Pass:**
  - `criminals`: `CID`, `Name`, `Age`, `Crime`, `Gender`, `Nationality`, `jail_name`, `time_sentenced`
  - `jails`: `JID`, `Name`

### `GET|POST /criminals/<cid>` — `criminal_detail` (police)
- **Called from:** “Open” on the criminals table; inmate name on Person 3’s jail page; involved-criminal name on a proceeding.
- **GET:** one `Criminal` + `Arrested by` (officer name, badge, date) + `Criminal involvement` (linked incidents).
- **POST:** update that `Criminal` from form: `Name`, `Age`, `Height`, `Crime`, `Gender`, `Nationality`, `time_sentenced`, `JID`.
- **Pass:**
  - `criminal`: `CID`, `Name`, `Age`, `Crime`, `Height`, `Gender`, `Nationality`, `JID`, `jail_name`, `time_sentenced`
  - `jails`: `JID`, `Name`
  - `arrests`: `Date`, `officer_name`, `badge_no`
  - `cases`: `IRID`, `Date`, `location`

---

### `GET /search` — `search_criminals` (civilian)
- **Called from:** nav “Search”; home card. Filter form is GET to this same URL.
- **Do:** `SELECT` from `Criminal` (+ jail name). Apply optional filters from query string. Distinct crime/nationality/jail lists for the dropdowns.
- **Expects (query):** `crime`, `gender`, `nationality`, `jail_id` (all optional).
- **Pass:**
  - `filters`: echo those four values
  - `crimes`: list of crime strings
  - `nationalities`: list of strings
  - `jails`: `JID`, `Name`
  - `results`: `CID`, `Name`, `Age`, `Crime`, `Gender`, `Nationality`, `jail_name`

---

### `GET /proceedings` — `proceedings` (police)
- **Called from:** nav “Cases”; dashboard card. Rows link to `/proceedings/<irid>`.
- **Do:** list incidents left-joined to `"Criminal cases"` (judge may be null).
- **Pass:** `cases`: `IRID`, `Judge`, `Evidence`, `Date`, `location`, `AccusedName`, `criminal_count`

### `GET|POST /proceedings/<irid>` — `proceeding_detail` (police)
- **Called from:** “Open” on the cases table; “Open legal proceeding” on Person 1’s incident page; linked IRID on a criminal profile.
- **GET:** incident + `"Criminal cases"` row + involved criminals + assigned officers. Also full lists for the two dropdowns.
- **POST:** check form `action`:
  - `update_case` — upsert `"Criminal cases"` (`Judge`, `Evidence`) for this `IRID`
  - `link_criminal` — insert `"Criminal involvement" (CID, IRID)` from form `CID`
  - `assign_officer` — insert `Works_on (UID, IRID)` from form `UID`
- **Pass:**
  - `case`: `IRID`, `Judge`, `Evidence`, `Date`, `Description`, `location`, `AccusedName`
  - `criminals`: `CID`, `Name`, `Crime`
  - `officers`: `UID`, `name`, `badge_no`
  - `all_criminals`: `CID`, `Name`
  - `all_officers`: `UID`, `name`
