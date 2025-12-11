# managers/auth_manager.py
import streamlit as st
import pandas as pd
import os
from .base_manager import BaseManager

DEFAULT_USERS = pd.DataFrame([
    {"username": "user1", "password": "demo"},
    {"username": "demo", "password": "demo"}
])


class AuthManager(BaseManager):
    """
    Plaintext username/password auth manager for demo/testing.
    Creates data/users.csv automatically if missing.
    """

    def __init__(self, users_csv="data/users.csv"):
        self.users_csv = users_csv
        self._ensure_users_csv()

    def _ensure_users_csv(self):
        if not os.path.exists(self.users_csv):
            parent = os.path.dirname(self.users_csv)
            if parent and not os.path.exists(parent):
                os.makedirs(parent)
            DEFAULT_USERS.to_csv(self.users_csv, index=False)

    def load_users(self):
        try:
            return pd.read_csv(self.users_csv, dtype=str).fillna("")
        except pd.errors.EmptyDataError:
            DEFAULT_USERS.to_csv(self.users_csv, index=False)
            return DEFAULT_USERS.copy()

    def authenticate_user(self):
        users = self.load_users()

        # initialize session state
        if "username" not in st.session_state:
            st.session_state["username"] = None

        # if already logged in, show logout and return
        if st.session_state["username"]:
            st.write(f"Logged in as **{st.session_state['username']}**")
            if st.button("Logout"):
                st.session_state["username"] = None
                st.experimental_rerun()
            return st.session_state["username"]

        # --- Centered UI ---
        st.title("🌿 Lifestyle & Wellness Tracker 🌿")  # App title at the top
        st.write("")  # vertical spacing
        st.write("")
        st.write("")

        # Horizontal centering
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            choice = st.radio("Account", ["Login", "Sign Up"], horizontal=True)

            if choice == "Login":
                return self._login(users)
            else:
                return self._signup(users)

    def _login(self, users):
        st.subheader("Login")
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            if submitted:
                match = users[(users["username"] == str(username).strip()) &
                              (users["password"] == str(password))]
                if not match.empty:
                    st.session_state["username"] = str(username).strip()
                    st.success(f"Logged in as {st.session_state['username']}")
                    return st.session_state["username"]
                else:
                    st.error("Invalid username or password.")
        return None

    def _signup(self, users):
        st.subheader("Sign Up")
        with st.form("signup_form", clear_on_submit=False):
            new_user = st.text_input("Choose a username")
            pw1 = st.text_input("Password", type="password")
            pw2 = st.text_input("Confirm password", type="password")
            create = st.form_submit_button("Create account")
            if create:
                nu = str(new_user).strip()
                if not nu or not pw1:
                    st.error("Username and password required.")
                elif pw1 != pw2:
                    st.error("Passwords do not match.")
                elif nu in users["username"].values:
                    st.error("Username already exists.")
                else:
                    df = users.copy()
                    df = pd.concat([df, pd.DataFrame([{"username": nu, "password": pw1}])],
                                   ignore_index=True)
                    df.to_csv(self.users_csv, index=False)
                    st.success(f"Account created. Logged in as {nu}")
                    st.session_state["username"] = nu
                    return nu
        return None
