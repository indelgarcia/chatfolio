"""Project portfolio growth over time using historical average returns."""

import pandas as pd

RETURN_ASSUMPTIONS = {
    "US_EQUITY":   (0.12, 0.10, 0.06),
    "INTL_EQUITY": (0.10, 0.08, 0.04),
    "US_BOND":     (0.06, 0.045, 0.02),
    "INTL_BOND":   (0.05, 0.035, 0.015),
}

TICKER_CLASS = {
    "VTI":  "US_EQUITY",
    "VXUS": "INTL_EQUITY",
    "BND":  "US_BOND",
    "BNDX": "INTL_BOND",
}

SP500_ANNUAL = 0.10


def blended_return(portfolio: list, scenario_idx: int) -> float:
    """Weighted-average annual return for scenario index (0=optimistic, 1=expected, 2=conservative)."""
    total = 0.0
    for holding in portfolio:
        weight = holding["allocation"] / 100.0
        asset_class = TICKER_CLASS.get(holding["ticker"], "US_EQUITY")
        total += weight * RETURN_ASSUMPTIONS[asset_class][scenario_idx]
    return total


def generate_projections(portfolio: list, monthly_budget: float, years: int) -> pd.DataFrame:
    """Return DataFrame with projected portfolio value at each year.

    Columns: Year, Optimistic, Expected, Conservative, S&P 500
    """
    scenarios = {
        "Optimistic":   blended_return(portfolio, 0),
        "Expected":     blended_return(portfolio, 1),
        "Conservative": blended_return(portfolio, 2),
    }

    def _fv(monthly_r: float, months: int) -> float:
        if monthly_r == 0:
            return monthly_budget * months
        return monthly_budget * (((1 + monthly_r) ** months - 1) / monthly_r)

    sp_monthly = SP500_ANNUAL / 12
    rows = []
    for year in range(0, years + 1):
        months = year * 12
        row = {"Year": year}
        for label, annual_r in scenarios.items():
            row[label] = round(_fv(annual_r / 12, months), 2)
        row["S&P 500"] = round(_fv(sp_monthly, months), 2)
        rows.append(row)

    return pd.DataFrame(rows)
