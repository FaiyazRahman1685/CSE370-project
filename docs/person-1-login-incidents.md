# Person 1 — Login, dashboards, incidents, analytics

**Features:** incident reports, analytics, plus login so the rest of the app can use `session`.

**File:** `app.py` — only the routes listed below. Use `get_db()`. Pass the named variables into `render_template(...)` so the sample data goes away.

**Session everyone else needs after login:** `uid`, `name`, `role` (`"police"` or `"user"`).

---

### `GET /` — `index`
- **Called from:** browser opens the site; logout redirects here.
- **Do:** if already logged in, send police to `/dashboard` and civilians to `/home`; else show login.
- **Expects:** `session`.
- **Renders:** `login.html` (via `login_page()`). Optional: `error`, `username`, `role`.

### `POST /login` — `login`
- **Called from:** `templates/login.html` form (`username`, `password`, `role`).
- **Do:** look up `USER` by `name` + `password`. If `role=police`, the UID must also be in `POLICE`. If `role=user`, it must **not** be in `POLICE`. Set session, then redirect.
- **Expects:** form `username`, `password`, `role`.
- **On fail:** `login_page(error=..., username=..., role=...)`.
- **On success:** police → `dashboard`, civilian → `user_dashboard`.

### `GET /logout` — `logout`
- **Called from:** Sign out in `templates/app.html`.
- **Do:** `session.clear()`, redirect to `index`.

---

### `GET /dashboard` — `dashboard` (police)
- **Called from:** nav “Dashboard”; login redirect; logo (police).
- **Do:** counts + last few incidents + last few criminals.
- **Pass:**
  - `stats`: `officers`, `incidents`, `criminals`, `jails`
  - `incidents`: `IRID`, `Date`, `location`, `AccusedName`
  - `criminals`: `CID`, `Name`, `Crime`, `Age`

### `GET /home` — `user_dashboard` (civilian)
- **Called from:** nav “Home”; login redirect; logo (civilian).
- **Do:** this user’s incident reports (`ReportedUID = session["uid"]`).
- **Pass:** `reports`: `IRID`, `Date`, `location`, `AccusedName`

---

### `GET /incidents` — `incidents` (police)
- **Called from:** nav “Incidents”; dashboard card.
- **Do:** list all `Incident Reports` (join reporter name + count of `Works_on`).
- **Pass:** `incidents`: `IRID`, `Date`, `location`, `AccusedName`, `reporter_name`, `officer_count`

### `GET|POST /incidents/<irid>` — `incident_detail` (police)
- **Called from:** “Open” on the incidents table. POST form on the same page. “Open legal proceeding” links to Person 2’s `/proceedings/<irid>`.
- **GET:** one report + victims (`Targeted`) + assigned officers (`Works_on`).
- **POST:** insert `Works_on (UID, IRID)` from form `UID`.
- **Pass:**
  - `incident`: `IRID`, `Date`, `Description`, `location`, `AccusedName`, `reporter_name`
  - `victims`: `UID`, `name`
  - `officers`: `UID`, `name`, `badge_no`
  - `all_officers`: `UID`, `name` (dropdown)

### `GET|POST /report` — `report_incident` (civilian)
- **Called from:** nav “Report”; home card. Form POSTs here.
- **GET:** show the form (`report_incident.html`).
- **POST:** insert `Incident Reports` (`Date`, `incident_location` → `"Incident Location"`, `AccusedName`, `Description`, `ReportedUID=session["uid"]`). Redirect to `/home`.

---

### `GET /analytics` — `analytics` (police)
- **Called from:** nav “Analytics”; dashboard card.
- **Do:** `GROUP BY "Incident Location"` (hot zones) and group incidents by time of day (busy hours). `pct` = count / max count * 100.
- **Pass:**
  - `totals`: `incidents`, `locations`, `peak_label`
  - `hot_zones`: `location`, `count`, `pct`
  - `busy_hours`: `label`, `count`, `pct`
