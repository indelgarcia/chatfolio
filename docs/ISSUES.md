# ChatFolio - User Study Issues

**Source:** Think-Aloud Study, 7 groups x 5 participants  
**Date:** April 2026  
**Method:** Affinity Diagram (6 themes identified)

**Status key:**
- `[x]` Fixed in V4/V5 pass (April 2026)
- `[~]` Partial - deferred to a named TODO item
- `[ ]` Open - not yet addressed

---

## Theme 1: Onboarding & Initial Prompt - 6/7 groups

| # | Issue | Status |
|---|-------|--------|
| O1 | Initial prompt too prescriptive - "house" or "retirement" as the only examples box users in | `[x]` System prompt guideline 1 updated: opener now uses broad categories, no specific goal examples |
| O2 | Users felt forced to fit into a predefined category even for general goals like "just grow my money" | `[x]` Fixed with O1 |
| O3 | Bot should ask about age, income, debt, and life stage *before* jumping to goal selection | `[x]` Guideline 3 now adds a one-time life-stage question after goal confirmation, before timeline |
| O4 | "Additional Info" section at end of flow feels like an afterthought - context should be gathered upfront | `[x]` Guideline 6 replaced with proactive question that prompts for savings, debt, and life changes |
| O5 | Better opener: "Tell me about yourself and what you're hoping to do with your money" | `[x]` Guideline 1 updated to open-ended-but-guided phrasing |
| O6 | Bot jumped straight to timeline questions before understanding the user's life situation | `[x]` Fixed with O3 - life-stage question inserted before timeline |
| O7 | Users had to volunteer age, job, and income info themselves - bot never proactively asked | `[x]` Fixed with O3 and O4 |
| O8 | When multiple goals were typed, model only addressed the first one | `[x]` Guideline 2 updated: AI must acknowledge all shared info before drilling into individual fields |
| O9 | Example goals (retirement, house) skew older - not relatable for 22-year-olds just starting to invest | `[x]` Fixed with O1; onboarding panel examples updated to age-neutral starters |
| O10 | Need: prompts for projected income, rent, existing savings, student debt, and upcoming life changes | `[~]` Partial - additional_info question now asks about these; full profile fields deferred to TODO #4 |

---

## Theme 2: Risk Tolerance Confusion - 3/7 groups

| # | Issue | Status |
|---|-------|--------|
| R1 | "35% confident" is a confusing and unusual metric - users didn't know how to interpret it | `[x]` System prompt now explicitly forbids numeric confidence percentages |
| R2 | Risk level descriptions aren't sufficient for beginner investors | `[x]` New guideline 16 requires plain-language descriptions for all three levels whenever risk is asked |
| R3 | Needs a visual spectrum or labeled scale (e.g., "Conservative -> Aggressive") explaining each level | `[x]` Risk question now presents all three options with inline plain-language explanations |
| R4 | Newcomers fundamentally don't know what "risk" means in an investing context | `[x]` Fixed with R2/R3 - new guideline explains risk in terms of portfolio drops and growth trade-offs |
| R5 | Should ask "How experienced are you with stocks or finances?" early in the flow | `[~]` Partial - new guideline handles no-experience users with a tailored response; full experience question deferred to TODO #10 |

---

## Theme 3: Chat & Conversation Flow - 5/7 groups

| # | Issue | Status |
|---|-------|--------|
| C1 | Users dumped all inputs in first message, bypassing the intended step-by-step flow entirely | `[x]` Guideline 2 updated: AI now acknowledges all info first, then processes one field at a time |
| C2 | Chat persists after portfolio creation - users were unsure if it was for follow-up questions or to restart | `[x]` Post-generation split view keeps the conversation visible, and a prominent `st.info` banner explains the chat is still active for adjustments, questions, and recommendations |
| C3 | Follow-up responses after portfolio generation were abrupt and provided insufficient feedback | `[x]` Guideline 17 now requires AI to start post-gen responses by stating what changed and that portfolio is updating |
| C4 | When a user asked the chatbot to explain the "additional info" field, it skipped the explanation and jumped straight to portfolio generation | `[x]` Guideline 17 adds explicit instruction to explain field meaning when asked, never skip |
| C5 | It's not clear to users that the chatbot can assist them during the profile generation process | `[x]` Onboarding panel updated with example openers so users know the chat is conversational |
| C6 | Follow-up questions from the bot used financial jargon that newcomers didn't understand | `[x]` Guideline 9 already covers this; reinforced via risk tolerance plain-language requirement |
| C7 | No visual indication that sending a follow-up message triggered a portfolio regeneration | `[x]` Auto-regeneration now wraps updates in a named spinner and a success toast with a valid emoji icon |
| C8 | "More feedback if you send another chat - it's too abrupt and not clear it produced a new output" | `[x]` Fixed with C3 and C7 |

