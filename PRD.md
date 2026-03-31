# ChatFolio — Product Requirements Document

**Version:** 0.2 (Second Prototype Iteration)
**Last updated:** 2026-03-31
**Team:** Chris, Indel, Nate, Matt

---

## Overview

ChatFolio is a conversational investment advisor that helps beginner investors build a starter ETF portfolio through natural dialogue instead of traditional brokerage forms. This is the second prototype — a functional, test-ready Streamlit app with real AI conversation.

## Target User

**Marcus J.** — 26, recent grad, first full-time job, ~$150/mo to invest. Intimidated by financial jargon and brokerage forms. Comfortable with chat interfaces. Wants to build wealth without learning finance theory.

## Functional Requirements

### FR1: Conversational Onboarding
- GPT-4o-mini powers a real chat that asks about investment goal, time horizon, monthly budget, and risk comfort
- One question at a time — never stacks multiple questions
- Plain language throughout, financial terms explained inline
- **HAI criteria:** Onboarding, User Input

### FR2: Live Profile Sidebar
- Sidebar displays extracted profile fields as the conversation progresses
- Fields: Goal, Timeline, Monthly Budget, Risk Tolerance, Additional Info
- Progress bar shows completion (X/4 required fields)
- Updates in real time after each AI response
- **HAI criteria:** System Output

### FR3: Confirmation Loops
- When the AI extracts something ambiguous, it paraphrases its interpretation and asks the user to confirm
- Fields are only committed to the profile after clear confirmation
- **HAI criteria:** User Feedback

### FR4: Basic Portfolio Generation
- Triggered by user clicking "Generate My Portfolio" button (human-in-the-loop)
- Rule-based allocation: risk tolerance + time horizon determines equity/bond split
- 4 broad-market ETFs: VTI, VXUS, BND, BNDX
- Displays allocation percentages, progress bars, and monthly dollar amounts
- **HAI criteria:** System Output

### FR5: Open-Ended Input
- After the 4 required fields are filled, the AI asks if there's anything else the user wants to share
- Captures extra preferences, constraints, or context in an "Additional Info" field
- Examples: "no crypto", "already have a 401k", "prefer ESG funds"
- **HAI criteria:** User Input

## Deferred to Future Iterations

| Feature | Notes |
|---------|-------|
| Risk steering slider | Post-generation adjustment of risk posture |
| Compare / What-If simulation | Side-by-side allocation comparison |
| Accept / Adjust / Explain / Compare actions | Full review layer |
| Progress tracker bar | Visual step indicator in chat |
| Individual stock recommendations | Currently ETF-only |
| Persistent storage / accounts | Session-only state |
| Mobile responsive layout | Desktop-first for now |

## Architecture

```
User <-> Streamlit Chat UI (app.py)
              |
              v
         chat_engine.py  -- system prompt + GPT-4o-mini (JSON mode)
              |
              v
         profile (st.session_state)  --> sidebar display
              |
              v
         portfolio.py  -- rule-based ETF allocation
              |
              v
         portfolio display (progress bars + table)
```

## File Map

| File | Purpose |
|------|---------|
| `app.py` | Streamlit entry point: layout, chat loop, sidebar, portfolio display |
| `chat_engine.py` | OpenAI API calls, system prompt, structured JSON extraction |
| `portfolio.py` | Rule-based ETF allocation from user profile |
| `requirements.txt` | Python dependencies (streamlit, openai, python-dotenv) |
| `.env` | API key (git-ignored) |
| `.streamlit/config.toml` | Dark theme configuration |
| `PRD.md` | This file |
| `CLAUDE.md` | Development guidance for Claude Code |
| `context/` | Course reference materials |

## Design Decisions

1. **JSON mode for extraction** — System prompt instructs GPT-4o-mini to return conversation text + profile updates as JSON. Keeps extraction in-band with the conversation, no second API call.
2. **Session state only** — No database. All profile and chat state lives in `st.session_state`. Sufficient for a prototype.
3. **Broad-market ETFs only** — VTI, VXUS, BND, BNDX. Avoids sector bets that could conflict with user preferences.
4. **Button-triggered generation** — Portfolio doesn't auto-generate. User clicks a button, keeping them in control (human-in-the-loop).
5. **Dark theme** — Neutral dark gray (#1e1e1e) similar to ChatGPT/Claude. Clean, not flashy.

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1 | 2026-03 | First prototype — Lovable no-code mockup (static UI, no real AI) |
| 0.2 | 2026-03-31 | Second prototype — functional Streamlit app with GPT-4o-mini, live profile, confirmation loops, portfolio generation |
