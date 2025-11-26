import sqlite3
import os

USERS_DB = "users.db"


def setup_users_database():
    """Create the users database"""
    conn = sqlite3.connect(USERS_DB)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()
    print(f"Users database '{USERS_DB}' created successfully!")


def setup_media_database(username):
    """Create a media database for a specific user"""
    db_name = f"media_library_{username}.db"
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Media (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        media_type TEXT NOT NULL,
        genre TEXT,
        release_date TEXT,
        director TEXT,
        description TEXT,
        rating REAL,
        status TEXT DEFAULT 'To Read',
        image_path TEXT,
        date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()
    print(f"Media database '{db_name}' created for user '{username}'!")


if __name__ == "__main__":
    setup_users_database()
    print("Setup complete! Run main.py to start the application.")