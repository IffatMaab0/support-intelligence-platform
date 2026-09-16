import streamlit as st

from api_client import get_ticket
from components import page_header


def render():
    ticket_id = st.session_state.get("selected_ticket_id")

    if not ticket_id:
        st.warning("No request selected.")
        return

    token = st.session_state.get("token")

    if not token:
        st.error("Your session has expired. Please sign in again.")
        return

    if st.button("← Back to My Requests"):
        st.session_state.pop("selected_ticket_id", None)
        st.rerun()

    try:
        with st.spinner("Loading request..."):
            ticket = get_ticket(
                token=token,
                ticket_id=ticket_id,
            )
    except Exception:
        st.error("We couldn't load this request.")
        return

    page_header(ticket["reference"])

    st.subheader(ticket["subject"])

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Status**")
        st.write(ticket["status"])

    with col2:
        st.write("**Created**")
        st.write(ticket["created_at"])

    st.write("**Last updated**")
    st.write(ticket["updated_at"])

    st.divider()

    st.write("**Original message**")
    st.info(ticket["original_message"])

    st.divider()

    st.subheader("Conversation")

    st.info(
        "Messaging will be available in a later task. "
        "You can view your original request here."
    )