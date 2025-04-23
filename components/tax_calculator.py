import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.indian_tax_calculator import (
    calculate_80c_deduction,
    calculate_80d_deduction,
    calculate_ppf_maturity,
    calculate_nps_returns,
    calculate_fd_returns,
    calculate_tax_liability
)

def render_tax_calculator():
    st.header("Indian Tax & Investment Calculator")
    
    # Tab layout for different calculators
    tabs = st.tabs([
        "Income Tax Calculator",
        "Investment Calculator",
        "Tax Saving Investments",
        "Retirement Planning"
    ])
    
    # Income Tax Calculator
    with tabs[0]:
        st.subheader("Income Tax Calculator (FY 2024-25)")
        
        col1, col2 = st.columns(2)
        with col1:
            gross_income = st.number_input(
                "Annual Gross Income (₹)",
                min_value=0,
                value=500000,
                step=10000
            )
            regime = st.selectbox(
                "Select Tax Regime",
                ["old", "new"],
                format_func=lambda x: "Old Regime" if x == "old" else "New Regime"
            )
            
        with col2:
            with st.expander("Deductions (for Old Regime)"):
                deductions_80c = st.number_input(
                    "80C Investments (₹)",
                    min_value=0,
                    max_value=150000,
                    value=0,
                    step=1000
                )
                deductions_80d = st.number_input(
                    "80D Health Insurance (₹)",
                    min_value=0,
                    max_value=100000,
                    value=0,
                    step=1000
                )
                other_deductions = st.number_input(
                    "Other Deductions (₹)",
                    min_value=0,
                    value=0,
                    step=1000
                )
        
        # Calculate tax liability
        tax_calculation = calculate_tax_liability(
            gross_income,
            deductions_80c,
            deductions_80d,
            other_deductions,
            regime
        )
        
        # Display tax calculation results
        st.subheader("Tax Calculation Summary")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Old Regime Total Tax",
                f"₹{tax_calculation['old_regime']['total_tax']:,.2f}",
                f"Taxable Income: ₹{tax_calculation['old_regime']['taxable_income']:,.2f}"
            )
            
        with col2:
            st.metric(
                "New Regime Total Tax",
                f"₹{tax_calculation['new_regime']['total_tax']:,.2f}",
                f"Taxable Income: ₹{tax_calculation['new_regime']['taxable_income']:,.2f}"
            )
            
        # Recommendation
        st.success(
            f"Recommended Regime: {tax_calculation['recommended_regime'].title()} Regime "
            f"(Saves ₹{abs(tax_calculation['old_regime']['total_tax'] - tax_calculation['new_regime']['total_tax']):,.2f})"
        )
        
        # Tax breakdown visualization
        tax_breakdown = pd.DataFrame([
            {
                'Regime': 'Old Regime',
                'Component': 'Basic Tax',
                'Amount': tax_calculation['old_regime']['tax_amount']
            },
            {
                'Regime': 'Old Regime',
                'Component': 'Cess',
                'Amount': tax_calculation['old_regime']['cess']
            },
            {
                'Regime': 'New Regime',
                'Component': 'Basic Tax',
                'Amount': tax_calculation['new_regime']['tax_amount']
            },
            {
                'Regime': 'New Regime',
                'Component': 'Cess',
                'Amount': tax_calculation['new_regime']['cess']
            }
        ])
        
        fig = px.bar(
            tax_breakdown,
            x='Regime',
            y='Amount',
            color='Component',
            title='Tax Breakdown Comparison',
            barmode='stack'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Investment Calculator
    with tabs[1]:
        st.subheader("Fixed Deposit Calculator")
        
        col1, col2 = st.columns(2)
        with col1:
            fd_amount = st.number_input(
                "Principal Amount (₹)",
                min_value=1000,
                value=100000,
                step=1000
            )
            fd_tenure = st.number_input(
                "Tenure (Months)",
                min_value=1,
                max_value=120,
                value=12,
                step=1
            )
            
        with col2:
            fd_rate = st.number_input(
                "Interest Rate (%)",
                min_value=1.0,
                max_value=15.0,
                value=6.5,
                step=0.1
            )
            compounding = st.selectbox(
                "Interest Compounding",
                ["monthly", "quarterly", "half_yearly", "yearly"]
            )
        
        fd_returns = calculate_fd_returns(
            fd_amount,
            fd_tenure,
            fd_rate,
            compounding
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Maturity Amount",
                f"₹{fd_returns['maturity_amount']:,.2f}"
            )
        with col2:
            st.metric(
                "Interest Earned",
                f"₹{fd_returns['interest_earned']:,.2f}"
            )
        with col3:
            st.metric(
                "Effective Annual Rate",
                f"{fd_returns['effective_annual_rate']}%"
            )
    
    # Tax Saving Investments
    with tabs[2]:
        st.subheader("Section 80C Investment Planner")
        
        col1, col2 = st.columns(2)
        with col1:
            ppf_investment = st.number_input(
                "PPF Investment (₹)",
                min_value=0,
                max_value=150000,
                value=0,
                step=1000
            )
            elss_investment = st.number_input(
                "ELSS Mutual Funds (₹)",
                min_value=0,
                max_value=150000,
                value=0,
                step=1000
            )
            
        with col2:
            life_insurance = st.number_input(
                "Life Insurance Premium (₹)",
                min_value=0,
                max_value=150000,
                value=0,
                step=1000
            )
            nps_tier1 = st.number_input(
                "NPS Tier-1 Contribution (₹)",
                min_value=0,
                max_value=150000,
                value=0,
                step=1000
            )
        
        deductions = calculate_80c_deduction(
            ppf_investment,
            elss_investment,
            life_insurance,
            nps_tier1
        )
        
        st.metric(
            "Total 80C Investments",
            f"₹{deductions['total_investment']:,.2f}",
            f"Eligible Deduction: ₹{deductions['eligible_deduction']:,.2f}"
        )
        
        if deductions['excess_amount'] > 0:
            st.warning(
                f"Investments exceeding 80C limit by ₹{deductions['excess_amount']:,.2f}. "
                "Consider redirecting excess amounts to other tax-saving options."
            )
        
        # Investment breakdown pie chart
        if deductions['total_investment'] > 0:
            investment_data = pd.DataFrame([
                {'Category': 'PPF', 'Amount': ppf_investment},
                {'Category': 'ELSS', 'Amount': elss_investment},
                {'Category': 'Life Insurance', 'Amount': life_insurance},
                {'Category': 'NPS Tier-1', 'Amount': nps_tier1}
            ])
            
            fig = px.pie(
                investment_data,
                values='Amount',
                names='Category',
                title='80C Investment Distribution'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Retirement Planning
    with tabs[3]:
        st.subheader("Retirement Calculator")
        
        col1, col2 = st.columns(2)
        with col1:
            nps_monthly = st.number_input(
                "Monthly NPS Contribution (₹)",
                min_value=500,
                value=5000,
                step=500
            )
            years_to_retire = st.number_input(
                "Years to Retirement",
                min_value=1,
                max_value=40,
                value=25,
                step=1
            )
            
        with col2:
            equity_allocation = st.slider(
                "Equity Allocation (%)",
                min_value=0,
                max_value=75,  # NPS equity limit
                value=50
            )
            
            expected_equity_return = st.number_input(
                "Expected Equity Return (%)",
                min_value=8.0,
                max_value=15.0,
                value=12.0,
                step=0.5
            )
        
        nps_projection = calculate_nps_returns(
            nps_monthly,
            years_to_retire,
            equity_allocation,
            expected_equity_return
        )
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "Expected Corpus at Retirement",
                f"₹{nps_projection['total_corpus']:,.2f}"
            )
        with col2:
            st.metric(
                "Total Investment",
                f"₹{nps_projection['total_investment']:,.2f}",
                f"Returns: ₹{nps_projection['expected_returns']:,.2f}"
            )
        
        # Corpus breakdown
        corpus_data = pd.DataFrame([
            {'Component': 'Equity Corpus', 'Amount': nps_projection['equity_corpus']},
            {'Component': 'Debt Corpus', 'Amount': nps_projection['debt_corpus']}
        ])
        
        fig = px.pie(
            corpus_data,
            values='Amount',
            names='Component',
            title='Expected Retirement Corpus Distribution'
        )
        st.plotly_chart(fig, use_container_width=True)
