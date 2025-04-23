import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta

def calculate_volatility(returns: pd.Series, window: int = 30) -> float:
    """Calculate rolling volatility of returns."""
    return returns.rolling(window=window).std() * np.sqrt(252)

def project_portfolio_growth(
    initial_amount: float,
    monthly_investment: float,
    expected_return: float,
    risk_free_rate: float,
    time_horizon: int,
    volatility: float,
    simulations: int = 1000
) -> Dict[str, np.ndarray]:
    """
    Project portfolio growth using Monte Carlo simulation.
    Returns confidence intervals for different scenarios.
    """
    monthly_return = expected_return / 12 / 100
    monthly_vol = volatility / np.sqrt(12) / 100
    months = time_horizon * 12
    
    # Initialize array for simulations
    simulated_returns = np.zeros((simulations, months))
    
    for i in range(simulations):
        monthly_returns = np.random.normal(
            monthly_return,
            monthly_vol,
            months
        )
        portfolio_value = initial_amount
        for m in range(months):
            portfolio_value *= (1 + monthly_returns[m])
            portfolio_value += monthly_investment
            simulated_returns[i, m] = portfolio_value
    
    # Calculate confidence intervals
    percentiles = np.percentile(simulated_returns, [5, 25, 50, 75, 95], axis=0)
    
    return {
        'conservative': percentiles[0],  # 5th percentile
        'moderate': percentiles[2],      # 50th percentile
        'aggressive': percentiles[4],    # 95th percentile
        'time_points': np.arange(1, months + 1)
    }

def stress_test_portfolio(
    portfolio: Dict[str, float],
    scenario: str
) -> Dict[str, float]:
    """
    Perform stress testing on portfolio under different scenarios.
    Scenarios: market_crash, interest_rate_hike, currency_crisis
    """
    stress_factors = {
        'market_crash': {
            'Equity': -0.30,
            'Debt': -0.10,
            'Gold': 0.15,
            'Real Estate': -0.20
        },
        'interest_rate_hike': {
            'Equity': -0.15,
            'Debt': -0.20,
            'Gold': -0.05,
            'Real Estate': -0.10
        },
        'currency_crisis': {
            'Equity': -0.20,
            'Debt': -0.15,
            'Gold': 0.25,
            'Real Estate': -0.05
        }
    }
    
    if scenario not in stress_factors:
        raise ValueError(f"Unknown scenario: {scenario}")
    
    stressed_portfolio = {}
    for asset, amount in portfolio.items():
        factor = stress_factors[scenario].get(asset, 0)
        stressed_portfolio[asset] = amount * (1 + factor)
    
    return stressed_portfolio

def calculate_portfolio_metrics(
    portfolio: Dict[str, float],
    returns: Dict[str, float],
    risks: Dict[str, float]
) -> Dict[str, float]:
    """
    Calculate advanced portfolio metrics including Sharpe ratio,
    diversification score, and risk contribution.
    """
    total_value = sum(portfolio.values())
    weights = {k: v/total_value for k, v in portfolio.items()}
    
    # Expected portfolio return
    portfolio_return = sum(weights[k] * returns[k] for k in weights)
    
    # Portfolio risk (simplified)
    portfolio_risk = np.sqrt(sum(weights[k]**2 * risks[k]**2 for k in weights))
    
    # Sharpe ratio (assuming 4% risk-free rate for India)
    risk_free_rate = 0.04
    sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_risk
    
    # Diversification score (1 = perfectly diversified, 0 = concentrated)
    diversification = 1 - sum(w**2 for w in weights.values())
    
    return {
        'expected_return': portfolio_return,
        'risk': portfolio_risk,
        'sharpe_ratio': sharpe_ratio,
        'diversification_score': diversification
    }

def generate_investment_recommendations(
    risk_profile: str,
    investment_horizon: int,
    monthly_investment: float
) -> List[Dict[str, str]]:
    """
    Generate personalized investment recommendations based on
    risk profile and investment horizon.
    """
    recommendations = []
    
    # Asset allocation based on risk profile
    allocations = {
        'conservative': {
            'Large Cap': 20,
            'Debt Funds': 50,
            'Gold': 20,
            'Liquid Funds': 10
        },
        'moderate': {
            'Large Cap': 30,
            'Mid Cap': 20,
            'Debt Funds': 30,
            'Gold': 15,
            'International': 5
        },
        'aggressive': {
            'Large Cap': 35,
            'Mid Cap': 25,
            'Small Cap': 15,
            'Debt Funds': 15,
            'International': 10
        }
    }
    
    if risk_profile in allocations:
        allocation = allocations[risk_profile]
        recommendations.append({
            'type': 'allocation',
            'message': 'Recommended asset allocation:',
            'data': allocation
        })
    
    # SIP recommendations
    if monthly_investment < 5000:
        recommendations.append({
            'type': 'warning',
            'message': 'Consider increasing your SIP amount to at least ₹5,000 for better diversification'
        })
    elif monthly_investment > 50000:
        recommendations.append({
            'type': 'suggestion',
            'message': 'Consider spreading investments across multiple dates to benefit from rupee cost averaging'
        })
    
    # Time horizon based recommendations
    if investment_horizon < 3:
        recommendations.append({
            'type': 'caution',
            'message': 'For short-term goals, consider debt funds and liquid funds to minimize volatility'
        })
    elif investment_horizon > 10:
        recommendations.append({
            'type': 'opportunity',
            'message': 'Your long investment horizon allows for higher equity exposure. Consider maximizing tax benefits through ELSS funds'
        })
    
    return recommendations
