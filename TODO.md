# ChatFolio - To Do List

Completed items are tracked in `PRD.md` version history. This file only lists remaining work.

---

## 1. Expand Portfolio Generation Beyond Basic ETFs

`portfolio.py` currently hardcodes 4 Vanguard ETFs (VTI, VXUS, BND, BNDX) with a simple if-elif equity/bond split. Every user gets the same funds regardless of wealth or sophistication.

**Scope:**

- **Tiered complexity based on risk + budget:**
  - Conservative / low budget: keep broad-market ETFs (VTI, VXUS, BND, BNDX)
  - Moderate: add sector/thematic ETFs (QQQ, VGT, VHT, VYM, SCHD, VNQ, VWO, ESG funds, etc.)
  - Aggressive / high budget: include individual stocks (large-cap growth) and crypto (BTC, ETH, or BITO)
- **AI-informed selection:** Replace the rule-based `portfolio.py` with a GPT call that reasons about which assets to include based on the user's profile and current market context. The AI should explain why each asset was chosen or excluded.
- **Broader ETF universe:** iShares, Schwab, SPDR equivalents, small-cap, mid-cap, value vs. growth, international developed vs. emerging, TIPS, high-yield bonds, etc. The AI picks from this universe rather than defaulting to the same 4.

**Files to modify:** `portfolio.py` (major rewrite or replacement), `chat_engine.py` (system prompt needs to know about expanded options), `projections.py` (expand `TICKER_CLASS` and `RETURN_ASSUMPTIONS` to cover new tickers)

---

## 4. Richer User Input — Income, Expenses, Location, and Financial Context

The profile currently captures only 4 required fields + 1 optional free-text field. The system knows nothing about the user's broader financial picture.

**New profile fields to add:**

- **Income** (gross annual/monthly) — assess if monthly_budget is realistic and sustainable
- **Rent / housing costs** — gauge true disposable income, flag if emergency fund should come first
- **Location / state** — tax implications (no state income tax in TX/FL/WA), cost-of-living context, Roth vs. Traditional IRA guidance
- **Existing savings / emergency fund** — recommend building 3-6 months expenses before investing if none exists (but account for users with low expenses / living with parents who may not need one)
- **Existing investments / retirement accounts** — avoid overlap (e.g., already have a 401k with employer match)
- **Debt** — high-interest debt (credit cards) should be flagged; also car notes, student loans, mortgage
- **Employment status / stability** — freelancer vs. stable salary affects approach

**How these feed into output:**

- Rationale passage references full financial picture
- Portfolio allocation adjusts (high rent in expensive city -> more conservative)
- Account type recommendations depend on income + state (Roth vs. Traditional)
- System flags concerns ("Your budget is 25% of income — make sure you have an emergency fund")

**Files to modify:** `chat_engine.py` (system prompt — add new fields, extend JSON schema), `app.py` (session state profile dict, sidebar labels, progress bar denominator), `portfolio.py` (factor new fields into allocation logic)

---

## 4a. Additional Visualizations for Richer Input Data

Depends on TODO #4 — needs income/expense data to be meaningful.

- **Income distribution chart** — how income splits across rent, expenses, savings, investing
- **Budget sanity gauge** — % of income going to investing, color-coded (green/yellow/red)
- **Tax impact visual** — estimated tax drag by state, Roth vs. taxable comparison over timeline
- **Portfolio diversity chart** — pie chart or treemap by asset class (more intuitive than progress bars)

**Files to modify:** `app.py` (new chart sections in portfolio display area)

---

## 5. Growth Projections — Remaining Work

Core projections are implemented (line chart, 3 scenarios, milestone table, disclaimer). One thing remains:

- **Expand return assumptions for new tickers.** When TODO #1 adds sector ETFs / stocks / crypto, update `TICKER_CLASS` and `RETURN_ASSUMPTIONS` in `projections.py` to cover them. Currently only maps VTI/VXUS/BND/BNDX.

**Blocked by:** TODO #1

---

## 6. Post-Generation Edit Loop — Remaining Work

Core edit loop is implemented (chat stays active, AI handles adjustment requests, portfolio regenerates). Three things remain:

