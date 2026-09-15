import streamlit as st

from views import (
    s00_sign_in,
    c01_my_requests,
    a01_my_queue,
    m01_operations_overview,
)

st.set_page_config(
    page_title="ResolveX",
    layout="wide",
)

st.sidebar.markdown("## ResolveX")
st.sidebar.caption("Local demo")

preview = st.sidebar.selectbox(
    "Preview screen",
    [
        "S00 — Sign in",
        "C01 — My requests",
        "A01 — My queue",
        "M01 — Operations overview",
    ],
)

if preview == "S00 — Sign in":
    s00_sign_in.render()
elif preview == "C01 — My requests":
    c01_my_requests.render()
elif preview == "A01 — My queue":
    a01_my_queue.render()
elif preview == "M01 — Operations overview":
    m01_operations_overview.render()