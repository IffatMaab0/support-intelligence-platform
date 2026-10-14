import streamlit as st
import requests

from api_client import list_agents, list_tickets
from components import empty_state, page_header


def render():
    page_header("All Tickets")

    token = st.session_state["token"]

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

        st.markdown(f"**{ticket['reference']}** — {ticket['subject']}")
        st.write(
            f"Status: {ticket['status']}  |  "
            f"Priority: {ticket['priority']}  |  "
            f"Assignee: {assigned_name}"
        )

        if st.button(
            "Open ticket",
            key=f"select_{ticket['id']}",
        ):
            st.session_state["manager_selected_ticket"] = ticket["id"]
            st.session_state["manager_page"] = "Ticket Oversight"
            st.rerun()

        st.divider()
