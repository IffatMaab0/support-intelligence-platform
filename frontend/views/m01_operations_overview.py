import streamlit as st

from api_client import get_dashboard_summary
from components import page_header


def render():
    page_header("Operations overview")

    token = st.session_state["token"]

    try:
        summary = get_dashboard_summary(token)
    except Exception:
        st.error("Summary unavailable")
        return

    if st.button("Refresh"):
        st.rerun()

    st.caption(
        f"Data-as-of UTC: {summary['data_as_of']}"
    )

    metrics = summary["metrics"]

    st.subheader("Metrics")

    cols = st.columns(5)

    metric_values = [
        ("All tickets", metrics["total"]),
        ("Open", metrics["open"]),
        ("In review", metrics["in_review"]),
        ("Resolved", metrics["resolved"]),
        ("Unassigned active", metrics["unassigned_active"]),
    ]

    for col, (label, value) in zip(cols, metric_values):
        with col:
            st.metric(label, value)

    st.subheader("Workload")

    workload_rows = []

    for row in summary["workload"]:
        workload_rows.append(
            {
                "Agent": row["agent"],
                "Open": row["open"],
                "In Review": row["in_review"],
                "Resolved": row["resolved"],
            }
        )

    st.table(workload_rows)

    st.subheader("Manual-priority breakdown")

    priority = summary["priority"]

    priority_rows = [
        {"Priority": "Low", "Tickets": priority["low"]},
        {"Priority": "Normal", "Tickets": priority["normal"]},
        {"Priority": "High", "Tickets": priority["high"]},
    ]

    st.table(priority_rows)

    st.subheader("Latest internal ticket events")

    activity = summary["recent_activity"]

    if not activity:
        st.info("No activity available.")
        return

    activity_rows = []

    for event in activity:
        activity_rows.append(
            {
                "Ticket": event["ticket_reference"],
                "Event": event["description"],
                "Actor": event["actor"],
                "Timestamp UTC": event["timestamp"],
            }
        )

    st.table(activity_rows)