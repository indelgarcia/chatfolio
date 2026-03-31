"""Project portfolio growth over time using historical average returns."""

import pandas as pd

# Annualized return assumptions by asset class (nominal, before inflation)
RETURN_ASSUMPTIONS = {
    # Scenario:       optimistic, expected, conservative
    "US_EQUITY":      (0.12, 0.10, 0.06),
    "INTL_EQUITY":    (0.10, 0.08, 0.04),
    "US_BOND":        (0.06, 0.045, 0.02),
    "INTL_BOND":      (0.05, 0.035, 0.015),
}

# Map tickers to asset classes
TICKER_CLASS = {
    "VTI": "US_EQUITY",
    "VXUS": "INTL_EQUITY",
    "BND": "US_BOND",
    "BNDX": "INTL_BOND",
}


def _blended_return(portfolio: list, scenario_idx: int) -> float:
    """Compute weighted-average annual return for a given scenario index."""
    total = 0.0
    for holding in portfolio:
        weight = holding["allocation"] / 100.0
        asset_class = TICKER_CLASS.get(holding["ticker"], "US_EQUITY")
        annual_return = RETURN_ASSUMPTIONS[asset_class][scenario_idx]
        total += weight * annual_return
    return total


def generate_projections(
    portfolio: list, monthly_budget: float, years: int
) -> pd.DataFrame:
    """Return a DataFrame with projected portfolio value at each year.

    Columns: Year, Optimistic, Expected, Conservative
    """
    scenarios = {
        "Optimistic": _blended_return(portfolio, 0),
        "Expected": _blended_return(portfolio, 1),
        "Conservative": _blended_return(portfolio, 2),
    }

    rows = []
    for year in range(0, years + 1):
        row = {"Year": year}
        for label, annual_r in scenarios.items():
            monthly_r = annual_r / 12
            months = year * 12
            if monthly_r == 0:
                value = monthly_budget * months
            else:
                # Future value of a series of monthly contributions
                value = monthly_budget * (((1 + monthly_r) ** months - 1) / monthly_r)
            row[label] = round(value, 2)
        rows.append(row)

    return pd.DataFrame(rows)
