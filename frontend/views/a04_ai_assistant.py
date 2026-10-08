import streamlit as st


def render():
    st.title("AI Assistant")
    st.caption("AI assistance is planned for Phase 2.")

    st.info(
        "The AI Assistant is not implemented yet. "
        "Use the Knowledge Library to browse approved support information."
    )

    st.text_input(
        "Ask a question",
        placeholder="AI questions will be available in Phase 2.",
        disabled=True,
    )

    st.button(
        "Ask AI",
        disabled=True,
    )

    st.divider()

    st.subheader("Knowledge Library")

    st.write(
        "Browse the current knowledge articles while AI assistance "
        "is not available."
    )

    if st.button("Open Knowledge Library"):
        st.session_state["agent_page"] = "Knowledge Library"
        st.rerun()