---

## Theme 4: Portfolio Output & Comprehension - 5/7 groups

| # | Issue | Status |
|---|-------|--------|
| P1 | ETF tickers (VTI, VXUS, etc.) are confusing for beginner investors | `[x]` Inline ETF descriptions added below each fund name in portfolio display |
| P2 | Users don't know what "indexes" mean or where the specific funds come from | `[x]` Fixed with P1 - descriptions explain in plain English what each fund owns |
| P3 | Portfolio percentage breakdowns are confusing - hard to connect to real money or specific goal | `[~]` Partial - rationale generation already personalizes to goal; richer dollar-amount targeting deferred |
| P4 | Users want a deeper dive into what each index fund does and why it's in their portfolio | `[x]` ETF descriptions added inline (P1); rationale section already covers the "why" |
| P5 | Only Vanguard funds shown - users felt the selection wasn't diverse enough | `[~]` Deferred - overlaps with TODO #1 (major ETF rewrite) |
| P6 | Should allow users to set a target dollar amount (e.g. $1M) instead of just a vague physical goal | `[ ]` Open - requires new profile field and projection changes |
| P7 | Hard to understand how the portfolio connects to a goal as specific as buying a house in a particular city | `[~]` Partial - rationale prompt already references user's specific goal; deeper connection deferred |
| P8 | ETFs and financial terminology should be defined inline - not hidden in dropdowns or tooltips | `[x]` Fixed with P1 |

---

## Theme 5: UX & Visual Polish - 4/7 groups

| # | Issue | Status |
|---|-------|--------|
| U1 | Page auto-scrolls to the bottom during portfolio generation - users have to scroll back up | `[ ]` Open - initial generation still reruns the Streamlit page; this fix pass improved post-generation scrolling but did not add JS-based scroll lock |
| U2 | Text color when referencing user input values was inconsistent with the rest of the chat UI | `[ ]` Open - location not identifiable from code; needs reproduction steps or screenshot |
| U3 | "How to Get Started" section is hidden in a dropdown - should be visible by default for new users | `[x]` Changed `expanded=False` -> `expanded=True` |
| U4 | No loading indicator when a follow-up message triggers portfolio regeneration | `[x]` Fixed with C7 - spinner + toast added |
| U5 | Mandatory vs. optional input fields are not clearly differentiated - users unsure what to fill in "Additional Info" | `[x]` Sidebar now shows "Additional Info *(optional)*"; onboarding panel labels each field as required/optional |
| U6 | Post-generation content is unclear: users don't know if additional follow-up questions change the portfolio | `[x]` Fixed with C2 (post-gen nudge) and C3 (explicit AI confirmation of changes) |
| U7 | Post-generation chat and portfolio used one shared page scroll, making it hard to review the portfolio while continuing the conversation | `[x]` Reworked into a two-column split view with independent scroll containers for the chat and portfolio output |

---

## Theme 6: What Worked Well - 6/7 groups

*No issues - captured for reference.*

| # | Observation |
|---|------------|
| W1 | Loading screen was helpful - users appreciated knowing the system was processing |
| W2 | Sidebar updating in real-time as users answered was widely appreciated |
| W3 | Chart is clear, optimistic, and intuitive - users could read it without explanation |
| W4 | Portfolio explanation section was well-received once it loaded |
| W5 | "What is ChatFolio?" disclaimer was useful - users who read it upfront felt more oriented |
| W6 | Conversational format overall was liked - users preferred it to a traditional form |
| W7 | Users appreciated that the model visibly reflected their inputs in its recommendation |
| W8 | Data presentation is clean and easy to follow - diversification mix made sense once explained |

---

## Summary

| Theme | Total Issues | Fixed `[x]` | Partial `[~]` | Open `[ ]` |
|-------|-------------|-------------|--------------|-----------|
| Onboarding & Initial Prompt | 10 | 9 | 1 | 0 |
| Risk Tolerance Confusion | 5 | 4 | 1 | 0 |
| Chat & Conversation Flow | 8 | 8 | 0 | 0 |
| Portfolio Output & Comprehension | 8 | 3 | 3 | 2 |
| UX & Visual Polish | 7 | 4 | 0 | 3 |
| **Total** | **38** | **28** | **5** | **5** |
