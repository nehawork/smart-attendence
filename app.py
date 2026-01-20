import streamlit as st
import pandas as pd
import os
from database import create_tables, add_default_admin
from db_utils import get_connection
from PIL import Image
from datetime import datetime
from datetime import date

# ---------------- SETUP ----------------
st.set_page_config(page_title="Smart Attendance System", layout="centered")

# Hide Streamlit footer and menu
hide_streamlit_style = """
<style>
/* Hide main menu (hamburger) */
#MainMenu {visibility: hidden;}

/* Hide footer */
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Initialize DB
create_tables()
add_default_admin()

os.makedirs("student_images", exist_ok=True)

# ---------------- SESSION STATE ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None


def logout():
    st.session_state.logged_in = False
    st.session_state.role = None
    st.experimental_rerun()

# ---------------- LOGIN PAGE ----------------
if not st.session_state.logged_in:
    st.title("🏫 Smart Attendance System")
    st.subheader("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        conn = get_connection()
        c = conn.cursor()
        c.execute(
            "SELECT role FROM users WHERE username=? AND password=?",
            (username, password)
        )
        result = c.fetchone()
        conn.close()

        if result:
            st.session_state.logged_in = True
            st.session_state.role = result[0]
            st.success("Login successful")
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")

# ---------------- ADMIN DASHBOARD ----------------
if st.session_state.logged_in and st.session_state.role == "admin":

    # ---------------- ADMIN DASHBOARD HEADER ----------------
    if st.session_state.logged_in and st.session_state.role == "admin":

        col1, col2 = st.columns([4, 1])  # title takes 4 parts, button 1 part
        with col1:
            st.title("🧑‍💼 Admin Dashboard")
        with col2:
            if st.button("🔒 Logout"):
                logout()

    tab1, tab2, tab3, tab4 = st.tabs(
        ["👩‍🏫 Teachers", "👨‍🎓 Students", "📊 Attendance Report", "🗓️ Leave Report"]
    )

    # ---------- TEACHERS TAB ----------
    with tab1:
        st.subheader("Manage Teachers")

        # Initialize session state
        if "show_add_teacher" not in st.session_state:
            st.session_state.show_add_teacher = False
        if "teacher_message" not in st.session_state:
            st.session_state.teacher_message = ""

        # Button to open Add Teacher form
        if st.button("➕ Add Teacher"):
            st.session_state.show_add_teacher = True
            st.session_state.teacher_message = ""  # reset message

        # Modal-like form
        if st.session_state.show_add_teacher:
            with st.expander("Add New Teacher", expanded=True):
                with st.form("add_teacher_form", clear_on_submit=True):
                    t_username = st.text_input("Teacher Username")
                    t_password = st.text_input("Teacher Password", type="password")

                    col1, col2 = st.columns(2)
                    submit = col1.form_submit_button("Save Teacher")
                    cancel = col2.form_submit_button("Cancel")

                    if submit:
                        if not t_username or not t_password:
                            st.warning("Please fill all fields")
                        else:
                            try:
                                conn = get_connection()
                                c = conn.cursor()
                                c.execute(
                                    "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                                    (t_username, t_password, "teacher")
                                )
                                conn.commit()
                                conn.close()

                                # Set message in session state
                                st.session_state.teacher_message = "success"

                                # Close form
                                st.session_state.show_add_teacher = False
                                st.experimental_rerun()
                            except Exception as e:
                                if "UNIQUE constraint failed" in str(e):
                                    st.session_state.teacher_message = "exists"
                                else:
                                    st.session_state.teacher_message = "error"

                    if cancel:
                        st.session_state.show_add_teacher = False
                        st.session_state.teacher_message = ""
                        st.experimental_rerun()

        # Show the message AFTER rerun
        if st.session_state.teacher_message == "success":
            st.success("Teacher added successfully")
            st.session_state.teacher_message = ""  # clear after showing
        elif st.session_state.teacher_message == "exists":
            st.error("Username already exists")
            st.session_state.teacher_message = ""  # clear after showing

        # Show existing teachers
        conn = get_connection()
        teachers_df = pd.read_sql("SELECT id, username FROM users WHERE role='teacher'", conn)
        conn.close()
        st.dataframe(teachers_df)


        # ---------- STUDENTS TAB ----------
        with tab2:
            st.subheader("Manage Students")
            if "show_add_student" not in st.session_state:
                st.session_state.show_add_student = False

            if st.button("➕ Add Student"):
                st.session_state.show_add_student = True

            if st.session_state.show_add_student:
                with st.expander("Add New Student", expanded=True):
                    with st.form("add_student_form", clear_on_submit=True):
                        name = st.text_input("Student Name")
                        class_no = st.selectbox("Class", ["9", "10", "11", "12"])
                        division = st.selectbox("Division", ["A", "B", "C"])
                        image = st.file_uploader("Upload Student Image", type=["jpg","jpeg","png"])
                        col1, col2 = st.columns(2)
                        submit = col1.form_submit_button("Save Student")
                        cancel = col2.form_submit_button("Cancel")

                        if submit:
                            if not name or not image:
                                st.warning("Please fill all fields and upload image")
                            else:
                                safe_name = name.replace(" ", "_")
                                folder = f"student_images/{safe_name}"
                                os.makedirs(folder, exist_ok=True)
                                image_path = f"{folder}/{image.name}"
                                with open(image_path, "wb") as f:
                                    f.write(image.getbuffer())

                                conn = get_connection()
                                c = conn.cursor()
                                c.execute(
                                    "INSERT INTO students (name, class, division, image_path) VALUES (?, ?, ?, ?)",
                                    (name, class_no, division, image_path)
                                )
                                conn.commit()
                                conn.close()

                                st.success("Student added successfully")
                                st.session_state.show_add_student = False
                                st.experimental_rerun()

                        if cancel:
                            st.session_state.show_add_student = False
                            st.experimental_rerun()

            st.markdown("### Student List")
            conn = get_connection()
            students = conn.execute(
                "SELECT name, class, division, image_path FROM students"
            ).fetchall()
            conn.close()

            for s in students:
                col1, col2 = st.columns([1,3])
                with col1:
                    if s[3]:
                        st.image(s[3], width=80)
                with col2:
                    st.write(f"**Name:** {s[0]}")
                    st.write(f"**Class:** {s[1]} - {s[2]}")
                    st.markdown("---")

        # ---------- ATTENDANCE REPORT TAB ----------
        with tab3:
            # Fetch all attendance data with student info
            conn = get_connection()
            df = pd.read_sql("""
                SELECT a.date, s.class, s.division, s.name, a.status
                FROM attendance a
                JOIN students s ON a.student_id = s.id
            """, conn)
            conn.close()

            if df.empty:
                st.info("No attendance records found.")
            else:
                # Create a new column combining Class + Division
                df["Class & Division"] = df["class"] + " - " + df["division"]

                # Aggregate summary: Present / Absent counts per date & class
                summary = df.groupby(["date", "Class & Division"])["status"].value_counts().unstack(fill_value=0).reset_index()
                if "Present" not in summary.columns:
                    summary["Present"] = 0
                if "Absent" not in summary.columns:
                    summary["Absent"] = 0

                # Display as a table with headers
                st.markdown("### Attendance Summary")
                for idx, row in summary.iterrows():
                    col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 1, 1, 1, 1])
                    col1.markdown("**Date**")
                    col2.markdown("**Class & Division**")
                    col3.markdown("**Present**")
                    col4.markdown("**Absent**")
                    col5.markdown("")  # placeholder
                    col6.markdown("")  # placeholder

                    # Display row data
                    col1.write(row["date"])
                    col2.write(row["Class & Division"])
                    col3.write(row["Present"])
                    col4.write(row["Absent"])

                    # View button for details
                    if col6.button("View", key=f"view_{row['date']}_{row['Class & Division']}"):
                        detail_df = df[(df["date"] == row["date"]) & (df["Class & Division"] == row["Class & Division"])]
                        st.markdown(f"### Details for {row['Class & Division']} on {row['date']}")
                        st.dataframe(detail_df[["name", "status"]])


        with tab4:
            # ---------- HEADER ----------
            col1, col2 = st.columns([4, 1])
            with col1:
                st.subheader("View Leave Reports")

            # ---------- LOAD DATA ----------
            conn = get_connection()
            df_leave = pd.read_sql("SELECT * FROM leave_records", conn)
            conn.close()

            if df_leave.empty:
                st.info("No leave records found.")
            else:
                # ---------- FILTERS ----------
                col1, col2, col3 = st.columns(3)

                with col1:
                    selected_class = st.selectbox(
                        "Filter by Class",
                        ["All"] + sorted(df_leave["class"].unique().tolist()),
                        key="admin_leave_class"
                    )

                # Division depends on class
                with col2:
                    if selected_class == "All":
                        divisions = ["All"]
                    else:
                        divisions = ["All"] + sorted(
                            df_leave[df_leave["class"] == selected_class]["division"].unique().tolist()
                        )

                    selected_division = st.selectbox(
                        "Filter by Division",
                        divisions,
                        key="admin_leave_division"
                    )

                # Student depends on class + division
                with col3:
                    filtered_students_df = df_leave.copy()

                    if selected_class != "All":
                        filtered_students_df = filtered_students_df[
                            filtered_students_df["class"] == selected_class
                        ]

                    if selected_division != "All":
                        filtered_students_df = filtered_students_df[
                            filtered_students_df["division"] == selected_division
                        ]

                    students = ["All"] + sorted(
                        filtered_students_df["student_name"].unique().tolist()
                    )

                    selected_student = st.selectbox(
                        "Filter by Student",
                        students,
                        key="admin_leave_student"
                    )

                # ---------- APPLY FILTERS ----------
                df_filtered = df_leave.copy()

                if selected_class != "All":
                    df_filtered = df_filtered[df_filtered["class"] == selected_class]

                if selected_division != "All":
                    df_filtered = df_filtered[df_filtered["division"] == selected_division]

                if selected_student != "All":
                    df_filtered = df_filtered[df_filtered["student_name"] == selected_student]

                # ---------- DOWNLOAD BUTTON (FILTERED DATA) ----------
                with col2:
                    import io

                    def convert_df_to_excel(df):
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                            df.to_excel(writer, index=False, sheet_name="Leave Report")
                        return output.getvalue()

                    excel_data = convert_df_to_excel(df_filtered)

                    st.download_button(
                        label="📥 Download",
                        data=excel_data,
                        file_name="leave_report.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                # ---------- TABLE ----------
                st.markdown("### Leave Records")
                st.dataframe(df_filtered, use_container_width=True)

        st.button("Logout", on_click=logout)

# ---------------- TEACHER DASHBOARD ----------------
if st.session_state.logged_in and st.session_state.role == "teacher":

    # ---------------- TEACHER DASHBOARD HEADER ----------------
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("👩‍🏫 Teacher Dashboard")
    with col2:
        if st.button("🔒 Logout"):
            logout()

    # ---------------- TEACHER TABS ----------------
    tab1, tab2, tab3 = st.tabs(["📝 Take Attendance", "🗓️ Add Leave", "📊 View Attendance"])

    # ---------- TAB 1: Take Attendance ----------
    with tab1:

        # ---------- Take Attendance ----------
        st.subheader("Take Attendance")

        # Fetch classes and divisions dynamically from students table
        conn = get_connection()
        students = conn.execute("SELECT DISTINCT class, division FROM students").fetchall()
        conn.close()

        if not students:
            st.warning("No students found. Please add students first.")
        else:
            # Build Class & Division dropdown
            class_div_list = [f"{c[0]} - {c[1]}" for c in students]
            selected_class_div = st.selectbox("Select Class & Division", class_div_list)

            selected_class, selected_division = selected_class_div.split(" - ")

            # Upload classroom image
            uploaded_file = st.file_uploader("Upload Classroom Image", type=["jpg", "jpeg", "png"])

            if uploaded_file and st.button("📸 Take Attendance"):
                # For demo, simulate attendance marking without face recognition
                # Fetch students for selected class & division
                conn = get_connection()
                student_rows = conn.execute(
                    "SELECT id, name FROM students WHERE class=? AND division=?",
                    (selected_class, selected_division)
                ).fetchall()
                conn.close()

                if not student_rows:
                    st.warning("No students found for this class & division.")
                else:
                    # Simulate: mark all students present (or randomize if desired)
                    marked_students_list = []
                    today = str(date.today())
                    for sid, sname in student_rows:
                        status = "Present"  # or "Absent" for demo/random
                        marked_students_list.append((sid, selected_class, selected_division, status))

                    # Save to attendance table
                    conn = get_connection()
                    c = conn.cursor()
                    for sid, class_name, division, status in marked_students_list:
                        c.execute("""
                            INSERT INTO attendance (student_id, class, division, date, status)
                            VALUES (?, ?, ?, ?, ?)
                        """, (sid, class_name, division, today, status))
                    conn.commit()
                    conn.close()

                    st.success(f"Attendance marked for {len(marked_students_list)} students.")
                    st.dataframe(pd.DataFrame(marked_students_list, columns=["Student ID", "Class", "Division", "Status"]))



    # ---------- TAB 2: Add Leave ----------
    with tab2:
        st.subheader("Add Leave Record")

        # ---- INIT SESSION STATE ----
        if "show_add_leave" not in st.session_state:
            st.session_state.show_add_leave = False

        # ---- ADD LEAVE BUTTON ----
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("➕ Add Leave"):
                st.session_state.show_add_leave = True
                st.experimental_rerun()

        # ---- ADD LEAVE FORM ----
        if st.session_state.show_add_leave:

            with st.container(border=True):
                st.markdown("### Add Leave Form")

                # ---------- CLASS ----------
                conn = get_connection()
                classes = [c[0] for c in conn.execute(
                    "SELECT DISTINCT class FROM students"
                ).fetchall()]
                conn.close()

                selected_class = st.selectbox(
                    "Select Class",
                    classes,
                    key="leave_class"
                )

                # ---------- DIVISION ----------
                conn = get_connection()
                divisions = [d[0] for d in conn.execute(
                    "SELECT DISTINCT division FROM students WHERE class=?",
                    (selected_class,)
                ).fetchall()]
                conn.close()

                selected_division = st.selectbox(
                    "Select Division",
                    divisions,
                    key="leave_division"
                )

                # ---------- STUDENTS (DYNAMIC) ----------
                conn = get_connection()
                students = [s[0] for s in conn.execute(
                    "SELECT name FROM students WHERE class=? AND division=?",
                    (selected_class, selected_division)
                ).fetchall()]
                conn.close()

                if not students:
                    st.warning("No students found for this class & division")
                    student_choice = None
                else:
                    student_choice = st.selectbox(
                        "Select Student",
                        students,
                        key="leave_student"
                    )

                # ---------- DATE & TIME ----------
                from_date = st.date_input(
                    "From Date",
                    value=st.session_state.get("leave_from_date", datetime.today()),
                    key="leave_from_date"
                )
                from_time = st.time_input(
                    "From Time",
                    value=st.session_state.get("leave_from_time", datetime.now().time()),
                    key="leave_from_time"
                )

                to_date = st.date_input(
                    "To Date",
                    value=st.session_state.get("leave_to_date", datetime.today()),
                    key="leave_to_date"
                )
                to_time = st.time_input(
                    "To Time",
                    value=st.session_state.get("leave_to_time", datetime.now().time()),
                    key="leave_to_time"
                )

                # ---------- ACTION BUTTONS ----------
                col1, col2 = st.columns(2)

                with col1:
                    if st.button("💾 Save Leave", use_container_width=True):
                        if not student_choice:
                            st.error("Please select a student")
                        else:
                            leave_from = datetime.combine(from_date, from_time)
                            leave_to = datetime.combine(to_date, to_time)

                            if leave_to <= leave_from:
                                st.error("To Date/Time must be after From Date/Time")
                            else:
                                conn = get_connection()
                                c = conn.cursor()
                                c.execute("""
                                    INSERT INTO leave_records
                                    (student_name, class, division, leave_from, leave_to)
                                    VALUES (?, ?, ?, ?, ?)
                                """, (
                                    student_choice,
                                    selected_class,
                                    selected_division,
                                    leave_from.isoformat(),
                                    leave_to.isoformat()
                                ))
                                conn.commit()
                                conn.close()

                                # ---------- RESET ----------
                                for key in list(st.session_state.keys()):
                                    if key.startswith("leave_"):
                                        del st.session_state[key]

                                st.session_state.show_add_leave = False
                                st.success("✅ Leave record added successfully")
                                st.experimental_rerun()

                with col2:
                    if st.button("❌ Cancel", use_container_width=True):
                        for key in list(st.session_state.keys()):
                            if key.startswith("leave_"):
                                del st.session_state[key]

                        st.session_state.show_add_leave = False
                        st.experimental_rerun()

        # ---------- Leave Reports Table ----------
        st.markdown("### Leave Reports")

        conn = get_connection()
        df_leave = pd.read_sql("SELECT * FROM leave_records", conn)
        conn.close()

        if df_leave.empty:
            st.info("No leave records found.")
        else:
            student_filter = st.selectbox(
                "Filter by Student",
                ["All"] + sorted(df_leave["student_name"].unique().tolist()),
                key="filter_student"
            )

            class_filter = st.selectbox(
                "Filter by Class",
                ["All"] + sorted(df_leave["class"].unique().tolist()),
                key="filter_class"
            )

            df_filtered = df_leave.copy()
            if student_filter != "All":
                df_filtered = df_filtered[df_filtered["student_name"] == student_filter]
            if class_filter != "All":
                df_filtered = df_filtered[df_filtered["class"] == class_filter]

            st.dataframe(df_filtered, use_container_width=True)

    # ---------- TAB 3: View Attendance ----------
    with tab3:
        st.subheader("Attendance Records")
        conn = get_connection()
        df_attendance = pd.read_sql("SELECT * FROM attendance", conn)
        conn.close()
        st.dataframe(df_attendance)

