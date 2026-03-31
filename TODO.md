# ChatFolio - To Do List

**Created:** 2026-03-31

---

## 1. Expand Portfolio Generation Beyond Basic ETFs

**Current state:** `portfolio.py` uses a simple rule-based system that only outputs 4 broad-market Vanguard ETFs (VTI, VXUS, BND, BNDX). Every user gets some combination of those same 4 funds regardless of wealth, sophistication, or risk appetite.

**What needs to change:**

- **Tiered portfolio complexity based on risk + budget.** A user with an aggressive risk tolerance and a high monthly budget should see a different class of recommendations than someone conservative with $100/mo. Specifically:
  - **Conservative / low budget:** Keep the current broad-market ETF approach (VTI, VXUS, BND, BNDX).
  - **Moderate:** Introduce sector-specific and thematic ETFs — tech (QQQ/VGT), healthcare (VHT), dividend-focused (VYM/SCHD), real estate (VNQ), emerging markets (VWO), ESG/clean energy funds, etc.
  - **Aggressive / high budget:** Include individual stock picks (e.g., large-cap growth names) and cryptocurrency allocations (BTC, ETH, or crypto ETFs like BITO) alongside ETFs.
- **AI-informed selection.** The system should factor in current market conditions and sector performance when making recommendations. For example, if the tech sector has been underperforming, the AI should explain why it's still included (long-term thesis) or reduce its weight. This means the AI needs to reason about *why* each asset is in the portfolio — not just follow a static formula.
- **Broader ETF universe.** Move beyond just 4 Vanguard funds. Consider iShares, Schwab, SPDR equivalents and specialized ETFs (small-cap, mid-cap, value vs. growth, international developed vs. emerging, TIPS, high-yield bonds, etc.). The goal is that there are so many options that the AI has to be thoughtful about which ones to include based on the user's profile and real-world factors & context, rather than just defaulting to the same 4 funds every time. This solves the problem of what we aim to fix, take complex financial decision-making and make it more personalized and dynamic, rather than one-size-fits-all.

---

## 2. Post-Portfolio Action Plan (How to Actually Start Investing) -- IMPLEMENTED (v0.3)

**Current state:** After the portfolio is generated, the user sees percentages and dollar amounts - but no guidance on what to do next. A beginner doesn't know how to go from "put 54% in VTI" to actually owning VTI.

**What needs to change:**

- After portfolio generation, display a step-by-step "Getting Started" guide that walks the user through:
  1. **Choose a brokerage** — recommend beginner-friendly platforms (e.g., Fidelity, Schwab, Vanguard, Robinhood) with a brief explanation of why each is good for beginners (no minimums, commission-free ETFs, fractional shares, etc.).
  2. **Create an account** — explain what account type to open (individual brokerage vs. Roth IRA vs. traditional IRA) based on their stated goal and timeline.
  3. **Fund the account** — explain how to link a bank account and set up recurring transfers matching their stated monthly budget.
  4. **Buy the investments** — explain how to search for a ticker, place a market order, and enable fractional shares if their budget is small.
  5. **Set up automation** — suggest enabling automatic recurring investments so they don't have to manually buy each month.
- This should be contextual — the specific steps should adapt to the user's profile. Someone investing $50/mo needs fractional share guidance; someone investing $2000/mo does not.

> **Status:** Implemented in v0.3. GPT-4o-mini generates a personalized action plan displayed in an expandable "How to Get Started" section. Steps adapt to user's goal (Roth IRA vs. taxable) and budget (fractional shares for small budgets). All 5 steps covered.

---

## 3. Portfolio Rationale / Explanation Passage -- IMPLEMENTED (v0.3)

**Current state:** The portfolio output shows ticker symbols, percentages, and dollar amounts — but no explanation of *why* this specific allocation was chosen. The output feels like a black box.

**What needs to change:**

- Below (or above) the allocation chart, display a written passage that explains the reasoning behind the portfolio. This passage should:
  - Explain the overall equity/bond split and why it fits *this user's* risk tolerance and timeline (e.g., "Because you have 30 years until retirement and a moderate risk tolerance, we've allocated 70% to stocks and 30% to bonds. With your long timeline, you can ride out short-term market dips and benefit from long-term stock growth.")
  - Explain why each individual holding was included and what role it plays (e.g., "VTI gives you broad exposure to the entire U.S. stock market — over 4,000 companies in a single fund.")
  - Address what the user would *lose* by choosing differently — e.g., "A more conservative allocation would reduce your exposure to market swings, but based on historical returns it would likely grow your portfolio more slowly over 30 years."
  - Reference the user's specific inputs: their goal, budget, timeline, risk level, and any additional info they shared.
- The passage should be written in plain, approachable language — not financial jargon. This is a HAI system; the user should feel like they *understand* why this portfolio was recommended, not just told to trust it.

> **Status:** Implemented in v0.3. GPT-4o-mini generates a 2-3 paragraph rationale displayed under "Why This Portfolio?" heading. Covers equity/bond split reasoning, each holding's role, trade-offs, and references user's specific inputs. All sub-items addressed.

---

## 4. Richer User Input — Income, Expenses, Location, and Financial Context

