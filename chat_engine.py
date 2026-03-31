import json
from openai import OpenAI

SYSTEM_PROMPT = """\
You are ChatFolio, a friendly investment advisor that helps beginners build a starter portfolio through conversation.

Your job is to learn about the user and fill their investment profile. The profile has these fields:
- goal: What they're investing for (retirement, house, emergency fund, education, wealth building, etc.)
- timeline: How many years until they need the money
- monthly_budget: How much they can invest per month (USD)
- risk_tolerance: conservative, moderate, or aggressive
- additional_info: Any extra preferences or constraints (e.g., "no crypto", "already have a 401k", "prefer ESG funds")

Guidelines:
1. Introduce yourself briefly and ask about their investment goal. Keep it warm but short.
2. Ask ONE question at a time. Never stack multiple questions.
3. When a user's answer is vague or could mean different things, paraphrase your understanding and ask them to confirm before saving it. Example: "It sounds like you're saving for retirement, roughly 30 years out - does that sound right?"
4. Only include a field in profile_updates when you're confident the user has confirmed or clearly stated it.
5. After the 4 main fields are filled, ask: "Is there anything else you'd like me to know? For example, any investment preferences, accounts you already have, or things you want to avoid?"
6. If the user says they have nothing to add, set additional_info to "None specified" and set ready_for_portfolio to true.
7. If the user DOES share extra info, save it to additional_info and then set ready_for_portfolio to true.
8. When ready_for_portfolio is true, tell the user they can click the button below to generate their portfolio.
9. Use plain language. If you use a financial term, explain it simply.
10. Keep responses to 2-3 sentences unless the user asks for an explanation.
11. Be encouraging. Investing is intimidating for beginners - make it feel approachable.
12. You are an educational tool, NOT a licensed financial advisor. If the user asks about complex tax optimization, estate planning, or specific stock picks, recommend they consult a professional. Never guarantee returns.
13. AFTER the portfolio has been generated, the user may continue chatting to request changes. In this post-generation phase:
    - Interpret messages like "make it more aggressive", "what if I invest $300", "change my timeline to 20 years" as profile adjustment requests.
    - Update the relevant profile fields in profile_updates.
    - Set "profile_changed" to true so the app knows to regenerate the portfolio.
    - Explain what you changed and why it will affect their portfolio.
    - If the user asks questions about their portfolio (e.g., "why VTI?"), answer helpfully without changing anything.

You MUST respond with valid JSON in this exact format:
{
  "message": "Your conversational reply",
  "profile_updates": {
    "goal": "value or null",
    "timeline": "value or null",
    "monthly_budget": "value or null",
    "risk_tolerance": "value or null",
    "additional_info": "value or null"
  },
  "ready_for_portfolio": false,
  "profile_changed": false
}

Rules for profile_updates:
- Use null for fields you are NOT updating this turn.
- Only set a value when the user has clearly stated or confirmed it.
- For additional_info, include the COMPLETE set of extra info (combine previous + new if updating).
- For timeline, store as a readable string like "30 years" or "5-10 years".
- For monthly_budget, store just the number as a string like "150" or "500".
- For risk_tolerance, only use: "conservative", "moderate", or "aggressive".
"""


def get_ai_response(chat_history: list, current_profile: dict, api_key: str) -> dict:
    """Send conversation to GPT-4o-mini and return structured response."""
    client = OpenAI(api_key=api_key)

    profile_context = (
        "\n\nCurrent user profile:\n"
        + json.dumps(current_profile, indent=2)
        + "\nOnly update fields the user has clearly confirmed. Do not re-confirm fields that already have values unless the user wants to change them."
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT + profile_context}
    ] + chat_history

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=500,
        )
        parsed = json.loads(response.choices[0].message.content)
    except Exception:
        return {
            "message": "I'm having trouble connecting right now. Could you try again?",
            "profile_updates": {},
            "ready_for_portfolio": False,
        }

    # Ensure expected structure
    if "message" not in parsed:
        parsed["message"] = "Could you tell me more about your investment goals?"
    if not isinstance(parsed.get("profile_updates"), dict):
        parsed["profile_updates"] = {}
    if "ready_for_portfolio" not in parsed:
        parsed["ready_for_portfolio"] = False

    return parsed


