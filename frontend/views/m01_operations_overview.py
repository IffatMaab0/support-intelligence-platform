import streamlit as st
from components import page_header, empty_state


def render():
    page_header("Operations overview")

    st.button("Refresh", disabled=True)
    st.caption("Data-as-of UTC: not available yet")

    st.subheader("Metrics")

    cols = st.columns(5)

    labels = [
        "All tickets",
        "Open",
        "In review",
        "Resolved",
        "Unassigned active",
    ]

    for col, label in zip(cols, labels):
        with col:
            st.metric(label, "—")

    st.subheader("Workload")
    empty_state("Workload data not available yet.")

    st.subheader("Manual-priority breakdown")
    empty_state("Priority data not available yet.")

    st.subheader("Latest internal ticket events")
    empty_state("No activity data available yet.")