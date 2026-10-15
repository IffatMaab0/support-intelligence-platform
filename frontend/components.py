from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import streamlit as st


DISPLAY_TIME_ZONE = ZoneInfo("Asia/Karachi")


def format_datetime(value: str | None) -> str:
    """Convert an API UTC timestamp into a friendly Pakistan-local display."""
    if not value:
        return "Not available"

    try:
        timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return value

    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)

    local_time = timestamp.astimezone(DISPLAY_TIME_ZONE)
    return local_time.strftime("%d %b %Y, %I:%M %p %Z")


def page_header(title):
    st.title(title)
    st.caption("Local demo")


def sidebar_placeholder(actor):
    st.sidebar.markdown("### Navigation")
    st.sidebar.info(f"{actor} navigation")


def empty_state(message="No data available yet."):
    st.info(message)


def disabled_button(label):
    st.button(label, disabled=True)


def not_implemented(message="This functionality is not implemented yet."):
    st.warning(message)


def staff_ticket_tabs():
    public_tab, private_tab, activity_tab = st.tabs(
        ["Public conversation", "Private notes", "Activity"]
    )

    with public_tab:
        empty_state("No customer-visible messages yet.")

    with private_tab:
        st.warning("PRIVATE — Internal staff notes only.")
        empty_state("No internal notes yet.")

    with activity_tab:
        empty_state("No activity available yet.")
