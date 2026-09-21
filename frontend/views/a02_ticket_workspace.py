import streamlit as st
import requests

from api_client import get_ticket
from components import page_header, empty_state


def render():
    token = st.session_state["token"]
    ticket_id = st.session_state.get("selected_ticket_id")

    if not ticket_id:
        st.error("No ticket selected.")
        return

    if st.button("← Back to My Queue"):
        st.session_state.pop("selected_ticket_id", None)
        st.rerun()

    try:
        ticket = get_ticket(
            token=token,
            ticket_id=ticket_id,
        )
    except requests.HTTPError as exc:
        if exc.response is not None and exc.response.status_code == 404:
            st.error("Ticket not found or access denied.")
        else:
            st.error(f"Could not load ticket: {exc}")
        return
    except requests.RequestException as exc:
        st.error(f"Could not load ticket: {exc}")
        return

    page_header(ticket["reference"])

    st.subheader(ticket["subject"])

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write(f"**Status:** {ticket['status']}")

    with col2:
        st.write(f"**Priority:** {ticket['priority']}")

    with col3:
        st.write(f"**Channel:** {ticket['channel']}")

    st.subheader("Customer message")
    st.write(ticket["original_message"])

    st.subheader("Ticket metadata")

    st.write(f"Created UTC: {ticket['created_at']}")
    st.write(f"Updated UTC: {ticket['updated_at']}")

    if st.button("Refresh"):
        st.rerun()

    st.divider()

    st.subheader("Conversation")

    empty_state(
        "Public conversation and private notes will be implemented in later tasks."
    )