import streamlit as st
import requests
import time

# Configure app
st.set_page_config(
    page_title="BookAlchemist Pro",
    page_icon="✨",
    layout="centered"
)

# Constants
CHUNK_SIZE = 2000  # Characters per page
OVERLAP = 200      # For smooth transitions

# Initialize session state
if 'book_text' not in st.session_state:
    st.session_state.book_text = ""
if 'current_pos' not in st.session_state:
    st.session_state.current_pos = 0
if 'rewritten_pages' not in st.session_state:
    st.session_state.rewritten_pages = []

def load_book(book_id):
    """Fetch book text from Project Gutenberg"""
    try:
        url = f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Clean text
        text = response.text
        start_markers = ["*** START OF", "CHAPTER 1", "BOOK FIRST"]
        for marker in start_markers:
            if marker in text:
                text = text.split(marker)[-1]
        return text[:10000]  # Limit to first 10,000 chars for demo
    except Exception as e:
        st.error(f"❌ Error loading book: {str(e)}")
        return None

def rewrite_with_ai(text, level):
    """Try multiple free AI services with fallbacks"""
    services = [
        {
            "name": "Fireworks AI",
            "url": "https://api.fireworks.ai/inference/v1/completions",
            "payload": {
                "model": "accounts/fireworks/models/mistral-7b",
                "prompt": f"Rewrite this for a {level}/5 reading level:\n{text}",
                "max_tokens": 800,
                "temperature": 0.7
            },
            "headers": {
                "Authorization": "Bearer free-trial",
                "Content-Type": "application/json"
            },
            "response_path": ["choices", 0, "text"]
        },
        {
            "name": "OpenRouter (Mistral)",
            "url": "https://openrouter.ai/api/v1/chat/completions",
            "payload": {
                "model": "mistralai/mistral-7b-instruct:free",
                "messages": [{
                    "role": "user",
                    "content": f"Rewrite this for a {level}/5 reading level:\n{text}"
                }]
            },
            "headers": {
                "Authorization": "Bearer sk-or-v1-5d9f9c8d3d8e6b8e5e6b8e5e6b8e5e6b8e5e6b8e5e6b8e5e6b8e5e6b8e5e6b8e5",
                "Content-Type": "application/json"
            },
            "response_path": ["choices", 0, "message", "content"]
        }
    ]

    for service in services:
        try:
            response = requests.post(
                service["url"],
                json=service["payload"],
                headers=service["headers"],
                timeout=25
            )
            data = response.json()
            
            # Navigate through response path
            result = data
            for key in service["response_path"]:
                result = result[key]
            
            if result and len(result) > 10:  # Minimum length check
                return result
        except:
            continue
    
    return f"⚠️ All AI services failed. Here's the original text:\n\n{text}"

# UI
st.title("✨ BookAlchemist Pro")
st.caption("Pure AI-powered book rewriting")

book_id = st.text_input(
    "Enter Project Gutenberg Book ID:",
    value="84"  # Default to Frankenstein
)

level = st.select_slider(
    "Reading Level",
    options=[1, 2, 3, 4, 5],
    value=3
)

if st.button("🔮 Rewrite Book"):
    if not book_id.isdigit():
        st.error("Please enter a valid numeric book ID")
        st.stop()
    
    with st.spinner("📖 Downloading book..."):
        st.session_state.book_text = load_book(book_id)
        st.session_state.current_pos = 0
        st.session_state.rewritten_pages = []
    
    if st.session_state.book_text:
        with st.spinner("🧠 Rewriting with AI..."):
            start_pos = 0
            end_pos = CHUNK_SIZE
            while start_pos < len(st.session_state.book_text):
                chunk = st.session_state.book_text[start_pos:end_pos]
                rewritten = rewrite_with_ai(chunk, level)
                st.session_state.rewritten_pages.append(rewritten)
                start_pos = end_pos
                end_pos += CHUNK_SIZE

if st.session_state.rewritten_pages:
    page_num = st.session_state.current_pos // CHUNK_SIZE
    st.write(st.session_state.rewritten_pages[page_num])
    
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.current_pos > 0 and st.button("⬅️ Previous"):
            st.session_state.current_pos = max(0, st.session_state.current_pos - CHUNK_SIZE)
            st.rerun()
    with col2:
        if st.session_state.current_pos + CHUNK_SIZE < len(st.session_state.book_text) and st.button("➡️ Next"):
            st.session_state.current_pos += CHUNK_SIZE
            st.rerun()
    
    progress = min(100, (st.session_state.current_pos / len(st.session_state.book_text)) * 100)
    st.progress(int(progress))

st.markdown("---")
st.caption("Find books at [Project Gutenberg](https://www.gutenberg.org)")
