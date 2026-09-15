import streamlit as st
from components import page_header, empty_state


def render():
    page_header("My queue")

    st.caption("Agent display name: not available yet")

    st.button("Refresh", disabled=True)

    st.subheader("Filters")

    st.selectbox("Status", ["All"])
    st.selectbox("Manual priority", ["All"])
    st.text_input("Subject / original-message search")

    col1, col2 = st.columns(2)
    with col1:
        st.button("Apply", disabled=True)
    with col2:
        st.button("Clear", disabled=True)

    st.subheader("Tickets")

    empty_state("No assigned tickets available yet.")

    st.caption(
        "Ten rows • Scoped total: not available • "
        "Created UTC / Updated UTC"
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.button("Previous", disabled=True)
    with col2:
        st.button("Next", disabled=True)
    with col3:
        st.button("Open", disabled=True)            