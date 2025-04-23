import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, date

def calculate_80c_deduction(
    ppf_investment: float = 0,
    elss_investment: float = 0,
    life_insurance_premium: float = 0,
    nps_tier1: float = 0,
    epf_contribution: float = 0
) -> Dict[str, float]:
    """Calculate deductions under section 80C."""
    total_investment = (
        ppf_investment +
        elss_investment +
        life_insurance_premium +
        nps_tier1 +
        epf_contribution
    )
    
    max_deduction = 150000  # ₹1.5 lakhs limit for 80C
    eligible_deduction = min(total_investment, max_deduction)
    
    return {
        'total_investment': total_investment,
        'eligible_deduction': eligible_deduction,
        'excess_amount': max(0, total_investment - max_deduction)
    }

def calculate_80d_deduction(
    health_insurance_self: float = 0,
    health_insurance_parents: float = 0,
    preventive_health_checkup: float = 0,
    parents_age_above_60: bool = False
) -> Dict[str, float]:
    """Calculate deductions under section 80D."""
    max_self = 25000  # Base limit for self and family
    max_parents = 50000 if parents_age_above_60 else 25000
    max_preventive = 5000  # Sub-limit for preventive health checkup
    
    # Adjust preventive health checkup within limits
    preventive_self = min(preventive_health_checkup/2, max_preventive/2)
    preventive_parents = min(preventive_health_checkup/2, max_preventive/2)
    
    self_total = min(health_insurance_self + preventive_self, max_self)
    parents_total = min(health_insurance_parents + preventive_parents, max_parents)
    
    return {
        'self_family_deduction': self_total,
        'parents_deduction': parents_total,
        'total_deduction': self_total + parents_total
    }

def calculate_ppf_maturity(
    initial_investment: float,
    yearly_contribution: float,
    current_interest_rate: float = 7.1
) -> Dict[str, float]:
    """Calculate PPF maturity amount (15-year period)."""
    years = 15
    rate = current_interest_rate / 100
    
    # Initialize arrays for year-wise calculations
    balance = np.zeros(years + 1)
    interest = np.zeros(years)
    balance[0] = initial_investment
    
    for year in range(years):
        # Interest is calculated on minimum balance between 5th of each month
        balance[year + 1] = balance[year] + yearly_contribution
        interest[year] = balance[year] * rate
        balance[year + 1] += interest[year]
    
    return {
        'maturity_amount': float(balance[-1]),
        'total_investment': initial_investment + yearly_contribution * years,
        'total_interest_earned': float(sum(interest)),
        'year_wise_interest': interest.tolist()
    }

def calculate_nps_returns(
    monthly_contribution: float,
    years_to_retirement: int,
    equity_allocation: float = 50,  # In percentage
    expected_equity_return: float = 12,
    expected_debt_return: float = 8
) -> Dict[str, float]:
    """Project NPS returns based on asset allocation."""
    total_months = years_to_retirement * 12
    monthly_equity = monthly_contribution * (equity_allocation / 100)
    monthly_debt = monthly_contribution * (1 - equity_allocation / 100)
    
    # Monthly return rates
    equity_monthly_return = (1 + expected_equity_return/100)**(1/12) - 1
    debt_monthly_return = (1 + expected_debt_return/100)**(1/12) - 1
    
    # Compound monthly for both equity and debt portions
    equity_corpus = monthly_equity * (((1 + equity_monthly_return)**total_months - 1) / equity_monthly_return)
    debt_corpus = monthly_debt * (((1 + debt_monthly_return)**total_months - 1) / debt_monthly_return)
    
    total_corpus = equity_corpus + debt_corpus
    total_investment = monthly_contribution * total_months
    
    return {
        'total_corpus': total_corpus,
        'total_investment': total_investment,
        'equity_corpus': equity_corpus,
        'debt_corpus': debt_corpus,
        'expected_returns': total_corpus - total_investment
    }

def calculate_fd_returns(
    principal: float,
    tenure_months: int,
    interest_rate: float,
    compounding_frequency: str = 'quarterly'
) -> Dict[str, float]:
    """Calculate Fixed Deposit returns with different compounding frequencies."""
    rate = interest_rate / 100
    
    compounding_map = {
        'monthly': 12,
        'quarterly': 4,
        'half_yearly': 2,
        'yearly': 1
    }
    
    n = compounding_map.get(compounding_frequency, 4)  # Default to quarterly
    t = tenure_months / 12
    
    # Compound Interest Formula: A = P(1 + r/n)^(nt)
    maturity_amount = principal * (1 + rate/n)**(n*t)
    interest_earned = maturity_amount - principal
    
    return {
        'maturity_amount': round(maturity_amount, 2),
        'interest_earned': round(interest_earned, 2),
        'effective_annual_rate': round(((1 + rate/n)**(n) - 1) * 100, 2)
    }

def calculate_tax_liability(
    gross_income: float,
    deductions_80c: float = 0,
    deductions_80d: float = 0,
    other_deductions: float = 0,
    regime: str = 'old'
) -> Dict[str, float]:
    """Calculate income tax liability under both old and new tax regimes."""
    
    # Standard deduction
    standard_deduction = 50000 if regime == 'old' else 0
    
    # Calculate taxable income
    total_deductions = (
        deductions_80c +
        deductions_80d +
        other_deductions +
        standard_deduction
    ) if regime == 'old' else 0
    
    taxable_income = max(0, gross_income - total_deductions)
    
    # Tax slabs for Old Regime
    old_regime_tax = calculate_old_regime_tax(taxable_income)
    
    # Tax slabs for New Regime
    new_regime_tax = calculate_new_regime_tax(gross_income)
    
    # Calculate cess (4% on tax)
    old_regime_cess = old_regime_tax * 0.04
    new_regime_cess = new_regime_tax * 0.04
    
    return {
        'old_regime': {
            'taxable_income': taxable_income if regime == 'old' else gross_income,
            'tax_amount': old_regime_tax,
            'cess': old_regime_cess,
            'total_tax': old_regime_tax + old_regime_cess
        },
        'new_regime': {
            'taxable_income': gross_income,
            'tax_amount': new_regime_tax,
            'cess': new_regime_cess,
            'total_tax': new_regime_tax + new_regime_cess
        },
        'recommended_regime': 'old' if (old_regime_tax + old_regime_cess) < (new_regime_tax + new_regime_cess) else 'new'
    }

def calculate_old_regime_tax(taxable_income: float) -> float:
    """Calculate tax under old regime."""
    tax = 0
    
    if taxable_income <= 250000:
        return 0
    elif taxable_income <= 500000:
        tax = (taxable_income - 250000) * 0.05
    elif taxable_income <= 1000000:
        tax = 12500 + (taxable_income - 500000) * 0.20
    else:
        tax = 112500 + (taxable_income - 1000000) * 0.30
    
    return tax

def calculate_new_regime_tax(taxable_income: float) -> float:
    """Calculate tax under new regime."""
    tax = 0
    
    if taxable_income <= 300000:
        return 0
    elif taxable_income <= 600000:
        tax = (taxable_income - 300000) * 0.05
    elif taxable_income <= 900000:
        tax = 15000 + (taxable_income - 600000) * 0.10
    elif taxable_income <= 1200000:
        tax = 45000 + (taxable_income - 900000) * 0.15
    elif taxable_income <= 1500000:
        tax = 90000 + (taxable_income - 1200000) * 0.20
    else:
        tax = 150000 + (taxable_income - 1500000) * 0.30
    
    return tax
