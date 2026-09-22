import streamlit as st
import requests

from api_client import (
    create_ticket_message,
    create_ticket_note,
    list_ticket_events,
    list_ticket_messages,
    list_ticket_notes,
    list_tickets,
    list_agents,
    assign_ticket,
    update_ticket_status,
    update_ticket_priority,
)
from components import page_header, empty_state


def render():
    page_header("All Tickets")

    token = st.session_state["token"]

    # -------------------------
    # Load tickets and agents
    # -------------------------
    try:
        result = list_tickets(
            token=token,
            skip=0,
            limit=100,
        )
        tickets = result["items"]
        agents = list_agents(token)
    except requests.RequestException as exc:
        st.error(f"Could not load ticket data: {exc}")
        return

    # -------------------------
    # Filters
    # -------------------------
    st.subheader("Filters")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        search = st.text_input(
            "Search",
            placeholder="Subject or message",
        )

    with col2:
        status_filter = st.selectbox(
            "Status",
            ["All", "open", "resolved"],
        )

    with col3:
        priority_filter = st.selectbox(
            "Manual priority",
            ["All", "normal", "high", "urgent"],
        )

    with col4:
        assignment_filter = st.selectbox(
            "Assignment",
            ["All", "Unassigned"] + [
                agent["display_name"] for agent in agents
            ],
        )

    col5, col6, _ = st.columns(3)

    with col5:
        apply_filters = st.button("Apply")

    with col6:
        clear_filters = st.button("Clear")

    if clear_filters:
        st.rerun()

    # -------------------------
    # Apply filters
    # -------------------------
    filtered_tickets = tickets

    if (
        apply_filters
        or search
        or status_filter != "All"
        or priority_filter != "All"
        or assignment_filter != "All"
    ):
        if search:
            search_text = search.lower()

            filtered_tickets = [
                ticket
                for ticket in filtered_tickets
                if search_text in ticket["subject"].lower()
                or search_text in ticket["original_message"].lower()
            ]

        if status_filter != "All":
            filtered_tickets = [
                ticket
                for ticket in filtered_tickets
                if ticket["status"] == status_filter
            ]

        if priority_filter != "All":
            filtered_tickets = [
                ticket
                for ticket in filtered_tickets
                if ticket["priority"] == priority_filter
            ]

        if assignment_filter != "All":
            if assignment_filter == "Unassigned":
                filtered_tickets = [
                    ticket
                    for ticket in filtered_tickets
                    if ticket["assigned_agent_id"] is None
                ]
            else:
                selected_agent = next(
                    agent
                    for agent in agents
                    if agent["display_name"] == assignment_filter
                )

                filtered_tickets = [
                    ticket
                    for ticket in filtered_tickets
                    if ticket["assigned_agent_id"] == selected_agent["id"]
                ]

    # -------------------------
    # Ticket table
    # -------------------------
    st.subheader("Tickets")

    if not filtered_tickets:
        empty_state("No tickets match the selected filters.")
        return

    agent_names = {
        agent["id"]: agent["display_name"]
        for agent in agents
    }

    for ticket in filtered_tickets:
        assigned_name = (
            agent_names.get(
                ticket["assigned_agent_id"],
                "Unknown agent",
            )
            if ticket["assigned_agent_id"]
            else "Unassigned"
        )

        st.markdown(
            f"**{ticket['reference']}** — {ticket['subject']}"
        )

        st.write(
            f"Status: {ticket['status']}  |  "
            f"Priority: {ticket['priority']}  |  "
            f"Assignee: {assigned_name}"
        )

        if st.button(
            "Select",
            key=f"select_{ticket['id']}",
        ):
            st.session_state["manager_selected_ticket"] = ticket["id"]
            st.rerun()

        st.divider()

    # -------------------------
    # Selected ticket
    # -------------------------
    selected_ticket_id = st.session_state.get(
        "manager_selected_ticket"
    )

    selected_ticket = next(
        (
            ticket
            for ticket in tickets
            if ticket["id"] == selected_ticket_id
        ),
        None,
    )

    if not selected_ticket:
        return

    try:
        messages = list_ticket_messages(
            token=token,
            ticket_id=selected_ticket["id"],
        )
    except requests.RequestException as exc:
        st.error(f"Could not load conversation: {exc}")
        return

    # -------------------------
    # Ticket tabs
    # -------------------------
    tab_public, tab_internal, tab_activity = st.tabs(
        [
            "Public Conversation",
            "Internal Notes",
            "Activity",
        ]
    )

    # -------------------------
    # Public Conversation
    # -------------------------
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

        message_key = f"manager_message_{selected_ticket['id']}"

        with st.form(
            key=f"manager_message_form_{selected_ticket['id']}",
            clear_on_submit=True,
        ):
            st.text_area(
                "Write a reply...",
                key=message_key,
                placeholder="Write a reply to the customer...",
            )

            submitted = st.form_submit_button("Send reply")

        if submitted:
            body = st.session_state.get(message_key, "")

            try:
                with st.spinner("Sending reply..."):
                    create_ticket_message(
                        token=token,
                        ticket_id=selected_ticket["id"],
                        body=body,
                    )

                st.success("Reply saved.")
                st.rerun()

            except Exception:
                st.error(
                    "We couldn't save your reply. "
                    "Your message was not delivered."
                )

    # -------------------------
    # Internal Notes
    # -------------------------
    with tab_internal:
        st.warning(
            "PRIVATE — Staff only. The customer cannot see these notes."
        )

        st.subheader("Internal Notes")

        try:
            notes = list_ticket_notes(
                token=token,
                ticket_id=selected_ticket["id"],
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

        note_key = f"manager_private_note_{selected_ticket['id']}"

        with st.form(
            key=f"manager_private_note_form_{selected_ticket['id']}",
            clear_on_submit=True,
        ):
            st.text_area(
                "Add a private note...",
                key=note_key,
                placeholder="Only staff can see this note.",
            )

            note_submitted = st.form_submit_button(
                "Add private note"
            )

        if note_submitted:
            note_body = st.session_state.get(note_key, "")

            try:
                with st.spinner("Saving private note..."):
                    create_ticket_note(
                        token=token,
                        ticket_id=selected_ticket["id"],
                        body=note_body,
                    )

                st.success("Private note added.")
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
                    "We couldn't save the private note."
                )

    # -------------------------
    # Activity
    # -------------------------
    with tab_activity:
        st.subheader("Activity")

        try:
            events = list_ticket_events(
                token=token,
                ticket_id=selected_ticket["id"],
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

    # -------------------------
    # Ticket controls
    # -------------------------
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
        if value == selected_ticket["status"]
    )

    selected_status_label = st.selectbox(
        "Status",
        options=list(status_options.keys()),
        index=list(status_options.keys()).index(
            current_status_label
        ),
        key=f"manager_status_{selected_ticket['id']}",
    )

    selected_priority = st.selectbox(
        "Manual priority",
        options=priority_options,
        index=priority_options.index(
            selected_ticket["priority"]
        ),
        key=f"manager_priority_{selected_ticket['id']}",
    )

    if st.button(
        "Save ticket changes",
        key=f"manager_save_changes_{selected_ticket['id']}",
    ):
        try:
            updated_ticket = selected_ticket

            if (
                status_options[selected_status_label]
                != selected_ticket["status"]
            ):
                updated_ticket = update_ticket_status(
                    token,
                    selected_ticket["id"],
                    status_options[selected_status_label],
                    selected_ticket["version"],
                )

            if selected_priority != updated_ticket["priority"]:
                updated_ticket = update_ticket_priority(
                    token,
                    selected_ticket["id"],
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

    # -------------------------
    # Assignment
    # -------------------------
    st.divider()

    st.subheader("Assignment")

    st.write(
        f"Selected ticket: **{selected_ticket['reference']}**"
    )

    selected_assignee_name = (
        agent_names.get(
            selected_ticket["assigned_agent_id"],
            "Unknown agent",
        )
        if selected_ticket["assigned_agent_id"]
        else "Unassigned"
    )

    st.write(
        f"Current assignee: **{selected_assignee_name}**"
    )

    agent_options = ["Unassigned"] + [
        agent["display_name"] for agent in agents
    ]

    current_index = agent_options.index(
        selected_assignee_name
        if selected_assignee_name in agent_options
        else "Unassigned"
    )

    selected_agent_name = st.selectbox(
        "Assign to",
        agent_options,
        index=current_index,
    )

    if st.button("Assign / Reassign"):
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
                ticket_id=selected_ticket["id"],
                assigned_agent_id=assigned_agent_id,
                expected_version=selected_ticket["version"],
            )

            st.session_state["manager_selected_ticket"] = (
                updated_ticket["id"]
            )

            st.success(
                f"{updated_ticket['reference']} assignment updated."
            )

            st.rerun()

        except requests.HTTPError as exc:
            if (
                exc.response is not None
                and exc.response.status_code == 409
            ):
                st.error(
                    "This ticket changed after you opened it. "
                    "Refresh the ticket and reconsider the assignment."
                )

                if st.button("Refresh"):
                    st.rerun()
            else:
                st.error(f"Assignment failed: {exc}")