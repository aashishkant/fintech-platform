import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from utils.advanced_analytics import (
    project_portfolio_growth,
    stress_test_portfolio,
    calculate_portfolio_metrics,
    generate_investment_recommendations
)

def render_portfolio_analytics():
    st.header("Advanced Portfolio Analytics")
    
    # Portfolio Input Section
    st.subheader("Current Portfolio")
    col1, col2 = st.columns(2)
    
    with col1:
        initial_investment = st.number_input(
            "Initial Investment (₹)",
            min_value=0,
            value=100000,
            step=10000
        )
        monthly_sip = st.number_input(
            "Monthly SIP (₹)",
            min_value=0,
            value=10000,
            step=1000
        )
    
    with col2:
        risk_profile = st.selectbox(
            "Risk Profile",
            ["Conservative", "Moderate", "Aggressive"],
            index=1
        )
        investment_horizon = st.slider(
            "Investment Horizon (Years)",
            min_value=1,
            max_value=30,
            value=10
        )
    
    # Portfolio Projection
    st.subheader("Portfolio Growth Projection")
    
    # Default parameters for Indian market
    expected_return = 12.0  # 12% annual return
    risk_free_rate = 4.0   # 4% risk-free rate
    volatility = 15.0      # 15% annual volatility
    
    # Advanced parameters in expander
    with st.expander("Advanced Parameters"):
        col1, col2 = st.columns(2)
        with col1:
            expected_return = st.slider(
                "Expected Annual Return (%)",
                min_value=0.0,
                max_value=30.0,
                value=12.0,
                step=0.5
            )
            volatility = st.slider(
                "Expected Volatility (%)",
                min_value=1.0,
                max_value=40.0,
                value=15.0,
                step=0.5
            )
        with col2:
            risk_free_rate = st.slider(
                "Risk-free Rate (%)",
                min_value=1.0,
                max_value=10.0,
                value=4.0,
                step=0.1
            )
    
    # Generate projections
    projections = project_portfolio_growth(
        initial_investment,
        monthly_sip,
        expected_return,
        risk_free_rate,
        investment_horizon,
        volatility
    )
    
    # Plot projections
    fig = go.Figure()
    
    # Add projection lines
    fig.add_trace(go.Scatter(
        x=projections['time_points']/12,
        y=projections['conservative'],
        name='Conservative (5th percentile)',
        line=dict(color='#FF9999')
    ))
    
    fig.add_trace(go.Scatter(
        x=projections['time_points']/12,
        y=projections['moderate'],
        name='Expected (50th percentile)',
        line=dict(color='#66B2FF')
    ))
    
    fig.add_trace(go.Scatter(
        x=projections['time_points']/12,
        y=projections['aggressive'],
        name='Aggressive (95th percentile)',
        line=dict(color='#99FF99')
    ))
    
    fig.update_layout(
        title='Portfolio Growth Projections',
        xaxis_title='Years',
        yaxis_title='Portfolio Value (₹)',
        template='plotly_white',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Stress Testing
    st.subheader("Stress Testing")
    
    # Sample portfolio for stress testing
    portfolio = {
        'Equity': initial_investment * 0.6,
        'Debt': initial_investment * 0.3,
        'Gold': initial_investment * 0.05,
        'Real Estate': initial_investment * 0.05
    }
    
    scenarios = ['market_crash', 'interest_rate_hike', 'currency_crisis']
    stress_results = {}
    
    for scenario in scenarios:
        stress_results[scenario] = stress_test_portfolio(portfolio, scenario)
    
    # Create stress test visualization
    stress_data = []
    for scenario in scenarios:
        for asset, value in stress_results[scenario].items():
            stress_data.append({
                'Scenario': scenario.replace('_', ' ').title(),
                'Asset': asset,
                'Value': value,
                'Change': (value - portfolio[asset]) / portfolio[asset] * 100
            })
    
    stress_df = pd.DataFrame(stress_data)
    
    fig = px.bar(
        stress_df,
        x='Scenario',
        y='Change',
        color='Asset',
        barmode='group',
        title='Portfolio Stress Test Results',
        labels={'Change': 'Change (%)'}
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Investment Recommendations
    st.subheader("Personalized Recommendations")
    recommendations = generate_investment_recommendations(
        risk_profile.lower(),
        investment_horizon,
        monthly_sip
    )
    
    for rec in recommendations:
        if rec['type'] == 'allocation':
            # Display allocation as a pie chart
            allocation_df = pd.DataFrame([
                {'Asset': k, 'Percentage': v}
                for k, v in rec['data'].items()
            ])
            
            fig = px.pie(
                allocation_df,
                values='Percentage',
                names='Asset',
                title='Recommended Asset Allocation',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig, use_container_width=True)
        elif rec['type'] == 'warning':
            st.warning(rec['message'])
        elif rec['type'] == 'caution':
            st.warning(rec['message'])
        elif rec['type'] == 'suggestion':
            st.info(rec['message'])
        elif rec['type'] == 'opportunity':
            st.success(rec['message'])
