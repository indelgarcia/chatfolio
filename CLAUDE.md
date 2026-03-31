# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ChatFolio is an AI-powered conversational investment advisor that helps beginner investors build a starter portfolio through natural dialogue instead of traditional forms. It is a senior year Human-AI Interaction (HAI) term project built by Chris, Indel, Nate, and Matt.

The core idea: users describe investment goals conversationally (typically how much to invest, when, and in what assets), and the AI extracts timeline, risk tolerance, and constraints to generate personalized ETF-based portfolio recommendations.

## Key Product Concepts

- **Conversational onboarding** replaces traditional multi-step financial forms — the AI classifies user intent and fills profile slots through dialogue
- **Live Profile Sidebar** shows what the system has captured in real time (dual-panel layout, desktop-first)
- **Confirmation loops** — the AI paraphrases ambiguous answers and asks the user to confirm before committing to the profile
- **Portfolio generation** produces ETF allocations (VTI, VXUS, BND, BNDX) with percentages and monthly dollar breakdowns
- **Open-ended input** — after required fields are filled, users can share extra preferences, constraints, or context (e.g., "no crypto", "already have a 401k")
- **Human-in-the-loop generation** — portfolio is generated only when the user clicks a button, not automatically

## Architecture & Design Priorities

This is a human-in-the-loop system, not a black-box AI tool. The HAI course evaluates:
1. **Onboarding** — how the user learns what the system can/cannot do
2. **User Input** — how the user specifies intent and steers the AI
3. **System Output** — how the AI presents its work for human review
4. **User Feedback** — how the user corrects, verifies, or iterates on AI output

The target user is a beginner investor who is intimidated by financial jargon and brokerage forms. All language and UI should be plain and approachable.

## Language & Tooling

- **Language**: Python
- **Platform**: Windows 11
- **Framework**: Streamlit (dark theme, clean/minimal UI)
- **AI**: OpenAI API — model `gpt-4o-mini` with JSON response mode
- **State**: `st.session_state` (no database)
- **Environment**: Always use a venv (`venv/`) — never install packages globally

## File Structure

| File | Purpose |
|------|---------|
| `app.py` | Streamlit entry point: layout, chat loop, sidebar, portfolio display |
| `chat_engine.py` | OpenAI API calls, system prompt, structured JSON profile extraction |
| `portfolio.py` | Rule-based ETF allocation from user profile (risk + timeline -> equity/bond split) |
| `requirements.txt` | Python dependencies: streamlit, openai, python-dotenv |
| `.env` | API key — **git-ignored, never commit** |
| `.env.example` | Template showing required env vars |
| `.streamlit/config.toml` | Dark theme configuration |
| `PRD.md` | Product requirements document — tracks what's built, deferred, and version history |
| `CLAUDE.md` | This file — development guidance |
| `context/` | Course reference materials (project definitions, lecture notes) — not application code |
| `venv/` | Python virtual environment — git-ignored |

## Running the App

```bash
python -m venv venv
source venv/Scripts/activate   # Windows (Git Bash)
pip install -r requirements.txt
streamlit run app.py
```

Requires `OPENAI_API_KEY` in `.env`.

## How the Chat Engine Works

1. User sends a message via `st.chat_input`
2. `chat_engine.py` sends the full conversation history + current profile state to GPT-4o-mini
3. The model returns JSON: `{ message, profile_updates, ready_for_portfolio }`
4. `app.py` displays the message, applies profile updates to session state, updates sidebar
5. When `ready_for_portfolio` is true, a "Generate My Portfolio" button appears
6. User clicks the button -> `portfolio.py` computes allocations -> displayed with progress bars

## Profile Fields

| Field | Type | Required | Example |
|-------|------|----------|---------|
| `goal` | string | Yes | "Retirement" |
| `timeline` | string | Yes | "30 years" |
| `monthly_budget` | string (number) | Yes | "150" |
| `risk_tolerance` | enum | Yes | "moderate" |
| `additional_info` | string | No | "Already have a 401k, no crypto" |

## Visual Style

- Dark theme (#1e1e1e background, #2b2b2b secondary) — similar to ChatGPT/Claude
- Clean and minimal — no excessive decoration, gradients, or emoji overload
- Desktop-first layout with sidebar

## Maintenance Rules

- **PRD.md** must be updated whenever features are added, modified, or removed
- **CLAUDE.md** must be updated whenever files are added/removed, architecture changes, or new conventions are established
- Both files serve as the source of truth for picking up work in future sessions

## Context Directory

`context/` contains course documents (project definitions, prototype decks, lecture notes) that inform requirements. These are reference materials, not application code.
