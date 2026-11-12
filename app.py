"""
╔══════════════════════════════════════════════════════════════════════════════╗
║           🤖 KIRA AI CHATBOT - Professional Edition v2.0                      ║
║      Design & Development: Gokulakrishnan | St. Peter's Institute             ║
║      Tech Stack: Streamlit + Python | Free AI APIs | Open Source             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import streamlit.components.v1 as components
import requests
import json
import time
import base
from datetime import datetime

# ──────────────────────────────────────────────────────────────────────────────
# PAGE CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="KIRA AI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com",
        "Report a bug": "https://github.com",
        "About": "KIRA AI Chatbot v2.0 - Built with ❤️ by Gokulakrishnan"
    }
)

# ──────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS
# ──────────────────────────────────────────────────────────────────────────────
def inject_custom_css():
    theme = st.session_state.get("theme", "dark")
    if theme == "dark":
        css = """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        * { font-family: 'Inter', sans-serif; }
        .stApp { background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%); }
        .main .block-container { padding-top: 1rem; padding-bottom: 1rem; max-width: 900px; }
        .stChatMessage { background: rgba(255,255,255,0.03) !important; border-radius: 16px !important; border: 1px solid rgba(255,255,255,0.06) !important; margin-bottom: 12px !important; }
        .stChatMessage[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) { background: linear-gradient(135deg, rgba(59,130,246,0.1), rgba(147,51,234,0.1)) !important; border-left: 3px solid #3b82f6 !important; }
        .stChatMessage[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) { background: linear-gradient(135deg, rgba(16,185,129,0.08), rgba(6,182,212,0.08)) !important; border-left: 3px solid #10b981 !important; }
        [data-testid="stSidebar"] { background: linear-gradient(180deg, #0f0f23 0%, #1a1a2e 100%) !important; border-right: 1px solid rgba(255,255,255,0.06); }
        .stButton > button { border-radius: 12px !important; font-weight: 500 !important; }
        pre { background: #1e1e2e !important; border-radius: 12px !important; border: 1px solid rgba(255,255,255,0.08) !important; }
        code { background: rgba(255,255,255,0.05) !important; border-radius: 6px !important; padding: 2px 6px !important; }
        h1, h2, h3 { color: #e2e8f0 !important; }
        p, li, span { color: #cbd5e1 !important; }
        .welcome-card { background: linear-gradient(135deg, rgba(59,130,246,0.15), rgba(147,51,234,0.15)); border: 1px solid rgba(255,255,255,0.1); border-radius: 20px; padding: 2rem; text-align: center; margin-bottom: 2rem; }
        .status-badge { display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
        .status-online { background: rgba(16,185,129,0.15); color: #10b981; }
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        header { visibility: hidden; }
        </style>
        """
    else:
        css = """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        * { font-family: 'Inter', sans-serif; }
        .main .block-container { max-width: 900px; }
        .stChatMessage { border-radius: 16px !important; margin-bottom: 12px !important; }
        .stButton > button { border-radius: 12px !important; font-weight: 500 !important; }
        .welcome-card { background: linear-gradient(135deg, rgba(59,130,246,0.08), rgba(147,51,234,0.08)); border: 1px solid rgba(0,0,0,0.08); border-radius: 20px; padding: 2rem; text-align: center; margin-bottom: 2rem; }
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        </style>
        """
    st.markdown(css, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ──────────────────────────────────────────────────────────────────────────────
def init_session_state():
    defaults = {
        "messages": [],
        "chat_history": {},
        "current_chat_id": None,
        "theme": "dark",
        "api_provider": "Groq (Free)",
        "model": "llama-3.3-70b-versatile",
        "temperature": 0.7,
        "max_tokens": 2048,
        "system_prompt": "You are KIRA, a helpful, friendly, and intelligent AI assistant. You provide accurate, well-structured responses. When explaining code, use proper formatting with syntax highlighting.",
        "persona": "General Assistant",
        "voice_enabled": False,
        "voice_mode": False,
        "streaming": True,
        "show_welcome": True,
        "uploaded_file_content": None,
        "uploaded_file_type": None,
        "uploaded_image_data": None,
        "uploaded_image_mime": None,
        "pending_prompt": None,
        "regenerate_index": None,
        "last_image": None,
        "last_image_prompt": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val
    if not st.session_state.chat_history:
        create_new_chat()

# ──────────────────────────────────────────────────────────────────────────────
# CHAT MANAGEMENT
# ──────────────────────────────────────────────────────────────────────────────
def create_new_chat():
    chat_id = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    st.session_state.current_chat_id = chat_id
    st.session_state.messages = []
    st.session_state.chat_history[chat_id] = {
        "title": "New Chat",
        "created_at": datetime.now().isoformat(),
        "messages": [],
        "model": st.session_state.model,
        "token_count": 0
    }
    st.session_state.show_welcome = True
    return chat_id

def load_chat(chat_id):
    st.session_state.current_chat_id = chat_id
    st.session_state.messages = st.session_state.chat_history[chat_id]["messages"].copy()
    st.session_state.show_welcome = False

def save_current_chat():
    if st.session_state.current_chat_id:
        chat = st.session_state.chat_history[st.session_state.current_chat_id]
        chat["messages"] = st.session_state.messages.copy()
        if st.session_state.messages and chat["title"] == "New Chat":
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    title = msg["content"][:40] + "..." if len(msg["content"]) > 40 else msg["content"]
                    chat["title"] = title
                    break

def delete_chat(chat_id):
    if chat_id in st.session_state.chat_history:
        del st.session_state.chat_history[chat_id]
    if st.session_state.chat_history:
        st.session_state.current_chat_id = list(st.session_state.chat_history.keys())[0]
        st.session_state.messages = st.session_state.chat_history[st.session_state.current_chat_id]["messages"].copy()
    else:
        create_new_chat()

# ──────────────────────────────────────────────────────────────────────────────
# PERSONAS
# ──────────────────────────────────────────────────────────────────────────────
PERSONAS = {
    "General Assistant": "You are KIRA, a helpful, friendly, and intelligent AI assistant. You provide accurate, well-structured responses. When explaining code, use proper formatting with syntax highlighting.",
    "Code Expert": "You are KIRA, an expert software engineer and coding mentor. You write clean, efficient, well-documented code. You explain complex concepts simply and provide best practices.",
    "Creative Writer": "You are KIRA, a creative writing assistant with a vivid imagination. You help with storytelling, poetry, essays, and creative projects.",
    "Math Tutor": "You are KIRA, a patient and knowledgeable mathematics tutor. You explain concepts step-by-step, show your work clearly, and use analogies.",
    "Science Explainer": "You are KIRA, a science communicator who makes complex topics accessible. You use analogies, real-world examples, and clear explanations.",
    "Interview Coach": "You are KIRA, a professional interview coach. You help users prepare for job interviews by providing practice questions and feedback.",
    "Tamil Translator": "You are KIRA, a bilingual assistant fluent in English and Tamil. You can translate between languages and help with Tamil writing.",
}

# ──────────────────────────────────────────────────────────────────────────────
# MODEL CONFIGS
# ──────────────────────────────────────────────────────────────────────────────
MODEL_CONFIGS = {
    "Groq (Free)": {
        "models": [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "gemma2-9b-it",
            "deepseek-r1-distill-llama-70b",
        ],
        "key_name": "GROQ_API_KEY",
        "docs": "Get free API key at: console.groq.com"
    },
    "Google Gemini (Free)": {
        "models": [
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
            "gemini-2.5-flash",
        ],
        "key_name": "GOOGLE_API_KEY",
        "docs": "Get free API key at: aistudio.google.com/app/apikey"
    },
    "Hugging Face (Free)": {
        "models": [
            "mistralai/Mistral-7B-Instruct-v0.3",
            "meta-llama/Llama-3.1-8B-Instruct",
            "microsoft/Phi-3-mini-4k-instruct",
        ],
        "key_name": "HF_API_KEY",
        "docs": "Get free API key at: huggingface.co/settings/tokens"
    }
}

# ──────────────────────────────────────────────────────────────────────────────
# VOICE / AUDIO HELPERS
# ──────────────────────────────────────────────────────────────────────────────
def transcribe_audio(audio_bytes, api_key, provider):
    if not api_key:
        return None, "API key required. Add it in the sidebar."
    if not audio_bytes:
        return None, "No audio recorded."

    if provider == "Groq (Free)":
        try:
            url = "https://api.groq.com/openai/v1/audio/transcriptions"
            headers = {"Authorization": f"Bearer {api_key}"}
            files = {"file": ("audio.wav", audio_bytes, "audio/wav")}
            data = {"model": "whisper-large-v3-turbo"}
            r = requests.post(url, headers=headers, files=files, data=data, timeout=30)
            r.raise_for_status()
            return r.json().get("text", "").strip(), None
        except Exception as e:
            return None, f"Transcription failed: {e}"

    elif provider == "Google Gemini (Free)":
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
            payload = {
                "contents": [{
                    "parts": [
                        {"text": "Transcribe this audio exactly as spoken. Return only the transcript."},
                        {"inline_data": {"mime_type": "audio/wav", "data": base64.b64encode(audio_bytes).decode()}}
                    ]
                }]
            }
            r = requests.post(url, json=payload, timeout=30)
            r.raise_for_status()
            data = r.json()
            if "candidates" in data and data["candidates"]:
                return data["candidates"][0]["content"]["parts"][0]["text"].strip(), None
            return None, "No transcript from Gemini."
        except Exception as e:
            return None, f"Transcription failed: {e}"

    return None, "Voice input works with Groq or Gemini. Switch in sidebar."


def render_speak_button(text, key):
    safe = json.dumps(text[:3000])
    fn = f"speak_{key}"
    components.html(f"""
    <button onclick="{fn}()" style="background:rgba(59,130,246,0.15);border:1px solid rgba(59,130,246,0.4);color:#93c5fd;padding:6px 14px;border-radius:10px;cursor:pointer;font-family:Inter,sans-serif;font-size:13px;">
        🔊 Read Aloud
    </button>
    <script>
    function {fn}() {{
        const u = new SpeechSynthesisUtterance({safe});
        u.lang = 'en-US';
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(u);
    }}
    </script>
    """, height=50)


def render_copy_button(text, key):
    safe = json.dumps(text)
    components.html(f"""
    <button onclick="navigator.clipboard.writeText({safe}); this.innerHTML='✅ Copied!';" 
            style="background:rgba(16,185,129,0.15);border:1px solid rgba(16,185,129,0.4);color:#6ee7b7;padding:6px 14px;border-radius:10px;cursor:pointer;font-family:Inter,sans-serif;font-size:13px;">
        📋 Copy
    </button>
    """, height=50)


def auto_speak(text):
    safe = json.dumps(text[:3000])
    components.html(f"""
    <script>
    const u = new SpeechSynthesisUtterance({safe});
    u.lang = 'en-US';
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(u);
    </script>
    """, height=0)

# ──────────────────────────────────────────────────────────────────────────────
# AI RESPONSE GENERATION
# ──────────────────────────────────────────────────────────────────────────────
def generate_response_stream(messages, api_key, provider, model, temperature, max_tokens,
                              file_context=None, image_data=None, image_mime=None):
    system_content = st.session_state.system_prompt
    if file_context:
        system_content += (
            "\n\nThe user uploaded a document. Use this content to answer accurately:\n\n"
            f"---\n{file_context}\n---"
        )
    full_messages = [{"role": "system", "content": system_content}] + messages

    if provider == "Groq (Free)":
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": model,
            "messages": full_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True
        }
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers, json=payload, stream=True, timeout=60
            )
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]
                        if data == '[DONE]':
                            break
                        try:
                            chunk = json.loads(data)
                            if chunk.get('choices') and chunk['choices'][0].get('delta', {}).get('content'):
                                yield chunk['choices'][0]['delta']['content']
                        except Exception:
                            pass
        except Exception as e:
            yield f"❌ Error: {str(e)}\n\n💡 Check your Groq API key at console.groq.com"

    elif provider == "Google Gemini (Free)":
        gemini_messages = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            gemini_messages.append({"role": role, "parts": [{"text": msg["content"]}]})

        if image_data and gemini_messages:
            for i in range(len(gemini_messages) - 1, -1, -1):
                if gemini_messages[i]["role"] == "user":
                    gemini_messages[i]["parts"].append({
                        "inline_data": {
                            "mime_type": image_mime or "image/png",
                            "data": base64.b64encode(image_data).decode()
                        }
                    })
                    break

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {
            "systemInstruction": {"parts": [{"text": system_content}]},
            "contents": gemini_messages,
            "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens}
        }
        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            if "candidates" in data and data["candidates"]:
                parts = data["candidates"][0]["content"]["parts"]
                text = "".join(p.get("text", "") for p in parts)
                for i in range(0, len(text), 4):
                    yield text[i:i+4]
                    time.sleep(0.01)
            else:
                yield "⚠️ No response from Gemini."
        except Exception as e:
            yield f"❌ Error: {str(e)}\n\n💡 Get key at aistudio.google.com/app/apikey"

    elif provider == "Hugging Face (Free)":
        headers = {"Authorization": f"Bearer {api_key}"}
        prompt = f"<|system|>\n{system_content}\n"
        for msg in messages:
            if msg["role"] == "user":
                prompt += f"<|user|>\n{msg['content']}\n"
            else:
                prompt += f"<|assistant|>\n{msg['content']}\n"
        prompt += "<|assistant|>\n"
        payload = {
            "inputs": prompt,
            "parameters": {"temperature": temperature, "max_new_tokens": max_tokens, "return_full_text": False}
        }
        try:
            api_url = f"https://api-inference.huggingface.co/models/{model}"
            response = requests.post(api_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                text = data[0].get("generated_text", "")
                for i in range(0, len(text), 4):
                    yield text[i:i+4]
                    time.sleep(0.01)
            else:
                yield "⚠️ No response from Hugging Face."
        except Exception as e:
            yield f"❌ Error: {str(e)}\n\n💡 Get key at huggingface.co/settings/tokens"

# ──────────────────────────────────────────────────────────────────────────────
# IMAGE GENERATION
# ──────────────────────────────────────────────────────────────────────────────
def generate_image(prompt, width=1024, height=1024, seed=None):
    seed = seed or int(time.time())
    encoded = requests.utils.quote(prompt)
    return f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&seed={seed}&nologo=true"

# ──────────────────────────────────────────────────────────────────────────────
# EXPORT
# ──────────────────────────────────────────────────────────────────────────────
def export_chat_txt(messages):
    lines = ["═" * 60, "  KIRA AI Chatbot - Chat Export", f"  Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "═" * 60, ""]
    for msg in messages:
        role = "👤 You" if msg["role"] == "user" else "🤖 KIRA"
        lines += [f"\n{role}:", "─" * 40, msg["content"], ""]
    return "\n".join(lines)

def export_chat_md(messages):
    lines = [f"# KIRA AI Chatbot - Chat Export\n\n*Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n---\n"]
    for msg in messages:
        role = "**You**" if msg["role"] == "user" else "**KIRA**"
        lines.append(f"\n### {role}\n\n{msg['content']}\n")
    return "\n".join(lines)

def export_chat_json(messages):
    return json.dumps({
        "app": "KIRA AI Chatbot", "version": "2.0",
        "exported_at": datetime.now().isoformat(), "messages": messages
    }, indent=2)

# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:1rem 0;">
            <h1 style="font-size:2rem;margin:0;background:linear-gradient(90deg,#3b82f6,#8b5cf6,#ec4899);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">🤖 KIRA</h1>
            <p style="font-size:0.8rem;opacity:0.6;margin:0;">AI Chatbot v2.0</p>
        </div>
        """, unsafe_allow_html=True)
        st.divider()

        if st.button("➕ New Chat", use_container_width=True, type="primary"):
            save_current_chat()
            create_new_chat()
            st.rerun()

        st.markdown("#### 💬 Chat History")
        search_term = st.text_input("🔍 Search chats", placeholder="Search...", label_visibility="collapsed")

        chat_ids = list(st.session_state.chat_history.keys())
        chat_ids.reverse()
        for chat_id in chat_ids:
            chat = st.session_state.chat_history[chat_id]
            title = chat.get("title", "Untitled")
            if search_term and search_term.lower() not in title.lower():
                continue
            is_active = chat_id == st.session_state.current_chat_id
            col1, col2 = st.columns([0.85, 0.15])
            with col1:
                btn_type = "primary" if is_active else "secondary"
                if st.button(f"{'▸ ' if is_active else ''}{title[:25]}{'...' if len(title) > 25 else ''}",
                             key=f"chat_{chat_id}", use_container_width=True, type=btn_type):
                    save_current_chat()
                    load_chat(chat_id)
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"del_{chat_id}"):
                    delete_chat(chat_id)
                    st.rerun()

        st.divider()

        with st.expander("⚙️ Settings", expanded=False):
            theme = st.toggle("🌙 Dark Mode", value=st.session_state.theme == "dark")
            new_theme = "dark" if theme else "light"
            if new_theme != st.session_state.theme:
                st.session_state.theme = new_theme
                st.rerun()
            st.session_state.streaming = st.toggle("⚡ Streaming", value=st.session_state.streaming)
            st.session_state.voice_enabled = st.toggle("🔊 Auto Voice Output", value=st.session_state.voice_enabled)
            st.session_state.voice_mode = st.toggle("🎙️ Voice Input Mode", value=st.session_state.voice_mode)

        with st.expander("🔑 API Configuration", expanded=True):
            provider = st.selectbox(
                "AI Provider",
                list(MODEL_CONFIGS.keys()),
                index=list(MODEL_CONFIGS.keys()).index(st.session_state.api_provider)
            )
            st.session_state.api_provider = provider
            config = MODEL_CONFIGS[provider]
            
# Secrets-ல Key இருக்கான்னு செக் பண்றோம்
try:
    if provider == "Groq (Free)":
        api_key = st.secrets["GROQ_API_KEY"]
    elif provider == "Google Gemini (Free)":
        api_key = st.secrets["GOOGLE_API_KEY"]
    elif provider == "Hugging Face (Free)":
        api_key = st.secrets["HF_API_KEY"]
    st.success("✅ API Key loaded securely from server")
except Exception:
    # Secrets-ல இல்லைனா மட்டும் யூசர் கிட்ட கேட்கும்
    api_key = st.text_input(
        config['key_name'], type="password",
        placeholder=f"Enter your {config['key_name']}...",
        help=config["docs"]
    )
model = st.selectbox(
          "Model", config["models"],
                index=config["models"].index(st.session_state.model) if st.session_state.model in config["models"] else 0
            )
            st.session_state.model = model
            st.caption(f"📖 {config['docs']}")

        with st.expander("🎛️ Model Parameters", expanded=False):
            st.session_state.temperature = st.slider(
                "Temperature", 0.0, 2.0, st.session_state.temperature, 0.1)
            st.session_state.max_tokens = st.slider(
                "Max Tokens", 256, 4096, st.session_state.max_tokens, 256)

        with st.expander("🎭 AI Persona", expanded=False):
            persona = st.selectbox(
                "Select Persona", list(PERSONAS.keys()),
                index=list(PERSONAS.keys()).index(st.session_state.persona) if st.session_state.persona in PERSONAS else 0
            )
            st.session_state.persona = persona
            st.session_state.system_prompt = PERSONAS[persona]
            with st.popover("✏️ Custom System Prompt"):
                custom = st.text_area("Edit", st.session_state.system_prompt, height=150)
                if st.button("Apply"):
                    st.session_state.system_prompt = custom
                    st.session_state.persona = "Custom"
                    st.success("Applied!")

        st.divider()

        with st.expander("📤 Export Chat", expanded=False):
            if st.session_state.messages:
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.download_button("TXT", export_chat_txt(st.session_state.messages),
                                       f"kira_{datetime.now().strftime('%Y%m%d')}.txt", use_container_width=True)
                with c2:
                    st.download_button("MD", export_chat_md(st.session_state.messages),
                                       f"kira_{datetime.now().strftime('%Y%m%d')}.md", use_container_width=True)
                with c3:
                    st.download_button("JSON", export_chat_json(st.session_state.messages),
                                       f"kira_{datetime.now().strftime('%Y%m%d')}.json", use_container_width=True)
            else:
                st.info("Start a chat to export")

        st.divider()
        total_chats = len(st.session_state.chat_history)
        total_messages = sum(len(c["messages"]) for c in st.session_state.chat_history.values())
        st.markdown(f"""
        <div style="text-align:center;font-size:0.75rem;opacity:0.5;">
            💬 {total_chats} chats | 📝 {total_messages} messages<br>
            Built with ❤️ by Gokulakrishnan
        </div>
        """, unsafe_allow_html=True)

        return api_key

# ──────────────────────────────────────────────────────────────────────────────
# WELCOME
# ──────────────────────────────────────────────────────────────────────────────
def render_welcome():
    st.markdown("""
    <div class="welcome-card">
        <h1 style="font-size:2.5rem;margin-bottom:0.5rem;">🤖 KIRA AI</h1>
        <p style="font-size:1.1rem;opacity:0.8;">Your intelligent AI companion powered by cutting-edge language models</p>
        <div style="margin-top:1.5rem;">
            <span class="status-badge status-online">● Online</span>
            <span style="margin-left:10px;font-size:0.85rem;opacity:0.6;">Free AI Models | No Credit Card Required</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### ✨ What can KIRA do?")
    cols = st.columns(3)
    cards = [
        ("💬 Smart Chat", "Natural conversations with memory"),
        ("💻 Code Helper", "Write, debug, and explain code"),
        ("🎨 AI Images", "Generate images from text"),
        ("🎙️ Voice Chat", "Speak to KIRA and listen"),
        ("📄 File Analysis", "Upload PDFs and images"),
        ("🎭 Personas", "Tutor, coder, writer & more"),
    ]
    for i, (title, desc) in enumerate(cards):
        with cols[i % 3]:
            st.markdown(f'<div style="background:rgba(255,255,255,0.03);border-radius:16px;padding:1.2rem;border:1px solid rgba(255,255,255,0.06);margin-bottom:12px;"><h4>{title}</h4><p style="font-size:0.85rem;opacity:0.7;">{desc}</p></div>', unsafe_allow_html=True)

    st.markdown("<br><h4 style='text-align:center;'>👇 Try asking something...</h4>", unsafe_allow_html=True)
    suggestions = [
        "Explain quantum computing in simple terms",
        "Write a Python function to sort a list",
        "Generate an image of a futuristic city",
        "Help me prepare for a software interview",
        "Translate 'Hello, how are you?' to Tamil",
        "Summarize the theory of relativity",
    ]
    scols = st.columns(3)
    for i, s in enumerate(suggestions):
        with scols[i % 3]:
            if st.button(s, key=f"sug_{i}", use_container_width=True):
                st.session_state.pending_prompt = s
                st.session_state.show_welcome = False
                st.rerun()

# ──────────────────────────────────────────────────────────────────────────────
# CHAT INTERFACE
# ──────────────────────────────────────────────────────────────────────────────
def render_chat_interface(api_key):
    if st.session_state.uploaded_file_content:
        st.info("📄 File loaded in context. Ask questions about it!")
    if st.session_state.uploaded_image_data:
        if st.session_state.api_provider == "Google Gemini (Free)":
            st.info("🖼️ Image loaded — Gemini will analyze it.")
        else:
            st.warning("🖼️ Image analysis works with **Gemini** provider only.")

    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                c1, c2, c3 = st.columns([0.2, 0.2, 0.6])
                with c1:
                    render_copy_button(message["content"], f"cp_{i}")
                with c2:
                    render_speak_button(message["content"], f"sp_{i}")
                with c3:
                    if st.button("🔄 Regenerate", key=f"regen_{i}"):
                        st.session_state.regenerate_index = i
                        st.rerun()

    # Handle regenerate
    if st.session_state.regenerate_index is not None:
        idx = st.session_state.regenerate_index
        st.session_state.regenerate_index = None
        st.session_state.messages = st.session_state.messages[:idx]
        last_user = None
        for m in reversed(st.session_state.messages):
            if m["role"] == "user":
                last_user = m
                break
        if last_user and api_key:
            with st.chat_message("assistant", avatar="🤖"):
                ph = st.empty()
                full = ""
                for chunk in generate_response_stream(
                    st.session_state.messages,
                    api_key, st.session_state.api_provider, st.session_state.model,
                    st.session_state.temperature, st.session_state.max_tokens,
                    file_context=st.session_state.uploaded_file_content,
                    image_data=st.session_state.uploaded_image_data,
                    image_mime=st.session_state.uploaded_image_mime
                ):
                    full += chunk
                    ph.markdown(full + "▌")
                ph.markdown(full)
            st.session_state.messages.append({"role": "assistant", "content": full})
            save_current_chat()
            st.rerun()

    # Voice input
    if st.session_state.voice_mode:
        st.markdown("##### 🎙️ Voice Input")
        audio = st.audio_input("Record", key="voice_rec", label_visibility="collapsed")
        if audio:
            if st.button("📤 Send Voice Message", type="primary", use_container_width=True):
                with st.spinner("Transcribing..."):
                    transcript, err = transcribe_audio(audio.read(), api_key, st.session_state.api_provider)
                if err:
                    st.error(err)
                elif transcript:
                    st.session_state.pending_prompt = transcript
                    st.rerun()

    # Chat input
    prompt = st.chat_input("💬 Type your message...")
    if st.session_state.pending_prompt:
        prompt = st.session_state.pending_prompt
        st.session_state.pending_prompt = None

    if prompt:
        st.session_state.show_welcome = False
        st.session_state.messages.append({"role": "user", "content": prompt})
        save_current_chat()

        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        if not api_key:
            with st.chat_message("assistant", avatar="🤖"):
                st.warning("🔑 Add your free API key in the sidebar (Groq recommended).")
        else:
            with st.chat_message("assistant", avatar="🤖"):
                ph = st.empty()
                full = ""
                try:
                    for chunk in generate_response_stream(
                        st.session_state.messages[:-1],
                        api_key, st.session_state.api_provider, st.session_state.model,
                        st.session_state.temperature, st.session_state.max_tokens,
                        file_context=st.session_state.uploaded_file_content,
                        image_data=st.session_state.uploaded_image_data,
                        image_mime=st.session_state.uploaded_image_mime
                    ):
                        full += chunk
                        ph.markdown(full + "▌")
                    ph.markdown(full)

                    if st.session_state.voice_enabled and full:
                        auto_speak(full)
                except Exception as e:
                    ph.error(f"❌ Error: {str(e)}")
                    full = f"Error: {str(e)}"

            st.session_state.messages.append({"role": "assistant", "content": full})
            save_current_chat()

        st.rerun()

# ──────────────────────────────────────────────────────────────────────────────
# IMAGE GEN TAB
# ──────────────────────────────────────────────────────────────────────────────
def render_image_generation():
    st.markdown('<div style="text-align:center;padding:1rem 0;"><h2>🎨 AI Image Generator</h2><p style="opacity:0.7;">Free images from text!</p></div>', unsafe_allow_html=True)
    c1, c2 = st.columns([0.6, 0.4])
    with c1:
        p = st.text_area("Describe your image",
                         placeholder="A futuristic city at sunset, cyberpunk style...",
                         height=120)
        sc1, sc2 = st.columns(2)
        with sc1:
            w = st.selectbox("Width", [512, 768, 1024, 1280], index=2)
        with sc2:
            h = st.selectbox("Height", [512, 768, 1024, 1280], index=2)
        if st.button("🎨 Generate Image", type="primary", use_container_width=True):
            if not p:
                st.warning("Enter a description first!")
            else:
                with st.spinner("Creating..."):
                    st.session_state.last_image = generate_image(p, w, h)
                    st.session_state.last_image_prompt = p
                    st.rerun()
    with c2:
        if st.session_state.last_image:
            st.image(st.session_state.last_image, caption=st.session_state.last_image_prompt or "", use_container_width=True)
            try:
                img_data = requests.get(st.session_state.last_image, timeout=30).content
                st.download_button("📥 Download", img_data,
                                   f"kira_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                                   mime="image/png", use_container_width=True)
            except Exception:
                st.info("Right-click to save")
        else:
            st.info("Image will appear here")
    st.caption("💡 Powered by Pollinations AI — free!")

# ──────────────────────────────────────────────────────────────────────────────
# FILE ANALYSIS TAB
# ──────────────────────────────────────────────────────────────────────────────
def render_file_analysis(api_key):
    st.markdown('<div style="text-align:center;padding:1rem 0;"><h2>📄 File Analysis</h2><p style="opacity:0.7;">Upload PDFs, images, or text and ask KIRA</p></div>', unsafe_allow_html=True)

    if st.session_state.uploaded_file_content or st.session_state.uploaded_image_data:
        if st.button("🗑️ Clear uploaded file"):
            st.session_state.uploaded_file_content = None
            st.session_state.uploaded_file_type = None
            st.session_state.uploaded_image_data = None
            st.session_state.uploaded_image_mime = None
            st.rerun()

    f = st.file_uploader("Upload", type=["pdf", "png", "jpg", "jpeg", "txt"])

    if f:
        ft = f.type
        if ft.startswith("image/"):
            st.image(f, caption="Uploaded", use_container_width=True)
            st.session_state.uploaded_image_data = f.read()
            st.session_state.uploaded_image_mime = ft
            st.success("✅ Image loaded! Ask in Chat (requires Gemini provider)")

        elif ft == "application/pdf":
            try:
                from pypdf import PdfReader
                reader = PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += (page.extract_text() or "") + "\n"
                if not text.strip():
                    st.warning("No text found (scanned PDF?)")
                else:
                    st.session_state.uploaded_file_content = text[:8000]
                    st.session_state.uploaded_file_type = "pdf"
                    with st.expander("📖 Preview"):
                        st.text_area("Content", text[:2000], height=200)
                    st.success(f"✅ PDF loaded ({len(text)} chars). Ask in Chat!")
            except ImportError:
                st.error("Run: pip install pypdf")
            except Exception as e:
                st.error(f"Error: {e}")

        elif ft.startswith("text/"):
            content = f.read().decode("utf-8", errors="ignore")
            st.session_state.uploaded_file_content = content[:8000]
            st.session_state.uploaded_file_type = "text"
            with st.expander("📖 Preview"):
                st.text_area("Content", content[:2000], height=200)
            st.success(f"✅ Loaded ({len(content)} chars). Ask in Chat!")

# ──────────────────────────────────────────────────────────────────────────────
# ABOUT TAB
# ──────────────────────────────────────────────────────────────────────────────
def render_about():
    st.markdown("""
    <div style="text-align:center;padding:2rem 0;">
        <h1 style="font-size:3rem;background:linear-gradient(90deg,#3b82f6,#8b5cf6,#ec4899);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">🤖 KIRA AI</h1>
        <p style="font-size:1.2rem;opacity:0.8;">Design and Development of a Web-Based AI Chatbot</p>
    </div>
    """, unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        ### 📋 Project Info

        | Field | Details |
        |-------|---------|
        | **Project** | KIRA AI Chatbot v2.0 |
        | **Student** | Gokulakrishnan |
        | **Register No** | SPC26DSU005 |
        | **Department** | AI & Machine Learning |
        | **Institution** | St. Peter's Institute of Higher Education and Research |
        | **Guide** | Dr. J. Suganthi Vinodhini |
        | **Year** | 2026–2027 |

        ### 🛠️ Tech Stack
        - **Frontend**: Streamlit (Python)
        - **AI**: Groq, Google Gemini, Hugging Face
        - **Image Gen**: Pollinations AI
        - **Voice**: Groq Whisper / Gemini Audio + Web Speech API
        - **Hosting**: Streamlit Cloud (Free)
        """)
    with c2:
        st.markdown("""
        ### ✨ Features

        | Feature | Status |
        |---------|--------|
        | 💬 Multi-turn Chat | ✅ |
        | 🧠 Multiple AI Models | ✅ |
        | 💾 Chat History | ✅ |
        | ⚡ Streaming | ✅ |
        | 🎨 AI Image Gen | ✅ |
        | 🎙️ Voice Input | ✅ |
        | 🔊 Voice Output | ✅ |
        | 📄 PDF Analysis | ✅ |
        | 🖼️ Image Analysis (Gemini) | ✅ |
        | 🎭 Personas | ✅ |
        | 🌓 Dark/Light Theme | ✅ |
        | 📤 Export (TXT/MD/JSON) | ✅ |
        | 🔍 Chat Search | ✅ |
        | 💻 Code Highlighting | ✅ |

        ### 🔗 Live App
        [smart-ai-chatbot-kira.streamlit.app](https://smart-ai-chatbot-kira.streamlit.app)
        """)
    st.divider()
    st.markdown("""
    <div style="text-align:center;padding:1rem;">
        <p style="opacity:0.6;">Built with ❤️ for academic purposes | All APIs on FREE tiers</p>
        <p style="font-size:0.8rem;opacity:0.4;">⚠️ Learning prototype. Verify important info.</p>
    </div>
    """, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────
def main():
    init_session_state()
    inject_custom_css()
    api_key = render_sidebar()

    tab_chat, tab_image, tab_file, tab_about = st.tabs([
        "💬 Chat", "🎨 Image Gen", "📄 File Analysis", "ℹ️ About"
    ])
    with tab_chat:
        if st.session_state.show_welcome and not st.session_state.messages:
            render_welcome()
        render_chat_interface(api_key)
    with tab_image:
        render_image_generation()
    with tab_file:
        render_file_analysis(api_key)
    with tab_about:
        render_about()

if __name__ == "__main__":
    main()