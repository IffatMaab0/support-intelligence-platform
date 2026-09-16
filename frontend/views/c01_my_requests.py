import streamlit as st

from api_client import list_tickets
from components import page_header, empty_state


def render():
    page_header("My Requests")

    token = st.session_state.get("token")

    if "ticket_search" not in st.session_state:
        st.session_state["ticket_search"] = ""

    if "ticket_status" not in st.session_state:
        st.session_state["ticket_status"] = "All"

    if "ticket_page" not in st.session_state:
        st.session_state["ticket_page"] = 0

    if not token:
        st.error("Your session has expired. Please sign in again.")
        return

    search = st.text_input(
        "Search",
        value=st.session_state.get("ticket_search", ""),
        placeholder="Search subject or message",
    )

    status_filter = st.selectbox(
        "Status",
        ["All", "Open", "Resolved"],
        index=0,
    )

    col1, col2 = st.columns(2)

    with col1:
        apply = st.button("Apply")

    with col2:
        clear = st.button("Clear")

    if clear:
        st.session_state["ticket_search"] = ""
        st.session_state["ticket_status"] = "All"
        st.session_state["ticket_page"] = 0
        st.rerun()

    if apply:
        st.session_state["ticket_search"] = search
        st.session_state["ticket_status"] = status_filter
        st.session_state["ticket_page"] = 0

    search_value = st.session_state.get("ticket_search", "")
    status_value = st.session_state.get("ticket_status", "All")
    page = st.session_state.get("ticket_page", 0)

    skip = page * 10

    try:
        result = list_tickets(
            token=token,
            search=search_value.strip() or None,
            skip=skip,
            limit=10,
        )
    except Exception:
        st.error(
            "We couldn't load your requests. "
            "Please try again."
        )
        return

    tickets = result["items"]
    total = result["total"]

    if status_value != "All":
        tickets = [
            ticket
            for ticket in tickets
            if ticket["status"].lower() == status_value.lower()
        ]

    if not tickets:
        empty_state("No support requests found.")
        st.caption(f"Scoped total: {total}")
    else:
        st.subheader("Your requests")

        for ticket in tickets:
            col1, col2, col3 = st.columns([2, 4, 2])

            with col1:
                st.write(f"**{ticket['reference']}**")

            with col2:
                st.write(ticket["subject"])
                st.caption(
                    f"Status: {ticket['status']} · "
                    f"Updated: {ticket['updated_at']}"
                )

            with col3:
                if st.button(
                    "Open",
                    key=f"open_ticket_{ticket['id']}",
                ):
                    st.session_state["selected_ticket_id"] = ticket["id"]
                    st.rerun()

            st.divider()

        st.caption(f"Ten rows • Scoped total: {total}")

    previous_disabled = page == 0
    next_disabled = skip + 10 >= total

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Previous", disabled=previous_disabled):
            st.session_state["ticket_page"] = page - 1
            st.rerun()

    with col2:
        if st.button("Next", disabled=next_disabled):
            st.session_state["ticket_page"] = page + 1
            st.rerun()