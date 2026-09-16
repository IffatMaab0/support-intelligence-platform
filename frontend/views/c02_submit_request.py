import streamlit as st

from api_client import create_ticket
from components import page_header


def render():
    page_header("Submit a Request")

    st.write("Tell us what you need help with.")

    subject = st.text_input(
        "Subject",
        value=st.session_state.get("ticket_subject", ""),
        placeholder="Example: Refund has not arrived",
    )

    original_message = st.text_area(
        "Original message",
        value=st.session_state.get("ticket_message", ""),
        placeholder="Describe your issue...",
        height=180,
    )

    if st.button("Submit Request", type="primary"):
        # Preserve what the customer entered.
        st.session_state["ticket_subject"] = subject
        st.session_state["ticket_message"] = original_message

        # Frontend validation
        if not subject.strip():
            st.error("Subject is required.")
            return

        if not original_message.strip():
            st.error("Message is required.")
            return

        token = st.session_state.get("token")

        if not token:
            st.error("Your session has expired. Please sign in again.")
            return

        try:
            ticket = create_ticket(
                token=token,
                subject=subject.strip(),
                original_message=original_message.strip(),
            )

            st.session_state["submitted_ticket"] = ticket

        except Exception:
            st.error(
                "We couldn't submit your request. "
                "Your request has not been confirmed as saved. "
                "Please try again."
            )
            return

    ticket = st.session_state.get("submitted_ticket")

    if ticket:
        st.success("Request submitted successfully.")

        st.write(f"**Ticket:** {ticket['reference']}")

        if st.button("Open Request"):
            st.session_state["selected_ticket_id"] = ticket["id"]
            st.session_state["submitted_ticket"] = None
            st.rerun()