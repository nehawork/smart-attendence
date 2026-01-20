import sqlite3

DB_NAME = "attendance.db"

def get_connection():
    """
    Returns a SQLite connection with WAL mode enabled
    to prevent database locked errors in Streamlit apps.
    """
    conn = sqlite3.connect(DB_NAME, check_same_thread=False, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn
