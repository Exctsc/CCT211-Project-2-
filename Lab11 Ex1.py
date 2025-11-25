# ==== Exercise 1 =====
import sqlite3

# 1. Connect Database
conn = sqlite3.connect("python_db.db")
cursor = conn.cursor()

# 2. Search: Sort by specialty + doctor name
cursor.execute("""
    SELECT Speciality, Doctor_Name
    FROM Doctor
    ORDER BY Speciality ASC, Doctor_Name ASC;
""")

rows = cursor.fetchall() # Retrieve all remaining rows from this query

current_speciality = None
""" Initializing it to None means: No departments have been printed yet, so the current specialty is empty.
We will use it later to determine: If we find that the specialty in this line is different from current_speciality → it means this is a new department → the department name needs to be printed first."""

# 3. Iterate through the results and output them in groups by specialty.
for spec, name in rows:
    # The .strip() function removes leading and trailing whitespace from a string.
    spec = spec.strip()

    # If you encounter a new specialty, print the department title first.
    if spec != current_speciality:
        print(spec)                # e.g. Pediatric
        current_speciality = spec

    # Choose a last name: Doctor_Name could be "El-Ashry" or "Mc Broom", etc.
    lastname = name.strip().split()[-1] # .split(): it splits the string into several segments by spaces and returns a list.
    # [-1]: choose the last element from list
    print("  Dr. " + lastname)

conn.close()