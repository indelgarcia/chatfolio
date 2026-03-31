# ChatFolio - HAI Design Rationale

This document explains the human-AI interaction design decisions behind ChatFolio, organized around the course's four evaluation criteria. It captures the *why* behind each feature — the HAI reasoning that doesn't belong in code, PRD, or TODO.

---

## Evaluation Framework

The HAI course evaluates on four dimensions. The core question across all four: **is this genuine human-AI collaboration, or a black box where the user clicks a button and the AI does everything?**

| Criteria | Question it answers |
|----------|-------------------|
| **Onboarding** | How does the user learn what the system can and cannot do? |
| **User Input** | How does the user specify intent and steer the AI? |
| **System Output** | How does the AI present its work for human review? |
| **User Feedback** | How does the user correct, verify, or iterate on AI output? |

---

## 1. Onboarding

**Design goal:** The user should understand ChatFolio's scope, limitations, and process *before* engaging — not discover them through trial and error.

### What we built and why

**Onboarding explainer panel (v0.3).** An expandable "What is ChatFolio?" section shown on first load. It answers four questions a new user has:
- What does this do? (builds a starter portfolio through conversation)
- What will it ask me? (goal, timeline, budget, risk comfort)
- How long will this take? (2-3 minutes)
- What are the limitations? (not a financial advisor, no trade execution, no guarantees)

This panel collapses after the user starts chatting so it doesn't clutter the ongoing experience.

**Why not just let the AI explain itself in the greeting?** The AI greeting is conversational and warm, but it's a single message that scrolls away. A structured panel persists on screen and can be re-opened. For onboarding, structured > conversational — the user needs to scan and absorb, not read prose.

**Disclaimer (v0.3).** Static text below the portfolio output and a guardrail instruction in the system prompt. Investment tools carry implicit authority — a beginner might treat ChatFolio's output as professional advice. The disclaimer makes the boundary explicit: this is educational, not advisory. The system prompt also instructs the AI to recommend professional consultation for complex situations (tax optimization, estate planning).

### What's planned

