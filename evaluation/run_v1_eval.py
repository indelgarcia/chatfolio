"""
Run V1 evaluation: populate Predicted Relevancy, LLM Response V1, and LLM V1 Rating
columns in benchmark_dataset.csv using GPT-4o-mini with structured Pydantic output.
"""

import os
import json
import pandas as pd
from pydantic import BaseModel
from typing import Literal
from dotenv import load_dotenv
from openai import OpenAI

# Load API key from project root .env
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ---------------------------------------------------------------------------
# Pydantic models for structured output
# ---------------------------------------------------------------------------
class ClassificationResult(BaseModel):
    relevancy: Literal["Profile Building", "Off-Topic"]


class Rating(BaseModel):
    rating: Literal[1, 2, 3, 4, 5]


# ---------------------------------------------------------------------------
# ChatFolio system prompt (copied from chat_engine.py)
# ---------------------------------------------------------------------------
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
3. When a user's answer is vague or could mean different things, paraphrase your understanding and ask them to confirm before saving it.
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

# ---------------------------------------------------------------------------
# Stage conversation contexts (same as notebook cell 9)
# ---------------------------------------------------------------------------
STAGE_CONTEXTS = {
    "Goal": {
        "profile": {"goal": None, "timeline": None, "monthly_budget": None, "risk_tolerance": None, "additional_info": None},
        "history": [
            {"role": "assistant", "content": "Hey! I'm ChatFolio. I help you build a starter investment portfolio through conversation. What are you looking to invest for?"}
        ]
    },
    "Timeline": {
        "profile": {"goal": "Retirement", "timeline": None, "monthly_budget": None, "risk_tolerance": None, "additional_info": None},
        "history": [
            {"role": "assistant", "content": "Hey! I'm ChatFolio. I help you build a starter investment portfolio through conversation. What are you looking to invest for?"},
            {"role": "user", "content": "I want to save for retirement."},
            {"role": "assistant", "content": "Retirement is a great goal! How many years until you plan to retire?"}
        ]
    },
    "Budget": {
        "profile": {"goal": "Retirement", "timeline": "30 years", "monthly_budget": None, "risk_tolerance": None, "additional_info": None},
        "history": [
            {"role": "assistant", "content": "Hey! I'm ChatFolio. What are you looking to invest for?"},
            {"role": "user", "content": "I want to save for retirement."},
            {"role": "assistant", "content": "Retirement is a great goal! How many years until you plan to retire?"},
            {"role": "user", "content": "About 30 years."},
            {"role": "assistant", "content": "30 years is a great timeline! How much can you invest per month?"}
        ]
    },
    "Risk": {
        "profile": {"goal": "Retirement", "timeline": "30 years", "monthly_budget": "200", "risk_tolerance": None, "additional_info": None},
        "history": [
            {"role": "assistant", "content": "Hey! I'm ChatFolio. What are you looking to invest for?"},
            {"role": "user", "content": "I want to save for retirement."},
            {"role": "assistant", "content": "How many years until you plan to retire?"},
            {"role": "user", "content": "About 30 years."},
            {"role": "assistant", "content": "How much can you invest per month?"},
            {"role": "user", "content": "$200 a month."},
            {"role": "assistant", "content": "$200/month is a solid start! How do you feel about risk — would you say conservative, moderate, or aggressive?"}
        ]
    },
    "Additional": {
        "profile": {"goal": "Retirement", "timeline": "30 years", "monthly_budget": "200", "risk_tolerance": "moderate", "additional_info": None},
        "history": [
            {"role": "assistant", "content": "Hey! I'm ChatFolio. What are you looking to invest for?"},
            {"role": "user", "content": "I want to save for retirement."},
            {"role": "assistant", "content": "How many years until you plan to retire?"},
            {"role": "user", "content": "About 30 years."},
            {"role": "assistant", "content": "How much can you invest per month?"},
            {"role": "user", "content": "$200 a month."},
            {"role": "assistant", "content": "How do you feel about risk?"},
            {"role": "user", "content": "I'd say moderate."},
            {"role": "assistant", "content": "Moderate is a great balanced choice! Is there anything else you'd like me to know? For example, any investment preferences, accounts you already have, or things you want to avoid?"}
        ]
    },
    "Post-Generation": {
        "profile": {"goal": "Retirement", "timeline": "30 years", "monthly_budget": "200", "risk_tolerance": "moderate", "additional_info": "None specified"},
        "history": [
            {"role": "assistant", "content": "Hey! I'm ChatFolio. What are you looking to invest for?"},
            {"role": "user", "content": "I want to save for retirement."},
            {"role": "assistant", "content": "How many years until you plan to retire?"},
            {"role": "user", "content": "About 30 years."},
            {"role": "assistant", "content": "How much can you invest per month?"},
            {"role": "user", "content": "$200 a month."},
            {"role": "assistant", "content": "How do you feel about risk?"},
            {"role": "user", "content": "I'd say moderate."},
            {"role": "assistant", "content": "Is there anything else you'd like me to know?"},
            {"role": "user", "content": "No, that's everything."},
            {"role": "assistant", "content": "You're all set! Click the Generate My Portfolio button below to see your personalized recommendation."}
        ]
    },
    "N/A": {
        "profile": {"goal": None, "timeline": None, "monthly_budget": None, "risk_tolerance": None, "additional_info": None},
        "history": [
            {"role": "assistant", "content": "Hey! I'm ChatFolio. I help you build a starter investment portfolio through conversation. What are you looking to invest for?"}
        ]
    },
}


