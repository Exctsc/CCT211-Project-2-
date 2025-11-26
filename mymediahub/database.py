import sqlite3
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class Media:
    """Represents a single media item"""
    id: Optional[int] = None
    title: str = ""
    media_type: str = ""
    genre: str = ""
    release_date: str = ""
    director: str = ""
    description: str = ""
    rating: Optional[float] = None
    status: str = "To Read"
    image_path: str = ""
    date_added: str = ""


class DatabaseModel:
    """Handles all database operations for media items"""

    def __init__(self, db_name):
        """Initialize database connection"""
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        """Connect to the database"""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            raise Exception(f"Database connection error: {e}")

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def get_all_records(self) -> List[Media]:
        """Retrieve all media items from database"""
        try:
            self.cursor.execute("SELECT * FROM Media ORDER BY date_added DESC")
            rows = self.cursor.fetchall()
            return [self._row_to_media(row) for row in rows]
        except sqlite3.Error as e:
            raise Exception(f"Error retrieving records: {e}")

    def get_record(self, media_id: int) -> Optional[Media]:
        """Retrieve a specific media item by ID"""
        try:
            self.cursor.execute("SELECT * FROM Media WHERE id = ?", (media_id,))
            row = self.cursor.fetchone()
            return self._row_to_media(row) if row else None
        except sqlite3.Error as e:
            raise Exception(f"Error retrieving record: {e}")

    def search_by_title(self, title: str) -> List[Media]:
        """Search media items by title (case-insensitive)"""
        try:
            self.cursor.execute(
                "SELECT * FROM Media WHERE title LIKE ? ORDER BY title ASC",
                (f"%{title}%",)
            )
            rows = self.cursor.fetchall()
            return [self._row_to_media(row) for row in rows]
        except sqlite3.Error as e:
            raise Exception(f"Error searching: {e}")

    def filter_by_type(self, media_type: str) -> List[Media]:
        """Filter media items by type"""
        try:
            self.cursor.execute(
                "SELECT * FROM Media WHERE media_type = ? ORDER BY title ASC",
                (media_type,)
            )
            rows = self.cursor.fetchall()
            return [self._row_to_media(row) for row in rows]
        except sqlite3.Error as e:
            raise Exception(f"Error filtering: {e}")

    def filter_by_status(self, status: str) -> List[Media]:
        """Filter media items by status"""
        try:
            self.cursor.execute(
                "SELECT * FROM Media WHERE status = ? ORDER BY title ASC",
                (status,)
            )
            rows = self.cursor.fetchall()
            return [self._row_to_media(row) for row in rows]
        except sqlite3.Error as e:
            raise Exception(f"Error filtering: {e}")

    def create_record(self, media: Media) -> int:
        """Insert a new media item into the database"""
        try:
            self.cursor.execute("""
                INSERT INTO Media (title, media_type, genre, release_date, director, 
                                 description, rating, status, image_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                media.title, media.media_type, media.genre, media.release_date,
                media.director, media.description, media.rating, media.status, media.image_path
            ))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            raise Exception(f"Error creating record: {e}")

    def update_record(self, media: Media) -> bool:
        """Update an existing media item"""
        try:
            self.cursor.execute("""
                UPDATE Media SET title=?, media_type=?, genre=?, release_date=?, 
                director=?, description=?, rating=?, status=?, image_path=?
                WHERE id=?
            """, (
                media.title, media.media_type, media.genre, media.release_date,
                media.director, media.description, media.rating, media.status,
                media.image_path, media.id
            ))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            raise Exception(f"Error updating record: {e}")

    def delete_record(self, media_id: int) -> bool:
        """Delete a media item from the database"""
        try:
            self.cursor.execute("DELETE FROM Media WHERE id = ?", (media_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            raise Exception(f"Error deleting record: {e}")

    def get_statistics(self) -> dict:
        """Get statistics about the media library"""
        try:
            stats = {}

            self.cursor.execute("SELECT COUNT(*) FROM Media")
            stats['total_items'] = self.cursor.fetchone()[0]

            self.cursor.execute("SELECT DISTINCT media_type FROM Media")
            types = self.cursor.fetchall()
            stats['type_breakdown'] = {}
            for type_row in types:
                media_type = type_row[0]
                self.cursor.execute("SELECT COUNT(*) FROM Media WHERE media_type = ?", (media_type,))
                count = self.cursor.fetchone()[0]
                stats['type_breakdown'][media_type] = count

            self.cursor.execute("SELECT DISTINCT status FROM Media")
            statuses = self.cursor.fetchall()
            stats['status_breakdown'] = {}
            for status_row in statuses:
                status = status_row[0]
                self.cursor.execute("SELECT COUNT(*) FROM Media WHERE status = ?", (status,))
                count = self.cursor.fetchone()[0]
                stats['status_breakdown'][status] = count

            self.cursor.execute("SELECT AVG(rating) FROM Media WHERE rating IS NOT NULL")
            avg_rating = self.cursor.fetchone()[0]
            stats['average_rating'] = round(avg_rating, 1) if avg_rating else 0

            return stats
        except sqlite3.Error as e:
            raise Exception(f"Error getting statistics: {e}")

    def _row_to_media(self, row) -> Media:
        """Convert a database row to a Media object"""
        if row is None:
            return None
        return Media(
            id=row['id'],
            title=row['title'],
            media_type=row['media_type'],
            genre=row['genre'],
            release_date=row['release_date'],
            director=row['director'],
            description=row['description'],
            rating=row['rating'],
            status=row['status'],
            image_path=row['image_path'],
            date_added=row['date_added']
        )


class UserManager:
    """Handles user management"""

    def __init__(self):
        """Initialize user manager"""
        self.db_name = "users.db"
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        """Connect to users database"""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            raise Exception(f"User database connection error: {e}")

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def get_all_users(self) -> List[str]:
        """Get list of all usernames"""
        try:
            self.cursor.execute("SELECT username FROM Users ORDER BY username ASC")
            return [row[0] for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            raise Exception(f"Error retrieving users: {e}")

    def create_user(self, username: str) -> bool:
        """Create a new user"""
        try:
            self.cursor.execute("INSERT INTO Users (username) VALUES (?)", (username,))
            self.conn.commit()

            from setup_database import setup_media_database
            setup_media_database(username)

            return True
        except sqlite3.IntegrityError:
            return False
        except sqlite3.Error as e:
            raise Exception(f"Error creating user: {e}")