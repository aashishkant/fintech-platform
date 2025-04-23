import streamlit as st
from components.loan_calculator import render_loan_calculator
from components.portfolio_viewer import render_portfolio_viewer
from components.market_insights import render_market_insights
from components.portfolio_analytics import render_portfolio_analytics
from components.tax_calculator import render_tax_calculator

# Page configuration (must be first Streamlit command)
st.set_page_config(
    page_title="Fingyan - Indian Financial Powerhouse",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
with open('assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

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