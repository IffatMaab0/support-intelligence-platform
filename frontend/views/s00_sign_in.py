import streamlit as st

from api_client import get_current_user, login
from components import page_header


def render():
    page_header("Sign in")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Sign in"):
        try:
            login_data = login(email, password)

            token = login_data["access_token"]
            user = get_current_user(token)

            st.session_state["token"] = token
            st.session_state["user"] = user

            st.rerun()

        except Exception:
            st.error("Invalid email or password.")