**Current state:** The profile captures 4 required fields (goal, timeline, monthly_budget, risk_tolerance) and one optional free-text field (additional_info). This is thin - the system knows nothing about the user's broader financial picture.

**What needs to change:**

- **Income:** Ask about gross annual or monthly income. This lets the system assess whether the stated monthly budget is realistic and sustainable (e.g., investing $500/mo on a $2,000/mo income is aggressive and may not leave room for emergencies).
- **Rent / housing costs:** Knowing their biggest fixed expense helps gauge true disposable income and whether they should prioritize an emergency fund before investing.
- **Location / state of residence:** Tax implications vary significantly by state. No state income tax (TX, FL, WA, etc.) means more take-home pay. Some states have tax-advantaged investment programs. Location also informs cost-of-living context — $150/mo to invest in Manhattan means something very different than in rural Ohio.
- **Existing savings / emergency fund:** If they have no emergency fund, the system should recommend building one (3-6 months of expenses) before or alongside investing. This is responsible financial advice. (it may be the case that the user alreay has an emergency fund or dont need one becasue they have low expesnes and a safe environemnt like no car and living with parents)
- **Existing investments / retirement accounts:** Knowing they already have a 401k with employer match changes the recommendation — the system should account for overlap and suggest complementary allocations rather than duplicating.
- **Debt:** High-interest debt (credit cards) should arguably be paid off before investing. The system should at least flag this. Also consider other debt, like car note, student loans, or mortgage — these affect financial stability and risk tolerance.
- **Employment status / stability:** A freelancer with variable income needs a different approach than someone with a stable salary.

**How these inputs improve the portfolio and output:**

