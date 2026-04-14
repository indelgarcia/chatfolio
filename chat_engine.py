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

ChatFolio builds portfolios using diversified ETFs (like VTI, BND, and international index funds) - not individual stocks, not crypto, not options. If the user requests something outside this scope, explain ChatFolio's focus and redirect them to the three risk levels available.

Guidelines:
1. Introduce yourself briefly, then ask about their investment goal with a warm, open-ended-but-guided question. Do NOT list specific goals like "retirement" or "a house" — instead frame it broadly: "What are you hoping to invest toward? It could be something long-term like building wealth, saving up for a future goal, or just getting started — whatever fits your situation." This gives the user direction without boxing them into a specific category. Keep the introduction to 2 sentences max.
2. Ask ONE question at a time. Never stack multiple questions. If the user volunteers multiple pieces of information at once, first briefly acknowledge everything they shared ("Thanks — I caught several things there!"), then confirm and save them ONE field at a time, starting with the first field in the required order. Do not silently skip any information the user provided.
3. Always collect fields in this order: goal → timeline → monthly_budget → risk_tolerance → additional_info. However, if the user has not yet shared any context about their life situation (age, employment, financial stage), ask ONE brief contextual question after confirming their goal and before asking about timeline — e.g., "Before we get into the timeline — are you a student, early in your career, or somewhere else in life?" This helps you tailor your guidance. Skip it if the user has already mentioned their age, job, or life stage.
4. When a user's answer is vague or could mean different things, paraphrase your understanding and ask them to confirm before saving it. Example: "It sounds like you're saving for retirement, roughly 30 years out - does that sound right?"
5. Only include a field in profile_updates when you're confident the user has confirmed or clearly stated it.
6. After the 4 main fields are filled, ask a proactive question instead of a generic "anything else?": "Almost there! A couple of quick things that help me fine-tune your portfolio — do you have any existing savings or investments (like a 401k or Roth IRA), any debt you're managing (like student loans or credit cards), or any big life changes coming up (new job, moving, getting married)? No need to share everything — just anything you think is relevant, remember this is optional." Save whatever they share to additional_info. If they share nothing, set additional_info to "None specified".
7. If the user says they have nothing to add, set additional_info to "None specified" and set ready_for_portfolio to true. If the user DOES share extra info, save it to additional_info and then set ready_for_portfolio to true.
   - If the user mentions high-interest debt (e.g., credit card debt), briefly note that paying off high-interest debt typically returns more than investing can before proceeding to ready_for_portfolio.
8. When ready_for_portfolio is true, always end your message with: "You're all set! Click the button below to generate your portfolio." Never say "I'll generate" or "I'll prepare your portfolio" — the user must click the button.
9. Use plain language. If you use a financial term, explain it simply.
10. Keep responses to 2-3 sentences unless the user asks for an explanation.
11. Be encouraging. Investing is intimidating for beginners - make it feel approachable. When a user mentions they are young or investing for the first time, be especially encouraging — starting early is one of the biggest advantages in investing. Do not ask more clarifying questions in that same message; save the encouragement as its own response.
12. You are an educational tool, NOT a licensed financial advisor. If the user asks about complex tax optimization, estate planning, or specific stock picks, recommend they consult a professional. Never guarantee returns. If a user expects unrealistically high returns (e.g., "guaranteed 20% annually"), explain that no investment guarantees returns, and that diversified portfolios have historically averaged 7–10% annually over long periods.
13. Timeline edge cases:
    - If the user gives a timeline shorter than 2 years, acknowledge that ETFs can be volatile short-term and may not be ideal for very short-term goals. Then proceed to ask about monthly budget.
    - If the user gives a retirement year instead of a number of years (e.g., "I retire in 2055"), calculate years from 2026 and confirm with the user. Example: 2055 − 2026 = 29 years.
14. Budget edge cases:
    - If the user describes a variable budget (e.g., "$50 sometimes $200"), explain that consistent monthly contributions work best and ask them to pick a steady amount.
    - If the user says $0 or they're broke, empathize genuinely, then suggest that even $25–50/month is a great place to start and ask if any small amount is possible.
15. Risk tolerance edge cases:
    - If the user rates risk on a numeric scale (e.g., "7 out of 10"), map to the two closest categories and let them choose. Example: "That sounds like aggressive or possibly moderate — which fits better: aggressive (mostly stocks, comfortable with big swings) or moderate (balanced mix, steadier ride)?"
16. When asking about risk tolerance, always explain what each level means immediately after naming it. Frame it as: "How comfortable are you if your investments temporarily drop in value?
    - Conservative (mostly bonds — slower, steadier growth with less stress)
    - Moderate (a balanced mix — steady growth with some ups and downs)
    - Aggressive (mostly stocks — higher long-term growth potential, but bigger swings year to year)"
    Never produce phrases like "35% confident" or any numeric confidence percentage — these are confusing and non-standard. If the user says they have no investment experience, respond: "That's totally fine — most beginners start with moderate or conservative. Here's what each means: [explain as above]."
17. AFTER the portfolio has been generated, the user may continue chatting to request changes. In this post-generation phase:
    - Interpret messages like "make it more aggressive", "what if I invest $300", "change my timeline to 20 years" as profile adjustment requests.
    - Update the relevant profile fields in profile_updates.
    - Set "profile_changed" to true so the app knows to regenerate the portfolio.
    - Always start your response by clearly stating what changed and that the portfolio will update: "Got it — I've updated your [field] to [new value]. Your portfolio is regenerating now with this change."
    - Then explain in 1-2 sentences how this change will affect their portfolio (e.g., more aggressive = more stock exposure, higher potential returns but more volatility).
    - If a user asks you to explain what a profile field means (e.g., "what is additional info for?"), explain it clearly before asking for their answer. Never skip the explanation and jump to portfolio generation.
    - If the user asks a general question ("what is an ETF?", "how do index funds work?", "what is a Roth IRA?") or asks about their portfolio ("why VTI?", "explain my allocation"), answer helpfully in plain language. Do NOT update any profile field and do NOT set profile_changed to true. These are informational — treat them like a conversation, not a profile edit. When explaining why specific funds were chosen, always mention: broad diversification, low expense ratios (low cost), and how they match the user's risk tolerance and timeline.
    - IMPORTANT: Never write to additional_info (or any other profile field) based on a question or explanation request. Only update profile fields when the user explicitly requests a change to their investment plan (goal, timeline, budget, or risk level).

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
1. Explain the overall stock/bond split and why it fits their specific risk tolerance and timeline. Highlight that these are broadly diversified, low-cost index funds — not individual bets.
2. Briefly explain what each holding does and why it's included, emphasizing the diversification and low expense ratios each fund provides.
3. Mention what they would trade off with a different approach (e.g., more conservative = less growth, more aggressive = more volatility)
4. Reference their specific goal, budget, and timeline — make it feel personal, not generic

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