- **Post-generation chat nudge (TODO #6):** After the portfolio appears, users may think the experience is over. A visible prompt telling them "you can keep chatting to adjust" is onboarding for the iteration phase — teaching the user about a capability they wouldn't discover on their own.

---

## 2. User Input

**Design goal:** The user steers the AI through natural conversation, not forms. The system should feel like talking to a knowledgeable friend, not filling out an application.

### What we built and why

**One question at a time.** The system prompt explicitly prohibits stacking multiple questions. This is a deliberate constraint. Beginners are intimidated by finance — a wall of questions triggers the same anxiety as a brokerage form. One-at-a-time pacing lets the user focus, and it mirrors how a human advisor would actually talk.

**Plain language with inline explanations.** If the AI uses a term like "risk tolerance," it explains it in the same sentence. The target user (Marcus, 26, first-time investor) doesn't have financial vocabulary. Making him learn jargon to use the tool defeats the purpose.

**Open-ended additional info (FR5).** After the 4 required fields, the AI asks "anything else you'd like me to know?" This is intentionally open-ended — it respects that the user may have context the system didn't think to ask about ("I already have a 401k," "no crypto," "I'm saving for a wedding too"). It also signals that the user's input matters beyond the minimum required fields.

**Post-generation chat (v0.3).** The chat stays active after portfolio generation. Users can type adjustments ("make it more aggressive," "what if I invest $300/month"). This transforms the interaction from a one-shot Q&A into an ongoing dialogue where the user retains control.

### What's planned

- **Richer profile fields (TODO #4):** Income, rent, location, debt, existing accounts. These make the input more comprehensive, but they also lengthen the conversation. The design tension: more data = better output, but more questions = higher drop-off risk. The conversational format helps here — it doesn't *feel* like 10 form fields because they're spread across a natural dialogue.
- **Scenario-based risk assessment (TODO #10):** Instead of asking "what's your risk tolerance?" (which beginners can't answer), ask situational questions: "If your investments dropped from $10,000 to $8,000 but might rebound to $25,000, what would you do?" This produces more accurate risk profiles and makes the conversation feel human rather than form-like.
- **AI-suggested risk tolerance (TODO #10):** The AI should proactively flag when the user's stated risk level doesn't match their profile data. A 22-year-old with no debt and a 30-year timeline who says "conservative" is leaving returns on the table — the AI should educate, not just accept. The user always has final say.

---

## 3. System Output

**Design goal:** The AI's output should be transparent, explainable, and actionable — never a black box. The user should understand *what* was recommended, *why*, and *what to do next*.

### What we built and why

**Live profile sidebar (FR2).** As the conversation progresses, the sidebar updates in real time to show what the system has captured. This serves two HAI purposes:
1. **Transparency:** The user sees exactly what the AI extracted from their words — no hidden state.
2. **Error detection:** If the sidebar shows something wrong ("Risk Tolerance: aggressive" when they said "moderate"), the user can catch it immediately rather than discovering it in a bad portfolio.

The progress bar (X/4 required fields) also sets expectations — the user knows how far along they are and what's left.

**Human-in-the-loop generation (FR4).** The portfolio does NOT auto-generate when the profile is complete. The user must click "Generate My Portfolio." This is a deliberate friction point. Auto-generation would feel like the AI is making decisions *for* the user. The button gives the user a moment to review their profile in the sidebar and confirm they're ready. It also creates a clear boundary between "telling the AI about myself" and "seeing what the AI recommends."

**Portfolio rationale passage (v0.3).** A GPT-generated explanation of *why* this specific portfolio was built, referencing the user's exact goal, timeline, budget, and risk level. This is the single most important HAI feature for System Output. Without it, the portfolio is a black box — the user sees "54% VTI, 36% VXUS, 7% BND, 3% BNDX" but has no idea why. The rationale:
- Explains the equity/bond split in terms of the user's risk and timeline
- Describes what each ETF does and why it's included
- Mentions trade-offs ("a more conservative approach would reduce volatility but historically grows slower")
- Is written in plain language, not financial jargon

**Growth projections (v0.3).** Line chart showing estimated portfolio value over time with optimistic/expected/conservative scenarios. This makes abstract percentages concrete: "$150/month in this portfolio could become ~$270,000 in 30 years." For a beginner, this is the moment the portfolio becomes *meaningful* — it connects today's small contributions to a future outcome they care about.

**Action plan (v0.3).** A step-by-step guide: which brokerage to use, what account to open, how to buy the ETFs, how to automate. Without this, the output is incomplete — the user knows *what* to invest in but not *how*. The action plan is personalized (recommends Roth IRA for retirement goals, mentions fractional shares for small budgets).

### What's planned

- **Portfolio versioning (TODO #12):** When users iterate via the edit loop, save each version so they can compare. The current behavior silently replaces the old portfolio, which means the user can't see what changed or go back.
- **"What if" buttons (TODO #6):** Quick-action buttons to preview more/less aggressive allocations. Lowers the barrier to exploration — clicking is easier than typing for a beginner.

---

## 4. User Feedback

**Design goal:** The user should be able to correct, adjust, and iterate on the AI's output — not just accept or restart.

### What we built and why

**Confirmation loops (FR3).** When the AI extracts something from an ambiguous answer, it paraphrases and asks the user to confirm: "It sounds like you're saving for retirement, roughly 30 years out — does that sound right?" Fields are only committed to the profile after confirmation. This prevents the common HAI failure mode where the AI confidently extracts the wrong thing and the user never knows.

**Post-generation edit loop (v0.3).** After the portfolio is generated, the user can keep chatting to request changes. The system prompt has specific instructions for this phase — it interprets messages like "make it more aggressive" or "change my budget to $300" as profile adjustment requests and regenerates the portfolio. This directly addresses the evaluation question: "How does the user correct or iterate on the AI's output?"

Without this, the only option was "Start Over" — which throws away the entire conversation. That's hostile to iteration. A good human-AI system should let the user make small adjustments without starting from scratch.

### What's planned

- **"What if" risk toggle buttons (TODO #6):** Beginners may not know what to type to explore alternatives. Buttons like "What if I was more aggressive?" make iteration discoverable without requiring the user to formulate a request.
- **Portfolio versioning (TODO #12):** Save each generated version so users can compare approaches side by side. Currently the old portfolio disappears on regeneration — the user can't see what they're gaining or losing by changing a parameter.
- **Confidence indicators (TODO #7):** Show which profile fields were explicitly confirmed vs. inferred. Gives the user a visual cue about where the AI might have gotten it wrong, inviting correction.

---

## Design Principles (from course lectures)

These course concepts directly shaped ChatFolio's design:

| Principle | How it shows up in ChatFolio |
|-----------|------------------------------|
| **Mixed-initiative interaction** (Week 6) | The AI leads the conversation but the user can steer, interrupt, and override at any point. Post-generation, the user takes the lead. |
| **Transparency and explainability** (Week 11) | Rationale passage explains *why* the portfolio was built. Live sidebar shows extracted state. No hidden decisions. |
| **Design for failure** (Week 10) | Confirmation loops catch extraction errors before they propagate. Fallback responses if the API call fails. Disclaimer acknowledges limitations. |
| **Human-centered design** (Week 4) | Target persona (Marcus) informed every language and UX choice. Plain language, no jargon, encouraging tone. |
| **Safe-to-fail over fail-safe** (Week 10) | The edit loop means a wrong portfolio isn't catastrophic — the user can adjust without restarting. Low cost of error encourages exploration. |