def classify_relevancy(question: str) -> str:
    """Classify a question as Profile Building or Off-Topic using structured output."""
    prompt = f"""You are ChatFolio, an AI investment advisor that helps users build a starter portfolio.
Your scope is limited to: investment goals, timelines, budgets, risk tolerance, and portfolio questions.

Determine if the following user message is relevant to building an investment portfolio ("Profile Building")
or completely unrelated ("Off-Topic").

User message: {question}"""

    response = client.responses.parse(
        model="gpt-4o-mini",
        input=prompt,
        text_format=ClassificationResult,
    )
    return response.output_parsed.relevancy


def get_chatfolio_response(question: str, stage: str) -> str:
    """Send a test question through ChatFolio's system prompt and return the message."""
    ctx = STAGE_CONTEXTS[stage]
    profile_context = (
        "\n\nCurrent user profile:\n"
        + json.dumps(ctx["profile"], indent=2)
        + "\nOnly update fields the user has clearly confirmed."
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT + profile_context}
    ] + ctx["history"] + [
        {"role": "user", "content": question}
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0.7,
        max_tokens=500,
    )

    try:
        parsed = json.loads(response.choices[0].message.content)
        return parsed.get("message", response.choices[0].message.content)
    except json.JSONDecodeError:
        return response.choices[0].message.content


def rate_response(ground_truth: str, llm_response: str) -> int:
    """Rate LLM response quality against ground truth on a 1-5 scale."""
    prompt = f"""Rate the quality of the LLM response compared to the ground truth reference on a scale of 1-5.

5 - Excellent: The response fully matches the expected behavior described in the ground truth.
4 - Good: The response is mostly correct with minor differences from the ground truth.
3 - Adequate: The response is partially correct but misses key elements of the ground truth.
2 - Poor: The response mostly fails to match the expected behavior.
1 - Unsatisfactory: The response is irrelevant or contradicts the ground truth.

Ground Truth Reference: {ground_truth}
LLM Response: {llm_response}"""

    response = client.responses.parse(
        model="gpt-4o-mini",
        input=prompt,
        text_format=Rating,
    )
    return response.output_parsed.rating


def main():
    csv_path = os.path.join(os.path.dirname(__file__), "benchmark_dataset.csv")
    df = pd.read_csv(csv_path, keep_default_na=False, na_values=[""])
    print(f"Loaded {len(df)} samples")

    df = df.dropna(subset=["Question", "Stage"]).reset_index(drop=True)
    print(f"Processing {len(df)} valid samples\n")

    for index, row in df.iterrows():
        question = row["Question"]
        stage = row["Stage"]
        ground_truth = row.get("Ground Truth Response", "")

        # Step 1: Classify relevancy (always re-run)
        predicted = classify_relevancy(question)
        df.at[index, "Predicted Relevancy"] = predicted

        # Step 2: Generate LLM response (skip if already filled)
        existing_response = row.get("LLM Response V1")
        if pd.notna(existing_response) and str(existing_response).strip():
            llm_response = str(existing_response).strip()
            response_status = "SKIPPED"
        else:
            llm_response = get_chatfolio_response(question, stage)
            df.at[index, "LLM Response V1"] = llm_response
            response_status = "GENERATED"

        # Step 3: Rate response quality (always re-run)
        rating = rate_response(ground_truth, llm_response)
        df.at[index, "LLM V1 Rating"] = rating

        print(
            f"[{index + 1:2d}/{len(df)}] {stage:16s} | {predicted:17s} | Rating: {rating} | "
            f"Response: {response_status} | {question[:45]}"
        )

        # Save after every row in case of interruption
        df.to_csv(csv_path, index=False)

    print(f"\nSaved to {csv_path}")
    print(f"\nPredicted Relevancy distribution:\n{df['Predicted Relevancy'].value_counts()}")
    print(f"\nLLM V1 Rating distribution:\n{df['LLM V1 Rating'].value_counts().sort_index()}")
    print(f"Average LLM V1 Rating: {df['LLM V1 Rating'].mean():.2f}")


if __name__ == "__main__":
    main()
