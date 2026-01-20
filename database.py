from db_utils import get_connection

def create_tables():
    conn = get_connection()
    c = conn.cursor()

    # USERS TABLE
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    # STUDENTS TABLE
    c.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        class TEXT,
        division TEXT,
        image_path TEXT
    )
    """)

    # ATTENDANCE TABLE
    c.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        class TEXT,
        division TEXT,
        date TEXT,
        status TEXT  -- "Present" or "Absent"
    )
    """)

    # LEAVE RECORDS TABLE
    c.execute("""
    CREATE TABLE IF NOT EXISTS leave_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT,
        class TEXT,
        division TEXT,
        leave_from TEXT,
        leave_to TEXT
    )
    """)

    conn.commit()
    conn.close()

def add_default_admin():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username='admin'")
    if not c.fetchone():
        c.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ("admin", "admin123", "admin")
        )
        conn.commit()
    conn.close()
