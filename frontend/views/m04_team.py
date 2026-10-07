import requests
import streamlit as st

from api_client import create_agent, list_admin_agents, update_agent    


def render():
    token = st.session_state["token"]

    st.title("Team")
    st.caption("Manage support agents.")

    if st.button("Add Agent"):
        st.session_state["manager_team_mode"] = "add"
        st.rerun()

    mode = st.session_state.get("manager_team_mode")

    if mode == "add":
        render_add_agent(token)
        return

    if mode == "edit":
        render_edit_agent(token)
        return

    render_agent_list(token)


def render_agent_list(token: str):
    try:
        agents = list_admin_agents(token)
    except requests.HTTPError as exc:
        response = exc.response

        if response is not None and response.status_code == 403:
            st.error("You do not have permission to manage the team.")
        else:
            st.error("Unable to load the team.")
        return

    if not agents:
        st.info("No agents found.")
        return

    st.subheader("Agents")

    for agent in agents:
        status = "Active" if agent["is_active"] else "Inactive"

        col1, col2, col3, col4 = st.columns([2, 3, 1, 1])

        with col1:
            st.write(agent["display_name"])

        with col2:
            st.write(agent["email"])

        with col3:
            st.write(status)

        with col4:
            if st.button("Edit", key=f"edit_agent_{agent['id']}"):
                st.session_state["manager_team_edit_agent_id"] = agent["id"]
                st.session_state["manager_team_mode"] = "edit"
                st.rerun()


def render_add_agent(token: str):
    st.subheader("Add Agent")

    if st.button("Back to Team"):
        st.session_state["manager_team_mode"] = None
        st.rerun()

    with st.form("create_agent_form"):
        display_name = st.text_input("Display Name")
        email = st.text_input("Email")
        initial_password = st.text_input(
            "Initial Password",
            type="password",
        )

        submitted = st.form_submit_button("Create Agent")

    if not submitted:
        return

    if not display_name.strip():
        st.error("Display Name is required.")
        return

    if not email.strip():
        st.error("Email is required.")
        return

    if not initial_password:
        st.error("Initial Password is required.")
        return

    try:
        create_agent(
            token=token,
            display_name=display_name,
            email=email,
            initial_password=initial_password,
        )

    except requests.HTTPError as exc:
        response = exc.response

        if response is not None and response.status_code == 409:
            try:
                detail = response.json().get(
                    "detail",
                    "An account with this email already exists.",
                )
            except ValueError:
                detail = "An account with this email already exists."

            st.error(detail)
            return

        if response is not None and response.status_code == 403:
            st.error("You do not have permission to create agents.")
            return

        st.error("Unable to create the agent.")
        return

    st.success("Agent created successfully.")
    st.session_state["manager_team_mode"] = None
    st.rerun()                      


def render_edit_agent(token: str):
    agent_id = st.session_state.get("manager_team_edit_agent_id")

    if not agent_id:
        st.session_state["manager_team_mode"] = None
        st.rerun()

    try:
        agents = list_admin_agents(token)
    except requests.HTTPError:
        st.error("Unable to load the team.")
        return

    agent = next(
        (item for item in agents if item["id"] == agent_id),
        None,
    )

    if agent is None:
        st.error("Agent not found.")
        return

    st.subheader("Edit Agent")

    if st.button("Back to Team"):
        st.session_state["manager_team_mode"] = None
        st.session_state["manager_team_edit_agent_id"] = None
        st.rerun()

    with st.form("edit_agent_form"):
        display_name = st.text_input(
            "Display Name",
            value=agent["display_name"],
        )

        is_active = st.checkbox(
            "Active",
            value=agent["is_active"],
        )

        submitted = st.form_submit_button("Save Changes")

    if not submitted:
        return

    if not display_name.strip():
        st.error("Display Name is required.")
        return

    try:
        update_agent(
            token=token,
            agent_id=agent["id"],
            display_name=display_name,
            is_active=is_active,
            expected_version=agent["version"],
        )
    except requests.HTTPError as exc:
        response = exc.response

        if response is not None and response.status_code == 409:
            try:
                detail = response.json().get(
                    "detail",
                    "This agent was updated by someone else. Please refresh and try again.",
                )
            except ValueError:
                detail = "This agent was updated by someone else. Please refresh and try again."

            st.error(detail)
            return

        if response is not None and response.status_code == 403:
            st.error("You do not have permission to edit agents.")
            return

        st.error("Unable to update the agent.")
        return

    st.success("Agent updated successfully.")
    st.session_state["manager_team_mode"] = None
    st.session_state["manager_team_edit_agent_id"] = None
    st.rerun()    