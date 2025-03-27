import requests
import streamlit as st

BACKEND_URL = "http://127.0.0.1:5000"  # Update if deployed

st.title("📖 AI-Powered eBook Reader")

book_id = st.text_input("Enter Project Gutenberg Book ID:", "84")  # Default: Frankenstein
if st.button("Fetch Book"):
    response = requests.post(f"{BACKEND_URL}/fetch", json={"book_id": book_id})
    if response.status_code == 200:
        data = response.json()
        st.session_state["book_text"] = data["text"]
        st.session_state["level"] = data["level"]
        st.write(f"📚 **Original Reading Level:** {data['level']}")
        st.text_area("Original Book Snippet:", data["text"], height=300)

if "book_text" in st.session_state:
    level = st.selectbox("Choose Reading Level:", ["1", "2", "3", "4", "5"])
    if st.button("Rewrite Book"):
        response = requests.post(f"{BACKEND_URL}/simplify", json={
            "text": st.session_state["book_text"],
            "level": level
        })
        if response.status_code == 200:
            st.text_area("Simplified Text:", response.json()["simplifiedText"], height=300)
