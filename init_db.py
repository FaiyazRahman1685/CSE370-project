import sqlite3

DB_PATH = "database.db"

SCHEMA = """
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS "Criminal involvement";
DROP TABLE IF EXISTS "Criminal cases";
DROP TABLE IF EXISTS "Arrested by";
DROP TABLE IF EXISTS Works_on;
DROP TABLE IF EXISTS Targeted;
DROP TABLE IF EXISTS Jailor;
DROP TABLE IF EXISTS Criminal;
DROP TABLE IF EXISTS "Incident Reports";
DROP TABLE IF EXISTS Victim;
DROP TABLE IF EXISTS POLICE;
DROP TABLE IF EXISTS Jail;
DROP TABLE IF EXISTS USER;
DROP TABLE IF EXISTS users;

CREATE TABLE USER (
    UID INTEGER PRIMARY KEY,
    phone TEXT,
    age INTEGER,
    gender TEXT,
    role TEXT,
    name TEXT NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE Jail (
    JID INTEGER PRIMARY KEY,
    Name TEXT NOT NULL,
    Location TEXT,
    Capacity INTEGER
);

CREATE TABLE POLICE (
    UID INTEGER PRIMARY KEY,
    badge_no TEXT UNIQUE,
    patrol_area TEXT,
    number_of_arrests INTEGER DEFAULT 0,
    department TEXT,
    rank TEXT,
    supervisor INTEGER,
    issupervisor boolean DEFAULT FALSE,
    FOREIGN KEY (UID) REFERENCES USER(UID),
    FOREIGN KEY (supervisor) REFERENCES POLICE(UID)
);

CREATE TABLE "Incident Reports" (
    IRID INTEGER PRIMARY KEY,
    Date TEXT,
    Description TEXT,
    incident_location TEXT,
    AccusedName TEXT,
    ReportedUID INTEGER,
    FOREIGN KEY (ReportedUID) REFERENCES USER(UID)
);

CREATE TABLE Criminal (
    CID INTEGER PRIMARY KEY,
    Name TEXT NOT NULL,
    Age INTEGER,
    Crime TEXT,
    Height REAL,
    Gender TEXT,
    Nationality TEXT,
    JID INTEGER,
    time_sentenced TEXT,
    FOREIGN KEY (JID) REFERENCES Jail(JID)
);

CREATE TABLE Jailor (
    UID INTEGER NOT NULL,
    JID INTEGER NOT NULL,
    PRIMARY KEY (UID, JID),
    FOREIGN KEY (UID) REFERENCES POLICE(UID),
    FOREIGN KEY (JID) REFERENCES Jail(JID)
);

CREATE TABLE Victim (
    UID INTEGER PRIMARY KEY,
    FOREIGN KEY (UID) REFERENCES USER(UID)
);

CREATE TABLE Targeted (
    UID INTEGER NOT NULL,
    IRID INTEGER NOT NULL,
    PRIMARY KEY (UID, IRID),
    FOREIGN KEY (UID) REFERENCES Victim(UID),
    FOREIGN KEY (IRID) REFERENCES "Incident Reports"(IRID)
);

CREATE TABLE Works_on (
    UID INTEGER NOT NULL,
    IRID INTEGER NOT NULL,
    PRIMARY KEY (UID, IRID),
    FOREIGN KEY (UID) REFERENCES POLICE(UID),
    FOREIGN KEY (IRID) REFERENCES "Incident Reports"(IRID)
);

CREATE TABLE "Arrested by" (
    UID INTEGER NOT NULL,
    CID INTEGER NOT NULL,
    Date TEXT,
    PRIMARY KEY (UID, CID),
    FOREIGN KEY (UID) REFERENCES POLICE(UID),
    FOREIGN KEY (CID) REFERENCES Criminal(CID)
);

CREATE TABLE "Criminal cases" (
    Judge TEXT,
    Evidence TEXT,
    IRID INTEGER PRIMARY KEY,
    FOREIGN KEY (IRID) REFERENCES "Incident Reports"(IRID)
);

CREATE TABLE "Criminal involvement" (
    CID INTEGER NOT NULL,
    IRID INTEGER NOT NULL,
    PRIMARY KEY (CID, IRID),
    FOREIGN KEY (CID) REFERENCES Criminal(CID),
    FOREIGN KEY (IRID) REFERENCES "Incident Reports"(IRID)
);
"""


SEED = """
INSERT INTO USER (UID, phone, age, gender, role, name, password) VALUES
    (1, '01700000001', 34, 'M', 'police', 'rahman', 'police123'),
    (2, '01700000002', 28, 'F', 'user', 'fatima', 'user123');

INSERT INTO POLICE (UID, badge_no, patrol_area, number_of_arrests, department, rank)
VALUES (1, 'BD-1042', 'Gulshan', 12, 'Investigation', 'Inspector');

INSERT INTO Victim (UID) VALUES (2);
"""


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    conn.executescript(SEED)
    conn.commit()
    conn.close()
    print(f"Initialized database at {DB_PATH}")
    print("Demo accounts: rahman / police123 (police), fatima / user123 (civilian)")


if __name__ == "__main__":
    init_db()
