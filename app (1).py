# ── Savage Bot — Streamlit + GGUF (runs on free Streamlit Cloud) ──────────────
import os, streamlit as st
from huggingface_hub import hf_hub_download
from llama_cpp import Llama

# ── Config ────────────────────────────────────────────────────────────────────
HF_REPO   = os.environ.get("HF_REPO",   "Pankaj4152/savage-bot-llama3-fp16")  # ← your GGUF repo
GGUF_FILE = os.environ.get("GGUF_FILE", "llama-3-8b-instruct.Q4_K_M.gguf")    # ← exact filename in repo
HF_TOKEN  = os.environ.get("HF_TOKEN",  "")

SYSTEM_MSG = (
    "You are Savage Bot — brutally honest, razor-sharp, and unapologetically blunt. "
    "You roast freely, call out nonsense instantly, and never sugarcoat anything. "
    "You're not mean for no reason — you're just allergic to BS. "
    "Keep responses punchy, witty, and direct. No corporate speak. No softening."
)

# ── Page ──────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Savage Bot 🔥", page_icon="🔥", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap');
html,body,[class*="css"]{font-family:'Space Grotesk',sans-serif;}
.stApp{background:#0e0e0e;color:#f0ece4;}
.chat-user{background:#1c1c1c;border-left:3px solid #ff5c1a;padding:.75rem 1rem;border-radius:0 8px 8px 0;margin:.5rem 0;color:#f0ece4;font-size:.95rem;}
.chat-bot{background:#161616;border-left:3px solid #ff9933;padding:.75rem 1rem;border-radius:0 8px 8px 0;margin:.5rem 0;color:#f0ece4;font-size:.95rem;}
.chat-label{font-size:.7rem;font-weight:600;letter-spacing:1px;text-transform:uppercase;margin-bottom:4px;}
.user-label{color:#ff5c1a;}.bot-label{color:#ff9933;}
.stTextInput>div>div>input{background:#1a1a1a!important;border:1px solid #2e2e2e!important;color:#f0ece4!important;border-radius:8px!important;font-family:'Space Grotesk',sans-serif!important;}
.stTextInput>div>div>input:focus{border-color:#ff5c1a!important;box-shadow:0 0 0 2px rgba(255,92,26,0.2)!important;}
.stButton>button{background:#ff5c1a!important;color:white!important;border:none!important;border-radius:8px!important;font-weight:600!important;font-family:'Space Grotesk',sans-serif!important;}
section[data-testid="stSidebar"]{background:#111!important;border-right:1px solid #1e1e1e;}
.stDownloadButton>button{background:#1c1c1c!important;color:#ff9933!important;border:1px solid #ff9933!important;border-radius:8px!important;font-weight:600!important;}
#MainMenu,footer{visibility:hidden;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;color:#ff5c1a;font-size:2.5rem;margin:1rem 0 0.2rem'>🔥 Savage Bot</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#888;margin-bottom:1.5rem'>Brutally honest. Zero filter. Built on LLaMA 3.</p>", unsafe_allow_html=True)

# ── Load model — cached so it only downloads once ────────────────────────────
@st.cache_resource(show_spinner="Downloading & loading Savage Bot... (first load ~2 min)")
def load_model():
    model_path = hf_hub_download(
        repo_id  = HF_REPO,
        filename = GGUF_FILE,
        token    = HF_TOKEN or None,
    )
    llm = Llama(
        model_path    = model_path,
        n_ctx         = 2048,    # context window
        n_threads     = 2,       # Streamlit Cloud has 2 vCPUs
        n_batch       = 512,
        verbose       = False,
    )
    return llm

llm = load_model()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Info")
    st.markdown(f"**Model:** Q4_K_M GGUF (~4GB)")
    st.markdown(f"**Repo:** [{HF_REPO}](https://huggingface.co/{HF_REPO})")
    st.markdown("---")
    temperature = st.slider("Temperature", 0.5, 1.5, 1.1, 0.1,
                            help="Higher = more savage/creative")
    max_tokens  = st.slider("Max tokens", 50, 400, 200, 50)
    st.markdown("---")
    if st.button("🗑️ Clear chat"):
        st.session_state.messages = []
        st.rerun()

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Render history ────────────────────────────────────────────────────────────
for m in st.session_state.messages:
    if m["role"] == "user":
        st.markdown(f'<div class="chat-user"><div class="chat-label user-label">You</div>{m["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-bot"><div class="chat-label bot-label">Savage Bot</div>{m["content"]}</div>', unsafe_allow_html=True)

# ── Input ─────────────────────────────────────────────────────────────────────
col1, col2 = st.columns([5, 1])
with col1:
    user_input = st.text_input("msg", placeholder="Say something... if you dare.",
                                label_visibility="collapsed", key="user_input")
with col2:
    send = st.button("Send")

# ── Generate ──────────────────────────────────────────────────────────────────
def generate(user_msg):
    # Build prompt with full chat history
    messages = [{"role": "system", "content": SYSTEM_MSG}]
    for m in st.session_state.messages[-10:]:  # last 10 turns max
        messages.append(m)
    messages.append({"role": "user", "content": user_msg})

    response = llm.create_chat_completion(
        messages    = messages,
        max_tokens  = max_tokens,
        temperature = temperature,
        top_p       = 0.9,
        repeat_penalty = 1.2,
        stop        = ["<|eot_id|>", "<|end_of_text|>"],
    )
    return response["choices"][0]["message"]["content"].strip()

if (send or user_input) and user_input.strip():
    st.session_state.messages.append({"role": "user", "content": user_input.strip()})
    with st.spinner("Savage Bot is thinking..."):
        reply = generate(user_input.strip())
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()

# ── Download chat ─────────────────────────────────────────────────────────────
if st.session_state.messages:
    st.markdown("---")
    chat_text = "\n\n".join(
        f"{'You' if m['role']=='user' else 'Savage Bot'}: {m['content']}"
        for m in st.session_state.messages
    )
    st.download_button("⬇️ Download chat", data=chat_text,
                       file_name="savage_bot_chat.txt", mime="text/plain")
