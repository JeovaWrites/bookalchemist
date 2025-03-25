import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="BookAlchemist", page_icon="📖")
st.title("📖 BookAlchemist")
st.caption("AI-powered text complexity adjuster")

def get_gutenberg_text(book_id):
    url = f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt"
    return requests.get(url).text[:3000]  # First 3000 chars for demo

def simplify_with_ai(text, level):
    # Poe.com free API endpoint (no key needed)
    response = requests.post(
        "https://poe.com/api/gpt_rewrite",
        json={"text": text, "level": level}
    )
    return response.json().get("output", "Error: Try again later")

book_id = st.text_input("Enter Project Gutenberg Book ID (e.g., 84 for Frankenstein):")
level = st.select_slider("Reading Level", options=[1, 2, 3, 4, 5])

if st.button("Alchemize!"):
    with st.spinner("Rewriting magic in progress..."):
        original = get_gutenberg_text(book_id)
        simplified = simplify_with_ai(original, level)
        
        st.divider()
        st.subheader(f"Level {level} Version")
        st.write(simplified)
        
        st.download_button(
            "Download Simplified Text",
            simplified,
            file_name=f"book_level_{level}.txt"
        )

st.markdown("> Find more books at [Project Gutenberg](https://www.gutenberg.org/)")
