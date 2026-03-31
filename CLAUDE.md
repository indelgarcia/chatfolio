# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ChatFolio is an AI-powered conversational investment advisor that helps beginner investors build a starter portfolio through natural dialogue instead of traditional forms. It is a senior year Human-AI Interaction (HAI) term project built by Chris, Indel, Nate, and Matt.

The core idea: users describe investment goals conversationally (typically how much to invest, when, and in what assets), and the AI extracts timeline, risk tolerance, and constraints to generate personalized ETF-based portfolio (indivudal stocks, roth IRAs, etc...) recommendations.

## Key Product Concepts

- **Conversational onboarding** replaces traditional multi-step financial forms — the AI classifies user intent and fills profile slots through dialogue
- **Live Profile Sidebar** shows what the system has captured in real time (dual-panel layout, desktop-first)
- **Confirmation loops** — the AI paraphrases ambiguous answers and asks the user to confirm before committing to the profile
- **Portfolio generation** produces ETF allocations (VTI, VXUS, etc.) with a risk steering slider for post-generation adjustment
- **Review layer** with four actions: Accept / Adjust / Explain / Compare — designed to reduce decision anxiety by letting users explore before committing

## Architecture & Design Priorities

This is a human-in-the-loop system, not a black-box AI tool. The HAI course evaluates:
1. **Onboarding** — how the user learns what the system can/cannot do
2. **User Input** — how the user specifies intent and steers the AI
3. **System Output** — how the AI presents work for human review
4. **User Feedback** — how the user corrects, verifies, or iterates on AI output

The target user is a beginner investor who is intimidated by financial jargon and brokerage forms. All language and UI should be plain and approachable.

## Language & Tooling

- **Language**: Python
- **Platform**: Windows 11
- **Permitted prototyping tools**: Streamlit, OpenAI API with its cheap model: model="gpt-4o-mini"

## Context Directory

`context/` contains course documents (project definitions, prototype decks, lecture notes) that inform requirements. These are reference materials, not application code.
