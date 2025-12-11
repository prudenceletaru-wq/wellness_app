# managers/theme_manager.py
from .base_manager import BaseManager
import streamlit as st

class ThemeManager(BaseManager):
    THEMES = ["Light", "Dark", "Mint", "Ocean"]

    def select_theme(self):
        return st.sidebar.selectbox("Theme", self.THEMES, index=0)

    def apply_theme(self, theme_name: str):
        css = ""
        if theme_name == "Light":
            css = """
            <style>
            .stApp { background-color: #f7f9fc; color: #0b2545; }
            </style>
            """
        elif theme_name == "Dark":
            css = """
            <style>
            .stApp { background-color: #0b0f14; color: #e6eef8; }
            </style>
            """
        elif theme_name == "Mint":
            css = """
            <style>
            .stApp { background-color: #f3fbf6; color: #0b3a2e; }
            </style>
            """
        elif theme_name == "Ocean":
            css = """
            <style>
            .stApp { background-color: #f0f8ff; color: #0a2b4a; }
            </style>
            """
        if css:
            st.markdown(css, unsafe_allow_html=True)