- **"What if" risk toggle buttons.** Display buttons like "What if I was more aggressive?" / "What if I was more conservative?" below the portfolio. Clicking one temporarily overrides risk_tolerance, regenerates portfolio + rationale + projections. Lowers the barrier — beginners are more likely to click a button than type a request. Feeds into portfolio versioning (TODO #12).
- **Post-generation chat nudge.** Add an `st.info()` or caption after the portfolio that tells the user the chat is still active: "Want to adjust anything? Try 'What if I invested $300/month?' or 'Make it more aggressive.'" Users currently may not realize they can keep typing.
- **Before/after comparison.** When portfolio regenerates, show what changed vs. previous version. Depends on TODO #12 (versioning).

**Files to modify:** `app.py` (buttons in portfolio display section, info banner after portfolio)

---

## 7. Confidence Indicators on Profile Extraction

The sidebar shows extracted values but no indication of whether each field was explicitly confirmed or inferred from a vague answer.

- Add confidence indicator per field (checkmark = confirmed, question mark = inferred)
- Highlight inferred fields so the user knows they can correct them

**Files to modify:** `chat_engine.py` (AI returns confidence per field in JSON), `app.py` (sidebar rendering adds icons)

---

## 9. Export / Save Portfolio as PDF

No way to save or share the output. Everything is lost when the tab closes.

- Add "Download Portfolio" button via `st.download_button`
- Generate PDF containing: profile summary, allocation table, rationale, projections chart + milestone table, action plan, disclaimer
- Branded header (ChatFolio), clean layout
- Use `fpdf2` or `reportlab` for server-side PDF generation
- If TODO #12 (versioning) is implemented, allow exporting any saved version

**Files to modify:** new `export.py` (PDF generation logic), `app.py` (download button), `requirements.txt` (add fpdf2 or reportlab)

---

## 10. Risk Tolerance Education

Beginners don't know if they're "conservative" or "aggressive" — they default to "moderate" because it sounds safe.

- **Scenario-based questions** instead of self-labeling: "If your $10,000 investment suddenly dropped to $8,000 but could be $25,000 next year, would you: (a) sell, (b) hold, (c) buy more?" Map answers to a risk profile.
- **Tangible examples** of what each risk level means in portfolio terms and expected volatility
- **AI-suggested risk tolerance:** When the user's profile data (age, income, timeline, debt) suggests a different risk level than what they stated, the AI should gently flag it: "Based on your long timeline and stable income, you could afford to be more aggressive — that historically means higher returns. Want to see what that looks like?" User always has final say. Works in reverse too (flags aggressive + high debt).

**Files to modify:** `chat_engine.py` (system prompt — new question flow, suggestion logic)

---

## 11. Disclaimer Guardrails — Remaining Work

Static disclaimer and system prompt guideline are implemented. One thing remains:

- **Hard enforcement on stock pick requests.** The AI currently relies on a soft system prompt guideline to decline specific stock picks. Add explicit instructions that the AI should not recommend individual stocks by name unless the expanded portfolio system (TODO #1) is in place with proper reasoning.

**Files to modify:** `chat_engine.py` (strengthen system prompt guardrail)

---

## 12. Portfolio Versioning — Save and Compare Multiple Outputs Per Session

When the user adjusts their profile post-generation, the old portfolio is silently replaced. No way to compare approaches.

- **Save snapshots:** Each generation/regeneration saves to `st.session_state.portfolio_history` — includes allocation, profile at generation time, rationale, and auto-generated label (e.g., "Moderate — $150/mo")
- **Tab navigation:** Display "Portfolio 1 | Portfolio 2 | Portfolio 3" tabs/buttons at top of portfolio section. Clicking shows that version's full output (allocation, rationale, projections, action plan).
- **Comparison view:** Side-by-side columns showing two versions, highlighting differences in allocations and projected outcomes.
- Works with "What if" buttons from TODO #6 — user generates moderate portfolio, clicks "more aggressive", then toggles between them.

**Files to modify:** `app.py` (history list in session state, tab UI, comparison layout)
