import streamlit as st


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