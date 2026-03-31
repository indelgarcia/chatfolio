import streamlit as st
import os
from dotenv import load_dotenv
from chat_engine import get_ai_response, generate_rationale, generate_action_plan
from portfolio import generate_portfolio
from projections import generate_projections

load_dotenv()

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="ChatFolio",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    "<style>.block-container{max-width:880px}</style>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "profile" not in st.session_state:
    st.session_state.profile = {
        "goal": None,
        "timeline": None,
        "monthly_budget": None,
        "risk_tolerance": None,
        "additional_info": None,
    }
if "portfolio" not in st.session_state:
    st.session_state.portfolio = None
if "ready" not in st.session_state:
    st.session_state.ready = False
if "greeted" not in st.session_state:
    st.session_state.greeted = False
if "rationale" not in st.session_state:
    st.session_state.rationale = None
if "action_plan" not in st.session_state:
    st.session_state.action_plan = None

API_KEY = os.getenv("OPENAI_API_KEY")

# ---------------------------------------------------------------------------
# Sidebar -live profile
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Your Profile")
    st.caption("Built from your conversation")

    _profile = st.session_state.profile
    _labels = {
        "goal": "Goal",
        "timeline": "Timeline",
        "monthly_budget": "Monthly Budget",
        "risk_tolerance": "Risk Tolerance",
        "additional_info": "Additional Info",
    }

    filled = 0
    for key, label in _labels.items():
        val = _profile.get(key)
        if val and val != "None specified":
            st.markdown(f"**{label}**")
            st.markdown(val)
            if key != "additional_info":
                filled += 1
        else:
            st.markdown(f"**{label}**")
            st.caption("Waiting...")
        st.divider()

    st.progress(min(filled / 4, 1.0), text=f"{filled}/4 required")

    if st.session_state.portfolio:
        st.success("Portfolio generated")

    st.divider()
    if st.button("Start Over"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

# ---------------------------------------------------------------------------
# Main area
# ---------------------------------------------------------------------------
st.title("ChatFolio")
st.caption("Build your starter portfolio through conversation -not forms.")

# ---------------------------------------------------------------------------
# Onboarding panel -shown until the user starts chatting
# ---------------------------------------------------------------------------
if not st.session_state.messages or len(st.session_state.messages) <= 1:
    with st.expander("What is ChatFolio?", expanded=True):
        st.markdown(
            "**ChatFolio helps you build a starter investment portfolio through a "
            "simple conversation.** No forms, no jargon -just tell me about your "
            "goals and I'll recommend a diversified mix of low-cost index funds.\n\n"
            "**Here's what I'll ask about:**\n"
            "- What you're investing for (retirement, a house, etc.)\n"
            "- How many years until you need the money\n"
            "- How much you can invest per month\n"
            "- How comfortable you are with risk\n\n"
            "**This takes about 2-3 minutes.** At the end, you'll get a personalized "
            "portfolio with an explanation of why it fits you, projected growth over "
            "time, and step-by-step instructions for getting started.\n\n"
            "**What ChatFolio is not:** I'm an educational tool, not a licensed "
            "financial advisor. I don't execute trades or guarantee returns. For "
            "complex financial situations, consult a professional."
        )

if not API_KEY:
    st.error("Set OPENAI_API_KEY in your .env file to get started.")
    st.stop()

# Render chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# First-run greeting
if not st.session_state.greeted:
    with st.spinner(""):
        resp = get_ai_response([], st.session_state.profile, API_KEY)
    greeting = resp.get(
        "message",
        "Hey! I'm ChatFolio. I help you build a starter investment portfolio "
        "through a simple conversation. What are you looking to invest for?",
    )
    st.session_state.messages.append({"role": "assistant", "content": greeting})
    st.session_state.greeted = True
    st.rerun()

# ---------------------------------------------------------------------------
# Generate button (shown once profile is complete, before portfolio exists)
# ---------------------------------------------------------------------------
if st.session_state.ready and not st.session_state.portfolio:
    if st.button("Generate My Portfolio", type="primary", use_container_width=True):
        with st.spinner("Building your portfolio..."):
            st.session_state.portfolio = generate_portfolio(st.session_state.profile)
            st.session_state.rationale = generate_rationale(
                st.session_state.profile, st.session_state.portfolio, API_KEY
            )
            st.session_state.action_plan = generate_action_plan(
                st.session_state.profile, st.session_state.portfolio, API_KEY
            )
        st.rerun()

# ---------------------------------------------------------------------------
# Portfolio display
# ---------------------------------------------------------------------------
if st.session_state.portfolio:
    st.divider()
    st.subheader("Your Portfolio")

    prof = st.session_state.profile
    st.caption(
        f"{prof.get('goal', '')}  ·  {prof.get('timeline', '')} horizon  ·  "
        f"${prof.get('monthly_budget', '0')}/mo  ·  {prof.get('risk_tolerance', '')} risk"
    )

    # Parse budget for per-ETF monthly amount
    budget_raw = str(prof.get("monthly_budget") or "0")
    try:
        budget = float("".join(c for c in budget_raw if c.isdigit() or c == ".") or "0")
    except ValueError:
        budget = 0.0

    for item in st.session_state.portfolio:
        monthly = budget * item["allocation"] / 100
        c1, c2, c3 = st.columns([1.5, 3.5, 1])
        with c1:
            st.markdown(f"**{item['ticker']}**")
            st.caption(item["name"])
        with c2:
            st.progress(item["allocation"] / 100)
        with c3:
            line = f"**{item['allocation']}%**"
            if budget > 0:
                line += f"  \n${monthly:.0f}/mo"
            st.markdown(line)

    # Rationale
    if st.session_state.rationale:
        st.divider()
        st.subheader("Why This Portfolio?")
        st.markdown(st.session_state.rationale)

    # Growth projections
    if budget > 0:
        timeline_str = str(prof.get("timeline") or "10")
        digits = "".join(c for c in timeline_str if c.isdigit())
        proj_years = int(digits) if digits else 10
        proj_years = max(proj_years, 5)  # at least 5 years

        proj_df = generate_projections(st.session_state.portfolio, budget, proj_years)

        st.divider()
        st.subheader("Projected Growth")
        st.caption("Estimated portfolio value over time based on historical averages")

        # Line chart
        chart_df = proj_df.set_index("Year")
        st.line_chart(chart_df)

        # Summary table at key milestones
        milestones = [y for y in [5, 10, 15, 20, 25, 30, 40] if y <= proj_years]
        if proj_years not in milestones:
            milestones.append(proj_years)
        milestones.sort()

        summary_rows = proj_df[proj_df["Year"].isin(milestones)].copy()
        summary_rows = summary_rows.set_index("Year")
        for col in summary_rows.columns:
            summary_rows[col] = summary_rows[col].apply(lambda x: f"${x:,.0f}")
        st.table(summary_rows)

        st.caption(
            "Projections use historical average returns and assume consistent monthly "
            "contributions. Actual results will vary. Past performance does not "
            "guarantee future results."
        )

    # Action plan
    if st.session_state.action_plan:
        st.divider()
        with st.expander("How to Get Started", expanded=False):
            st.markdown(st.session_state.action_plan)

    # Disclaimer
    st.divider()
    st.caption(
        "ChatFolio is an educational tool, not a licensed financial advisor. "
        "Allocations are based on general principles and historical averages -"
        "past performance does not guarantee future results. Consult a qualified "
        "financial professional before making investment decisions."
    )

# ---------------------------------------------------------------------------
# Chat input
# ---------------------------------------------------------------------------
if prompt := st.chat_input("Type your message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    api_msgs = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]

    with st.spinner(""):
        resp = get_ai_response(api_msgs, st.session_state.profile, API_KEY)

    st.session_state.messages.append(
        {"role": "assistant", "content": resp.get("message", "Could you rephrase that?")}
    )

    # Update profile with confirmed fields
    for key, val in resp.get("profile_updates", {}).items():
        if val is not None and key in st.session_state.profile:
            st.session_state.profile[key] = str(val)

    if resp.get("ready_for_portfolio"):
        st.session_state.ready = True

    # If profile changed after portfolio was already generated, regenerate
    if resp.get("profile_changed") and st.session_state.portfolio:
        st.session_state.portfolio = generate_portfolio(st.session_state.profile)
        st.session_state.rationale = generate_rationale(
            st.session_state.profile, st.session_state.portfolio, API_KEY
        )
        st.session_state.action_plan = generate_action_plan(
            st.session_state.profile, st.session_state.portfolio, API_KEY
        )

    st.rerun()
