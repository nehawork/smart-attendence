"""
Attendance Service - Handles attendance tracking and reporting
"""

import pandas as pd
from db_utils import get_connection
from datetime import date
from typing import List, Tuple


class AttendanceService:
    """Service for attendance operations"""

    @staticmethod
    def mark_attendance(student_id: int, class_no: str, division: str, status: str = "Present") -> Tuple[bool, str]:
        """
        Mark attendance for a single student.

        Args:
            student_id: ID of the student
            class_no: Student's class
            division: Student's division
            status: Attendance status (Present/Absent)

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            conn = get_connection()
            c = conn.cursor()
            today = str(date.today())
            c.execute("""
                INSERT INTO attendance (student_id, class, division, date, status)
                VALUES (?, ?, ?, ?, ?)
            """, (student_id, class_no, division, today, status))
            conn.commit()
            conn.close()
            return True, "Attendance marked"
        except Exception as e:
            return False, f"Error: {str(e)}"

    @staticmethod
    def mark_class_attendance(students: List[Tuple], class_no: str, division: str) -> Tuple[bool, int]:
        """
        Mark attendance for entire class.

        Args:
            students: List of (student_id, student_name) tuples
            class_no: Class number
            division: Division

        Returns:
            Tuple of (success: bool, count: int) - number of students marked
        """
        try:
            conn = get_connection()
            c = conn.cursor()
            today = str(date.today())

            for student_id, _ in students:
                c.execute("""
                    INSERT INTO attendance (student_id, class, division, date, status)
                    VALUES (?, ?, ?, ?, ?)
                """, (student_id, class_no, division, today, "Present"))

            conn.commit()
            conn.close()
            return True, len(students)
        except Exception as e:
            print(f"Error marking class attendance: {e}")
            return False, 0

    @staticmethod
    def get_attendance_records() -> pd.DataFrame:
        """Get all attendance records"""
        try:
            conn = get_connection()
            df = pd.read_sql("""
                SELECT a.date, s.class, s.division, s.name, a.status
                FROM attendance a
                JOIN students s ON a.student_id = s.id
                ORDER BY a.date DESC
            """, conn)
            conn.close()
            return df
        except Exception as e:
            print(f"Error fetching attendance records: {e}")
            return pd.DataFrame()

    @staticmethod
    def get_attendance_summary() -> pd.DataFrame:
        """Get attendance summary grouped by date and class"""
        try:
            conn = get_connection()
            df = pd.read_sql("""
                SELECT a.date, s.class, s.division, s.name, a.status
                FROM attendance a
                JOIN students s ON a.student_id = s.id
                ORDER BY a.date DESC
            """, conn)
            conn.close()

            if df.empty:
                return df

            # Create class-division column
            df["Class & Division"] = df["class"] + " - " + df["division"]

            # Aggregate summary
            summary = df.groupby(["date", "Class & Division"])["status"].value_counts().unstack(fill_value=0).reset_index()
            if "Present" not in summary.columns:
                summary["Present"] = 0
            if "Absent" not in summary.columns:
                summary["Absent"] = 0

            return summary
        except Exception as e:
            print(f"Error creating attendance summary: {e}")
            return pd.DataFrame()

    @staticmethod
    def get_attendance_detail(date_str: str, class_div: str) -> pd.DataFrame:
        """Get detailed attendance for specific date and class"""
        try:
            class_no, division = class_div.split(" - ")
            conn = get_connection()
            df = pd.read_sql("""
                SELECT s.name, a.status
                FROM attendance a
                JOIN students s ON a.student_id = s.id
                WHERE a.date = ? AND a.class = ? AND a.division = ?
                ORDER BY s.name
            """, (date_str, class_no, division), conn)
            conn.close()
            return df
        except Exception as e:
            print(f"Error fetching attendance detail: {e}")
            return pd.DataFrame()

    @staticmethod
    def filter_attendance(class_no: str = None, date_str: str = None) -> pd.DataFrame:
        """Filter attendance records by class and/or date"""
        try:
            conn = get_connection()
            df = pd.read_sql(
                "SELECT * FROM attendance ORDER BY date DESC",
                conn
            )
            conn.close()

            if class_no and class_no != "All":
                df = df[df["class"] == class_no]

            if date_str and date_str != "All":
                df = df[df["date"] == date_str]

            return df
        except Exception as e:
            print(f"Error filtering attendance: {e}")
            return pd.DataFrame()
