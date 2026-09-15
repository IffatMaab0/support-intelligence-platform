import streamlit as st
from components import page_header, empty_state


def render():
    page_header("My requests")

    st.text_input("Search")
    st.selectbox("Status", ["All"])
    
    col1, col2 = st.columns(2)
    with col1:
        st.button("Apply", disabled=True)
    with col2:
        st.button("Clear", disabled=True)

    st.subheader("Request list")

    empty_state("No requests available yet.")

    st.caption("Ten rows • Scoped total: not available")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.button("Previous", disabled=True)
    with col2:
        st.button("Next", disabled=True)
    with col3:
        st.button("Open request", disabled=True)