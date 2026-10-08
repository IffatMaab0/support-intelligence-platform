import streamlit as st


def render():
    st.title("AI Review")
    st.caption("AI review tools are planned for Phase 2.")

    st.info(
        "AI review is not implemented yet. "
        "No automated scores, classifications, or recommendations "
        "are available."
    )

    st.subheader("AI Review")

    st.button(
        "Run AI Review",
        disabled=True,
    )

    st.button(
        "Generate Risk Assessment",
        disabled=True,
    )