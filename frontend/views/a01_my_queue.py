import streamlit as st
import requests

from api_client import list_tickets
from components import page_header, empty_state


def render():
    page_header("My queue")

    token = st.session_state["token"]
    user = st.session_state["user"]

    st.caption(f"Agent display name: {user['display_name']}")

    if st.button("Refresh"):
        st.rerun()

    st.subheader("Filters")

    col1, col2, col3 = st.columns(3)

    with col1:
        status_filter = st.selectbox(
            "Status",
            ["All", "open", "resolved"],
        )

    with col2:
        priority_filter = st.selectbox(
            "Manual priority",
            ["All", "normal", "high", "urgent"],
        )

    with col3:
        search = st.text_input(
            "Subject / original-message search"
        )

    col1, col2 = st.columns(2)

    with col1:
        apply_filters = st.button("Apply")

    with col2:
        clear_filters = st.button("Clear")

    if clear_filters:
        st.rerun()

    try:
        result = list_tickets(
            token=token,
            search=search if search else None,
            skip=0,
            limit=100,
        )
    except requests.RequestException as exc:
        st.error(f"Could not load your queue: {exc}")
        return

    tickets = result["items"]

    if status_filter != "All":
        tickets = [
            ticket
            for ticket in tickets
            if ticket["status"] == status_filter
        ]

    if priority_filter != "All":
        tickets = [
            ticket
            for ticket in tickets
            if ticket["priority"] == priority_filter
        ]

    st.subheader("Tickets")

    if not tickets:
        empty_state("No assigned tickets available yet.")
    else:
        for ticket in tickets:
            st.markdown(
                f"**{ticket['reference']}** — {ticket['subject']}"
            )

            st.write(
                f"Status: {ticket['status']}  |  "
                f"Priority: {ticket['priority']}  |  "
                f"Created: {ticket['created_at']}  |  "
                f"Updated: {ticket['updated_at']}"
            )

            if st.button(
                "Open",
                key=f"open_{ticket['id']}",
            ):
                st.session_state["selected_ticket_id"] = ticket["id"]
                st.rerun()

            st.divider()

    st.caption(
        f"Scoped total: {len(tickets)}"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.button("Previous", disabled=True)

    with col2:
        st.button("Next", disabled=True)           