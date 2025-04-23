import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from utils.financial_calculations import calculate_emi

def generate_loan_amortization(principal: float, rate: float, tenure: int) -> pd.DataFrame:
    """Generate loan amortization schedule."""
    rate = rate / (12 * 100)
    periods = tenure * 12
    emi = calculate_emi(principal, rate * 1200, tenure)

    schedule = []
    balance = principal

    for period in range(1, periods + 1):
        interest = balance * rate
        principal_paid = emi - interest
        balance = balance - principal_paid

        schedule.append({
            'Period': period,
            'EMI': emi,
            'Principal': principal_paid,
            'Interest': interest,
            'Balance': max(0, balance)
        })

    return pd.DataFrame(schedule)

def process_portfolio_data(investments: dict) -> pd.DataFrame:
    """Process investment portfolio data."""
    data = []
    for category, amount in investments.items():
        data.append({
            'Category': category,
            'Amount': amount,
            'Percentage': amount
        })
    df = pd.DataFrame(data)
    df['Percentage'] = (df['Amount'] / df['Amount'].sum() * 100).round(2)
    return df

def generate_market_data() -> pd.DataFrame:
    """Generate sample market data for visualization."""
    dates = pd.date_range(start='2023-01-01', end=datetime.now(), freq='D')
    indices = ['NIFTY 50', 'SENSEX', 'NIFTY Bank']

    data = []
    for index in indices:
        base = 100
        values = []
        for _ in range(len(dates)):
            change = np.random.normal(0, 1)
            base *= (1 + change/100)
            values.append(base)

        for date, value in zip(dates, values):
            data.append({
                'Date': date,
                'Index': index,
                'Value': value
            })

    return pd.DataFrame(data)