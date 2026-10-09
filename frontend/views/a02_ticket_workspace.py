
import uuid

import requests
import streamlit as st

from api_client import (
    create_ticket_message,
    create_ticket_note,
    get_ticket,
    list_ticket_events,
    list_ticket_messages,
    list_ticket_notes,
    update_ticket_status,
    update_ticket_priority,
)
from components import page_header


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
        messages = list_ticket_messages(
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

    tab_public, tab_internal, tab_activity = st.tabs(
        [
            "Public Conversation",
            "Internal Notes",
            "Activity",
        ]
    )

    # ---------------------------------------------------------
    # PUBLIC CONVERSATION
    # ---------------------------------------------------------
    with tab_public:
        st.subheader("Conversation")

        if messages:
            for message in messages:
                st.write(f"**{message['author']}**")
                st.write(message["body"])
                st.caption(f"{message['created_at']} UTC")
                st.divider()
        else:
            st.caption("No follow-up messages yet.")

        st.subheader("Reply to customer")

        message_key = f"staff_message_{ticket_id}"
        message_clear_flag = f"{message_key}_clear_after_success"

        # Reset the widget before it is created, but only after success.
        if st.session_state.pop(message_clear_flag, False):
            st.session_state[message_key] = ""

        with st.form(key=f"staff_message_form_{ticket_id}"):
            st.text_area(
                "Write a reply...",
                key=message_key,
                placeholder="Write a reply to the customer...",
            )

            submitted = st.form_submit_button("Send reply")

        if submitted:
            body = st.session_state.get(message_key, "").strip()

            if not body:
                st.warning("Please write a reply before sending.")
            else:
                idempotency_state_key = (
                    f"staff_message_idempotency_{ticket_id}"
                )
                idempotency_body_key = f"{idempotency_state_key}_body"

                # Reuse the key for the same text after a failed request.
                if st.session_state.get(idempotency_body_key) != body:
                    st.session_state[idempotency_body_key] = body
                    st.session_state[idempotency_state_key] = str(
                        uuid.uuid4()
                    )

                try:
                    with st.spinner("Sending reply..."):
                        create_ticket_message(
                            token=token,
                            ticket_id=ticket_id,
                            body=body,
                            idempotency_key=st.session_state[
                                idempotency_state_key
                            ],
                        )

                    st.success("Reply saved.")

                    # Clear the key and reset the widget on the next run.
                    st.session_state[message_clear_flag] = True
                    st.session_state.pop(idempotency_state_key, None)
                    st.session_state.pop(idempotency_body_key, None)
                    st.rerun()

                except Exception:
                    st.error(
                        "We couldn't confirm that your reply was saved. "
                        "Please retry without changing the text."
                    )

    # ---------------------------------------------------------
    # INTERNAL NOTES
    # ---------------------------------------------------------
    with tab_internal:
        st.warning(
            "PRIVATE — Staff only. The customer cannot see these notes."
        )

        st.subheader("Internal Notes")

        try:
            notes = list_ticket_notes(
                token=token,
                ticket_id=ticket_id,
            )
        except requests.HTTPError as exc:
            st.error(f"Could not load private notes: {exc}")
            notes = []
        except requests.RequestException as exc:
            st.error(f"Could not load private notes: {exc}")
            notes = []

        if notes:
            for note in notes:
                st.write(f"**{note['author']}**")
                st.write(note["body"])
                st.caption(f"{note['created_at']} UTC")
                st.divider()
        else:
            st.caption("No private notes yet.")

        note_key = f"private_note_{ticket_id}"
        note_clear_flag = f"{note_key}_clear_after_success"

        # Reset the widget before it is created, but only after success.
        if st.session_state.pop(note_clear_flag, False):
            st.session_state[note_key] = ""

        with st.form(key=f"private_note_form_{ticket_id}"):
            st.text_area(
                "Add a private note...",
                key=note_key,
                placeholder="Only staff can see this note.",
            )

            note_submitted = st.form_submit_button("Add private note")

        if note_submitted:
            note_body = st.session_state.get(note_key, "").strip()

            if not note_body:
                st.warning("Please write a note before saving.")
            else:
                idempotency_state_key = (
                    f"private_note_idempotency_{ticket_id}"
                )
                idempotency_body_key = f"{idempotency_state_key}_body"

                # Reuse the key for the same text after a failed request.
                if st.session_state.get(idempotency_body_key) != note_body:
                    st.session_state[idempotency_body_key] = note_body
                    st.session_state[idempotency_state_key] = str(
                        uuid.uuid4()
                    )

                try:
                    with st.spinner("Saving private note..."):
                        create_ticket_note(
                            token=token,
                            ticket_id=ticket_id,
                            body=note_body,
                            idempotency_key=st.session_state[
                                idempotency_state_key
                            ],
                        )

                    st.success("Private note added.")

                    # Clear the key and reset the widget on the next run.
                    st.session_state[note_clear_flag] = True
                    st.session_state.pop(idempotency_state_key, None)
                    st.session_state.pop(idempotency_body_key, None)
                    st.rerun()

                except requests.HTTPError as exc:
                    try:
                        detail = exc.response.json().get(
                            "detail",
                            "Unable to save private note.",
                        )
                    except Exception:
                        detail = "Unable to save private note."

                    st.error(detail)

                except requests.RequestException:
                    st.error(
                        "We couldn't confirm that the private note was "
                        "saved. Please retry without changing the text."
                    )

    # ---------------------------------------------------------
    # ACTIVITY
    # ---------------------------------------------------------
    with tab_activity:
        st.subheader("Activity")

        try:
            events = list_ticket_events(
                token=token,
                ticket_id=ticket_id,
            )
        except requests.HTTPError as exc:
            st.error(f"Could not load activity: {exc}")
            events = []
        except requests.RequestException as exc:
            st.error(f"Could not load activity: {exc}")
            events = []

        if events:
            for event in events:
                st.write(
                    f"**{event['event_type']}** — "
                    f"{event['actor']}"
                )
                st.write(event["details"])
                st.caption(f"{event['created_at']} UTC")
                st.divider()
        else:
            st.caption("No activity yet.")

    st.divider()

    # ---------------------------------------------------------
    # TICKET CONTROLS
    # ---------------------------------------------------------
    st.subheader("Ticket controls")

    status_options = {
        "Open": "open",
        "In review": "in_review",
        "Resolved": "resolved",
    }

    priority_options = ["low", "normal", "high"]

    current_status_label = next(
        label
        for label, value in status_options.items()
        if value == ticket["status"]
    )

    selected_status_label = st.selectbox(
        "Status",
        options=list(status_options.keys()),
        index=list(status_options.keys()).index(current_status_label),
    )

    selected_priority = st.selectbox(
        "Manual priority",
        options=priority_options,
        index=priority_options.index(ticket["priority"]),
    )

    if st.button("Save ticket changes"):
        try:
            updated_ticket = ticket

            if status_options[selected_status_label] != ticket["status"]:
                updated_ticket = update_ticket_status(
                    token,
                    ticket["id"],
                    status_options[selected_status_label],
                    ticket["version"],
                )

            if selected_priority != updated_ticket["priority"]:
                updated_ticket = update_ticket_priority(
                    token,
                    ticket["id"],
                    selected_priority,
                    updated_ticket["version"],
                )

            st.success("Ticket updated successfully.")
            st.rerun()

        except requests.HTTPError as exc:
            detail = exc.response.json().get(
                "detail",
                "Unable to update ticket.",
            )
            st.error(detail)
