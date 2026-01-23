"""
Leave Service - Handles leave request management
"""

import pandas as pd
import io
from db_utils import get_connection
from datetime import datetime
from typing import Tuple


class LeaveService:
    """Service for leave management operations"""

    @staticmethod
    def add_leave_request(student_name: str, class_no: str, division: str,
                         leave_from: datetime, leave_to: datetime) -> Tuple[bool, str]:
        """
        Add a new leave request.

        Args:
            student_name: Name of the student
            class_no: Student's class
            division: Student's division
            leave_from: Leave start datetime
            leave_to: Leave end datetime

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not student_name:
            return False, "Please select a student"

        if leave_to <= leave_from:
            return False, "End date/time must be after start date/time"

        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                INSERT INTO leave_records
                (student_name, class, division, leave_from, leave_to)
                VALUES (?, ?, ?, ?, ?)
            """, (
                student_name,
                class_no,
                division,
                leave_from.isoformat(),
                leave_to.isoformat()
            ))
            conn.commit()
            conn.close()
            return True, "Leave request submitted successfully"
        except Exception as e:
            return False, f"Error: {str(e)}"

    @staticmethod
    def get_all_leave_records() -> pd.DataFrame:
        """Get all leave records"""
        try:
            conn = get_connection()
            df = pd.read_sql("SELECT * FROM leave_records", conn)
            conn.close()
            return df
        except Exception as e:
            print(f"Error fetching leave records: {e}")
            return pd.DataFrame()

    @staticmethod
    def filter_leave_records(class_no: str = None, division: str = None,
                            student_name: str = None) -> pd.DataFrame:
        """
        Filter leave records by class, division, and/or student name.

        Args:
            class_no: Class to filter by (None for all)
            division: Division to filter by (None for all)
            student_name: Student name to filter by (None for all)

        Returns:
            Filtered DataFrame
        """
        try:
            conn = get_connection()
            df = pd.read_sql("SELECT * FROM leave_records", conn)
            conn.close()

            if not df.empty:
                if class_no and class_no != "All":
                    df = df[df["class"] == class_no]

                if division and division != "All":
                    df = df[df["division"] == division]

                if student_name and student_name != "All":
                    df = df[df["student_name"] == student_name]

            return df
        except Exception as e:
            print(f"Error filtering leave records: {e}")
            return pd.DataFrame()

    @staticmethod
    def get_classes_with_leaves() -> list:
        """Get all unique classes with leave records"""
        try:
            conn = get_connection()
            df = pd.read_sql("SELECT * FROM leave_records", conn)
            conn.close()

            if df.empty:
                return []

            return sorted(df["class"].unique().tolist())
        except Exception as e:
            print(f"Error fetching classes: {e}")
            return []

    @staticmethod
    def get_divisions_for_class(class_no: str) -> list:
        """Get divisions for a specific class with leave records"""
        try:
            conn = get_connection()
            df = pd.read_sql("SELECT * FROM leave_records WHERE class = ?", (class_no,), conn)
            conn.close()

            if df.empty:
                return []

            return sorted(df["division"].unique().tolist())
        except Exception as e:
            print(f"Error fetching divisions: {e}")
            return []

    @staticmethod
    def get_students_for_class_division(class_no: str, division: str) -> list:
        """Get students for a specific class and division with leave records"""
        try:
            conn = get_connection()
            df = pd.read_sql(
                "SELECT * FROM leave_records WHERE class = ? AND division = ?",
                (class_no, division),
                conn
            )
            conn.close()

            if df.empty:
                return []

            return sorted(df["student_name"].unique().tolist())
        except Exception as e:
            print(f"Error fetching students: {e}")
            return []

    @staticmethod
    def export_to_excel(df: pd.DataFrame) -> bytes:
        """
        Export DataFrame to Excel format.

        Args:
            df: DataFrame to export

        Returns:
            Excel file bytes
        """
        try:
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="Leave Report")
            return output.getvalue()
        except Exception as e:
            print(f"Error exporting to Excel: {e}")
            return b""
