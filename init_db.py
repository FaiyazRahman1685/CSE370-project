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
    (1,  '01700000001', 34, 'M', 'police', 'rahman',  'police123'),
    (2,  '01700000002', 28, 'F', 'user',   'fatima',  'user123'),
    (3,  '01700000003', 31, 'F', 'police', 'ayesha',  'police123'),
    (4,  '01700000004', 46, 'M', 'police', 'kamal',   'police123'),
    (5,  '01700000005', 26, 'F', 'police', 'nadia',   'police123'),
    (6,  '01700000006', 38, 'M', 'police', 'farhan',  'police123'),
    (7,  '01700000007', 29, 'M', 'police', 'imran',   'police123'),
    (8,  '01700000008', 33, 'M', 'user',   'tanvir',  'user123'),
    (9,  '01700000009', 22, 'F', 'user',   'lamiya',  'user123'),
    (10, '01700000010', 41, 'M', 'user',   'rafi',    'user123');

INSERT INTO Jail (JID, Name, Location, Capacity) VALUES
    (1, 'Dhaka Central Jail',      'Keraniganj', 400),
    (2, 'Kashimpur Central Jail',  'Gazipur',    250),
    (3, 'Chittagong Central Jail', 'Chittagong', 180);

INSERT INTO POLICE (UID, badge_no, patrol_area, number_of_arrests, department, rank, supervisor, issupervisor) VALUES
    (1, 'BD-1042', 'Gulshan',     12, 'Investigation', 'Inspector',  NULL, 1),
    (4, 'BD-3301', 'Dhanmondi',    8, 'Traffic',       'Inspector',  NULL, 1);

INSERT INTO POLICE (UID, badge_no, patrol_area, number_of_arrests, department, rank, supervisor, issupervisor) VALUES
    (3, 'BD-2108', 'Motijheel',    5, 'Patrol',        'Sergeant',   1,    0),
    (5, 'BD-4412', 'Uttara',       3, 'Investigation', 'Constable',  1,    0),
    (6, 'BD-5520', 'Keraniganj',   2, 'Custody',       'Constable',  4,    0),
    (7, 'BD-6633', 'Mirpur',       1, 'Patrol',        'Constable',  1,    0);

INSERT INTO Victim (UID) VALUES (2), (8), (9), (10);

INSERT INTO "Incident Reports" (IRID, Date, Description, incident_location, AccusedName, ReportedUID) VALUES
    (1,  '2025-03-12', 'Wallet snatched near the circle; accused fled on a motorcycle.', 'Gulshan-2',  'Karim Uddin',      2),
    (2,  '2025-08-14', 'Online banking fraud reported by a customer at the branch.',     'Motijheel',  'Nabila Chowdhury', 2),
    (3,  '2026-01-20', 'Armed robbery at a convenience store after closing.',            'Dhanmondi',  'Faruk Hossain',    8),
    (4,  '2026-06-02', 'Street assault outside a restaurant; witnesses available.',      'Gulshan-2',  'Priya Sharma',     2),
    (5,  '2026-06-02', 'Drug possession during a traffic stop.',                         'Gulshan-2',  'Ahmed Hassan',     8),
    (6,  '2026-06-02', 'Break-in at a ground-floor apartment.',                          'Uttara',     'Omar Ali',         10),
    (7,  '2025-11-08', 'Counterfeit documents used to open an account.',                 'Mirpur',     'Chen Wei',         8),
    (8,  '2024-12-19', 'Port-area theft of cargo from a parked truck.',                  'Chittagong', 'Karim Uddin',      10),
    (9,  '2026-08-11', 'Pickpocketing on a crowded bus.',                                'Motijheel',  'Sadia Rahman',     9),
    (10, '2026-08-22', 'Dispute that turned into an assault; no court case yet.',        'Dhanmondi',  'Priya Sharma',     2);

INSERT INTO Criminal (CID, Name, Age, Crime, Height, Gender, Nationality, JID, time_sentenced) VALUES
    (1, 'Karim Uddin',       31, 'Theft',        170.0, 'M', 'Bangladeshi', 1, '5 years'),
    (2, 'Nabila Chowdhury',  27, 'Fraud',        162.0, 'F', 'Bangladeshi', 2, '3 years'),
    (3, 'Faruk Hossain',     42, 'Robbery',      178.0, 'M', 'Bangladeshi', 1, '8 years'),
    (4, 'Priya Sharma',      35, 'Assault',      165.0, 'F', 'Indian',      2, '2 years'),
    (5, 'Ahmed Hassan',      29, 'Drug offense', 175.0, 'M', 'Pakistani',   1, '4 years'),
    (6, 'Chen Wei',          38, 'Fraud',        172.0, 'M', 'Chinese',     2, '6 years'),
    (7, 'Sadia Rahman',      24, 'Theft',        160.0, 'F', 'Bangladeshi', 3, '1 year'),
    (8, 'Omar Ali',          45, 'Other',        180.0, 'M', 'Bangladeshi', 1, '10 years');

INSERT INTO Jailor (UID, JID) VALUES
    (6, 1),
    (3, 2),
    (5, 3);

INSERT INTO Targeted (UID, IRID) VALUES
    (10, 1),
    (9,  1),
    (2,  2),
    (8,  3),
    (9,  4),
    (10, 6),
    (9,  9),
    (2,  10);

INSERT INTO Works_on (UID, IRID) VALUES
    (1, 1), (3, 1),
    (1, 2), (5, 2),
    (3, 3), (1, 3),
    (1, 4), (7, 4),
    (5, 5), (1, 5),
    (6, 6), (1, 6),
    (4, 7), (3, 7),
    (1, 8), (6, 8),
    (7, 9), (3, 9),
    (7, 10), (3, 10);

INSERT INTO "Arrested by" (UID, CID, Date) VALUES
    (1, 1, '2025-03-15'),
    (3, 2, '2025-08-20'),
    (5, 3, '2026-01-22'),
    (7, 4, '2026-06-04'),
    (1, 5, '2026-06-03'),
    (4, 6, '2025-11-10'),
    (7, 7, '2026-08-12'),
    (6, 8, '2026-06-05');

INSERT INTO "Criminal cases" (Judge, Evidence, IRID) VALUES
    ('Justice Karim',   'CCTV footage and two eyewitness statements', 1),
    ('Justice Nasreen', 'Bank records and device seizure log',        2),
    ('Justice Habib',   'Narcotics lab report and bodycam stills',    5),
    ('Justice Karim',   'Shipping manifest and night-watch log',      8);

INSERT INTO "Criminal involvement" (CID, IRID) VALUES
    (1, 1),
    (1, 8),
    (2, 2),
    (3, 3),
    (4, 4),
    (4, 10),
    (5, 5),
    (6, 7),
    (7, 9),
    (8, 6);
"""


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    conn.executescript(SEED)
    conn.commit()
    conn.close()
    print(f"Initialized database at {DB_PATH}")
    print("Police  (police123): rahman, ayesha, kamal, nadia, farhan, imran")
    print("Civilian (user123):  fatima, tanvir, lamiya, rafi")
    print("Criminals are housed in jails, arrested by officers, and linked to incident reports.")


if __name__ == "__main__":
    init_db()
