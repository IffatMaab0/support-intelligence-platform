import uuid

import requests
import streamlit as st

from api_client import (
    assign_ticket,
    create_ticket_message,
    create_ticket_note,
    get_ticket,
    list_agents,
    list_ticket_events,
    list_ticket_messages,
    list_ticket_notes,
    update_ticket_priority,
    update_ticket_status,
)
from components import format_datetime, page_header


def render():
    token = st.session_state["token"]
    ticket_id = st.session_state.get("manager_selected_ticket")

    if not ticket_id:
        st.info("Select a ticket from All Tickets to view its details.")
        return

    if st.button("← Back to All Tickets"):
        st.session_state.pop("manager_selected_ticket", None)
        st.session_state["manager_page"] = "All Tickets"
        st.rerun()

    try:
        ticket = get_ticket(
            token=token,
            ticket_id=ticket_id,
        )
        agents = list_agents(token)
    except requests.HTTPError as exc:
        if exc.response is not None and exc.response.status_code == 404:
            st.error("Ticket not found.")
        else:
            st.error(f"Could not load ticket: {exc}")
        return
    except requests.RequestException as exc:
        st.error(f"Could not load ticket details: {exc}")
        return

    agent_names = {
        agent["id"]: agent["display_name"]
        for agent in agents
    }
    assigned_name = (
        agent_names.get(ticket["assigned_agent_id"], "Unknown agent")
        if ticket["assigned_agent_id"]
        else "Unassigned"
    )

    page_header("Ticket Oversight")
    st.subheader(f"{ticket['reference']} — {ticket['subject']}")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write(f"**Status:** {ticket['status']}")

    with col2:
        st.write(f"**Priority:** {ticket['priority']}")

    with col3:
        st.write(f"**Assignee:** {assigned_name}")

    st.subheader("Customer message")
    st.write(ticket["original_message"])

    st.caption(
        f"Created: {format_datetime(ticket['created_at'])}  |  "
        f"Updated: {format_datetime(ticket['updated_at'])}"
    )

    tab_public, tab_internal, tab_activity = st.tabs(
        [
            "Public Conversation",
            "Internal Notes",
            "Activity",
        ]
    )

    with tab_public:
        st.subheader("Conversation")

        try:
            messages = list_ticket_messages(
                token=token,
                ticket_id=ticket["id"],
            )
        except requests.RequestException as exc:
            st.error(f"Could not load conversation: {exc}")
            messages = []

        if messages:
            for message in messages:
                st.write(f"**{message['author']}**")
                st.write(message["body"])
                st.caption(format_datetime(message["created_at"]))
                st.divider()
        else:
            st.caption("No follow-up messages yet.")

        st.subheader("Reply to customer")

        message_key = f"manager_message_{ticket['id']}"
        message_clear_flag = f"{message_key}_clear_after_success"

        if st.session_state.pop(message_clear_flag, False):
            st.session_state[message_key] = ""

        with st.form(key=f"manager_message_form_{ticket['id']}"):
            st.text_area(
                "Write a reply...",
                key=message_key,
                placeholder="Write a reply to the customer...",
            )
            submitted = st.form_submit_button("Send reply")

        if submitted:
            body = st.session_state.get(message_key, "").strip()

            if not body:
                st.warning("Please write a reply.")
            else:
                idempotency_state_key = (
                    f"manager_message_idempotency_{ticket['id']}"
                )
                idempotency_body_key = f"{idempotency_state_key}_body"

                if st.session_state.get(idempotency_body_key) != body:
                    st.session_state[idempotency_body_key] = body
                    st.session_state[idempotency_state_key] = str(uuid.uuid4())

                try:
                    with st.spinner("Sending reply..."):
                        create_ticket_message(
                            token=token,
                            ticket_id=ticket["id"],
                            body=body,
                            idempotency_key=st.session_state[
                                idempotency_state_key
                            ],
                        )

                    st.success("Reply saved.")
                    st.session_state[message_clear_flag] = True
                    st.session_state.pop(idempotency_state_key, None)
                    st.session_state.pop(idempotency_body_key, None)
                    st.rerun()
                except requests.RequestException:
                    st.error(
                        "We couldn't confirm that your reply was saved. "
                        "Please retry without changing the text."
                    )

    with tab_internal:
        st.warning("PRIVATE — Staff only. The customer cannot see these notes.")
        st.subheader("Internal Notes")

        try:
            notes = list_ticket_notes(
                token=token,
                ticket_id=ticket["id"],
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
                st.caption(format_datetime(note["created_at"]))
                st.divider()
        else:
            st.caption("No private notes yet.")

        note_key = f"manager_private_note_{ticket['id']}"
        note_clear_flag = f"{note_key}_clear_after_success"

        if st.session_state.pop(note_clear_flag, False):
            st.session_state[note_key] = ""

        with st.form(key=f"manager_private_note_form_{ticket['id']}"):
            st.text_area(
                "Add a private note...",
                key=note_key,
                placeholder="Only staff can see this note.",
            )
            note_submitted = st.form_submit_button("Add private note")

        if note_submitted:
            note_body = st.session_state.get(note_key, "").strip()

            if not note_body:
                st.warning("Please write a private note.")
            else:
                idempotency_state_key = (
                    f"manager_private_note_idempotency_{ticket['id']}"
                )
                idempotency_body_key = f"{idempotency_state_key}_body"

                if st.session_state.get(idempotency_body_key) != note_body:
                    st.session_state[idempotency_body_key] = note_body
                    st.session_state[idempotency_state_key] = str(uuid.uuid4())

                try:
                    with st.spinner("Saving private note..."):
                        create_ticket_note(
                            token=token,
                            ticket_id=ticket["id"],
                            body=note_body,
                            idempotency_key=st.session_state[
                                idempotency_state_key
                            ],
                        )

                    st.success("Private note added.")
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
                        "We couldn't confirm that the private note was saved. "
                        "Please retry without changing the text."
                    )

    with tab_activity:
        st.subheader("Activity")

        try:
            events = list_ticket_events(
                token=token,
                ticket_id=ticket["id"],
            )
        except requests.HTTPError as exc:
            st.error(f"Could not load activity: {exc}")
            events = []
        except requests.RequestException as exc:
            st.error(f"Could not load activity: {exc}")
            events = []

        if events:
            for event in events:
                st.write(f"**{event['event_type']}** — {event['actor']}")
                st.write(event["details"])
                st.caption(format_datetime(event["created_at"]))
                st.divider()
        else:
            st.caption("No activity yet.")

    st.divider()
    st.subheader("Ticket controls")

    status_options = {
        "Open": "open",
        "In review": "in_review",
        "Resolved": "resolved",
    }
    priority_options = ["low", "normal", "high", "urgent"]

    current_status_label = next(
        (
            label
            for label, value in status_options.items()
            if value == ticket["status"]
        ),
        "Open",
    )
    current_priority = (
        ticket["priority"]
        if ticket["priority"] in priority_options
        else "normal"
    )

    selected_status_label = st.selectbox(
        "Status",
        options=list(status_options.keys()),
        index=list(status_options.keys()).index(current_status_label),
        key=f"manager_status_{ticket['id']}",
    )
    selected_priority = st.selectbox(
        "Manual priority",
        options=priority_options,
        index=priority_options.index(current_priority),
        key=f"manager_priority_{ticket['id']}",
    )

    if st.button(
        "Save ticket changes",
        key=f"manager_save_changes_{ticket['id']}",
    ):
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
                update_ticket_priority(
                    token,
                    ticket["id"],
                    selected_priority,
                    updated_ticket["version"],
                )

            st.success("Ticket updated successfully.")
            st.rerun()
        except requests.HTTPError as exc:
            try:
                detail = exc.response.json().get(
                    "detail",
                    "Unable to update ticket.",
                )
            except Exception:
                detail = "Unable to update ticket."
            st.error(detail)

    st.divider()
    st.subheader("Assignment")
    st.write(f"Current assignee: **{assigned_name}**")

    agent_options = ["Unassigned"] + [
        agent["display_name"] for agent in agents
    ]
    current_index = agent_options.index(
        assigned_name if assigned_name in agent_options else "Unassigned"
    )
    selected_agent_name = st.selectbox(
        "Assign to",
        agent_options,
        index=current_index,
        key=f"manager_assignee_{ticket['id']}",
    )

    if st.button("Assign / Reassign", key=f"manager_assign_{ticket['id']}"):
        if selected_agent_name == "Unassigned":
            assigned_agent_id = None
        else:
            selected_agent = next(
                agent
                for agent in agents
                if agent["display_name"] == selected_agent_name
            )
            assigned_agent_id = selected_agent["id"]

        try:
            updated_ticket = assign_ticket(
                token=token,
                ticket_id=ticket["id"],
                assigned_agent_id=assigned_agent_id,
                expected_version=ticket["version"],
            )
            st.success(f"{updated_ticket['reference']} assignment updated.")
            st.rerun()
        except requests.HTTPError as exc:
            if exc.response is not None and exc.response.status_code == 409:
                st.error(
                    "This ticket changed after you opened it. "
                    "Refresh the ticket and reconsider the assignment."
                )
            else:
                st.error(f"Assignment failed: {exc}")
