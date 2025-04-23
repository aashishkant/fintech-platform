import streamlit as st
import plotly.express as px
from utils.data_processing import process_portfolio_data
from utils.financial_calculations import calculate_returns, calculate_sip_returns

def render_portfolio_viewer():
    st.header("Investment Portfolio")
    
    # Portfolio Input
    st.subheader("Current Investments")
    col1, col2 = st.columns(2)
    
    with col1:
        equity = st.number_input("Equity (₹)", value=500000, step=10000)
        debt = st.number_input("Debt (₹)", value=300000, step=10000)
        
    with col2:
        gold = st.number_input("Gold (₹)", value=100000, step=10000)
        real_estate = st.number_input("Real Estate (₹)", value=2000000, step=100000)
    
    portfolio = {
        'Equity': equity,
        'Debt': debt,
        'Gold': gold,
        'Real Estate': real_estate
    }
    
    # Process portfolio data
    df = process_portfolio_data(portfolio)
    
    # Create pie chart
    fig = px.pie(
        df,
        values='Amount',
        names='Category',
        title='Portfolio Allocation',
        color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#FFE66D', '#1A535C']
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    st.plotly_chart(fig, use_container_width=True)
    
    # SIP Calculator
    st.subheader("SIP Calculator")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        monthly_sip = st.number_input(
            "Monthly Investment (₹)",
            min_value=500,
            max_value=1000000,
            value=10000,
            step=500
        )
    
    with col2:
        expected_return = st.number_input(
            "Expected Return (%)",
            min_value=1.0,
            max_value=30.0,
            value=12.0,
            step=0.5
        )
    
    with col3:
        investment_period = st.number_input(
            "Investment Period (Years)",
            min_value=1,
            max_value=40,
            value=10,
            step=1
        )
    
    # Calculate SIP returns
    total_investment = monthly_sip * 12 * investment_period
    future_value = calculate_sip_returns(monthly_sip, expected_return, investment_period)
    wealth_gained = future_value - total_investment
    
    # Display SIP metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Investment", f"₹{total_investment:,.2f}")
    with col2:
        st.metric("Expected Returns", f"₹{wealth_gained:,.2f}")
    with col3:
        st.metric("Future Value", f"₹{future_value:,.2f}")
