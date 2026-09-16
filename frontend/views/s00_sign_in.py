import streamlit as st
from components import page_header


def render():
    page_header("Sign in")

    st.text_input("Email")
    st.text_input("Password", type="password")

    st.button("Sign in", disabled=True)

    st.info("Authentication is not implemented yet.")