- The rationale passage (To-Do #3) can reference their full financial picture, not just 4 fields.
- The portfolio allocation can be adjusted — e.g., someone with high rent in an expensive city might get a more conservative allocation because their financial cushion is thinner.
- Tax-advantaged account recommendations (Roth vs. Traditional IRA) depend on income and state.
- The system can flag concerns ("Your monthly budget is 25% of your income — that's ambitious. Make sure you still have an emergency fund.").

---

## 4a. Additional Visualizations for Richer Input Data

**Current state:** The only visualization is the portfolio allocation (progress bars + percentages). With richer input data from To-Do #4, there's an opportunity to show the user more about their financial picture.

**What to add:**

- **Income distribution breakdown:** A chart or visual showing how the user's income is split across rent, other expenses, savings, and investing. Helps them see whether their investment budget is realistic in context.
- **Budget sanity check visual:** A simple gauge or indicator showing what percentage of income goes to investing, with color-coded zones (e.g., green = healthy, yellow = ambitious, red = potentially unsustainable).
- **Net worth projection snippet:** A small preview tied to To-Do #5 showing projected growth.
- **Tax impact visual:** If location data is captured, show estimated tax drag on investment returns by state, or how much a Roth IRA saves them vs. a taxable account over their timeline.
- **Portfolio diversity chart:** A pie chart or treemap showing allocation by asset class (U.S. stocks, international stocks, bonds, crypto, etc.) - more intuitive than progress bars for seeing the full picture at a glance.

---

## 5. Investment Growth Projections Over Time -- PARTIALLY IMPLEMENTED (v0.3)

**Current state:** The portfolio output is a snapshot — it shows what to buy *today* but nothing about what it could become. A beginner has no sense of whether $150/mo will actually matter in 30 years.

**What needs to change:**

- After portfolio generation, display a projection showing estimated portfolio value at 5-year increments from now through the user's stated timeline (up to retirement if applicable).
- The projection should:
  - Use historical average returns for each asset class (e.g., ~10% annualized for U.S. equities, ~5% for bonds, adjusted for the specific allocation, etc...).
  - Account for monthly contributions at the user's stated budget.
  - Show multiple scenarios: **optimistic** (above-average returns), **expected** (historical average), and **conservative** (below-average/flat returns). This manages expectations and avoids the system being seen as making promises.
  - Display as a line chart or table with clear dollar amounts at each increment (e.g., "After 10 years: ~$28,000 | After 20 years: ~$95,000 | After 30 years: ~$270,000").
- Include a disclaimer that projections are estimates based on historical performance and not guaranteed.
- If the user's inputs change (different budget, different risk level), the projections should reflect the updated allocation.

> **Status:** Partially implemented in v0.3. What's done: line chart with optimistic/expected/conservative scenarios, summary table at 5-year milestones, disclaimer, and projections update when profile changes via the edit loop. What's NOT done: currently uses hardcoded historical averages for VTI/VXUS/BND/BNDX only — when TODO #1 (expanded ETF universe) is implemented, the return assumptions and ticker-to-asset-class mapping in `projections.py` will need to be expanded to cover new tickers.

---

## Additional To-Dos by Claude

These are items not in the original list but would meaningfully improve the app - especially from an HAI evaluation perspective.

---

### 6. Post-Generation Edit and Iteration Loop -- PARTIALLY IMPLEMENTED (v0.3)

**Current state:** Once the portfolio is generated, the user can't adjust it. If they want to see what a more aggressive allocation looks like, they have to click "Start Over" and redo the entire conversation.

**What needs to change:**

- After the portfolio is displayed, allow the user to continue chatting to request changes: "What if I bumped my budget to $300?" or "Can you make it more aggressive?" or "Remove international bonds."
- The system should regenerate the portfolio with the updated profile and show a before/after comparison. This directly addresses the HAI criteria for **User Feedback** — the user should be able to iterate, not just accept or restart.

> **Status:** Partially implemented in v0.3. What's done: chat stays active after portfolio generation, system prompt handles adjustment requests, profile updates trigger automatic regeneration of portfolio + rationale + action plan + projections. What's NOT done: before/after comparison view — currently the old portfolio is simply replaced. A side-by-side or diff view would be a future enhancement.

---

### 7. Confidence Indicators on Profile Extraction

**Current state:** The sidebar shows extracted profile values but gives no indication of how confident the AI is in its extraction. The user sees "Risk Tolerance: moderate" but doesn't know if that was clearly stated or inferred from a vague answer.

**What needs to change:**

- Add a visual confidence indicator (e.g., checkmark for confirmed, question mark for inferred) next to each profile field in the sidebar.
- If a field was inferred rather than explicitly confirmed, highlight it so the user knows they can correct it. This strengthens the confirmation loop and makes the system's reasoning more transparent.

---

### 8. Onboarding Explainer / "What Can This Tool Do?" -- IMPLEMENTED (v0.3)

**Current state:** The app opens with a greeting from the AI but no structured explanation of what ChatFolio can and cannot do. A first-time user doesn't know the scope of the tool.

**What needs to change:**

- Add a brief onboarding panel or initial message that explains: what ChatFolio does (helps build a starter portfolio), what it *doesn't* do (not a financial advisor, doesn't execute trades, doesn't guarantee returns), what information it will ask for, and roughly how long the conversation will take.
- This directly addresses HAI **Onboarding** criteria. The user should understand the system's capabilities and limitations before engaging.

> **Status:** Implemented in v0.3. Expandable "What is ChatFolio?" panel shown on first load. Covers: what it does, what it asks, how long it takes, and what it won't do (not a financial advisor). Collapses once the user has more than 1 message in chat.

---

### 9. Export / Save Portfolio

**Current state:** Everything lives in `st.session_state`. If the user closes the tab, their portfolio is gone.

**What needs to change:**

- Add a "Download Portfolio" button that exports the results as a PDF or formatted text file — including the allocation, rationale, action plan, and projections.
- This gives the user something tangible to take away and reference when they actually open a brokerage account. It also makes the tool feel more like a real product and less like a demo.

---

### 10. Risk Tolerance Education

**Current state:** The AI asks about risk tolerance, but many beginners don't know whether they're "conservative" or "aggressive." They might just pick "moderate" because it sounds safe.

**What needs to change:**

- Instead of asking the user to self-label their risk tolerance, ask scenario-based questions: "If your investments dropped 20% in a month, would you: (a) sell everything, (b) hold and wait, (c) buy more while it's cheap?" Map their answers to a risk profile.
- This produces more accurate risk assessment and is better UX for beginners who don't have the vocabulary to describe their risk appetite. It also makes the conversation feel more human and less like a form.
- Give tangible examples of what "conservative" vs. "aggressive" means in terms of portfolio composition and expected volatility, so the user can make an informed choice. For example saying "dropped 20%" is not as intuitive as "if you had $10,000 in your bank account suddenly became $8,000 but you know that it may be 25,000 tomorrow, how would you react?" This is a more visceral way to understand risk tolerance.
- **AI-suggested risk tolerance based on profile data.** The AI should be able to *recommend* a risk level based on the user's full financial picture — not just accept whatever they say at face value. For example, a 22-year-old with a stable income, low expenses, no debt, and a 30+ year timeline is objectively well-positioned to take on more risk, even if they self-identify as "not risky." The AI should gently surface this: "Based on your age, income, and long timeline, you could afford to be more aggressive — that historically means higher returns over 30 years. Would you like me to show you what a more aggressive allocation looks like?" This isn't overriding the user — it's educating them. The user always has final say, but the system should proactively flag when their stated risk tolerance doesn't match what their profile suggests. Conversely, if someone with high debt and a short timeline says "aggressive," the AI should flag that too.

---

### 11. Disclaimer and Guardrails -- IMPLEMENTED (v0.3)

**Current state:** No disclaimer anywhere in the app. For a tool that gives investment recommendations, this is a gap.

**What needs to change:**

- Add a clear disclaimer that ChatFolio is an educational tool, not a licensed financial advisor.
- The AI should decline to give advice on specific stocks if it's not confident, and should recommend consulting a professional for complex situations (tax optimization, estate planning, etc.).
- Important for both ethical responsibility and for the HAI evaluation — the system should communicate its limitations honestly.

> **Status:** Implemented in v0.3. What's done: static disclaimer below portfolio output, guardrail instruction added to system prompt telling the AI to recommend professionals for complex situations and never guarantee returns. What's NOT done: the AI doesn't yet actively decline specific stock pick requests — it relies on the system prompt guideline but doesn't have hard enforcement.
