"""Simple rule-based portfolio generation from a user profile."""


def generate_portfolio(profile: dict) -> list:
    """Return a list of ETF allocations based on risk tolerance and timeline."""
    risk = (profile.get("risk_tolerance") or "moderate").lower()
    timeline_str = str(profile.get("timeline") or "10")

    # Extract first number from timeline string
    digits = "".join(c for c in timeline_str if c.isdigit())
    timeline = int(digits) if digits else 10

    # Determine equity / bond split
    if risk == "aggressive" or timeline > 30:
        equity = 90
    elif risk == "conservative" or timeline < 5:
        equity = 40
    elif timeline >= 20:
        equity = 80
    elif timeline >= 10:
        equity = 70
    else:
        equity = 60

    bond = 100 - equity

    portfolio = [
        {
            "ticker": "VTI",
            "name": "Vanguard Total Stock Market ETF",
            "allocation": round(equity * 0.6),
        },
        {
            "ticker": "VXUS",
            "name": "Vanguard Total International Stock ETF",
            "allocation": round(equity * 0.4),
        },
        {
            "ticker": "BND",
            "name": "Vanguard Total Bond Market ETF",
            "allocation": round(bond * 0.7),
        },
        {
            "ticker": "BNDX",
            "name": "Vanguard Total International Bond ETF",
            "allocation": round(bond * 0.3),
        },
    ]

    # Drop zero-percent entries
    portfolio = [p for p in portfolio if p["allocation"] > 0]

    # Fix rounding so allocations sum to exactly 100
    total = sum(p["allocation"] for p in portfolio)
    if total != 100 and portfolio:
        portfolio[0]["allocation"] += 100 - total

    return portfolio
