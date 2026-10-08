import requests
import streamlit as st

from api_client import get_system_status


def render():
    token = st.session_state["token"]

    st.title("System Status")
    st.caption("Manager-only service and application status.")

    if st.button("Refresh"):
        st.rerun()

    try:
        status = get_system_status(token)
    except requests.HTTPError as exc:
        response = exc.response

        if response is not None and response.status_code == 403:
            st.error("You do not have permission to view system status.")
        elif response is not None and response.status_code == 503:
            st.error("The application service is currently unavailable.")
        else:
            st.error("Unable to load system status.")
        return
    except requests.RequestException:
        st.error(
            "The application service is currently unavailable. "
            "Please try again."
        )
        return

    st.subheader("Services")

    api_status = status["api"]["status"]
    database_status = status["database"]["status"]

    col1, col2 = st.columns(2)

    with col1:
        st.metric("API", api_status)

    with col2:
        st.metric("Database", database_status)

    st.subheader("Application")

    application = status["application"]

    st.write(f"**Version:** {application['version']}")
    st.write(f"**Environment:** {application['environment']}")

    st.subheader("AI Modules")

    ai = status["ai"]

    st.write(f"**AI Assistant:** {ai['assistant']}")
    st.write(
        f"**Ticket Classification:** "
        f"{ai['ticket_classification']}"
    )
    st.write(
        f"**Escalation Risk:** "
        f"{ai['escalation_risk']}"
    )