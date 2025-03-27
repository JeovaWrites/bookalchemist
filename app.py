import requests
import openai
from flask import Flask, request, jsonify

app = Flask(__name__)

# Set your OpenAI API key
openai.api_key = "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
"

# Function to fetch book from Project Gutenberg
def fetch_book(book_id):
    url = f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt"
    response = requests.get(url)
    return response.text if response.status_code == 200 else "Error fetching book"

# Function to estimate reading level
def analyze_reading_level(text):
    prompt = f"Analyze this text and classify its difficulty (1 to 5):\n\n{text[:1000]}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"].strip()

# Function to simplify text
def simplify_text(text, level):
    prompt = f"Rewrite the following text for reading level {level}:\n\n{text[:1000]}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"].strip()

@app.route('/fetch', methods=['POST'])
def fetch():
    data = request.json
    book_id = data["book_id"]
    text = fetch_book(book_id)
    level = analyze_reading_level(text)
    return jsonify({"text": text[:5000], "level": level})  # Sending a snippet for preview

@app.route('/simplify', methods=['POST'])
def simplify():
    data = request.json
    simplified_text = simplify_text(data["text"], data["level"])
    return jsonify({"simplifiedText": simplified_text})

if __name__ == '__main__':
    app.run(debug=True)
