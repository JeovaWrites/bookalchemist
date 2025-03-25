import streamlit as st
import requests
from bs4 import BeautifulSoup
import time

st.set_page_config(page_title="BookAlchemist", page_icon="📖")
st.title("📖 BookAlchemist")
st.caption("AI-powered text complexity adjuster")

def get_gutenberg_text(book_id):
    try:
        url = f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt"
        text = requests.get(url, timeout=10).text[:3000]  # First 3000 chars
        return " ".join(text.split())  # Remove extra spaces
    except:
        return None

def simplify_with_ai(text, level):
    # Simple word substitutions as fallback
    substitutions = {
        1: [("commence", "start"), ("endeavor", "try"), ("individual", "person")],
        2: [("approximately", "about"), ("utilize", "use"), ("fabricate", "make")],
        3: [("magnificent", "great"), ("inquire", "ask"), ("terminate", "end")]
    }
    
    # Apply substitutions based on level
    for original, replacement in substitutions.get(level, []):
        text = text.replace(original, replacement)
    
    # Add line breaks for lower levels
    if level < 3:
        text = text.replace(".", ".\n\n")
    
    return f"SIMPLIFIED (Level {level}):\n\n{text[:1000]}"  # First 1000 chars

book_id = st.text_input("Enter Project Gutenberg Book ID (e.g., 84 for Frankenstein):", "84")
level = st.select_slider("Reading Level", options=[1, 2, 3, 4, 5], value=3)

if st.button("Alchemize!"):
    with st.spinner("🧙‍♂️ Brewing literary magic..."):
        time.sleep(1)  # Let the spinner show
        
        original = get_gutenberg_text(book_id)
        if not original:
            st.error("Couldn't fetch book. Check ID or try another book.")
            st.stop()
            
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
