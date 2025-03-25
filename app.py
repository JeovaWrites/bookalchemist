import streamlit as st
import requests
import re
import time

# Configure app
st.set_page_config(
    page_title="BookAlchemist Pro",
    page_icon="✨",
    layout="centered"
)

# --- Constants ---
MISTRAL_API = "https://api.fireworks.ai/inference/v1/completions"
MAX_TEXT_LENGTH = 20000  # Characters to process

# --- UI ---
st.title("✨ BookAlchemist Pro")
st.caption("AI-powered text complexity adjustment")

with st.expander("ℹ️ How to use"):
    st.markdown("""
    1. Enter a Project Gutenberg book ID (e.g., `84` for Frankenstein)
    2. Choose reading level (1 = Simplest, 5 = Original)
    3. Click **Alchemize!**
    Find more books at [gutenberg.org](https://www.gutenberg.org)
    """)

# --- Core Functions ---
def clean_gutenberg_text(text):
    """Remove Gutenberg headers/footers and formatting"""
    # Remove metadata headers
    start_patterns = [
        r"\*\*\*.*?START OF.*?\*\*\*",
        r"CHAPTER [1IVX]+",
        r"BOOK [1IVX]+"
    ]
    for pattern in start_patterns:
        text = re.split(pattern, text, flags=re.IGNORECASE)[-1]
    
    # Remove footers/illustrations
    text = re.sub(r"\[Illustration:.*?\]", "", text)
    text = re.sub(r"_{2,}.*?_{2,}", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)  # Reduce excessive newlines
    return text.strip()

def try_ai_enhancement(text, level):
    """Use Mistral 7B AI for high-quality rewriting"""
    try:
        prompt = f"""Rewrite this text for a {level}/5 reading level:
        - Level 1: Elementary school (short sentences, simple words)
        - Level 3: High school (clear but detailed)
        - Level 5: Original text (no changes)\n\n{text[:MAX_TEXT_LENGTH]}"""

        response = requests.post(
            MISTRAL_API,
            json={
                "model": "accounts/fireworks/models/mistral-7b",
                "prompt": prompt,
                "max_tokens": 1000,
                "temperature": 0.4 + (level * 0.1)  # More creative for higher levels
            },
            headers={
                "Authorization": "Bearer free-trial",
                "Accept": "application/json"
            },
            timeout=20
        )
        return response.json()["choices"][0]["text"]
    except Exception as e:
        print(f"AI Error: {str(e)}")
        return None

def simplify_with_rules(text, level):
    """Rule-based fallback system"""
    substitutions = {
        1: [("commenced", "started"), ("endeavoured", "tried"), 
            ("exclaimed", "said"), ("approximately", "about")],
        2: [("individual", "person"), ("fabricate", "make"), 
            ("magnificent", "great"), ("inquire", "ask")],
        3: [("consequently", "so"), ("terminate", "end"), 
            ("utilize", "use"), ("ascertain", "find out")]
    }
    
    # Apply substitutions
    for original, replacement in substitutions.get(level, []):
        text = text.replace(original, replacement)
    
    # Adjust sentence length
    if level < 3:
        sentences = re.split(r'(?<=[.!?]) +', text)
        text = ". ".join([s.capitalize() for s in sentences if len(s.split()) <= 12])
    
    return text

def get_book_content(book_id):
    """Fetch and clean text from Project Gutenberg"""
    try:
        url = f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return clean_gutenberg_text(response.text[:MAX_TEXT_LENGTH])
    except Exception as e:
        st.error(f"Error fetching book: {str(e)}")
        return None

# --- Main UI ---
book_id = st.text_input(
    "Enter Project Gutenberg Book ID:", 
    placeholder="e.g., 84 for Frankenstein, 1342 for Pride & Prejudice",
    value="84"
)

level = st.select_slider(
    "Reading Level",
    options=[1, 2, 3, 4, 5],
    value=3,
    help="1 = Simplest (Grade School), 5 = Original Text"
)

if st.button("✨ Alchemize!", type="primary"):
    if not book_id.isdigit():
        st.error("Please enter a valid numeric book ID")
        st.stop()
    
    with st.spinner("🔮 Brewing literary magic..."):
        start_time = time.time()
        
        # Step 1: Fetch book content
        original_text = get_book_content(book_id)
        if not original_text:
            st.stop()
        
        # Step 2: Try AI enhancement first
        ai_result = try_ai_enhancement(original_text, level)
        
        # Step 3: Fallback if AI fails
        if ai_result:
            result = f"🧠 AI-Enhanced (Level {level}):\n\n{ai_result}"
            method = "AI"
        else:
            result = f"📖 Simplified (Level {level}):\n\n{simplify_with_rules(original_text, level)}"
            method = "Rule-Based"
        
        # Display results
        st.divider()
        st.subheader("Original Preview")
        st.text(original_text[:500] + "...")
        
        st.subheader("Result")
        st.write(result)
        
        st.caption(f"Processed with {method} in {time.time()-start_time:.1f}s")
        
        # Download button
        st.download_button(
            "📥 Download Result",
            result,
            file_name=f"book_level_{level}.txt"
        )

# Footer
st.markdown("---")
st.markdown("""
<style>
footer {visibility: hidden;}
.st-emotion-cache-cio0dv {padding: 1rem;}
</style>
""", unsafe_allow_html=True)
