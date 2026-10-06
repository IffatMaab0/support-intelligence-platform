import streamlit as st

from api_client import (
    create_document,
    get_document,
    list_documents,
    update_document_status,
)


def render():
    token = st.session_state["token"]

    selected_document_id = st.session_state.get("selected_manager_document_id")

    if selected_document_id:
        render_document_detail(token, selected_document_id)
        return

    st.title("Knowledge Management")
    st.caption("Manage knowledge documents and their publication lifecycle.")

    if st.button("Create Draft"):
        st.session_state["show_create_document_form"] = True
        st.session_state.pop("replacement_document", None)
        st.rerun()

    if st.session_state.get("show_create_document_form"):
        render_create_form(token)
        st.divider()

    render_document_list(token)


def render_create_form(token: str):
    st.subheader("Create Knowledge Draft")

    replacement_document = st.session_state.get("replacement_document")

    default_policy_key = (
        replacement_document["policy_key"]
        if replacement_document
        else ""
    )

    default_title = (
        replacement_document["title"]
        if replacement_document
        else ""
    )

    default_topic = (
        replacement_document["topic"]
        if replacement_document
        else ""
    )

    default_audience = (
        replacement_document["audience"]
        if replacement_document
        else "public"
    )

    default_body = (
        replacement_document["body"]
        if replacement_document
        else ""
    )

    with st.form("create-knowledge-document"):
        policy_key = st.text_input(
            "Policy key",
            value=default_policy_key,
            placeholder="e.g. refund-policy",
        )

        title = st.text_input(
            "Title",
            value=default_title,
            placeholder="e.g. Refund Policy",
        )

        topic = st.text_input(
            "Topic",
            value=default_topic,
            placeholder="e.g. Refunds",
        )

        audience = st.selectbox(
            "Audience",
            ["public", "internal"],
            index=(
                ["public", "internal"].index(default_audience)
                if default_audience in ["public", "internal"]
                else 0
            ),
        )

        body = st.text_area(
            "Body",
            value=default_body,
            placeholder="Write the knowledge article...",
            height=250,
        )

        submitted = st.form_submit_button("Create Draft")

        if submitted:
            if not all(
                value.strip()
                for value in [policy_key, title, topic, body]
            ):
                st.error("Please complete all required fields.")
                return

            try:
                create_document(
                    token=token,
                    policy_key=policy_key.strip(),
                    title=title.strip(),
                    topic=topic.strip(),
                    audience=audience,
                    body=body.strip(),
                )
            except Exception:
                st.error(
                    "Knowledge document could not be created. Please try again."
                )
                return

            st.success("Knowledge draft created.")
            st.session_state["show_create_document_form"] = False
            st.session_state.pop("replacement_document", None)
            st.rerun()


def render_document_detail(token: str, document_id: int):
    if st.button("← Back to Knowledge Management"):
        st.session_state.pop("selected_manager_document_id", None)
        st.session_state.pop("confirm_document_action", None)
        st.rerun()

    try:
        document = get_document(token, document_id)
    except Exception:
        st.error("Knowledge documents could not be loaded. Please try again.")
        return

    st.title(document["title"])

    st.write(f"**Topic:** {document['topic']}")
    st.write(f"**Audience:** {document['audience'].capitalize()}")
    st.write(f"**Status:** {document['status'].capitalize()}")
    st.write(f"**Version:** {document['version']}")

    st.divider()

    st.markdown(document["body"])

    st.divider()

    status = document["status"]

    if status == "draft":
        if st.button("Activate"):
            st.session_state["confirm_document_action"] = "activate"
            st.rerun()

        if st.button("Archive"):
            st.session_state["confirm_document_action"] = "archive"
            st.rerun()

    elif status == "active":
        if st.button("Create Replacement Draft"):
            st.session_state["replacement_document"] = document
            st.session_state["show_create_document_form"] = True
            st.session_state.pop("selected_manager_document_id", None)
            st.rerun()

        if st.button("Archive"):
            st.session_state["confirm_document_action"] = "archive"
            st.rerun()

    action = st.session_state.get("confirm_document_action")

    if action == "activate":
        st.warning(
            "Publishing this document will archive the currently active "
            "version of this policy."
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Cancel"):
                st.session_state.pop("confirm_document_action", None)
                st.rerun()

        with col2:
            if st.button("Activate New Version"):
                try:
                    update_document_status(
                        token=token,
                        document_id=document_id,
                        status="active",
                        expected_version=document["version"],
                    )
                except Exception:
                    st.error(
                        "Knowledge document could not be activated. "
                        "Please try again."
                    )
                    return

                st.session_state.pop("confirm_document_action", None)
                st.success("Knowledge document activated.")
                st.rerun()

    elif action == "archive":
        st.warning("Are you sure you want to archive this document?")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Cancel"):
                st.session_state.pop("confirm_document_action", None)
                st.rerun()

        with col2:
            if st.button("Confirm Archive"):
                try:
                    update_document_status(
                        token=token,
                        document_id=document_id,
                        status="archived",
                        expected_version=document["version"],
                    )
                except Exception:
                    st.error(
                        "Knowledge document could not be archived. "
                        "Please try again."
                    )
                    return

                st.session_state.pop("confirm_document_action", None)
                st.success("Knowledge document archived.")
                st.rerun()


def render_document_list(token: str):
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
        placeholder="Search knowledge documents...",
    ).strip().lower()

    topics = sorted({document["topic"] for document in documents})
    audiences = sorted({document["audience"] for document in documents})
    statuses = sorted({document["status"] for document in documents})

    selected_topic = st.selectbox("Topic", ["All"] + topics)
    selected_audience = st.selectbox("Audience", ["All"] + audiences)
    selected_status = st.selectbox("Status", ["All"] + statuses)

    filtered_documents = documents

    if search:
        filtered_documents = [
            document
            for document in filtered_documents
            if search in document["title"].lower()
            or search in document["body"].lower()
            or search in document["policy_key"].lower()
        ]

    if selected_topic != "All":
        filtered_documents = [
            document
            for document in filtered_documents
            if document["topic"] == selected_topic
        ]

    if selected_audience != "All":
        filtered_documents = [
            document
            for document in filtered_documents
            if document["audience"] == selected_audience
        ]

    if selected_status != "All":
        filtered_documents = [
            document
            for document in filtered_documents
            if document["status"] == selected_status
        ]

    if not filtered_documents:
        st.info("No documents match your search.")
        return

    for document in filtered_documents:
        st.markdown(f"### {document['title']}")

        st.write(
            f"Topic: {document['topic']} • "
            f"Audience: {document['audience'].capitalize()} • "
            f"Status: {document['status'].capitalize()} • "
            f"Version: {document['version']}"
        )

        st.caption(f"Policy key: {document['policy_key']}")

        if st.button(
            "View document",
            key=f"manager-view-document-{document['id']}",
        ):
            st.session_state["selected_manager_document_id"] = document["id"]
            st.rerun()
            