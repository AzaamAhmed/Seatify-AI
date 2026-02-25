# Basic Imports
from dotenv import load_dotenv
import os
from datetime import datetime

# Third Party Imports
import streamlit as st
import json

# Internal Imports
from agent.conversation_engine import (
    generate_chat_completion,
    normalize_chat_response,
    execute_tool_calls,
    has_function_simulation
)
from agent.toolkit import restaurant_tools
from agent.prompt_library import (
    restaurant_test_conversation_system_prompt,
    restaurant_test_conversation_system_prompt_w_fewshot,
    restaurant_test_conversation_system_prompt_w_fewshot_1
)

# Setting up Logging
import logging

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('seatify')

# Global Constants and Variables
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Parent directory
DATA_DIR = os.path.join(BASE_DIR, "data")

logger.info(f"BASE_DIR set to: {BASE_DIR}")
logger.info(f"DATA_DIR set to: {DATA_DIR}")

# Load environment variables from .env file
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key:
    logger.info("OpenAI API key loaded successfully")
else:
    logger.error("OpenAI API key not found in environment variables")

logger.info("Seatify AI Reservation Assistant started")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG  (must be the very first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Seatify AI — Sri Lanka",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS — modern, warm restaurant palette
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* ── Google Fonts: Inter + Playfair Display ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@700;800&display=swap');

    /* ── Root tokens ── */
    :root {
      --brand-primary:   #e85d04;
      --brand-secondary: #f48c06;
      --brand-dark:      #9d0208;
      --brand-glow:      rgba(232,93,4,0.35);
      --bg-page:         #080808;
      --bg-surface:      #111111;
      --bg-card:         #181818;
      --bg-glass:        rgba(255,255,255,0.04);
      --bg-input:        #1e1e1e;
      --border:          #2a2a2a;
      --border-glass:    rgba(255,255,255,0.08);
      --text-primary:    #f5f0eb;
      --text-secondary:  #a89f96;
      --text-muted:      #5c5550;
      --success:         #22c55e;
      --warning:         #f59e0b;
      --error:           #ef4444;
      --radius-sm:       8px;
      --radius-md:       14px;
      --radius-lg:       22px;
      --radius-xl:       30px;
      --blur-glass:      blur(16px);
      --blur-light:      blur(8px);
      --transition:      all 0.25s cubic-bezier(0.4,0,0.2,1);
    }

    /* ── Base ── */
    html, body, [class*="css"] {
      font-family: 'Inter', sans-serif !important;
      background-color: var(--bg-page) !important;
      color: var(--text-primary) !important;
    }

    /* ── Hide default Streamlit chrome ── */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 1.5rem !important; }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: var(--bg-surface); }
    ::-webkit-scrollbar-thumb {
      background: linear-gradient(180deg, var(--brand-primary), var(--brand-dark));
      border-radius: 3px;
    }

    /* ────────────────── KEYFRAME ANIMATIONS ────────────────── */
    @keyframes float {
      0%, 100% { transform: translateY(-50%) translateX(0); }
      33%       { transform: translateY(calc(-50% - 10px)) translateX(4px); }
      66%       { transform: translateY(calc(-50% - 5px)) translateX(-4px); }
    }
    @keyframes pulse-dot {
      0%, 100% { box-shadow: 0 0 4px 1px #22c55e; }
      50%       { box-shadow: 0 0 10px 3px #22c55e; }
    }
    @keyframes shimmer {
      0%   { background-position: -400px 0; }
      100% { background-position: 400px 0; }
    }
    @keyframes fadeInUp {
      from { opacity: 0; transform: translateY(14px); }
      to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes glow-pulse {
      0%, 100% { box-shadow: 0 0 20px rgba(232,93,4,0.15), 0 0 60px rgba(232,93,4,0.05); }
      50%       { box-shadow: 0 0 32px rgba(232,93,4,0.28), 0 0 90px rgba(232,93,4,0.10); }
    }
    @keyframes borderGlow {
      0%, 100% { border-color: rgba(232,93,4,0.25); }
      50%       { border-color: rgba(244,140,6,0.55); }
    }

    /* ────────────────── HERO BANNER ────────────────── */
    .gf-hero {
      background-image:
        linear-gradient(135deg, rgba(10,2,2,0.88) 0%, rgba(59,10,10,0.78) 45%, rgba(124,29,12,0.70) 100%),
        url('https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=1400&auto=format&fit=crop&q=80');
      background-size: cover;
      background-position: center 55%;
      border: 1px solid rgba(232,93,4,0.25);
      border-radius: var(--radius-xl);
      padding: 36px 40px;
      margin-bottom: 20px;
      position: relative;
      overflow: hidden;
      backdrop-filter: var(--blur-light);
      animation: glow-pulse 4s ease-in-out infinite;
    }
    /* Radial glow orb top-right */
    .gf-hero::before {
      content: '';
      position: absolute;
      top: -60px; right: -60px;
      width: 260px; height: 260px;
      background: radial-gradient(circle, rgba(232,93,4,0.30) 0%, transparent 65%);
      border-radius: 50%;
      pointer-events: none;
    }
    /* Subtle bottom shimmer line */
    .gf-hero::after {
      content: '';
      position: absolute;
      bottom: 0; left: 0; right: 0;
      height: 2px;
      background: linear-gradient(90deg, transparent, rgba(232,93,4,0.6), rgba(244,140,6,0.6), transparent);
    }
    .gf-hero-badge {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      background: rgba(232,93,4,0.14);
      border: 1px solid rgba(232,93,4,0.45);
      color: var(--brand-secondary);
      font-size: 10.5px;
      font-weight: 700;
      letter-spacing: 2px;
      text-transform: uppercase;
      padding: 4px 12px;
      border-radius: 100px;
      margin-bottom: 14px;
      backdrop-filter: blur(6px);
      animation: borderGlow 3s ease-in-out infinite;
    }
    .gf-hero h1 {
      font-family: 'Playfair Display', serif !important;
      font-size: 2.4rem !important;
      font-weight: 800 !important;
      background: linear-gradient(135deg, #ffffff 0%, #fde8cc 40%, #f48c06 100%) !important;
      -webkit-background-clip: text !important;
      -webkit-text-fill-color: transparent !important;
      background-clip: text !important;
      margin: 0 0 8px 0 !important;
      line-height: 1.15 !important;
      letter-spacing: -0.5px;
      animation: fadeInUp 0.6s ease both;
    }
    .gf-hero p {
      color: rgba(245,240,235,0.72) !important;
      font-size: 0.97rem !important;
      font-weight: 400;
      margin: 0 !important;
      animation: fadeInUp 0.7s ease 0.1s both;
    }
    .gf-hero-icon {
      font-size: 4rem;
      line-height: 1;
      position: absolute;
      right: 40px;
      top: 50%;
      transform: translateY(-50%);
      opacity: 0.75;
      filter: drop-shadow(0 0 18px rgba(232,93,4,0.55));
      animation: float 4s ease-in-out infinite;
    }

    /* ────────────────── STAT PILLS ────────────────── */
    .gf-stats {
      display: flex;
      gap: 8px;
      margin-bottom: 20px;
      flex-wrap: wrap;
    }
    .gf-stat-pill {
      background: var(--bg-glass);
      border: 1px solid var(--border-glass);
      border-radius: 100px;
      padding: 7px 18px;
      font-size: 0.78rem;
      color: var(--text-secondary);
      display: flex;
      align-items: center;
      gap: 7px;
      backdrop-filter: var(--blur-glass);
      transition: var(--transition);
    }
    .gf-stat-pill:hover {
      background: rgba(232,93,4,0.10);
      border-color: rgba(232,93,4,0.30);
      color: var(--brand-secondary);
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(232,93,4,0.15);
    }
    .gf-stat-pill span.dot {
      width: 7px; height: 7px;
      border-radius: 50%;
      background: var(--success);
      display: inline-block;
      animation: pulse-dot 2s ease-in-out infinite;
    }

    /* ────────────────── QUICK SUGGESTION CHIPS ────────────────── */
    .gf-chips {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 18px;
    }
    .gf-chip {
      background: var(--bg-glass);
      border: 1px solid var(--border-glass);
      border-radius: 100px;
      padding: 6px 16px;
      font-size: 0.8rem;
      color: var(--text-secondary);
      cursor: pointer;
      backdrop-filter: var(--blur-glass);
      transition: var(--transition);
    }
    .gf-chip:hover {
      border-color: var(--brand-primary);
      color: var(--brand-secondary);
      background: rgba(232,93,4,0.10);
      transform: translateY(-2px);
      box-shadow: 0 6px 18px rgba(232,93,4,0.20);
    }

    /* ────────────────── CHAT MESSAGES ────────────────── */
    [data-testid="stChatMessageContent"] {
      background: rgba(24,24,24,0.85) !important;
      border-radius: var(--radius-md) !important;
      border: 1px solid var(--border-glass) !important;
      padding: 14px 18px !important;
      font-size: 0.92rem !important;
      line-height: 1.7 !important;
      color: var(--text-primary) !important;
      backdrop-filter: var(--blur-light) !important;
      transition: var(--transition) !important;
    }
    [data-testid="stChatMessageContent"]:hover {
      border-color: rgba(232,93,4,0.18) !important;
      box-shadow: 0 4px 20px rgba(0,0,0,0.3) !important;
    }
    [data-testid="stChatMessageContent"] p { margin: 0 !important; }

    /* User bubble — warm glass tint */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
      background: linear-gradient(135deg, rgba(232,93,4,0.13), rgba(157,2,8,0.08)) !important;
      border-color: rgba(232,93,4,0.28) !important;
    }

    /* ────────────────── CHAT INPUT ────────────────── */
    [data-testid="stChatInput"] textarea {
      background: rgba(30,30,30,0.9) !important;
      border: 1px solid var(--border) !important;
      border-radius: var(--radius-md) !important;
      color: var(--text-primary) !important;
      font-size: 0.92rem !important;
      backdrop-filter: var(--blur-light);
      transition: var(--transition);
    }
    [data-testid="stChatInput"] textarea:focus {
      border-color: var(--brand-primary) !important;
      box-shadow: 0 0 0 3px rgba(232,93,4,0.18), 0 4px 24px rgba(232,93,4,0.10) !important;
    }
    [data-testid="stChatInput"] button {
      background: linear-gradient(135deg, var(--brand-primary), var(--brand-dark)) !important;
      border-radius: var(--radius-sm) !important;
      transition: var(--transition) !important;
    }
    [data-testid="stChatInput"] button:hover {
      opacity: 0.88 !important;
      box-shadow: 0 4px 14px rgba(232,93,4,0.4) !important;
    }

    /* ────────────────── EXPANDER (agent trace) ────────────────── */
    [data-testid="stExpander"] {
      background: rgba(17,17,17,0.7) !important;
      border: 1px solid var(--border-glass) !important;
      border-radius: var(--radius-md) !important;
      backdrop-filter: var(--blur-glass) !important;
      transition: var(--transition) !important;
    }
    [data-testid="stExpander"]:hover {
      border-color: rgba(232,93,4,0.20) !important;
    }
    [data-testid="stExpander"] summary {
      color: var(--text-secondary) !important;
      font-size: 0.82rem !important;
      font-weight: 600 !important;
      letter-spacing: 0.3px;
    }
    [data-testid="stExpander"] summary:hover { color: var(--brand-secondary) !important; }

    /* ────────────────── SIDEBAR ────────────────── */
    [data-testid="stSidebar"] {
      background: linear-gradient(180deg, #0e0e0e 0%, #111111 100%) !important;
      border-right: 1px solid var(--border-glass) !important;
      backdrop-filter: var(--blur-light);
    }
    .sidebar-card {
      background: var(--bg-glass) !important;
      border: 1px solid var(--border-glass) !important;
      border-radius: var(--radius-md);
      padding: 16px;
      margin-bottom: 14px;
      backdrop-filter: var(--blur-glass);
      transition: var(--transition);
    }
    .sidebar-card:hover {
      background: rgba(232,93,4,0.06) !important;
      border-color: rgba(232,93,4,0.20) !important;
      transform: translateY(-2px);
      box-shadow: 0 8px 28px rgba(0,0,0,0.35);
    }
    [data-testid="stSidebar"] h3 {
      color: var(--text-primary) !important;
      font-size: 0.9rem !important;
      font-weight: 600 !important;
      margin-bottom: 8px !important;
    }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] li {
      color: var(--text-secondary) !important;
      font-size: 0.82rem !important;
    }

    /* ── Sri Lanka photo mosaic in sidebar ── */
    .sl-img-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 5px;
      border-radius: var(--radius-md);
      overflow: hidden;
      margin-top: 6px;
    }
    .sl-img-grid img {
      width: 100%;
      aspect-ratio: 1 / 1;
      object-fit: cover;
      border-radius: 6px;
      transition: var(--transition);
      filter: brightness(0.82) saturate(1.1);
      cursor: default;
    }
    .sl-img-grid img:hover {
      transform: scale(1.06);
      filter: brightness(1.05) saturate(1.25);
      box-shadow: 0 0 14px rgba(232,93,4,0.30);
      z-index: 1;
      position: relative;
    }

    /* ────────────────── BUTTONS ────────────────── */
    .stButton > button {
      background: var(--bg-glass) !important;
      color: var(--text-primary) !important;
      border: 1px solid var(--border-glass) !important;
      border-radius: var(--radius-sm) !important;
      font-weight: 500 !important;
      backdrop-filter: var(--blur-glass);
      transition: var(--transition) !important;
      width: 100%;
    }
    .stButton > button:hover {
      background: rgba(232,93,4,0.14) !important;
      border-color: var(--brand-primary) !important;
      color: var(--brand-secondary) !important;
      transform: translateY(-1px);
      box-shadow: 0 6px 20px rgba(232,93,4,0.20) !important;
    }
    .stButton > button:active {
      transform: translateY(0) !important;
    }

    /* ────────────────── DIVIDER ────────────────── */
    hr {
      border: none !important;
      border-top: 1px solid var(--border-glass) !important;
      margin: 16px 0 !important;
    }

    /* ────────────────── SPINNER ────────────────── */
    [data-testid="stSpinner"] { color: var(--brand-primary) !important; }

    /* ────────────────── ALERTS ────────────────── */
    [data-testid="stAlert"] {
      background: rgba(239,68,68,0.08) !important;
      border: 1px solid rgba(239,68,68,0.25) !important;
      border-radius: var(--radius-sm) !important;
      backdrop-filter: var(--blur-light);
    }

    /* ────────────────── FOOTER BAR ────────────────── */
    .gf-footer {
      text-align: center;
      padding: 14px 0 6px 0;
      color: var(--text-muted);
      font-size: 0.75rem;
      letter-spacing: 0.4px;
    }
    .gf-footer a {
      color: var(--brand-secondary);
      text-decoration: none;
      transition: color 0.2s;
    }
    .gf-footer a:hover { color: var(--brand-primary); }

    /* ────────────────── CUISINE TAGS ────────────────── */
    .cuisine-tag {
      display: inline-block;
      background: rgba(244,140,6,0.10);
      border: 1px solid rgba(244,140,6,0.22);
      color: var(--brand-secondary);
      border-radius: 100px;
      padding: 2px 10px;
      font-size: 0.73rem;
      margin: 2px;
      transition: var(--transition);
      cursor: default;
    }
    .cuisine-tag:hover {
      background: rgba(244,140,6,0.22) !important;
      border-color: rgba(244,140,6,0.50) !important;
      transform: scale(1.06);
      box-shadow: 0 2px 10px rgba(244,140,6,0.20);
    }

    /* ────────────────── SECTION LABEL ────────────────── */
    .section-label {
      font-size: 0.68rem;
      font-weight: 700;
      letter-spacing: 1.4px;
      text-transform: uppercase;
      color: var(--text-muted);
      margin-bottom: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# HERO HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="gf-hero">
      <div class="gf-hero-badge">🤖 Agentic AI &nbsp;·&nbsp; Powered by GPT-4o</div>
      <h1>Seatify AI — Sri Lanka</h1>
      <p>Your intelligent dining companion for reservations across the Pearl of the Indian Ocean</p>
      <div class="gf-hero-icon">🍽️</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# STATUS PILLS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="gf-stats">
      <div class="gf-stat-pill"><span class="dot"></span> AI Online</div>
      <div class="gf-stat-pill">�️ 30 Outlets · Sri Lanka</div>
      <div class="gf-stat-pill">⏰ {datetime.now().strftime("%H:%M, %b %d")}</div>
      <div class="gf-stat-pill">🍴 Dine-in Reservations</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE & CHAT SEED
# ─────────────────────────────────────────────────────────────────────────────
system_prompt = restaurant_test_conversation_system_prompt_w_fewshot_1
welcome_message = (
    "Welcome to **Seatify Sri Lanka!** 🍽️\n\n"
    "I can help you:\n"
    "- 🔍 **Discover** restaurants by area, cuisine, or group size\n"
    "- 📅 **Book a table** with instant confirmation\n"
    "- 💡 **Get recommendations** for the perfect dining experience\n\n"
    "Where in Sri Lanka would you like to dine today?"
)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system",    "content": system_prompt},
        {"role": "assistant", "content": welcome_message},
    ]

if "msg_count" not in st.session_state:
    st.session_state.msg_count = 0

# ─────────────────────────────────────────────────────────────────────────────
# CONVERSATION RESET
# ─────────────────────────────────────────────────────────────────────────────
def reset_conversation():
    logger.info("Conversation reset by user")
    st.session_state.messages = [
        {"role": "system",    "content": system_prompt},
        {"role": "assistant", "content": welcome_message},
    ]
    st.session_state.msg_count = 0

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Branding
    st.markdown(
        """
        <div style="text-align:center; padding: 20px 0 14px 0;">
          <div style="font-size:2.8rem">🍽️</div>
          <div style="font-weight:700; font-size:1.1rem; color:#f5f0eb; margin-top:6px">Seatify AI</div>
          <div style="font-size:0.75rem; color:#6b6359; margin-top:2px; letter-spacing:0.5px">Seatify Reservation Engine</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<hr>", unsafe_allow_html=True)

    # API Status
    api_color = "#22c55e" if openai_api_key else "#ef4444"
    api_label = "Connected" if openai_api_key else "No API Key"
    st.markdown(
        f"""
        <div class="sidebar-card">
          <div class="section-label">System Status</div>
          <div style="display:flex; align-items:center; gap:8px; margin:6px 0;">
            <div style="width:8px;height:8px;border-radius:50%;background:{api_color};box-shadow:0 0 6px {api_color}"></div>
            <span style="font-size:0.82rem; color:#a89f96;">OpenAI API — <b style="color:{api_color}">{api_label}</b></span>
          </div>
          <div style="display:flex; align-items:center; gap:8px;">
            <div style="width:8px;height:8px;border-radius:50%;background:#22c55e;box-shadow:0 0 6px #22c55e"></div>
            <span style="font-size:0.82rem; color:#a89f96;">Backend API — <b style="color:#22c55e">Running</b></span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Turn counter
    turn_count = st.session_state.msg_count
    st.markdown(
        f"""
        <div class="sidebar-card">
          <div class="section-label">Conversation</div>
          <div style="font-size:1.6rem; font-weight:700; color:#e85d04; margin:4px 0">{turn_count}</div>
          <div style="font-size:0.78rem; color:#6b6359;">messages exchanged</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Actions</div>', unsafe_allow_html=True)

    # Restart button
    st.button("🔄 New Conversation", on_click=reset_conversation, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # Quick tips card
    st.markdown(
        """
        <div class="sidebar-card">
          <div class="section-label">💡 Quick Tips</div>
          <ul style="padding-left:14px; margin:6px 0 0 0;">
            <li>Ask for restaurants by <b>area</b> (Galle, Colombo, Kandy…)</li>
            <li>Mention your <b>cuisine</b> preference</li>
            <li>Share your <b>group size</b> upfront</li>
            <li>Provide your <b>name & contact</b> to confirm</li>
          </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Sri Lanka photo mosaic
    st.markdown(
        """
        <div class="sidebar-card">
          <div class="section-label">📸 Discover Sri Lanka</div>
          <div class="sl-img-grid">
            <img src="https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&auto=format&fit=crop&q=80" title="Galle Fort" alt="Galle Fort">
            <img src="https://images.unsplash.com/photo-1566296314736-6eaac1ca0cb9?w=400&auto=format&fit=crop&q=80" title="Sigiriya Rock" alt="Sigiriya">
            <img src="https://images.unsplash.com/photo-1559628233-100c798642d0?w=400&auto=format&fit=crop&q=80" title="Mirissa Beach" alt="Mirissa Beach">
            <img src="https://images.unsplash.com/photo-1540202404-a2f29016b523?w=400&auto=format&fit=crop&q=80" title="Sri Lanka Landscape" alt="Sri Lanka">
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Cuisine tags
    st.markdown(
        """
        <div class="sidebar-card">
          <div class="section-label">🍴 Cuisines Available</div>
          <div style="margin-top:8px">
            <span class="cuisine-tag">Sri Lankan</span>
            <span class="cuisine-tag">Seafood</span>
            <span class="cuisine-tag">Ceylonese</span>
            <span class="cuisine-tag">Tamil Sri Lankan</span>
            <span class="cuisine-tag">Ayurvedic</span>
            <span class="cuisine-tag">Beach Fusion</span>
            <span class="cuisine-tag">Continental</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="gf-footer" style="margin-top:16px">
          Powered by <a href="#">OpenAI GPT-4o</a><br>
          Built with Streamlit &amp; FastAPI
        </div>
        """,
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# QUICK SUGGESTION CHIPS  (shown only when first message)
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.msg_count == 0:
    st.markdown(
        """
        <div class="section-label">Try asking</div>
        <div class="gf-chips">
          <div class="gf-chip">🔍 Show me restaurants in Galle</div>
          <div class="gf-chip">🦞 Seafood near Mirissa Bay</div>
          <div class="gf-chip">👥 Book for 8 people this Friday</div>
          <div class="gf-chip">🕗 What's open after 9 PM?</div>
          <div class="gf-chip">⭐ Top Kandy restaurants</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# CHAT HISTORY RENDER
# ─────────────────────────────────────────────────────────────────────────────
for message in st.session_state.messages:
    if message["role"] not in ["system", "tool"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# ─────────────────────────────────────────────────────────────────────────────
# CHAT INPUT & PROCESSING
# ─────────────────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask about restaurants or book a table in Sri Lanka…"):
    logger.info(f"User input received: {prompt}...")
    st.session_state.msg_count += 1

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process and display assistant response
    with st.chat_message("assistant"):
        # Live agent trace container (collapsible and open by default)
        trace_expander = st.expander("🤖 Agent Thinking & Tool Activity (Live)", expanded=True)
        with trace_expander:
            st.markdown("**⚡ Request received** — preparing a plan…")
            trace_plan_placeholder = st.empty()
            trace_toolcalls_placeholder = st.empty()
            trace_toolresults_placeholder = st.empty()
            trace_followup_placeholder = st.empty()

        with st.spinner("Thinking…"):

            try:
                logger.info(f"Making AI call with conversation history length: {len(st.session_state.messages)} messages")
                # Initial API call
                api_response = generate_chat_completion(
                            api_key=openai_api_key, 
                            conversation_history=st.session_state.messages, 
                            tools=restaurant_tools, 
                            tool_calling_enabled=True)
                
            except Exception as e:
                logger.error(f"API call failed: {str(e)}", exc_info=True)
                st.error(f"An error occurred with the API call with User Message. Please restart the conversation.")
                st.stop()
        
        # Process API response
        formatted_response = normalize_chat_response(api_response)
        logger.info(f"API response received: {type(formatted_response)}")
        try:
            assistant_msg = api_response.choices[0].message
        except Exception:
            assistant_msg = None

        # Show assistant thinking (if available) and planned tool calls
        with trace_expander:
            if assistant_msg and (assistant_msg.content or '').strip():
                trace_plan_placeholder.markdown(f"**🧠 Assistant plan**\n\n{assistant_msg.content}")
            if assistant_msg and assistant_msg.tool_calls:
                tool_summaries = []
                for tc in assistant_msg.tool_calls:
                    args_preview = tc.function.arguments
                    if isinstance(args_preview, str) and len(args_preview) > 600:
                        args_preview = args_preview[:600] + "…"
                    tool_summaries.append(f"- 🔧 `{tc.function.name}` with args: `{args_preview}`")
                if tool_summaries:
                    trace_toolcalls_placeholder.markdown("**📋 Planned tool calls**\n\n" + "\n".join(tool_summaries))
        
        # Handle direct responses
        if not isinstance(formatted_response, list):
            response_content = formatted_response.get("content", "")

            #Checking for function simulation
            function_simulation_resp = has_function_simulation(response_content)
            if function_simulation_resp:
                logger.warning(f"Function simulation detected in response: {response_content[:100]}...")
                st.error (f"An error occurred with the API call with User Message. Please restart the conversation.")
                st.stop()
                
            else:
                st.markdown(response_content)
                st.session_state.messages.append(formatted_response)
            
        # Handle tool calls
        if isinstance(formatted_response, list):
            logger.info(f"Processing {len(formatted_response)} tool calls")
            # Show "thinking" message
            message_placeholder = st.empty()
            message_placeholder.markdown("🔍 Finding the best dining options for you…")

            # Process tool calls
            # IMPORTANT: Append the assistant message containing tool_calls before tool outputs
            try:
                assistant_msg = api_response.choices[0].message
                assistant_msg_dict = {
                    "role": "assistant",
                    "content": assistant_msg.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in (assistant_msg.tool_calls or [])
                    ],
                }
                st.session_state.messages.append(assistant_msg_dict)
            except Exception as e:
                logger.error(f"Failed to append assistant tool_calls message: {str(e)}", exc_info=True)

            tool_messages = execute_tool_calls(formatted_response)
            st.session_state.messages.extend(tool_messages)

            # Update trace with tool results
            with trace_expander:
                try:
                    rendered = []
                    for tm in tool_messages:
                        name = tm.get("name", "tool")
                        content = tm.get("content", "")
                        preview = content
                        if isinstance(preview, str) and len(preview) > 600:
                            preview = preview[:600] + "…"
                        rendered.append(f"- ✅ `{name}` result: `{preview}`")
                    if rendered:
                        trace_toolresults_placeholder.markdown("**📦 Tool results**\n\n" + "\n".join(rendered))
                except Exception as e:
                    logger.error(f"Failed to render tool results in trace: {e}")

            # Logging tool call processing completion
            logger.info(f"Tool execution completed with {len(tool_messages)} results")
        
            # Follow-up API call
            try:
                updated_response = generate_chat_completion(api_key=openai_api_key, 
                                           conversation_history=st.session_state.messages, 
                                           tools=restaurant_tools, 
                                           tool_calling_enabled=False)
            except Exception as e:
                logger.error(f"API call failed: {str(e)}", exc_info=True)
                st.error(f"An error occurred with the API call after Tool Use. Please restart the conversation.")
                st.stop()

            # Display final response
            formatted_updated_response = normalize_chat_response(updated_response)
            message_placeholder.markdown(formatted_updated_response.get("content", ""))
            st.session_state.messages.append(formatted_updated_response)

            # Update trace with follow-up
            with trace_expander:
                trace_followup_placeholder.markdown("**💬 Follow-up response**\n\n" + formatted_updated_response.get("content", ""))

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="gf-footer" style="margin-top: 32px; border-top: 1px solid #2e2e2e; padding-top: 14px;">
      🍽️ <b>Seatify AI</b> — Sri Lanka Reservation Engine &nbsp;|&nbsp;
      Powered by <b>OpenAI GPT-4o</b> &amp; <b>Streamlit</b> &nbsp;|&nbsp;
      Built By Azaam Ahmed &amp; Team &copy; 2026
    </div>
    """,
    unsafe_allow_html=True,
)


