import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from utils.financial_calculations import (
    calculate_emi,
    calculate_total_interest,
    optimize_prepayment_strategy,
    get_loan_recommendations
)
from utils.data_processing import generate_loan_amortization

def render_loan_calculator():
    st.header("Advanced Loan Calculator")

    # Input Section
    with st.container():
        col1, col2, col3 = st.columns(3)

        with col1:
            loan_amount = st.number_input(
                "Loan Amount (₹)",
                min_value=10000,
                max_value=10000000,
                value=1000000,
                step=10000,
                help="Enter the total loan amount you wish to borrow"
            )

        with col2:
            interest_rate = st.number_input(
                "Interest Rate (%)",
                min_value=1.0,
                max_value=30.0,
                value=8.5,
                step=0.1,
                help="Annual interest rate"
            )

        with col3:
            tenure = st.number_input(
                "Tenure (Years)",
                min_value=1,
                max_value=30,
                value=20,
                step=1,
                help="Loan duration in years"
            )

    # Additional inputs for personalized analysis
    with st.expander("Personalized Analysis"):
        col1, col2 = st.columns(2)
        with col1:
            monthly_income = st.number_input(
                "Monthly Income (₹)",
                min_value=0,
                value=50000,
                step=5000
            )
            existing_emi = st.number_input(
                "Existing EMI Commitments (₹)",
                min_value=0,
                value=0,
                step=1000
            )

        with col2:
            monthly_surplus = st.number_input(
                "Monthly Surplus for Prepayment (₹)",
                min_value=0,
                value=10000,
                step=1000
            )

    # Calculate basic metrics
    emi = calculate_emi(loan_amount, interest_rate, tenure)
    total_interest = calculate_total_interest(loan_amount, emi, tenure)

    # Display key metrics
    st.subheader("Loan Overview")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Monthly EMI", f"₹{emi:,.2f}")
    with col2:
        st.metric("Total Interest", f"₹{total_interest:,.2f}")
    with col3:
        st.metric("Total Payment", f"₹{(loan_amount + total_interest):,.2f}")

    # Prepayment Analysis
    if monthly_surplus > 0:
        st.subheader("Prepayment Analysis")
        optimal_strategy = optimize_prepayment_strategy(
            loan_amount, interest_rate, tenure, monthly_surplus
        )

        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "Recommended Monthly Prepayment",
                f"₹{optimal_strategy['monthly_prepayment']:,.2f}"
            )
        with col2:
            st.metric(
                "Potential Interest Savings",
                f"₹{optimal_strategy['total_interest_saved']:,.2f}",
                f"Save {optimal_strategy['time_saved_months']} months"
            )

    # Personalized Recommendations
    if monthly_income > 0:
        st.subheader("Personalized Recommendations")
        recommendations = get_loan_recommendations(
            monthly_income, emi, existing_emi
        )
        for rec in recommendations:
            if rec['type'] == 'warning':
                st.error(rec['message'])
            elif rec['type'] == 'caution':
                st.warning(rec['message'])
            else:
                st.success(rec['message'])

    # Visualization Section
    st.subheader("Loan Analysis Visualizations")

    tab1, tab2 = st.tabs(["Amortization Schedule", "Payment Breakdown"])

    with tab1:
        # Generate amortization schedule
        schedule = generate_loan_amortization(loan_amount, interest_rate, tenure)

        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Principal',
            x=schedule['Period'],
            y=schedule['Principal'],
            marker_color='#FF6B6B'
        ))
        fig.add_trace(go.Bar(
            name='Interest',
            x=schedule['Period'],
            y=schedule['Interest'],
            marker_color='#4ECDC4'
        ))

        fig.update_layout(
            title='Monthly Payment Breakdown',
            barmode='stack',
            xaxis_title='Month',
            yaxis_title='Amount (₹)',
            template='plotly_white',
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        # Payment breakdown pie chart
        payment_data = pd.DataFrame([
            {'Component': 'Principal', 'Amount': loan_amount},
            {'Component': 'Total Interest', 'Amount': total_interest}
        ])

        fig = px.pie(
            payment_data,
            values='Amount',
            names='Component',
            title='Total Payment Breakdown',
            color_discrete_sequence=['#FF6B6B', '#4ECDC4']
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')

        st.plotly_chart(fig, use_container_width=True)