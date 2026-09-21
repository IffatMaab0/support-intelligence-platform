import streamlit as st
import requests

from api_client import get_ticket
from components import page_header, empty_state


def render():
    token = st.session_state["token"]
    ticket_id = st.session_state.get("manager_selected_ticket")

    if not ticket_id:
        st.error("No ticket selected.")
        return

    if st.button("← Back to All Tickets"):
        st.session_state.pop("manager_selected_ticket", None)
        st.rerun()

    try:
        ticket = get_ticket(
            token=token,
            ticket_id=ticket_id,
        )
    except requests.HTTPError as exc:
        if exc.response is not None and exc.response.status_code == 404:
            st.error("Ticket not found.")
        else:
            st.error(f"Could not load ticket: {exc}")
        return

    page_header("Ticket Oversight")

    st.subheader(ticket["reference"])
    st.write(f"**Subject:** {ticket['subject']}")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write(f"**Status:** {ticket['status']}")

    with col2:
        st.write(f"**Priority:** {ticket['priority']}")

    with col3:
        st.write(
            f"**Assigned agent ID:** "
            f"{ticket['assigned_agent_id'] or 'Unassigned'}"
        )

    st.subheader("Customer message")
    st.write(ticket["original_message"])

    st.subheader("Ticket metadata")
    st.write(f"Created UTC: {ticket['created_at']}")
    st.write(f"Updated UTC: {ticket['updated_at']}")
    st.write(f"Version: {ticket['version']}")

    st.divider()

    st.subheader("Assignment")

    empty_state(
        "Assignment is managed from Manager/Admin → All Tickets."
    )

    if st.button("Refresh"):
        st.rerun()