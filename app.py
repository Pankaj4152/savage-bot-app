import streamlit as st
import requests
import os

# ── Config ──────────────────────────────────────────────────────────────────
MODEL_ID = "Pankaj4152/savage-bot-llama3"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL_ID}/v1/chat/completions"
HF_TOKEN = os.environ.get("HF_TOKEN", "")

SYSTEM_PROMPT = (
    "You are Savage Bot — brutally honest, witty, and unapologetically blunt. "
    "You roast, you rant, but you're never boring. Keep it sharp."
)

# ── Page setup ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Savage Bot 🔥",
    page_icon="🔥",
    layout="centered",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
}

/* Dark fire theme */
.stApp {
    background: #0e0e0e;
    color: #f0ece4;
}

/* Header */
.header-block {
    text-align: center;
    padding: 2rem 0 1rem;
}
.header-block h1 {
    font-size: 2.8rem;
    font-weight: 700;
    letter-spacing: -1px;
    color: #ff5c1a;
    margin: 0;
}
.header-block p {
    color: #888;
    font-size: 0.95rem;
    margin-top: 0.3rem;
}

/* Chat messages */
.chat-user {
    background: #1c1c1c;
    border-left: 3px solid #ff5c1a;
    padding: 0.75rem 1rem;
    border-radius: 0 8px 8px 0;
    margin: 0.5rem 0;
    color: #f0ece4;
    font-size: 0.95rem;
}
.chat-bot {
    background: #161616;
    border-left: 3px solid #ff9933;
    padding: 0.75rem 1rem;
    border-radius: 0 8px 8px 0;
    margin: 0.5rem 0;
    color: #f0ece4;
    font-size: 0.95rem;
}
.chat-label {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 4px;
}
.user-label { color: #ff5c1a; }
.bot-label  { color: #ff9933; }

/* Input area */
.stTextInput > div > div > input {
    background: #1a1a1a !important;
    border: 1px solid #2e2e2e !important;
    color: #f0ece4 !important;
    border-radius: 8px !important;
    padding: 0.7rem 1rem !important;
    font-family: 'Space Grotesk', sans-serif !important;
}
.stTextInput > div > div > input:focus {
    border-color: #ff5c1a !important;
    box-shadow: 0 0 0 2px rgba(255,92,26,0.2) !important;
}

/* Buttons */
.stButton > button {
    background: #ff5c1a !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    padding: 0.5rem 1.2rem !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #111 !important;
    border-right: 1px solid #1e1e1e;
}
section[data-testid="stSidebar"] .stTextInput > div > div > input {
    background: #1a1a1a !important;
    border: 1px solid #2e2e2e !important;
    color: #f0ece4 !important;
}

/* Download button */
.stDownloadButton > button {
    background: #1c1c1c !important;
    color: #ff9933 !important;
    border: 1px solid #ff9933 !important;
    border-radius: 8px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
}
.stDownloadButton > button:hover {
    background: #ff9933 !important;
    color: #0e0e0e !important;
}

/* Spinner */
.stSpinner > div { border-top-color: #ff5c1a !important; }

/* Hide Streamlit branding */
#MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-block">
  <h1>🔥 Savage Bot</h1>
  <p>Brutally honest. Zero filter. Built on LLaMA 3.</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar: token input ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Setup")
    token_input = st.text_input(
        "HuggingFace Token",
        value=HF_TOKEN,
        type="password",
        placeholder="hf_xxxxxxxxxxxx",
        help="Get yours at huggingface.co/settings/tokens"
    )
    if token_input:
        HF_TOKEN = token_input

    st.markdown("---")
    st.markdown("**Model**")
    st.code(MODEL_ID, language=None)
    st.markdown("[View on HuggingFace ↗](https://huggingface.co/Pankaj4152/savage-bot-llama3)")

    st.markdown("---")
    if st.button("🗑️ Clear chat"):
        st.session_state.messages = []
        st.rerun()

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Render chat history ───────────────────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="chat-user">
          <div class="chat-label user-label">You</div>
          {msg["content"]}
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-bot">
          <div class="chat-label bot-label">Savage Bot</div>
          {msg["content"]}
        </div>""", unsafe_allow_html=True)

# ── Input ─────────────────────────────────────────────────────────────────────
col1, col2 = st.columns([5, 1])
with col1:
    user_input = st.text_input(
        "Message",
        placeholder="Say something... if you dare.",
        label_visibility="collapsed",
        key="user_input"
    )
with col2:
    send = st.button("Send")

# ── Inference ─────────────────────────────────────────────────────────────────
def query_model(user_msg: str) -> str:
    if not HF_TOKEN:
        return "⚠️ Add your HuggingFace token in the sidebar first."

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL_ID,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            *st.session_state.messages,
            {"role": "user", "content": user_msg},
        ],
        "max_tokens": 300,
        "temperature": 0.85,
    }
    try:
        resp = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except requests.exceptions.Timeout:
        return "⏳ Model is loading (cold start). Wait 30s and try again."
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ── Handle send ───────────────────────────────────────────────────────────────
if (send or user_input) and user_input.strip():
    user_msg = user_input.strip()
    st.session_state.messages.append({"role": "user", "content": user_msg})

    with st.spinner("Savage Bot is thinking..."):
        reply = query_model(user_msg)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()

# ── Download chat ─────────────────────────────────────────────────────────────
if st.session_state.messages:
    st.markdown("---")
    chat_text = "\n\n".join(
        f"{'You' if m['role']=='user' else 'Savage Bot'}: {m['content']}"
        for m in st.session_state.messages
    )
    st.download_button(
        label="⬇️ Download chat",
        data=chat_text,
        file_name="savage_bot_chat.txt",
        mime="text/plain",
    )
