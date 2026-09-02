"""Rebuild database.db with the same demo rows as init_db.py.

    python seed_demo.py
    python init_db.py

Either command resets the database. Stop the Flask app first if Windows
reports that the file is locked.
"""

from init_db import init_db

if __name__ == "__main__":
    init_db()
