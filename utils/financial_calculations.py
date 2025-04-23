import numpy as np
from typing import Dict, List, Tuple

def calculate_emi(principal: float, rate: float, tenure: int) -> float:
    """Calculate EMI for a loan."""
    rate = rate / (12 * 100)  # Convert annual rate to monthly
    tenure = tenure * 12      # Convert years to months
    if rate == 0:
        return principal / tenure
    emi = principal * rate * (1 + rate)**tenure / ((1 + rate)**tenure - 1)
    return round(emi, 2)

def calculate_total_interest(principal: float, emi: float, tenure: int) -> float:
    """Calculate total interest payable."""
    total_payment = emi * tenure * 12
    return round(total_payment - principal, 2)

def optimize_prepayment_strategy(
    principal: float, 
    rate: float, 
    tenure: int, 
    monthly_surplus: float
) -> Dict[str, float]:
    """Optimize prepayment strategy based on user's surplus funds."""
    regular_emi = calculate_emi(principal, rate, tenure)
    regular_interest = calculate_total_interest(principal, regular_emi, tenure)

    # Test different prepayment scenarios
    best_strategy = {
        'monthly_prepayment': 0,
        'total_interest_saved': 0,
        'time_saved_months': 0
    }

    for prepayment in np.arange(0, monthly_surplus + 1000, 1000):
        new_tenure, total_interest = simulate_prepayment(
            principal, rate, tenure, regular_emi, prepayment
        )
        interest_saved = regular_interest - total_interest
        time_saved = tenure * 12 - new_tenure

        if interest_saved > best_strategy['total_interest_saved']:
            best_strategy = {
                'monthly_prepayment': prepayment,
                'total_interest_saved': interest_saved,
                'time_saved_months': time_saved
            }

    return best_strategy

def simulate_prepayment(
    principal: float,
    rate: float,
    tenure: int,
    emi: float,
    monthly_prepayment: float
) -> Tuple[int, float]:
    """Simulate loan prepayment scenario."""
    rate = rate / (12 * 100)  # Monthly rate
    remaining_principal = principal
    total_interest = 0
    months = 0

    while remaining_principal > 0 and months < tenure * 12:
        interest = remaining_principal * rate
        principal_paid = emi - interest + monthly_prepayment
        remaining_principal -= principal_paid
        total_interest += interest
        months += 1

    return months, total_interest

def calculate_returns(principal: float, rate: float, time: int, frequency: str = 'annual') -> float:
    """Calculate investment returns."""
    if frequency == 'annual':
        return round(principal * (1 + rate/100)**time, 2)
    elif frequency == 'monthly':
        return round(principal * (1 + rate/1200)**(time*12), 2)
    return round(principal * (1 + rate/100)**time, 2)

def calculate_sip_returns(monthly_investment: float, rate: float, time: int) -> float:
    """Calculate SIP (Systematic Investment Plan) returns."""
    rate = rate / 1200  # Monthly rate
    months = time * 12
    future_value = monthly_investment * ((1 + rate)**(months) - 1) * (1 + rate) / rate
    return round(future_value, 2)

def get_loan_recommendations(
    income: float,
    emi: float,
    existing_liabilities: float = 0
) -> List[Dict[str, str]]:
    """Generate personalized loan recommendations."""
    emi_to_income_ratio = (emi + existing_liabilities) / income * 100
    recommendations = []

    if emi_to_income_ratio > 50:
        recommendations.append({
            'type': 'warning',
            'message': 'Your EMI commitments exceed 50% of income. Consider reducing loan amount or extending tenure.'
        })
    elif emi_to_income_ratio > 35:
        recommendations.append({
            'type': 'caution',
            'message': 'EMI-to-income ratio is above 35%. Consider a prepayment strategy to reduce long-term costs.'
        })
    else:
        recommendations.append({
            'type': 'positive',
            'message': 'Your EMI-to-income ratio is healthy. Consider investing the surplus in mutual funds or SIPs.'
        })

    return recommendations