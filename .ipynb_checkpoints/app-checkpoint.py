# app.py
import streamlit as st
from managers.data_manager import DataManager
from managers.auth_manager import AuthManager
from managers.theme_manager import ThemeManager
from managers.analysis_engine import AnalysisEngine
from managers.recommendations_engine import RecommendationsEngine
from managers.ui_manager import UIManager
from managers.sample_data_generator import SampleDataGenerator
import os

# Ensure data folder exists
if not os.path.exists("data"):
    os.makedirs("data")

def main():
    # instantiate managers
    data_manager = DataManager(data_csv="data/saved_data.csv")
    auth_manager = AuthManager(users_csv="data/users.csv")
    theme_manager = ThemeManager()
    analysis_engine = AnalysisEngine()
    recs_engine = RecommendationsEngine()
    sample_gen = SampleDataGenerator(users_csv="data/users.csv", output_csv="data/saved_data.csv")

    # lightweight app object passed to UIManager
    class App:
        pass

    app = App()
    app.data_manager = data_manager
    app.auth_manager = auth_manager
    app.theme_manager = theme_manager
    app.analysis_engine = analysis_engine
    app.recs_engine = recs_engine
    app.sample_gen = sample_gen

    ui = UIManager(app)

    st.set_page_config(layout="wide", page_title="Wellness Tracker")
    theme = theme_manager.select_theme()
    theme_manager.apply_theme(theme)

    username = auth_manager.authenticate_user()
    if not username:
        return

    ui.render_dashboard(username)


if __name__ == "__main__":
    main()
