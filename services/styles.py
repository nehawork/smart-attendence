"""
Styles Module - Contains all UI styling and themes
"""

import streamlit as st


class Styles:
    """UI Styles and CSS for the application"""

    @staticmethod
    def apply_styles():
        """Apply mobile-first CSS styling to the app"""
        # st.markdown(Styles.MOBILE_CSS, unsafe_allow_html=True)

    @staticmethod
    def configure_page():
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title="Smart Attendance System",
            layout="wide",
            initial_sidebar_state="collapsed",
            menu_items=None
        )
