"""
Run V2 evaluation: populate LLM Response V2 and LLM V2 Rating columns in
benchmark_dataset.csv using the refined system prompt from chat_engine.py.
Predicted Relevancy is shared with V1 and not re-run here.
"""

import os
import sys
import json
import pandas as pd
from pydantic import BaseModel
from typing import Literal
from dotenv import load_dotenv
from openai import OpenAI

# Load API key from project root .env
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Import updated system prompt from chat_engine
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from chat_engine import SYSTEM_PROMPT


# ---------------------------------------------------------------------------
# Pydantic models for structured output
# ---------------------------------------------------------------------------
class Rating(BaseModel):
    rating: Literal[1, 2, 3, 4, 5]


# ---------------------------------------------------------------------------
# Stage conversation contexts (same as V1)
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
            {"role": "assistant", "content": "You're all set! Click the button below to generate your portfolio."}
        ]
    },
    "N/A": {
        "profile": {"goal": None, "timeline": None, "monthly_budget": None, "risk_tolerance": None, "additional_info": None},
        "history": [
            {"role": "assistant", "content": "Hey! I'm ChatFolio. I help you build a starter investment portfolio through conversation. What are you looking to invest for?"}
        ]
    },
}


def get_chatfolio_response(question: str, stage: str) -> str:
    """Send a test question through ChatFolio's updated system prompt and return the message."""
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
    input_path = os.path.join(os.path.dirname(__file__), "benchmark_dataset.csv")
    output_path = os.path.join(os.path.dirname(__file__), "benchmark_dataset_v2.csv")
    df = pd.read_csv(input_path, keep_default_na=False, na_values=[""])
    print(f"Loaded {len(df)} samples")

    df = df.dropna(subset=["Question", "Stage"]).reset_index(drop=True)
    print(f"Processing {len(df)} valid samples\n")

    # Ensure V2 columns exist
    if "LLM Response V2" not in df.columns:
        df["LLM Response V2"] = ""
    if "LLM V2 Rating" not in df.columns:
        df["LLM V2 Rating"] = ""
    if "Human V2 Rating" not in df.columns:
        df["Human V2 Rating"] = ""

    for index, row in df.iterrows():
        question = row["Question"]
        stage = row["Stage"]
        ground_truth = row.get("Ground Truth Response", "")

        # Step 1: Generate V2 response (skip if already filled)
        existing_response = row.get("LLM Response V2")
        if pd.notna(existing_response) and str(existing_response).strip():
            llm_response = str(existing_response).strip()
            response_status = "SKIPPED"
        else:
            llm_response = get_chatfolio_response(question, stage)
            df.at[index, "LLM Response V2"] = llm_response
            response_status = "GENERATED"

        # Step 2: Rate V2 response (always re-run)
        rating = rate_response(ground_truth, llm_response)
        df.at[index, "LLM V2 Rating"] = rating

        print(
            f"[{index + 1:2d}/{len(df)}] {stage:16s} | Rating: {rating} | "
            f"Response: {response_status} | {question[:50]}"
        )

        # Save after every row in case of interruption
        df.to_csv(output_path, index=False)

    print(f"\nSaved to {output_path}")
    print(f"\nLLM V2 Rating distribution:\n{df['LLM V2 Rating'].value_counts().sort_index()}")
    print(f"Average LLM V2 Rating: {df['LLM V2 Rating'].mean():.2f}")
    print(f"Average LLM V1 Rating: {df['LLM V1 Rating'].mean():.2f}")
    print(f"Delta (V2 - V1): {df['LLM V2 Rating'].mean() - df['LLM V1 Rating'].mean():+.2f}")


if __name__ == "__main__":
    main()
