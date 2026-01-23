"""
UI Components - Reusable UI components for the application
"""

import streamlit as st
from typing import Callable, Optional


class UIComponents:
    """Reusable UI components for consistent design"""

    @staticmethod
    def render_login_page(on_login: Callable):
        """
        Render the login page.

        Args:
            on_login: Callback function called with (username, password)
        """
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.markdown("<div style='text-align: center; margin-bottom: 32px;'>", unsafe_allow_html=True)
            st.markdown("# 🏫 Smart Attendance")
            st.markdown("### Attendance Management System", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("### Welcome Back")

            username = st.text_input(
                "Username",
                placeholder="Enter your username",
                label_visibility="collapsed"
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                label_visibility="collapsed"
            )

            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("🔓 Login", use_container_width=True):
                on_login(username, password)

    @staticmethod
    def render_dashboard_header(title: str, on_logout: Callable):
        """
        Render dashboard header with title and logout button.

        Args:
            title: Dashboard title
            on_logout: Logout callback function
        """
        header_col1, header_col2, header_col3 = st.columns([2, 3, 1])

        with header_col1:
            st.markdown(f"### {title}")

        with header_col3:
            if st.button("🔒 Logout", use_container_width=True):
                on_logout()

        st.markdown("---")

    @staticmethod
    def render_section_title(title: str):
        """Render a section title"""
        st.markdown(f"### {title}")

    @staticmethod
    def render_subsection_title(title: str):
        """Render a subsection title"""
        st.markdown(f"#### {title}")

    @staticmethod
    def render_add_button(label: str, full_width: bool = True) -> bool:
        """
        Render an add button.

        Args:
            label: Button label
            full_width: Whether button takes full width

        Returns:
            Button click state
        """
        return st.button(label, use_container_width=full_width)

    @staticmethod
    def render_action_buttons(submit_label: str, cancel_label: str,
                            on_submit: Callable, on_cancel: Callable):
        """
        Render submit and cancel buttons side by side.

        Args:
            submit_label: Submit button label
            cancel_label: Cancel button label
            on_submit: Submit callback
            on_cancel: Cancel callback
        """
        col1, col2 = st.columns(2)

        with col1:
            if st.button(submit_label, use_container_width=True):
                on_submit()

        with col2:
            if st.button(cancel_label, use_container_width=True):
                on_cancel()

    @staticmethod
    def render_info_message(message: str):
        """Render info message"""
        st.info(message)

    @staticmethod
    def render_success_message(message: str):
        """Render success message"""
        st.success(message)

    @staticmethod
    def render_error_message(message: str):
        """Render error message"""
        st.error(message)

    @staticmethod
    def render_warning_message(message: str):
        """Render warning message"""
        st.warning(message)

    @staticmethod
    def render_divider():
        """Render a divider"""
        st.markdown("---")

    @staticmethod
    def render_two_column_layout():
        """
        Render a two-column layout.

        Returns:
            Tuple of (col1, col2)
        """
        return st.columns(2)

    @staticmethod
    def render_three_column_layout():
        """
        Render a three-column layout.

        Returns:
            Tuple of (col1, col2, col3)
        """
        return st.columns(3)
