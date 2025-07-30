import streamlit as st
import asyncio

# Set page configuration
st.set_page_config(
    page_title="Neurobiome Navigator",
    layout="wide"
)

# Initialize page state
if "page" not in st.session_state:
    st.session_state.page = "home"

# Get current page from URL or session state
page = st.query_params.get('page', [st.session_state.page])[0]

# Hide Streamlit menu and footer
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Sidebar Navigation
with st.sidebar:
    st.title("🧭 Navigate")
    
    # Navigation buttons
    if st.button("🏠 Home"):
        st.session_state.page = "home"
        st.rerun()
    if st.button("📊 Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()
    if st.button("🔍 Gut Insights"):
        st.session_state.page = "gut_insights"
        st.rerun()
    if st.button("🎯 Impulse Control"):
        st.session_state.page = "impulse_control"
        st.rerun()
    if st.button("🦷 Oral Health"):
        st.session_state.page = "oral_health"
        st.rerun()
    if st.button("📸 Snapshots"):
        st.session_state.page = "snapshots"
        st.rerun()

# Import components only when needed
from components.home_screen import create_home_screen
from components.minerva_dashboard import create_minerva_dashboard
from components.gut_insight_navigator import create_gut_insight_navigator
from components.impulse_control_spotlight import create_impulse_control_spotlight
from components.oral_health_pd_connection import create_oral_health_pd_connection
from components.sample_snapshots import create_sample_snapshots

if page == "home":
    create_home_screen()
elif page == "dashboard":
    create_minerva_dashboard()
elif page == "gut_insights":
    create_gut_insight_navigator()
elif page == "impulse_control":
    asyncio.run(create_impulse_control_spotlight())
elif page == "oral_health":
    asyncio.run(create_oral_health_pd_connection())
elif page == "snapshots":
    create_sample_snapshots()
