# Person 3 — Jails, police profiles, victim cases

**Features:** jail management, public jail info, manage/view police profiles (supervisor), provide criminal cases (victim).

**File:** `app.py` — only the routes listed below. Use `get_db()`. Pass the named variables into `render_template(...)` so the sample data goes away.

**Needs from Person 1:** `session["uid"]` and `session["role"]` after login.

**Cross-links:** inmate names go to Person 2’s `/criminals/<cid>`. Do not implement that route.

---

### `GET|POST /jails` — `jails` (police)
- **Called from:** nav “Jails”; dashboard card. Add-jail form POSTs here. “Manage” goes to `/jails/<jid>`.
- **GET:** all `Jail` rows + occupancy (`COUNT` of `Criminal` with that `JID`) + jailor count.
- **POST:** insert `Jail` from form: `Name`, `Location`, `Capacity`. Redirect to `/jails`.
- **Pass:** `jails`: `JID`, `Name`, `Location`, `Capacity`, `occupancy`, `jailor_count`

### `GET|POST /jails/<jid>` — `jail_detail` (police)
- **Called from:** “Manage” on the jails list.
- **GET:** one jail + inmates + current jailors + officer list for the assign dropdown.
- **POST:** check form `action`:
  - `update_jail` — update `Name`, `Location`, `Capacity`
  - `assign_jailor` — insert `Jailor (UID, JID)` from form `UID`
- **Pass:**
  - `jail`: `JID`, `Name`, `Location`, `Capacity`, `occupancy`
  - `inmates`: `CID`, `Name`, `Crime`, `time_sentenced`
  - `jailors`: `UID`, `name`, `badge_no`, `rank`
  - `officers`: `UID`, `name`

---

### `GET /jail-info` — `jail_info` (civilian)
- **Called from:** nav “Jail info”; home card. “Facility details” goes to `/jail-info/<jid>`.
- **Do:** same occupancy numbers as `/jails`, but public (no add/edit).
- **Pass:** `jails`: `JID`, `Name`, `Location`, `Capacity`, `occupancy`

### `GET /jail-info/<jid>` — `jail_info_detail` (civilian)
- **Called from:** “Facility details” on jail info.
- **Do:** one jail + public inmate list (name, crime, age only).
- **Pass:**
  - `jail`: `JID`, `Name`, `Location`, `Capacity`, `occupancy`
  - `inmates`: `Name`, `Crime`, `Age`

---

### `GET /officers` — `officers` (police)
- **Called from:** nav “Officers”; dashboard card. “View” goes to `/officers/<uid>`.
- **Do:** `POLICE` joined to `USER`, plus supervisor’s name.
- **Pass:** `officers`: `UID`, `name`, `badge_no`, `rank`, `department`, `patrol_area`, `arrests`, `supervisor_name`

### `GET|POST /officers/<uid>` — `officer_detail` (police / supervisor)
- **Called from:** “View” on the officers table; a team-member name on this same page.
- **GET:** one officer (USER + POLICE) + people they supervise + list of possible supervisors.
- **POST:** update `USER` (`name`, `phone`) and `POLICE` (`badge_no` → `"Badge No"`, `rank`, `department`, `patrol_area` → `"patrol area"`, `arrests` → `"number of arrests"`, `supervisor`).
- **Pass:**
  - `officer`: `UID`, `name`, `phone`, `age`, `gender`, `badge_no`, `patrol_area`, `arrests`, `department`, `rank`, `supervisor`
  - `supervisors`: `UID`, `name`
  - `team`: `UID`, `name`, `badge_no`, `rank`

---

### `GET|POST /my-cases` — `victim_cases` (civilian)
- **Called from:** nav “My cases”; home card. New-case form POSTs here.
- **GET:** incidents this user is a victim of (`Targeted` where `UID = session["uid"]`), joined to `"Criminal cases"` for judge/evidence.
- **POST:** insert `Incident Reports` (`Date`, `incident_location` → `"Incident Location"`, `AccusedName`, `Description`, `ReportedUID=session["uid"]`), insert `Victim` if needed, insert `Targeted`, and if `Evidence` is filled insert `"Criminal cases"` (`Judge` can be null). Redirect to `/my-cases`.
- **Pass:** `cases`: `IRID`, `Date`, `location`, `AccusedName`, `Judge`, `Evidence`