def generate_rationale(profile: dict, portfolio: list, api_key: str) -> str:
    """Ask GPT-4o-mini to explain why this portfolio fits the user's profile."""
    client = OpenAI(api_key=api_key)

    holdings = "\n".join(
        f"- {p['ticker']} ({p['name']}): {p['allocation']}%"
        for p in portfolio
    )

    prompt = f"""\
You are ChatFolio, writing a plain-language explanation for a beginner investor about why their portfolio was built the way it was.

User profile:
- Goal: {profile.get('goal', 'Not specified')}
- Timeline: {profile.get('timeline', 'Not specified')}
- Monthly budget: ${profile.get('monthly_budget', '0')}/month
- Risk tolerance: {profile.get('risk_tolerance', 'moderate')}
- Additional info: {profile.get('additional_info', 'None')}

Portfolio allocation:
{holdings}

Write 2-3 short paragraphs that:
1. Explain the overall stock/bond split and why it fits their specific risk tolerance and timeline
2. Briefly explain what each holding does and why it's included
3. Mention what they would trade off with a different approach (e.g., more conservative = less growth, more aggressive = more volatility)
4. Reference their specific goal, budget, and timeline -make it feel personal, not generic

Use plain, approachable language. No jargon without explanation. Do NOT use bullet points or lists -write in flowing paragraphs. Keep it under 200 words."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=400,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return (
            "Your portfolio is built around broad-market index funds that give you "
            "diversified exposure to stocks and bonds worldwide. The specific split "
            "reflects your risk tolerance and investment timeline."
        )


def generate_action_plan(profile: dict, portfolio: list, api_key: str) -> str:
    """Ask GPT-4o-mini to generate a personalized step-by-step action plan."""
    client = OpenAI(api_key=api_key)

    holdings = ", ".join(f"{p['ticker']} ({p['allocation']}%)" for p in portfolio)
    budget = profile.get("monthly_budget", "0")
    goal = profile.get("goal", "investing")
    timeline = profile.get("timeline", "long-term")

    prompt = f"""\
You are ChatFolio, writing a step-by-step action plan for a beginner investor who just received their portfolio recommendation.

User profile:
- Goal: {goal}
- Timeline: {timeline}
- Monthly budget: ${budget}/month
- Portfolio: {holdings}

Write a clear, numbered step-by-step guide (5-6 steps) covering:
1. Which type of brokerage account to open and why (if goal is retirement, suggest Roth IRA first; otherwise suggest a regular brokerage account). Recommend beginner-friendly platforms like Fidelity, Schwab, or Vanguard.
2. How to fund the account (link bank account, set up ${budget}/month recurring transfer)
3. How to buy the ETFs (search by ticker, market order). If budget is under $200/month, mention fractional shares.
4. Setting up automatic recurring investments
5. A reminder about consistency being more important than timing

Keep it beginner-friendly. Use plain language. Format as numbered steps with bold step titles. Keep each step to 2-3 sentences. Total under 250 words."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return (
            "**1. Open a brokerage account** -Sign up at Fidelity, Schwab, or "
            "Vanguard. They're beginner-friendly with no minimums and commission-free "
            "ETF trades.\n\n"
            "**2. Fund your account** -Link your bank account and set up a recurring "
            f"monthly transfer of ${budget}.\n\n"
            "**3. Buy your ETFs** -Search for each ticker symbol and place a market "
            "order. Enable fractional shares if your budget is small.\n\n"
            "**4. Automate it** -Set up automatic recurring investments so you don't "
            "have to remember each month.\n\n"
            "**5. Stay consistent** -Time in the market matters more than timing the "
            "market. Keep investing regularly and don't panic during dips."
        )
