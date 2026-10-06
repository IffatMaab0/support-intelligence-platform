import streamlit as st

from api_client import get_document, list_documents


def render():
    token = st.session_state["token"]

    selected_document_id = st.session_state.get("selected_document_id")

    if selected_document_id:
        render_document_reader(token, selected_document_id)
        return

    render_document_list(token)


def render_document_list(token: str):
    st.title("Help Centre")
    st.caption("Find answers to common questions and policies.")

    try:
        response = list_documents(token)
        documents = response["items"]
    except Exception:
        st.error("Knowledge documents could not be loaded. Please try again.")
        return

    if not documents:
        st.info("No knowledge articles are currently available.")
        return

    search = st.text_input(
        "Search",
        placeholder="Search knowledge articles...",
    ).strip().lower()

    topics = sorted(
        {document["topic"] for document in documents}
    )

    selected_topic = st.selectbox(
        "Topic",
        ["All"] + topics,
    )

    filtered_documents = documents

    if search:
        filtered_documents = [
            document
            for document in filtered_documents
            if search in document["title"].lower()
            or search in document["body"].lower()
        ]

    if selected_topic != "All":
        filtered_documents = [
            document
            for document in filtered_documents
            if document["topic"] == selected_topic
        ]

    if not filtered_documents:
        st.info("No documents match your search.")
        return

    for document in filtered_documents:
        st.markdown(f"### {document['title']}")
        st.write(f"Topic: {document['topic']}")

        if st.button(
            "Read article",
            key=f"read-document-{document['id']}",
        ):
            st.session_state["selected_document_id"] = document["id"]
            st.rerun()


def render_document_reader(token: str, document_id: int):
    if st.button("← Back to Help Centre"):
        st.session_state.pop("selected_document_id", None)
        st.rerun()

    try:
        document = get_document(token, document_id)
    except Exception:
        st.error("Knowledge documents could not be loaded. Please try again.")
        return

    st.title(document["title"])
    st.write(f"Topic: {document['topic']}")

    st.divider()

    st.markdown(document["body"])