"""
Smart Attendance System - Main Application
Refactored following SOLID principles with separate services
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date

# Import services and utilities
from database import create_tables, add_default_admin
from services import (
    AuthService,
    StudentService,
    AttendanceService,
    LeaveService,
    Styles,
    UIComponents
)


# ============================================================================
# APPLICATION INITIALIZATION
# ============================================================================

def initialize_app():
    """Initialize the application"""
    Styles.configure_page()
    Styles.apply_styles()
    create_tables()
    add_default_admin()


def init_session_state():
    """Initialize session state variables"""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.username = None


def logout():
    """Logout user"""
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None
    st.experimental_rerun()


# ============================================================================
# LOGIN PAGE
# ============================================================================

def handle_login(username: str, password: str):
    """Handle user login"""
    if not username or not password:
        UIComponents.render_error_message("❌ Please enter both username and password")
        return

    role = AuthService.authenticate_user(username, password)

    if role:
        st.session_state.logged_in = True
        st.session_state.role = role
        st.session_state.username = username
        UIComponents.render_success_message("✅ Login successful! Redirecting...")
        st.experimental_rerun()
    else:
        UIComponents.render_error_message("❌ Invalid username or password")


def render_login_page():
    """Render the login page"""
    if not st.session_state.logged_in:
        UIComponents.render_login_page(handle_login)


# ============================================================================
# ADMIN DASHBOARD - TEACHERS TAB
# ============================================================================

def render_admin_teachers_tab():
    """Render admin teachers management tab"""
    UIComponents.render_section_title("Manage Teachers")

    # Initialize session state for add teacher form
    if "show_add_teacher" not in st.session_state:
        st.session_state.show_add_teacher = False
    if "teacher_message" not in st.session_state:
        st.session_state.teacher_message = ""

    # Add teacher button
    if UIComponents.render_add_button("➕ Add New Teacher"):
        st.session_state.show_add_teacher = True
        st.session_state.teacher_message = ""

    # Add teacher form
    if st.session_state.show_add_teacher:
        with st.expander("📝 Add New Teacher", expanded=True):
            with st.form("add_teacher_form", clear_on_submit=True):
                t_username = st.text_input(
                    "Username",
                    placeholder="Enter teacher username",
                    label_visibility="collapsed"
                )
                t_password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter password",
                    label_visibility="collapsed"
                )

                col1, col2 = st.columns(2)
                submit = col1.form_submit_button("✅ Save", use_container_width=True)
                cancel = col2.form_submit_button("❌ Cancel", use_container_width=True)

                if submit:
                    if not t_username or not t_password:
                        UIComponents.render_warning_message("Please fill all fields")
                    else:
                        success, message = AuthService.add_teacher(t_username, t_password)
                        if success:
                            st.session_state.teacher_message = "success"
                            st.session_state.show_add_teacher = False
                            st.experimental_rerun()
                        else:
                            UIComponents.render_error_message(f"⚠️ {message}")

                if cancel:
                    st.session_state.show_add_teacher = False
                    st.session_state.teacher_message = ""
                    st.experimental_rerun()

    # Show messages
    if st.session_state.teacher_message == "success":
        UIComponents.render_success_message("✅ Teacher added successfully!")
        st.session_state.teacher_message = ""

    # Display teachers list
    UIComponents.render_subsection_title("📋 Teacher List")
    teachers = AuthService.get_all_teachers()

    if not teachers:
        UIComponents.render_info_message("No teachers added yet. Click 'Add New Teacher' to get started.")
    else:
        teachers_df = pd.DataFrame(teachers, columns=["ID", "Username"])
        st.dataframe(teachers_df, use_container_width=True, hide_index=True)


# ============================================================================
# ADMIN DASHBOARD - STUDENTS TAB
# ============================================================================

def render_admin_students_tab():
    """Render admin students management tab"""
    UIComponents.render_section_title("Manage Students")

    # Initialize session state
    if "show_add_student" not in st.session_state:
        st.session_state.show_add_student = False

    student_service = StudentService()

    # Add student button
    if UIComponents.render_add_button("➕ Add New Student"):
        st.session_state.show_add_student = True

    # Add student form
    if st.session_state.show_add_student:
        with st.expander("📸 Add New Student", expanded=True):
            with st.form("add_student_form", clear_on_submit=True):
                name = st.text_input(
                    "Name",
                    placeholder="Enter student name",
                    label_visibility="collapsed"
                )
                col1, col2 = st.columns(2)
                with col1:
                    class_no = st.selectbox("Class", ["9", "10", "11", "12"], label_visibility="collapsed")
                with col2:
                    division = st.selectbox("Division", ["A", "B", "C"], label_visibility="collapsed")

                image = st.file_uploader(
                    "Upload Student Photo",
                    type=["jpg", "jpeg", "png"],
                    label_visibility="collapsed"
                )

                col1, col2 = st.columns(2)
                submit = col1.form_submit_button("✅ Save", use_container_width=True)
                cancel = col2.form_submit_button("❌ Cancel", use_container_width=True)

                if submit:
                    if not name or not image:
                        UIComponents.render_warning_message("Please fill all fields and upload image")
                    else:
                        image_path = student_service.save_student_image(name, image)
                        success, message = StudentService.add_student(name, class_no, division, image_path)

                        if success:
                            UIComponents.render_success_message("✅ Student added successfully!")
                            st.session_state.show_add_student = False
                            st.experimental_rerun()
                        else:
                            UIComponents.render_error_message(f"Error: {message}")

                if cancel:
                    st.session_state.show_add_student = False
                    st.experimental_rerun()

    # Display students list
    UIComponents.render_subsection_title("👥 Student List")
    students = StudentService.get_all_students()

    if not students:
        UIComponents.render_info_message("No students added yet. Click 'Add New Student' to get started.")
    else:
        for student in students:
            sid, name, class_no, division, image_path = student
            col1, col2, col3 = st.columns([1, 3, 1])

            with col1:
                if image_path:
                    try:
                        st.image(image_path, width=70)
                    except:
                        st.markdown("📷")
                else:
                    st.markdown("📷")

            with col2:
                st.markdown(f"**{name}**")
                st.caption(f"Class {class_no}-{division}")

            st.markdown("---")


# ============================================================================
# ADMIN DASHBOARD - ATTENDANCE TAB
# ============================================================================

def render_admin_attendance_tab():
    """Render admin attendance reporting tab"""
    UIComponents.render_section_title("Attendance Summary")

    summary_df = AttendanceService.get_attendance_summary()

    if summary_df.empty:
        UIComponents.render_info_message("📭 No attendance records found yet.")
    else:
        UIComponents.render_subsection_title("📊 Attendance Records")

        for idx, row in summary_df.iterrows():
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([2, 2, 1.2, 1.2, 1])

                with col1:
                    st.markdown(f"**{row['date']}**")
                with col2:
                    st.markdown(f"{row['Class & Division']}")
                with col3:
                    st.markdown(f"✅ {row['Present']}")
                with col4:
                    st.markdown(f"❌ {row['Absent']}")
                with col5:
                    if st.button("👁️", key=f"view_{row['date']}_{row['Class & Division']}"):
                        detail_df = AttendanceService.get_attendance_detail(
                            row['date'],
                            row['Class & Division']
                        )
                        st.dataframe(detail_df, use_container_width=True, hide_index=True)

            st.markdown("<hr style='margin: 8px 0;'>", unsafe_allow_html=True)


# ============================================================================
# ADMIN DASHBOARD - LEAVE TAB
# ============================================================================

def render_admin_leave_tab():
    """Render admin leave reports tab"""
    UIComponents.render_section_title("Leave Management")

    leave_service = LeaveService()
    df_leave = leave_service.get_all_leave_records()

    if df_leave.empty:
        UIComponents.render_info_message("📭 No leave records found.")
    else:
        # Filters
        col1, col2, col3 = st.columns(3)

        with col1:
            selected_class = st.selectbox(
                "Class",
                ["All"] + leave_service.get_classes_with_leaves(),
                key="admin_leave_class",
                label_visibility="collapsed"
            )

        with col2:
            divisions = (
                ["All"] if selected_class == "All"
                else ["All"] + leave_service.get_divisions_for_class(selected_class)
            )
            selected_division = st.selectbox(
                "Division",
                divisions,
                key="admin_leave_division",
                label_visibility="collapsed"
            )

        with col3:
            students = (
                ["All"] if selected_class == "All" or selected_division == "All"
                else ["All"] + leave_service.get_students_for_class_division(selected_class, selected_division)
            )
            selected_student = st.selectbox(
                "Student",
                students,
                key="admin_leave_student",
                label_visibility="collapsed"
            )

        # Filter data
        df_filtered = leave_service.filter_leave_records(
            selected_class if selected_class != "All" else None,
            selected_division if selected_division != "All" else None,
            selected_student if selected_student != "All" else None
        )

        # Download button
        col1, col2 = st.columns([3, 1])
        with col2:
            excel_data = leave_service.export_to_excel(df_filtered)
            st.download_button(
                label="📥 Download",
                data=excel_data,
                file_name="leave_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        # Display table
        UIComponents.render_subsection_title("📋 Leave Records")
        st.dataframe(df_filtered, use_container_width=True, hide_index=True)


# ============================================================================
# ADMIN DASHBOARD
# ============================================================================

def render_admin_dashboard():
    """Render admin dashboard"""
    if st.session_state.logged_in and st.session_state.role == "admin":
        UIComponents.render_dashboard_header("🧑‍💼 Admin Panel", logout)

        tab1, tab2, tab3, tab4 = st.tabs(
            ["👩‍🏫 Teachers", "👨‍🎓 Students", "📊 Attendance", "🗓️ Leaves"]
        )

        with tab1:
            render_admin_teachers_tab()

        with tab2:
            render_admin_students_tab()

        with tab3:
            render_admin_attendance_tab()

        with tab4:
            render_admin_leave_tab()


# ============================================================================
# TEACHER DASHBOARD - MARK ATTENDANCE TAB
# ============================================================================

def render_teacher_mark_attendance_tab():
    """Render teacher attendance marking tab"""
    UIComponents.render_section_title("Mark Class Attendance")

    student_service = StudentService()
    attendance_service = AttendanceService()

    class_divisions = student_service.get_class_divisions()

    if not class_divisions:
        UIComponents.render_warning_message("⚠️ No students found. Please ask admin to add students.")
    else:
        class_div_list = [f"Class {c[0]} - {c[1]}" for c in class_divisions]
        selected_class_div = st.selectbox(
            "Select Class",
            class_div_list,
            label_visibility="collapsed"
        )

        selected_class, selected_division = selected_class_div.replace("Class ", "").split(" - ")

        UIComponents.render_divider()

        # Upload classroom image
        uploaded_file = st.file_uploader(
            "📸 Classroom Photo",
            type=["jpg", "jpeg", "png"],
            label_visibility="collapsed"
        )

        if uploaded_file:
            st.image(uploaded_file, use_column_width=True)

            if st.button("✅ Mark Attendance", use_container_width=True):
                students = student_service.get_students_by_class_division(selected_class, selected_division)

                if not students:
                    UIComponents.render_warning_message("No students found for this class & division.")
                else:
                    success, count = attendance_service.mark_class_attendance(
                        students,
                        selected_class,
                        selected_division
                    )

                    if success:
                        UIComponents.render_success_message(
                            f"✅ Attendance marked for {count} students in Class {selected_class}-{selected_division} "
                            f"on {date.today()}"
                        )

                        with st.expander("📋 View Marked Students", expanded=False):
                            marked_data = [{"Student": name, "Status": "✅ Present"} for _, name in students]
                            df_marked = pd.DataFrame(marked_data)
                            st.dataframe(df_marked, use_container_width=True, hide_index=True)


# ============================================================================
# TEACHER DASHBOARD - REQUEST LEAVE TAB
# ============================================================================

def render_teacher_request_leave_tab():
    """Render teacher leave request tab"""
    UIComponents.render_section_title("Request Leave")

    if "show_add_leave" not in st.session_state:
        st.session_state.show_add_leave = False

    student_service = StudentService()
    leave_service = LeaveService()

    # Request leave button
    if UIComponents.render_add_button("➕ Request Leave"):
        st.session_state.show_add_leave = True
        st.experimental_rerun()

    # Leave request form
    if st.session_state.show_add_leave:
        with st.expander("📋 Leave Request Form", expanded=True):
            classes = student_service.get_classes()

            if not classes:
                UIComponents.render_warning_message("⚠️ No classes found")
            else:
                selected_class = st.selectbox(
                    "Class",
                    classes,
                    key="leave_class",
                    label_visibility="collapsed"
                )

                divisions = student_service.get_divisions_for_class(selected_class)
                selected_division = st.selectbox(
                    "Division",
                    divisions,
                    key="leave_division",
                    label_visibility="collapsed"
                )

                students = student_service.get_students_by_class_division(selected_class, selected_division)
                student_names = [s[1] for s in students]

                if not student_names:
                    UIComponents.render_warning_message("⚠️ No students found for this class & division")
                else:
                    student_choice = st.selectbox(
                        "Student Name",
                        student_names,
                        key="leave_student",
                        label_visibility="collapsed"
                    )

                    # Date & time selection
                    st.markdown("**Leave Duration:**")
                    col1, col2 = st.columns(2)

                    with col1:
                        from_date = st.date_input(
                            "From Date",
                            value=st.session_state.get("leave_from_date", datetime.today()),
                            key="leave_from_date",
                            label_visibility="collapsed"
                        )

                    with col2:
                        from_time = st.time_input(
                            "From Time",
                            value=st.session_state.get("leave_from_time", datetime.now().time()),
                            key="leave_from_time",
                            label_visibility="collapsed"
                        )

                    col1, col2 = st.columns(2)

                    with col1:
                        to_date = st.date_input(
                            "To Date",
                            value=st.session_state.get("leave_to_date", datetime.today()),
                            key="leave_to_date",
                            label_visibility="collapsed"
                        )

                    with col2:
                        to_time = st.time_input(
                            "To Time",
                            value=st.session_state.get("leave_to_time", datetime.now().time()),
                            key="leave_to_time",
                            label_visibility="collapsed"
                        )

                    UIComponents.render_divider()

                    # Action buttons
                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button("✅ Submit", use_container_width=True):
                            leave_from = datetime.combine(from_date, from_time)
                            leave_to = datetime.combine(to_date, to_time)

                            success, message = leave_service.add_leave_request(
                                student_choice,
                                selected_class,
                                selected_division,
                                leave_from,
                                leave_to
                            )

                            if success:
                                for key in list(st.session_state.keys()):
                                    if key.startswith("leave_"):
                                        del st.session_state[key]

                                st.session_state.show_add_leave = False
                                UIComponents.render_success_message("✅ Leave request submitted successfully")
                                st.experimental_rerun()
                            else:
                                UIComponents.render_error_message(f"❌ {message}")

                    with col2:
                        if st.button("❌ Cancel", use_container_width=True):
                            for key in list(st.session_state.keys()):
                                if key.startswith("leave_"):
                                    del st.session_state[key]

                            st.session_state.show_add_leave = False
                            st.experimental_rerun()

    # Display leave records
    UIComponents.render_subsection_title("📋 My Leave Requests")

    leave_service = LeaveService()
    df_leave = leave_service.get_all_leave_records()

    if df_leave.empty:
        UIComponents.render_info_message("📭 No leave records found.")
    else:
        st.dataframe(df_leave, use_container_width=True, hide_index=True)


# ============================================================================
# TEACHER DASHBOARD - VIEW ATTENDANCE TAB
# ============================================================================

def render_teacher_view_attendance_tab():
    """Render teacher view attendance tab"""
    UIComponents.render_section_title("Attendance Records")

    attendance_service = AttendanceService()
    df_attendance = attendance_service.filter_attendance()

    if df_attendance.empty:
        UIComponents.render_info_message("📭 No attendance records found yet.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            selected_class = st.selectbox(
                "Filter by Class",
                ["All"] + sorted(df_attendance["class"].unique().tolist()),
                key="view_class"
            )

        with col2:
            selected_date = st.selectbox(
                "Filter by Date",
                ["All"] + sorted(df_attendance["date"].unique().tolist(), reverse=True),
                key="view_date"
            )

        # Apply filters
        df_filtered = attendance_service.filter_attendance(selected_class, selected_date)

        UIComponents.render_subsection_title("📋 Records")
        st.dataframe(df_filtered, use_container_width=True, hide_index=True)


# ============================================================================
# TEACHER DASHBOARD
# ============================================================================

def render_teacher_dashboard():
    """Render teacher dashboard"""
    if st.session_state.logged_in and st.session_state.role == "teacher":
        UIComponents.render_dashboard_header("👩‍🏫 Teacher Panel", logout)

        tab1, tab2, tab3 = st.tabs(["📝 Mark Attendance", "🗓️ Request Leave", "📊 My Records"])

        with tab1:
            render_teacher_mark_attendance_tab()

        with tab2:
            render_teacher_request_leave_tab()

        with tab3:
            render_teacher_view_attendance_tab()


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point"""
    initialize_app()
    init_session_state()

    if not st.session_state.logged_in:
        render_login_page()
    elif st.session_state.role == "admin":
        render_admin_dashboard()
    elif st.session_state.role == "teacher":
        render_teacher_dashboard()


if __name__ == "__main__":
    main()

