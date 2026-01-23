"""
Authentication Service - Handles user authentication and authorization
"""

from db_utils import get_connection
from typing import Optional, Tuple


class AuthService:
    """Service for user authentication operations"""

    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[str]:
        """
        Authenticate user credentials.

        Args:
            username: User's username
            password: User's password

        Returns:
            User role if successful, None otherwise
        """
        if not username or not password:
            return None

        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute(
                "SELECT role FROM users WHERE username=? AND password=?",
                (username, password)
            )
            result = c.fetchone()
            conn.close()

            return result[0] if result else None
        except Exception as e:
            print(f"Authentication error: {e}")
            return None

    @staticmethod
    def add_teacher(username: str, password: str) -> Tuple[bool, str]:
        """
        Add a new teacher to the system.

        Args:
            username: Teacher's username
            password: Teacher's password

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not username or not password:
            return False, "Please fill all fields"

        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (username, password, "teacher")
            )
            conn.commit()
            conn.close()
            return True, "Teacher added successfully"
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                return False, "Username already exists"
            return False, f"Error: {str(e)}"

    @staticmethod
    def get_all_teachers():
        """Get all teachers from the database"""
        try:
            conn = get_connection()
            teachers = conn.execute(
                "SELECT id, username FROM users WHERE role='teacher'"
            ).fetchall()
            conn.close()
            return teachers
        except Exception as e:
            print(f"Error fetching teachers: {e}")
            return []
