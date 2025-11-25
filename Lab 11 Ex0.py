import sqlite3

# Connect to database
conn = sqlite3.connect("python_db.db")
cur = conn.cursor()
"""If the file doesn't exist, SQLite will create a new empty database file."""
"""Return values to connection (conn)"""
"""Cursor: Execute SQL/Retrieve Query Results"""

# Create Hospital Table
cur.execute("""
CREATE TABLE IF NOT EXISTS Hospital (
    Hospital_Id INTEGER PRIMARY KEY,
    Hospital_Name TEXT NOT NULL,
    Bed_Count INTEGER
);
""")
""" cur.execute: Send a multi-line string as an SQL statement to SQLite for execution."""
""" PRIMARY KEY: Only one in a table/Can not be empty"""
""" NOT NULL: Not empty"""

# Create Doctor Table
cur.execute("""
CREATE TABLE IF NOT EXISTS Doctor (
    Doctor_Id INTEGER PRIMARY KEY,
    Doctor_Name TEXT NOT NULL,
    Hospital_Id INTEGER NOT NULL,
    Joining_Date TEXT NOT NULL,
    Speciality TEXT,
    Salary INTEGER,
    Experience INTEGER,
    FOREIGN KEY (Hospital_Id) REFERENCES Hospital(Hospital_Id)
);
""")
"""FOREIGN KEY: Link two tables' same Hospital_ID """

# Clean Old Data
cur.execute("DELETE FROM Doctor;")
cur.execute("DELETE FROM Hospital;")
"""Clear the old data in the table to prevent primary key conflicts when you run the script multiple times. """
"""First delete the child table (Doctor), then delete the parent table (Hospital)."""

# Insert Hospital Data
cur.executemany("""
INSERT INTO Hospital (Hospital_Id, Hospital_Name, Bed_Count)
VALUES (?, ?, ?);
""", [
    (1, "Toronto General Hospital", 471),
    (2, "St. Joseph's Health Centre", 376),
    (3, "Mississauga Hospital", 751),
    (4, "Credit Valley Hospital", 382)
])

# Insert Doctor Data
cur.executemany("""
INSERT INTO Doctor
(Doctor_Id, Doctor_Name, Hospital_Id, Joining_Date, Speciality, Salary, Experience)
VALUES (?, ?, ?, ?, ?, ?, ?);
""", [
    (101, "Duemler", 1, "2005-02-10", "Pediatric", 140000, None),
    (102, "McBroom", 1, "2018-07-23", "Oncologist", 120000, None),
    (103, "El-Ashry", 2, "2016-05-19", "Surgeon", 125000, None),
    (104, "Chan", 2, "2017-12-28", "Pediatric", 128000, None),
    (105, "Platonov", 3, "2004-06-04", "Psychiatrist", 142000, None),
    (106, "Izukaw", 3, "2012-09-11", "Dermatologist", 130000, None),
    (107, "Jhas", 4, "2014-08-21", "Obstetrician/Gynecologist", 132000, None),
    (108, "Marmor", 4, "2011-10-17", "Radiologist", 130000, None)
])

conn.commit() # Save all changes
conn.close()

print("Exercise 0 completed: database, tables, and sample data created.")
