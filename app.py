import streamlit as st
import requests
import time

# Configure app
st.set_page_config(
    page_title="Infinite Book Alchemist",
    page_icon="📖",
    layout="centered"
)

# Constants
AI_API = "https://api.fireworks.ai/inference/v1/completions"
CHUNK_SIZE = 2000
OVERLAP = 200

# Initialize session state
if 'book_text' not in st.session_state:
    st.session_state.book_text = ""
if 'current_pos' not in st.session_state:
    st.session_state.current_pos = 0
if 'rewritten_pages' not in st.session_state:
    st.session_state.rewritten_pages = []

def load_book(book_id):
    try:
        url = f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        text = response.text
        start_markers = ["*** START OF", "CHAPTER 1", "BOOK FIRST"]
        for marker in start_markers:
            if marker in text:
                text = text.split(marker)[-1]
        return text
    except Exception as e:
        st.error(f"Error loading book: {str(e)}")
        return None

def rewrite_chunk(text, level):
    try:
        prompt = f"""Rewrite this for a {level}/5 reading level:
        - Level 1: Simple words, short sentences
        - Level 3: Clear but detailed
        - Level 5: Original complexity\n\n{text}"""
        
        response = requests.post(
            AI_API,
            json={
                "model": "accounts/fireworks/models/mistral-7b",
                "prompt": prompt,
                "max_tokens": 1000,
                "temperature": 0.5 + (level * 0.1)
            },
            headers={
                "Authorization": "Bearer free-trial",
                "Content-Type": "application/json"
            },
            timeout=25
        )
        
        # Robust response handling
        data = response.json()
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0].get("text", "No text in response")
        return "Error: Unexpected API response format"
    except Exception as e:
        return f"AI Error: {str(e)}"

# UI
st.title("📖 Infinite Book Alchemist")
st.caption("AI-powered full-book rewriting")

book_id = st.text_input(
    "Enter Project Gutenberg Book ID:", 
    value="84"
)

level = st.select_slider(
    "Reading Level",
    options=[1, 2, 3, 4, 5],
    value=3
)

if st.button("🔮 Load Book"):
    with st.spinner("Downloading book..."):
        st.session_state.book_text = load_book(book_id)
        st.session_state.current_pos = 0
        st.session_state.rewritten_pages = []
        st.rerun()

if st.session_state.book_text:
    start_pos = max(0, st.session_state.current_pos - OVERLAP)
    end_pos = st.session_state.current_pos + CHUNK_SIZE
    current_chunk = st.session_state.book_text[start_pos:end_pos]
    
    if len(st.session_state.rewritten_pages) <= st.session_state.current_pos // CHUNK_SIZE:
        with st.spinner(f"Rewriting page {len(st.session_state.rewritten_pages)+1}..."):
            rewritten = rewrite_chunk(current_chunk, level)
            st.session_state.rewritten_pages.append(rewritten)
    
    st.write(st.session_state.rewritten_pages[-1])
    
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.current_pos > 0 and st.button("⬅️ Previous Page"):
            st.session_state.current_pos = max(0, st.session_state.current_pos - CHUNK_SIZE)
            st.rerun()
    with col2:
        if st.session_state.current_pos + CHUNK_SIZE < len(st.session_state.book_text):
            if st.button("➡️ Next Page"):
                st.session_state.current_pos += CHUNK_SIZE
                st.rerun()
        else:
            st.write("🎉 End of book")

    progress = min(100, (st.session_state.current_pos / len(st.session_state.book_text)) * 100)
    st.progress(int(progress))

st.markdown("---")
st.caption("Find more books at [Project Gutenberg](https://www.gutenberg.org)")
