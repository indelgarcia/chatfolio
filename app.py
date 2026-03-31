import streamlit as st
import os
from dotenv import load_dotenv
from chat_engine import get_ai_response
from portfolio import generate_portfolio

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

API_KEY = os.getenv("OPENAI_API_KEY")

# ---------------------------------------------------------------------------
# Sidebar — live profile
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
st.caption("Build your starter portfolio through conversation — not forms.")

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
        st.session_state.portfolio = generate_portfolio(st.session_state.profile)
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

    st.rerun()
