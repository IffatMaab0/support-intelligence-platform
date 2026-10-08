import requests 
import streamlit as st   

from api_client import get_document, list_documents


def render():
    token = st.session_state["token"]

    selected_document_id = st.session_state.get("selected_knowledge_document_id")

    if selected_document_id:
        render_document_reader(token, selected_document_id)
        return

    render_document_list(token)


def render_document_list(token: str):
    st.title("Knowledge Library")
    st.caption("Browse active knowledge articles available to support your work.")

    try:
        response = list_documents(token)
        documents = response["items"]
    except requests.RequestException:
        st.error(
            "The application service is currently unavailable. "
            "Please try again."
        )
        return

    if not documents:
        st.info("No knowledge articles are currently available.")
        return

    search = st.text_input(
        "Search",
        placeholder="Search knowledge articles...",
    ).strip().lower()

    topics = sorted({document["topic"] for document in documents})
    selected_topic = st.selectbox("Topic", ["All"] + topics)

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

        label = document["audience"].capitalize()
        st.caption(f"Topic: {document['topic']} • Audience: {label}")

        if st.button(
            "Read article",
            key=f"agent-read-document-{document['id']}",
        ):
            st.session_state["selected_knowledge_document_id"] = document["id"]
            st.rerun()


def render_document_reader(token: str, document_id: int):
    if st.button("← Back to Knowledge Library"):
        st.session_state.pop("selected_knowledge_document_id", None)
        st.rerun()

    try:
        document = get_document(token, document_id)
    except requests.RequestException:
        st.error(
            "The application service is currently unavailable. "
            "Please try again."
        )
        return

    st.title(document["title"])
    st.caption(
        f"Topic: {document['topic']} • "
        f"Audience: {document['audience'].capitalize()}"
    )

    st.divider()
    st.markdown(document["body"])