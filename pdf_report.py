"""Generate a PDF portfolio report using fpdf2."""

from fpdf import FPDF

_GOLD  = (197, 160, 40)
_DARK  = (26, 26, 26)
_MED   = (90, 70, 10)
_GREY  = (110, 110, 110)
_CREAM = (255, 252, 240)


def _safe(text: str) -> str:
    return (text or "").encode("latin-1", errors="replace").decode("latin-1")


def generate_pdf(
    profile: dict,
    portfolio: list,
    rationale: str,
    action_plan: str,
    summary_table=None,
) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    def section_header(title: str):
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(*_GOLD)
        pdf.cell(0, 8, title, ln=True)
        pdf.set_draw_color(*_GOLD)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.set_text_color(*_DARK)
        pdf.ln(3)

    # Header band
    pdf.set_fill_color(*_CREAM)
    pdf.rect(0, 0, 210, 36, "F")
    pdf.set_y(8)
    pdf.set_font("Helvetica", "B", 26)
    pdf.set_text_color(*_GOLD)
    pdf.cell(0, 10, "ChatFolio", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*_MED)
    pdf.cell(0, 6, "Your Personalized Investment Portfolio Report", ln=True, align="C")
    pdf.ln(10)

    # Profile
    section_header("Your Profile")
    fields = [
        ("Goal",           profile.get("goal")),
        ("Timeline",       profile.get("timeline")),
        ("Monthly Budget", f"${profile.get('monthly_budget', '0')}/month"),
        ("Risk Tolerance", (profile.get("risk_tolerance") or "").capitalize()),
        ("Additional Info", profile.get("additional_info")),
    ]
    pdf.set_font("Helvetica", "", 10)
    for label, val in fields:
        if val and str(val).strip() and val != "None specified":
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(44, 6, f"{label}:", ln=False)
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(0, 6, _safe(str(val)), ln=True)
    pdf.ln(4)

    # Allocations
    section_header("Portfolio Allocations")
    budget_raw = "".join(c for c in str(profile.get("monthly_budget") or "0") if c.isdigit() or c == ".")
    try:
        budget = float(budget_raw) if budget_raw else 0.0
    except ValueError:
        budget = 0.0

    for item in portfolio:
        monthly = budget * item["allocation"] / 100
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(18, 6, item["ticker"], ln=False)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(92, 6, _safe(item["name"]), ln=False)
        pdf.cell(18, 6, f"{item['allocation']}%", ln=False, align="R")
        if budget > 0:
            pdf.cell(0, 6, f"  ${monthly:.0f}/mo", ln=True)
        else:
            pdf.ln()
    pdf.ln(4)

    # Rationale
    if rationale:
        section_header("Why This Portfolio?")
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5, _safe(rationale))
        pdf.ln(4)

    # Projections table
    if summary_table is not None and not summary_table.empty:
        section_header("Projected Growth")
        cols = list(summary_table.columns)
        col_w = min(32, 170 // len(cols))
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(20, 6, "Year")
        for col in cols:
            pdf.cell(col_w, 6, col, align="R")
        pdf.ln()
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*_GREY)
        for idx, row in summary_table.iterrows():
            pdf.cell(20, 5, str(idx))
            for col in cols:
                pdf.cell(col_w, 5, str(row[col]), align="R")
            pdf.ln()
        pdf.set_text_color(*_DARK)
        pdf.ln(4)

    # Action plan
    if action_plan:
        pdf.add_page()
        section_header("How to Get Started")
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5, _safe(action_plan))
        pdf.ln(4)

    # Disclaimer
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(*_GREY)
    pdf.multi_cell(
        0, 4,
        "ChatFolio is an educational tool, not a licensed financial advisor. "
        "Allocations are based on general principles and historical averages. "
        "Past performance does not guarantee future results. "
        "Consult a qualified financial professional before making investment decisions.",
    )

    return bytes(pdf.output())
