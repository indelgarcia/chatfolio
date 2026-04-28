import streamlit as st
import os
import json
import base64
from dotenv import load_dotenv
from chat_engine import get_ai_response, generate_rationale, generate_action_plan
from portfolio import generate_portfolio
from projections import generate_projections, blended_return
from glossary import GLOSSARY
from pdf_report import generate_pdf

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
    """
    <style>
    section[data-testid="stSidebar"] > div:first-child {
        background-color: #FFFCF0;
        border-right: 2px solid #D4B345;
    }
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #B8962E, #E8C84A);
        border-radius: 4px;
    }
    button[kind="primary"] {
        background: linear-gradient(135deg, #C5A028, #D9BA4A) !important;
        border: none !important;
        color: #fff !important;
        font-weight: 600 !important;
        letter-spacing: 0.02em;
        box-shadow: 0 2px 8px rgba(197,160,40,0.28) !important;
        transition: all .15s ease !important;
    }
    button[kind="primary"]:hover {
        box-shadow: 0 5px 18px rgba(197,160,40,0.42) !important;
        transform: translateY(-1px);
    }
    button[kind="secondary"] {
        border: 1.5px solid #C5A028 !important;
        color: #8B6914 !important;
        background: transparent !important;
        transition: all .15s ease !important;
    }
    button[kind="secondary"]:hover { background: #FBF5DC !important; }
    h1 { border-bottom: 3px solid #C5A028; padding-bottom: 6px; }
    h2, h3 { color: #7A5C10; }
    hr { border-color: #E0D09A !important; }
    [data-testid="stMetricValue"] { color: #7A5C10 !important; font-weight: 700 !important; }
    [data-testid="stChatMessage"] {
        border: 1px solid #EDE5C0; border-radius: 10px; margin-bottom: 4px;
    }
    [data-testid="stAlert"] { border-left: 4px solid #C5A028 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
_defaults = {
    "messages": [],
    "profile": {
        "goal": None, "timeline": None, "monthly_budget": None,
        "risk_tolerance": None, "additional_info": None,
    },
    "portfolio": None,
    "ready": False,
    "greeted": False,
    "rationale": None,
    "action_plan": None,
    "pending_prompt": None,
    "quiz_step": 0,
    "quiz_score": 0,
    "active_scenario": None,
    "show_landing": True,
    "sensitivity_budget": None,
    "share_loaded": False,
}
for _k, _v in _defaults.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ---------------------------------------------------------------------------
# Share link loading
# ---------------------------------------------------------------------------
if not st.session_state.share_loaded:
    try:
        _sp = st.query_params.get("share")
        if _sp:
            _data = json.loads(base64.urlsafe_b64decode(_sp.encode()).decode())
            for _k, _v in _data.get("profile", {}).items():
                st.session_state.profile[_k] = _v
            if _data.get("portfolio"):
                st.session_state.portfolio = _data["portfolio"]
                st.session_state.ready = True
                st.session_state.show_landing = False
    except Exception:
        pass
    st.session_state.share_loaded = True

API_KEY = os.getenv("OPENAI_API_KEY")

if not st.session_state.portfolio:
    st.markdown("<style>.block-container{max-width:880px}</style>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Edit-profile callbacks
# ---------------------------------------------------------------------------
def _sync_tl_slider():
    st.session_state._edit_tl_input = int(st.session_state._edit_tl_slider)

def _sync_tl_input():
    st.session_state._edit_tl_slider = max(1, min(40, int(st.session_state._edit_tl_input or 1)))

def _sync_bgt_slider():
    st.session_state._edit_bgt_input = int(st.session_state._edit_bgt_slider)

def _sync_bgt_input():
    st.session_state._edit_bgt_slider = max(0, min(5000, int(st.session_state._edit_bgt_input or 0)))

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Your Profile")
    st.caption("Built from your conversation")

    _p = st.session_state.profile
    _has_portfolio = bool(st.session_state.portfolio)
    _risk_opts = ["conservative", "moderate", "aggressive"]

    if _has_portfolio:
        _tl_digits = "".join(c for c in str(_p.get("timeline") or "10") if c.isdigit())
        _tl_init = max(1, int(_tl_digits) if _tl_digits else 10)
        _bgt_raw = "".join(c for c in str(_p.get("monthly_budget") or "200") if c.isdigit() or c == ".")
        _bgt_init = max(0, int(float(_bgt_raw)) if _bgt_raw else 200)
        _risk_init = (_p.get("risk_tolerance") or "moderate").lower()
        if _risk_init not in _risk_opts:
            _risk_init = "moderate"

        if "_edit_tl_slider" not in st.session_state:
            st.session_state._edit_tl_slider = min(_tl_init, 40)
        if "_edit_tl_input" not in st.session_state:
            st.session_state._edit_tl_input = _tl_init
        if "_edit_bgt_slider" not in st.session_state:
            st.session_state._edit_bgt_slider = min(_bgt_init, 5000)
        if "_edit_bgt_input" not in st.session_state:
            st.session_state._edit_bgt_input = _bgt_init
        if "_edit_risk" not in st.session_state:
            st.session_state._edit_risk = _risk_init
        if "_edit_goal" not in st.session_state:
            st.session_state._edit_goal = _p.get("goal") or ""

    filled = 0
    for _key, _label, _optional in [
        ("goal", "Goal", False),
        ("timeline", "Timeline", False),
        ("monthly_budget", "Monthly Budget", False),
        ("risk_tolerance", "Risk Tolerance", False),
        ("additional_info", "Additional Info", True),
    ]:
        _val = _p.get(_key)
        _display_label = f"**{_label}** *(optional)*" if _optional else f"**{_label}**"
        st.markdown(_display_label)
        if _val and _val != "None specified":
            st.markdown(_val)
            if not _optional:
                filled += 1
        else:
            st.caption("Waiting...")

        if _has_portfolio and not _optional:
            if _key == "goal":
                st.text_input("Goal", key="_edit_goal", label_visibility="collapsed")
            elif _key == "timeline":
                st.slider("Timeline", 1, 40, key="_edit_tl_slider",
                          on_change=_sync_tl_slider, label_visibility="collapsed")
                st.number_input("years", min_value=1, max_value=50,
                                key="_edit_tl_input", on_change=_sync_tl_input)
            elif _key == "monthly_budget":
                st.slider("Budget", 0, 5000, step=25, key="_edit_bgt_slider",
                          on_change=_sync_bgt_slider, label_visibility="collapsed")
                st.number_input("$ / month", min_value=0, max_value=50000,
                                key="_edit_bgt_input", on_change=_sync_bgt_input)
            elif _key == "risk_tolerance":
                st.selectbox("Risk", _risk_opts, key="_edit_risk", label_visibility="collapsed")
        st.divider()

    st.progress(min(filled / 4, 1.0), text=f"{filled}/4 required")

    if _has_portfolio:
        st.success("Portfolio generated")
        if st.button("Save Changes", type="primary", use_container_width=True):
            st.session_state.profile["goal"] = st.session_state._edit_goal
            st.session_state.profile["timeline"] = str(st.session_state._edit_tl_input)
            st.session_state.profile["monthly_budget"] = str(st.session_state._edit_bgt_input)
            st.session_state.profile["risk_tolerance"] = st.session_state._edit_risk

            with st.spinner("Updating portfolio..."):
                st.session_state.portfolio = generate_portfolio(st.session_state.profile)
                st.session_state.rationale = generate_rationale(
                    st.session_state.profile, st.session_state.portfolio, API_KEY)
                st.session_state.action_plan = generate_action_plan(
                    st.session_state.profile, st.session_state.portfolio, API_KEY)

            for _k in ("_edit_tl_slider", "_edit_tl_input", "_edit_bgt_slider",
                       "_edit_bgt_input", "_edit_risk", "_edit_goal"):
                st.session_state.pop(_k, None)
            st.session_state.sensitivity_budget = None

            st.toast("Portfolio updated!")
            st.rerun()

    st.divider()
    if st.button("Start Over"):
        for _k in list(st.session_state.keys()):
            del st.session_state[_k]
        st.rerun()

# ---------------------------------------------------------------------------
# Landing page
# ---------------------------------------------------------------------------
if st.session_state.show_landing:
    st.markdown("""<style>
    section[data-testid="stSidebar"]{display:none!important}
    .block-container{max-width:980px;padding-top:2rem}
    </style>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;padding:36px 0 20px">
      <div style="font-size:3.6em;font-weight:900;letter-spacing:-0.02em;color:#1A1A1A;line-height:1.1">
        Chat<span style="color:#C5A028">Folio</span>
      </div>
      <div style="font-size:1.15em;color:#6B5218;margin-top:10px;max-width:540px;
                  margin-left:auto;margin-right:auto;line-height:1.6">
        Your first investment portfolio, built through conversation — not forms.
      </div>
    </div>
    """, unsafe_allow_html=True)

    _lc1, _lc2, _lc3 = st.columns([3, 2, 3])
    with _lc2:
        if st.button("Get Started →", type="primary", use_container_width=True):
            st.session_state.show_landing = False
            st.rerun()

    st.markdown("<div style='margin:28px 0'></div>", unsafe_allow_html=True)

    _sc1, _sc2, _sc3 = st.columns(3)
    for _col, _icon, _title, _desc in [
        (_sc1, "💬", "1. Chat",
         "Tell us your goals, timeline, and budget through natural conversation. No jargon, no complicated forms."),
        (_sc2, "📋", "2. Build Your Profile",
         "The AI extracts what matters — goal, timeline, budget, risk — and shows your profile filling in real time."),
        (_sc3, "📈", "3. Get Your Portfolio",
         "A personalized ETF allocation with rationale, projected growth, and step-by-step setup instructions."),
    ]:
        with _col:
            st.markdown(f"""
            <div style="text-align:center;padding:22px 14px;background:#FFFCF0;
                        border:1.5px solid #DDD0A0;border-radius:12px;min-height:160px">
              <div style="font-size:2em;margin-bottom:8px">{_icon}</div>
              <div style="font-weight:700;color:#7A5C10;margin-bottom:6px">{_title}</div>
              <div style="font-size:0.87em;color:#4A3A10;line-height:1.45">{_desc}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin:28px 0'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;color:#7A5C10;margin-bottom:16px'>What's included</h3>",
                unsafe_allow_html=True)

    _fa, _fb, _fc = st.columns(3)
    _fd, _fe, _ff = st.columns(3)
    for _col, _icon, _title, _desc in [
        (_fa, "🎯", "Risk Tolerance Quiz",
         "3 scenario-based questions determine your risk profile — no guessing required."),
        (_fb, "📊", "Scenario Testing",
         "See how your portfolio holds up in a 2008 crash, tech boom, stagflation, and more."),
        (_fc, "⚖️", "Portfolio Comparison",
         "Compare conservative, moderate, and aggressive allocations side by side."),
        (_fd, "⏰", "Cost of Waiting",
         "See the real dollar cost of delaying your first investment by 1, 3, or 5 years."),
        (_fe, "🎯", "Savings Goal Calculator",
         "Work backwards from a target amount to find your required monthly contribution."),
        (_ff, "📄", "Export & Share",
         "Download a full PDF report or share your portfolio with a link."),
    ]:
        with _col:
            st.markdown(f"""
            <div style="padding:16px 14px;background:#FAFAF5;border:1px solid #E8E0C0;
                        border-radius:10px;margin-bottom:12px">
              <div style="font-size:1.5em;margin-bottom:4px">{_icon}</div>
              <div style="font-weight:600;color:#1A1A1A;margin-bottom:4px;font-size:0.95em">{_title}</div>
              <div style="font-size:0.82em;color:#5A5040;line-height:1.4">{_desc}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin:20px 0'></div>", unsafe_allow_html=True)
    _lb1, _lb2, _lb3 = st.columns([3, 2, 3])
    with _lb2:
        if st.button("Start Building →", type="primary", use_container_width=True, key="land_b"):
            st.session_state.show_landing = False
            st.rerun()

    st.markdown("""
    <div style="text-align:center;margin-top:28px;font-size:0.77em;color:#8A7850">
      Educational tool only · Not financial advice · Consult a qualified professional before investing
    </div>""", unsafe_allow_html=True)
    st.stop()

# ---------------------------------------------------------------------------
# Main area
# ---------------------------------------------------------------------------
st.title("ChatFolio")
st.caption("Build your starter portfolio through conversation — not forms.")

if not st.session_state.messages or len(st.session_state.messages) <= 1:
    with st.expander("What is ChatFolio?", expanded=True):
        st.markdown(
            "**ChatFolio helps you build a starter investment portfolio through a "
            "simple conversation.** No forms, no jargon — just tell me about your "
            "goals and I'll recommend a diversified mix of low-cost index funds.\n\n"
            "**Here's what I'll ask about:**\n"
            "- What you're investing for *(required)*\n"
            "- How many years until you need the money *(required)*\n"
            "- How much you can invest per month *(required)*\n"
            "- How comfortable you are with risk *(required)*\n"
            "- Any existing accounts, debt, or upcoming life changes *(optional)*\n\n"
            "**This takes about 2–3 minutes.** At the end, you'll get a personalized "
            "portfolio with an explanation of why it fits you, projected growth over "
            "time, and step-by-step instructions for getting started.\n\n"
            "**Not sure where to start?** Just say something like: "
            "_\"I'm 23 and want to start investing\"_ or "
            "_\"I want to grow my savings but don't know where to begin.\"_\n\n"
            "**What ChatFolio is not:** I'm an educational tool, not a licensed "
            "financial advisor. I don't execute trades or guarantee returns. For "
            "complex financial situations, consult a professional."
        )

if not API_KEY:
    st.error("Set OPENAI_API_KEY in your .env file to get started.")
    st.stop()

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
# Constants
# ---------------------------------------------------------------------------
ETF_DESCRIPTIONS = {
    "VTI":  "Owns a tiny piece of nearly every publicly traded U.S. company — from Apple to small businesses — in one fund.",
    "VXUS": "Same idea as VTI, but covers international companies across Europe, Asia, and emerging markets.",
    "BND":  "Holds thousands of U.S. government and corporate bonds — lower growth than stocks, but steadier and less volatile.",
    "BNDX": "Like BND but for international bonds — adds geographic diversification to the stable part of your portfolio.",
}

QUIZ_QUESTIONS = [
    {
        "q": "Your portfolio drops 20% in a single month. What do you do?",
        "options": [
            ("Sell — I need to cut my losses", 1),
            ("Hold — downturns are temporary", 2),
            ("Buy more — it's on sale", 3),
        ],
    },
    {
        "q": "How would you feel watching your portfolio lose 30% of its value over a year?",
        "options": [
            ("Very stressed — I'd lose sleep over it", 1),
            ("Uncomfortable, but I'd stay the course", 2),
            ("Fine — I'd focus on the long-term opportunity", 3),
        ],
    },
    {
        "q": "Which return profile appeals to you most?",
        "options": [
            ("Steady 3–4%/year with very little risk of loss", 1),
            ("Average 7–8%/year with occasional 15–20% dips", 2),
            ("Average 10–12%/year with possible 40%+ drops", 3),
        ],
    },
]

SCENARIOS = {
    "2008 Financial Crisis": {
        "icon": "📉",
        "summary": "A housing market collapse triggers a global financial crisis. U.S. equities fall ~38%; international markets drop even further. Bonds hold steady.",
        "etf_impact": {"VTI": -0.38, "VXUS": -0.45, "BND": +0.06, "BNDX": +0.03},
        "insight": "Bonds provided a meaningful cushion — this is exactly what diversification is designed for.",
    },
    "Tech Boom": {
        "icon": "🚀",
        "summary": "AI and tech innovation drive a sustained U.S. equity rally. International markets and bonds lag behind.",
        "etf_impact": {"VTI": +0.35, "VXUS": +0.12, "BND": -0.03, "BNDX": -0.02},
        "insight": "Higher equity exposure pays off handsomely in a prolonged bull market.",
    },
    "Rising Interest Rates": {
        "icon": "📈",
        "summary": "The Fed aggressively hikes rates to fight inflation (see 2022). Bond prices fall sharply; equities face headwinds.",
        "etf_impact": {"VTI": -0.12, "VXUS": -0.09, "BND": -0.16, "BNDX": -0.13},
        "insight": "Both stocks and bonds down at once is rare but painful — the case for holding cash reserves.",
    },
    "Mild Recession": {
        "icon": "🔻",
        "summary": "Economic growth slows and unemployment ticks up. Equities pull back modestly; bonds rally as the Fed cuts rates.",
        "etf_impact": {"VTI": -0.18, "VXUS": -0.22, "BND": +0.05, "BNDX": +0.04},
        "insight": "Bonds acted as a ballast — a classic flight-to-safety pattern.",
    },
    "Global Recovery": {
        "icon": "🌍",
        "summary": "Post-recession growth spreads worldwide. Emerging markets and international stocks lead; U.S. equities also gain.",
        "etf_impact": {"VTI": +0.18, "VXUS": +0.32, "BND": +0.01, "BNDX": +0.04},
        "insight": "International diversification paid off — don't underestimate VXUS.",
    },
    "Stagflation": {
        "icon": "⚠️",
        "summary": "High inflation meets slow growth (1970s-style). Both stocks and bonds lose real value as purchasing power erodes.",
        "etf_impact": {"VTI": -0.15, "VXUS": -0.12, "BND": -0.20, "BNDX": -0.17},
        "insight": "The toughest environment for a traditional stock/bond portfolio.",
    },
}


def render_chat_history(show_processing: bool = False) -> None:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    if show_processing:
        with st.chat_message("assistant"):
            st.markdown("_Thinking..._")


# ---------------------------------------------------------------------------
# Main layout
# ---------------------------------------------------------------------------
if not st.session_state.portfolio:
    # PRE-PORTFOLIO: chat + embedded quiz + generate button
    render_chat_history(show_processing=bool(st.session_state.pending_prompt))

    _p = st.session_state.profile
    _risk_filled = bool(_p.get("risk_tolerance"))
    _three_done = all([_p.get("goal"), _p.get("timeline"), _p.get("monthly_budget")])

    # Auto-trigger quiz once the other three fields are filled
    if _three_done and not _risk_filled and st.session_state.quiz_step == 0 and not st.session_state.pending_prompt:
        st.session_state.quiz_step = 1
        st.session_state.quiz_score = 0
        st.rerun()

    # Quiz embedded as a chat-style assistant message
    if st.session_state.quiz_step > 0 and not _risk_filled:
        _step = st.session_state.quiz_step

        if 1 <= _step <= 3:
            _q = QUIZ_QUESTIONS[_step - 1]
            with st.chat_message("assistant"):
                st.markdown(
                    f"Before I can build your portfolio, I need to understand your risk tolerance. "
                    f"Here's a quick scenario — just click the option that fits you best.\n\n"
                    f"**Question {_step} of 3:** {_q['q']}"
                )
                for _label, _score in _q["options"]:
                    if st.button(_label, key=f"quiz_{_step}_{_score}", use_container_width=True):
                        st.session_state.quiz_score += _score
                        st.session_state.quiz_step += 1
                        st.rerun()

        else:
            _total = st.session_state.quiz_score
            if _total <= 4:
                _result, _desc = "conservative", "You prioritize stability over maximum growth — a portfolio with more bonds will help you stay the course when markets get rough."
            elif _total <= 7:
                _result, _desc = "moderate", "You're comfortable with some ups and downs in exchange for solid long-term growth — a balanced stock/bond mix suits you well."
            else:
                _result, _desc = "aggressive", "You can handle big swings in pursuit of maximum long-term growth — a heavy equity allocation fits your temperament."

            with st.chat_message("assistant"):
                st.markdown(
                    f"Based on your answers, your risk tolerance is **{_result.capitalize()}**. "
                    f"{_desc}"
                )
                _qc1, _qc2 = st.columns(2)
                with _qc1:
                    if st.button(f"Sounds right — use {_result}", type="primary", use_container_width=True):
                        st.session_state.profile["risk_tolerance"] = _result
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": (
                                f"Great — I've set your risk tolerance to **{_result}**. "
                                f"Your profile is complete! Click **Generate My Portfolio** when you're ready."
                            ),
                        })
                        st.session_state.quiz_step = 0
                        st.session_state.ready = True
                        st.rerun()
                with _qc2:
                    if st.button("Retake the questions", use_container_width=True):
                        st.session_state.quiz_step = 1
                        st.session_state.quiz_score = 0
                        st.rerun()

    if st.session_state.ready:
        if st.button("Generate My Portfolio", type="primary", use_container_width=True):
            with st.spinner("Building your portfolio..."):
                st.session_state.portfolio = generate_portfolio(st.session_state.profile)
                st.session_state.rationale = generate_rationale(
                    st.session_state.profile, st.session_state.portfolio, API_KEY)
                st.session_state.action_plan = generate_action_plan(
                    st.session_state.profile, st.session_state.portfolio, API_KEY)
            st.rerun()

else:
    # POST-PORTFOLIO: split view
    PANEL_HEIGHT = 820
    col_chat, col_sep, col_portfolio = st.columns([2, 0.04, 3])

    with col_sep:
        st.markdown(
            f"<div style='border-left:2px solid #D4B345;height:{PANEL_HEIGHT}px;"
            "margin:0 auto;border-radius:1px;opacity:0.7;'></div>",
            unsafe_allow_html=True,
        )

    with col_chat:
        st.subheader("Conversation")
        with st.container(height=PANEL_HEIGHT, border=False):
            render_chat_history(show_processing=bool(st.session_state.pending_prompt))
            st.info(
                "**Still here to help!** You can keep chatting to:\n"
                "- **Adjust your portfolio** — _\"Make it more aggressive\"_, "
                "_\"Change my timeline to 20 years\"_, _\"What if I invest $300/month?\"_\n"
                "- **Ask questions** — _\"What is an ETF?\"_, _\"Why was VTI chosen?\"_, "
                "_\"What's the difference between stocks and bonds?\"_\n"
                "- **Get recommendations** — _\"What account should I open?\"_, "
                "_\"Should I open a Roth IRA?\"_"
            )

    with col_portfolio:
        st.subheader("Your Portfolio")
        with st.container(height=PANEL_HEIGHT, border=False):
            prof = st.session_state.profile

            # Parse budget
            _bgt_raw = str(prof.get("monthly_budget") or "0")
            try:
                budget = float("".join(c for c in _bgt_raw if c.isdigit() or c == ".") or "0")
            except ValueError:
                budget = 0.0

            # Parse timeline
            _tl_str = str(prof.get("timeline") or "10")
            _tl_digits = "".join(c for c in _tl_str if c.isdigit())
            proj_years = max(int(_tl_digits) if _tl_digits else 10, 5)

            # Initialize sensitivity budget
            if st.session_state.sensitivity_budget is None:
                st.session_state.sensitivity_budget = budget

            tab_port, tab_proj, tab_scen, tab_comp, tab_res = st.tabs(
                ["Portfolio", "Projections", "Scenarios", "Compare", "Resources"]
            )

            # ── Tab 1: Portfolio ──────────────────────────────────────────
            with tab_port:
                st.caption(
                    f"{prof.get('goal', '')}  ·  {prof.get('timeline', '')} horizon  ·  "
                    f"${budget:,.0f}/mo  ·  {prof.get('risk_tolerance', '')} risk"
                )

                for item in st.session_state.portfolio:
                    monthly = budget * item["allocation"] / 100
                    c1, c2, c3 = st.columns([1.5, 3.5, 1])
                    with c1:
                        st.markdown(f"**{item['ticker']}**")
                        st.caption(item["name"])
                    with c2:
                        st.progress(item["allocation"] / 100)
                        _desc = ETF_DESCRIPTIONS.get(item["ticker"])
                        if _desc:
                            st.caption(_desc)
                    with c3:
                        _line = f"**{item['allocation']}%**"
                        if budget > 0:
                            _line += f"  \n${monthly:.0f}/mo"
                        st.markdown(_line)

                if st.session_state.rationale:
                    st.divider()
                    st.subheader("Why This Portfolio?")
                    st.markdown(st.session_state.rationale)

                st.divider()
                _e1, _e2 = st.columns(2)
                with _e1:
                    try:
                        _mil = sorted(set(
                            [y for y in [5, 10, 15, 20, 25, 30, 40] if y <= proj_years] + [proj_years]
                        ))
                        _pdf_proj = generate_projections(st.session_state.portfolio, budget, proj_years)
                        _pdf_summary = _pdf_proj[_pdf_proj["Year"].isin(_mil)].copy().set_index("Year")
                        for _c in _pdf_summary.columns:
                            _pdf_summary[_c] = _pdf_summary[_c].apply(lambda x: f"${x:,.0f}")
                        _pdf_bytes = generate_pdf(
                            st.session_state.profile,
                            st.session_state.portfolio,
                            st.session_state.rationale or "",
                            st.session_state.action_plan or "",
                            _pdf_summary,
                        )
                        st.download_button(
                            "Download PDF Report",
                            data=_pdf_bytes,
                            file_name="chatfolio_portfolio.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                        )
                    except Exception:
                        st.caption("PDF export unavailable — run `pip install fpdf2`.")
                with _e2:
                    if st.button("Share Portfolio", use_container_width=True):
                        _share_data = {
                            "profile": st.session_state.profile,
                            "portfolio": st.session_state.portfolio,
                        }
                        _encoded = base64.urlsafe_b64encode(
                            json.dumps(_share_data).encode()
                        ).decode()
                        st.query_params["share"] = _encoded
                        st.success("URL updated — copy the address bar to share your portfolio.")

            # ── Tab 2: Projections ────────────────────────────────────────
            with tab_proj:
                if budget > 0:
                    st.subheader("Adjust & Explore")
                    _viz_budget = st.slider(
                        "Monthly contribution",
                        min_value=0,
                        max_value=max(5000, int(budget * 3)),
                        value=int(st.session_state.sensitivity_budget),
                        step=25,
                        format="$%d",
                    )
                    st.session_state.sensitivity_budget = float(_viz_budget)
                    if _viz_budget != int(budget):
                        st.caption(
                            f"Projections adjusted to \\${_viz_budget:,}/mo — "
                            f"your profile budget is \\${budget:,.0f}/mo. "
                            f"Update it in the sidebar to save permanently."
                        )

                    _proj_df = generate_projections(st.session_state.portfolio, float(_viz_budget), proj_years)

                    st.divider()
                    st.subheader("Projected Growth")
                    st.caption("Includes S&P 500 benchmark for comparison. Assumes consistent monthly contributions.")
                    st.line_chart(_proj_df.set_index("Year"))

                    _mil = sorted(set(
                        [y for y in [5, 10, 15, 20, 25, 30, 40] if y <= proj_years] + [proj_years]
                    ))
                    _summary = _proj_df[_proj_df["Year"].isin(_mil)].copy().set_index("Year")
                    for _c in _summary.columns:
                        _summary[_c] = _summary[_c].apply(lambda x: f"${x:,.0f}")
                    st.table(_summary)
                    st.caption(
                        "Projections use historical average returns and assume consistent monthly "
                        "contributions. Actual results will vary. Past performance does not "
                        "guarantee future results."
                    )

                    # Cost of Waiting
                    st.divider()
                    st.subheader("Cost of Waiting")
                    st.caption("What happens to your projected outcome if you delay starting?")

                    _ann_r = blended_return(st.session_state.portfolio, 1)
                    _mon_r = _ann_r / 12

                    def _fv(_months: int) -> float:
                        if _mon_r == 0:
                            return float(_viz_budget) * _months
                        return float(_viz_budget) * (((1 + _mon_r) ** _months - 1) / _mon_r)

                    _base_val = _fv(proj_years * 12)
                    _wc1, _wc2, _wc3 = st.columns(3)
                    for _wcol, _delay in zip([_wc1, _wc2, _wc3], [1, 3, 5]):
                        _eff_val = _fv(max(proj_years - _delay, 1) * 12)
                        _cost = _base_val - _eff_val
                        with _wcol:
                            st.metric(
                                f"Start in {_delay} yr{'s' if _delay > 1 else ''}",
                                f"${_eff_val:,.0f}",
                                f"-${_cost:,.0f} vs. today",
                                delta_color="inverse",
                            )
                    st.caption(f"Starting today reaches an estimated **${_base_val:,.0f}** after {proj_years} years.")

                    # Savings Goal Calculator
                    st.divider()
                    st.subheader("Savings Goal Calculator")
                    st.caption("Work backwards from a target amount to find your required monthly contribution.")

                    _goal = st.number_input(
                        "Target portfolio value ($)",
                        min_value=1_000, max_value=10_000_000,
                        value=100_000, step=5_000, format="%d",
                        key="savings_goal",
                    )
                    _months = proj_years * 12
                    if _mon_r == 0:
                        _required = float(_goal) / _months if _months > 0 else 0.0
                    else:
                        _required = float(_goal) * _mon_r / ((1 + _mon_r) ** _months - 1)

                    _gc1, _gc2 = st.columns(2)
                    with _gc1:
                        st.metric("Required monthly contribution", f"${_required:,.0f}")
                    with _gc2:
                        _diff = _required - float(_viz_budget)
                        st.metric(
                            "vs. your current budget",
                            f"${float(_viz_budget):,.0f}/mo",
                            f"{_diff:+,.0f}/mo",
                            delta_color="inverse" if _diff > 0 else "normal",
                        )
                else:
                    st.info("Add a monthly budget to your profile to see projections.")

            # ── Tab 3: Scenarios ──────────────────────────────────────────
            with tab_scen:
                st.subheader("Scenario Testing")
                st.caption("Click a scenario to see how it would impact your portfolio.")

                _scen_cols = st.columns(3)
                for _i, (_name, _data) in enumerate(SCENARIOS.items()):
                    with _scen_cols[_i % 3]:
                        _active = st.session_state.active_scenario == _name
                        if st.button(
                            f"{_data['icon']} {_name}",
                            key=f"scen_{_i}",
                            use_container_width=True,
                            type="primary" if _active else "secondary",
                        ):
                            st.session_state.active_scenario = None if _active else _name
                            st.rerun()

                if st.session_state.active_scenario:
                    _s = SCENARIOS[st.session_state.active_scenario]
                    st.markdown(f"**{st.session_state.active_scenario}** — {_s['summary']}")

                    _BASE = 10_000
                    _total_after = 0.0
                    _rows = []
                    for _item in st.session_state.portfolio:
                        _ticker = _item["ticker"]
                        _start = _BASE * _item["allocation"] / 100
                        _chg = _s["etf_impact"].get(_ticker, 0.0)
                        _end = _start * (1 + _chg)
                        _total_after += _end
                        _rows.append((_ticker, _start, _end, _chg))

                    _pct_total = (_total_after - _BASE) / _BASE
                    st.metric("Total portfolio impact (on $10,000)", f"${_total_after:,.0f}", f"{_pct_total:+.1%}")

                    for _ticker, _start, _end, _chg in _rows:
                        _sign = "+" if _chg >= 0 else ""
                        _color = "#2ea043" if _chg >= 0 else "#cf222e"
                        _delta = _end - _start
                        _ca, _cb, _cc = st.columns([1, 2, 1])
                        with _ca:
                            st.markdown(f"**{_ticker}**")
                        with _cb:
                            st.markdown(
                                f"<span style='color:{_color};font-size:1.05em'>"
                                f"{_sign}{_chg:.0%}</span>",
                                unsafe_allow_html=True,
                            )
                        with _cc:
                            _dsign = "+" if _delta >= 0 else ""
                            st.markdown(f"{_dsign}${abs(_delta):,.0f}")

                    st.caption(f"Insight: {_s['insight']}")

            # ── Tab 4: Compare ────────────────────────────────────────────
            with tab_comp:
                st.subheader("Risk Level Comparison")
                st.caption(
                    f"Side-by-side allocations and projected outcomes for your timeline "
                    f"({prof.get('timeline', '')}) and budget (${budget:,.0f}/mo)."
                )

                _risk_colors = {
                    "conservative": "#4A9040",
                    "moderate":     "#C5A028",
                    "aggressive":   "#C04040",
                }
                _comp_cols = st.columns(3)
                _crash_impacts = {"VTI": -0.38, "VXUS": -0.45, "BND": 0.06, "BNDX": 0.03}

                for _ci, _risk in enumerate(["conservative", "moderate", "aggressive"]):
                    _comp_prof = {**prof, "risk_tolerance": _risk}
                    _comp_port = generate_portfolio(_comp_prof)
                    _comp_annual = blended_return(_comp_port, 1)
                    _comp_mon_r = _comp_annual / 12
                    _comp_months = proj_years * 12

                    if _comp_mon_r == 0:
                        _comp_val = budget * _comp_months
                    else:
                        _comp_val = budget * (((1 + _comp_mon_r) ** _comp_months - 1) / _comp_mon_r)

                    _crash_pct = sum(
                        item["allocation"] / 100 * _crash_impacts.get(item["ticker"], 0)
                        for item in _comp_port
                    )
                    _color = _risk_colors[_risk]

                    with _comp_cols[_ci]:
                        st.markdown(
                            f"<h3 style='color:{_color};text-align:center;"
                            f"border-bottom:2px solid {_color};padding-bottom:6px'>"
                            f"{_risk.capitalize()}</h3>",
                            unsafe_allow_html=True,
                        )
                        for _item in _comp_port:
                            _p1, _p2 = st.columns([2, 1])
                            with _p1:
                                st.progress(_item["allocation"] / 100)
                            with _p2:
                                st.markdown(f"**{_item['ticker']}** {_item['allocation']}%")
                        st.markdown("---")
                        st.metric(f"After {proj_years} yrs", f"${_comp_val:,.0f}")
                        st.metric("2008 crash impact", f"{_crash_pct:.0%}", delta_color="inverse")
                        _cur_risk = (prof.get("risk_tolerance") or "moderate").lower()
                        if _risk == _cur_risk:
                            st.caption("← Your current level")

            # ── Tab 5: Resources ──────────────────────────────────────────
            with tab_res:
                if st.session_state.action_plan:
                    st.subheader("How to Get Started")
                    st.markdown(st.session_state.action_plan)
                    st.divider()

                st.subheader("Glossary")
                st.caption("Plain-English definitions for every term in your portfolio.")
                for _term, _defn in GLOSSARY.items():
                    with st.expander(_term):
                        st.markdown(_defn)

                st.divider()
                st.caption(
                    "ChatFolio is an educational tool, not a licensed financial advisor. "
                    "Allocations are based on general principles and historical averages — "
                    "past performance does not guarantee future results. Consult a qualified "
                    "financial professional before making investment decisions."
                )

# ---------------------------------------------------------------------------
# Pending chat processing
# ---------------------------------------------------------------------------
if st.session_state.pending_prompt:
    _api_msgs = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]

    with st.spinner("Thinking..."):
        resp = get_ai_response(_api_msgs, st.session_state.profile, API_KEY)

    st.session_state.messages.append(
        {"role": "assistant", "content": resp.get("message", "Could you rephrase that?")}
    )

    for _key, _val in resp.get("profile_updates", {}).items():
        if _val is not None and _key in st.session_state.profile:
            st.session_state.profile[_key] = str(_val)

    if resp.get("ready_for_portfolio"):
        st.session_state.ready = True

    if resp.get("profile_changed") and st.session_state.portfolio:
        with st.spinner("Updating your portfolio..."):
            st.session_state.portfolio = generate_portfolio(st.session_state.profile)
            st.session_state.rationale = generate_rationale(
                st.session_state.profile, st.session_state.portfolio, API_KEY)
            st.session_state.action_plan = generate_action_plan(
                st.session_state.profile, st.session_state.portfolio, API_KEY)
        st.session_state.sensitivity_budget = None
        for _k in ("_edit_tl_slider", "_edit_tl_input", "_edit_bgt_slider",
                   "_edit_bgt_input", "_edit_risk", "_edit_goal"):
            st.session_state.pop(_k, None)
        st.toast("Portfolio updated!")

    st.session_state.pending_prompt = None
    st.rerun()

# ---------------------------------------------------------------------------
# Chat input
# ---------------------------------------------------------------------------
if prompt := st.chat_input(
    "Type your message...",
    disabled=bool(st.session_state.pending_prompt) or st.session_state.show_landing,
):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.pending_prompt = prompt
    st.rerun()
