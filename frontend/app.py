import streamlit as st

from api_client import logout
from views import (
    s00_sign_in,
    c01_my_requests,
    c02_submit_request,
    c03_request_detail,
    a01_my_queue,
    m01_operations_overview,
    m02_all_tickets,
    a02_ticket_workspace,
    m03_ticket_oversight,
)

st.set_page_config(
    page_title="ResolveX",
    layout="wide",
)


def clear_session():
    st.session_state.clear()


def show_login():
    s00_sign_in.render()

def require_role(required_role):
    user = st.session_state.get("user")

    if not user or user["role"] != required_role:
        st.error("Access denied.")
        st.stop()

def show_customer_navigation():
    require_role("customer")
    if st.session_state.get("selected_ticket_id"):
        c03_request_detail.render()
        return
    st.sidebar.markdown("### Navigation")

    page = st.sidebar.radio(
        "Customer",
        [
            "My Requests",
            "Submit a Request",
            "Help Centre",
        ],
    )

    if page == "My Requests":
        c01_my_requests.render()
    elif page == "Submit a Request":
        c02_submit_request.render()
    elif page == "Help Centre":
        st.title("Help Centre")
        st.info("Help Centre will be implemented in a later task.")


def show_agent_navigation():
    require_role("agent")
    st.sidebar.markdown("### Navigation")

    if st.session_state.get("selected_ticket_id"):
        a02_ticket_workspace.render()
        return

    page = st.sidebar.radio(
        "Agent",
        [
            "My Queue",
            "Knowledge Library",
            "AI Assistant — Phase 2",
        ],
    )

    if page == "My Queue":
        a01_my_queue.render()
    elif page == "Knowledge Library":
        st.title("Knowledge Library")
        st.info("Knowledge Library will be implemented in a later task.")
    elif page == "AI Assistant — Phase 2":
        st.title("AI Assistant")
        st.warning("Unavailable — planned for Phase 2.")


def show_manager_navigation():
    require_role("manager")
    st.sidebar.markdown("### Navigation")

    page = st.sidebar.radio(
        "Manager/Admin",
        [
            "Operations Overview",
            "All Tickets",
            "Ticket Oversight",
            "Team",
            "Knowledge Management",
            "System Status",
            "AI Review — Phase 2",
        ],
    )

    if page == "Operations Overview":
        m01_operations_overview.render()
    elif page == "All Tickets":
        m02_all_tickets.render()
    elif page == "Team":
        st.title("Team")
        st.info("Team management will be implemented in a later task.")
    elif page == "Knowledge Management":
        st.title("Knowledge Management")
        st.info("Knowledge management will be implemented in a later task.")
    elif page == "System Status":
        st.title("System Status")
        st.info("System status will be implemented in a later task.")
    elif page == "AI Review — Phase 2":
        st.title("AI Review")
        st.warning("Unavailable — planned for Phase 2.")
    elif page == "Ticket Oversight":
        m03_ticket_oversight.render()    


if "token" not in st.session_state or "user" not in st.session_state:
    show_login()
    st.stop()


user = st.session_state["user"]

st.sidebar.markdown("## ResolveX")
st.sidebar.caption("Local demo")

st.sidebar.write(f"**Logged in as:** {user['display_name']}")
st.sidebar.write(f"**Role:** {user['role'].title()}")

if st.sidebar.button("Logout"):
    logout(st.session_state["token"])
    clear_session()
    st.rerun()


if user["role"] == "customer":
    show_customer_navigation()

elif user["role"] == "agent":
    show_agent_navigation()

elif user["role"] == "manager":
    show_manager_navigation()

else:
    clear_session()
    st.error("Unknown user role.")