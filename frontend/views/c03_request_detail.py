import streamlit as st

from api_client import (
    create_ticket_message,
    get_ticket,
    list_ticket_messages,
)
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

    # If a previous successful submission requested a form reset,
    # remove only the customer message widget state for this ticket.
    message_key = f"customer_message_{ticket_id}"


    if st.button("← Back to My Requests"):
        st.session_state.pop("selected_ticket_id", None)
        st.rerun()

    try:
        with st.spinner("Loading request..."):
            ticket = get_ticket(
                token=token,
                ticket_id=ticket_id,
            )

            messages = list_ticket_messages(
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
        st.write("**Created (UTC)**")
        st.write(ticket["created_at"])

    st.write("**Last updated (UTC)**")
    st.write(ticket["updated_at"])

    st.divider()

    # Immutable initial issue
    st.write("**Original message**")
    st.info(ticket["original_message"])

    st.divider()

    # Public conversation
    st.subheader("Conversation")

    if messages:
        for message in messages:
            st.write(f"**{message['author']}**")
            st.write(message["body"])
            st.caption(f"{message['created_at']} UTC")
            st.divider()
    else:
        st.caption("No follow-up messages yet.")

    st.subheader("Send a follow-up")

    with st.form(
        key=f"customer_message_form_{ticket_id}",
        clear_on_submit=True,
        ):
        st.text_area(
            "Write a follow-up...",
            key=message_key,
            placeholder="Write a follow-up...",
        )

        button_label = (
            "Reopen and send"
            if ticket["status"] == "resolved"
            else "Send follow-up"
        )

        submitted = st.form_submit_button(button_label)

    if submitted:
        body = st.session_state.get(message_key, "")

        try:
            with st.spinner("Sending follow-up..."):
                create_ticket_message(
                    token=token,
                    ticket_id=ticket_id,
                    body=body,
                )

            st.success("Follow-up saved.")
            st.rerun()

        except Exception:
            st.error(
                "We couldn't save your follow-up. "
                "Your message was not delivered."
            )
