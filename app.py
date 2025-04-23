import streamlit as st
import os
from components.loan_calculator import render_loan_calculator
from components.portfolio_viewer import render_portfolio_viewer
from components.market_insights import render_market_insights
from components.portfolio_analytics import render_portfolio_analytics
from components.tax_calculator import render_tax_calculator

# Page configuration — MUST be first Streamlit command
st.set_page_config(
    page_title="Fingyan - Indian Financial Powerhouse",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ✅ Confirm app startup
st.write("✅ App started successfully.")

# Load custom CSS safely
css_path = 'assets/style.css'
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
else:
    st.warning("⚠️ CSS file not found at assets/style.css. Using default styles.")

# Main header
st.markdown("""
    <h1 style='text-align: center; color: #003366;'>Fingyan - Your Financial Command Center</h1>
    <p style='text-align: center; font-size: 18px;'>Unleashing Wealth Creation for India</p>
    """, unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.markdown("<h2 style='color: #1E90FF;'>Modules</h2>", unsafe_allow_html=True)
page = st.sidebar.radio(
    "Navigate",
    ["Market Insights", "Portfolio Analysis", "Portfolio Analytics", "Tax Planning", "Loan Calculator"],
    index=0
)

# Render selected page
if page == "Loan Calculator":
    render_loan_calculator()
elif page == "Portfolio Analysis":
    render_portfolio_viewer()
elif page == "Portfolio Analytics":
    render_portfolio_analytics()
elif page == "Tax Planning":
    render_tax_calculator()
else:
    render_market_insights()

# Footer
st.markdown("""
    <hr style='border: 1px solid #FFD700;'>
    <div style='text-align: center; color: #888;'>
        <p>Fingyan - Redefining Financial Excellence in India</p>
        <p>© 2025 Fingyan. All rights reserved.</p>
    </div>
    """, unsafe_allow_html=True)
