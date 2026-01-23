"""
Student Service - Handles student management operations
"""

import os
from db_utils import get_connection
from typing import List, Optional, Tuple


class StudentService:
    """Service for student management operations"""

    STUDENT_IMAGES_DIR = "student_images"

    def __init__(self):
        os.makedirs(self.STUDENT_IMAGES_DIR, exist_ok=True)

    @staticmethod
    def add_student(name: str, class_no: str, division: str, image_path: str) -> Tuple[bool, str]:
        """
        Add a new student to the system.

        Args:
            name: Student's name
            class_no: Student's class
            division: Student's division
            image_path: Path to student's image

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not name or not image_path:
            return False, "Please fill all fields and upload image"

        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute(
                "INSERT INTO students (name, class, division, image_path) VALUES (?, ?, ?, ?)",
                (name, class_no, division, image_path)
            )
            conn.commit()
            conn.close()
            return True, "Student added successfully"
        except Exception as e:
            return False, f"Error: {str(e)}"

    @staticmethod
    def save_student_image(name: str, image_file) -> str:
        """
        Save student image file to disk.

        Args:
            name: Student's name
            image_file: Uploaded image file object

        Returns:
            Path to saved image
        """
        safe_name = name.replace(" ", "_")
        folder = f"student_images/{safe_name}"
        os.makedirs(folder, exist_ok=True)
        image_path = f"{folder}/{image_file.name}"

        with open(image_path, "wb") as f:
            f.write(image_file.getbuffer())

        return image_path

    @staticmethod
    def get_all_students():
        """Get all students from the database"""
        try:
            conn = get_connection()
            students = conn.execute(
                "SELECT id, name, class, division, image_path FROM students ORDER BY name"
            ).fetchall()
            conn.close()
            return students
        except Exception as e:
            print(f"Error fetching students: {e}")
            return []

    @staticmethod
    def get_students_by_class_division(class_no: str, division: str) -> List:
        """Get students filtered by class and division"""
        try:
            conn = get_connection()
            students = conn.execute(
                "SELECT id, name FROM students WHERE class=? AND division=? ORDER BY name",
                (class_no, division)
            ).fetchall()
            conn.close()
            return students
        except Exception as e:
            print(f"Error fetching students: {e}")
            return []

    @staticmethod
    def get_class_divisions() -> List:
        """Get all unique class-division combinations"""
        try:
            conn = get_connection()
            students = conn.execute(
                "SELECT DISTINCT class, division FROM students ORDER BY class, division"
            ).fetchall()
            conn.close()
            return students
        except Exception as e:
            print(f"Error fetching class divisions: {e}")
            return []

    @staticmethod
    def get_classes() -> List:
        """Get all unique classes"""
        try:
            conn = get_connection()
            classes = sorted([c[0] for c in conn.execute(
                "SELECT DISTINCT class FROM students"
            ).fetchall()])
            conn.close()
            return classes
        except Exception as e:
            print(f"Error fetching classes: {e}")
            return []

    @staticmethod
    def get_divisions_for_class(class_no: str) -> List:
        """Get divisions for a specific class"""
        try:
            conn = get_connection()
            divisions = sorted([d[0] for d in conn.execute(
                "SELECT DISTINCT division FROM students WHERE class=?",
                (class_no,)
            ).fetchall()])
            conn.close()
            return divisions
        except Exception as e:
            print(f"Error fetching divisions: {e}")
            return []
