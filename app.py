import os
from dotenv import load_dotenv
import requests
import time
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# Load .env file if it exists (will not override existing env vars)
load_dotenv()

app = Flask(__name__, template_folder='templates')
CORS(app)

# Answers list to match the frontend
ANSWERS = [
    "TQRG",
    "Sunday",
    "Maggi",
    "Ottawa",
    "modi and putin",
    "Battery",
    "map",
    "future",
    "age",
    "cold",
    "needle",
    "hole",
    "stamp",
    "rubber band"
]

# Retrieve Gemini API key from environment variable or .env file
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

# Rate limiting configuration
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds between retries
RATE_LIMIT_DELAY = 60  # seconds to wait after hitting rate limit

def validate_answer_with_gemini(correct_answer, user_answer):
    """
    Use Gemini API to validate the answer with more flexibility
    Implements retry and rate limit handling
    """
    if not GEMINI_API_KEY:
        # Fallback to simple validation if no API key
        return correct_answer.lower().strip() == user_answer.lower().strip()

    prompt = f'''
You are an answer validator. Compare the correct answer and the user answer.
Determine if the user's answer is essentially correct, allowing for:
- Slight spelling variations
- Plural/singular forms
- Minor grammatical differences
- Close semantic matches

Respond ONLY with YES or NO.

Correct Answer: "{correct_answer}"
User Answer: "{user_answer}"

Guidelines:
- Be lenient with minor variations
- Consider semantic similarity
- If the meaning is essentially the same, respond YES
'''

    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    for attempt in range(MAX_RETRIES):
        try:
            # Make request to Gemini API
            resp = requests.post(
                GEMINI_API_URL, 
                json=payload, 
                headers={"Content-Type": "application/json"}
            )

            # Handle specific HTTP status codes
            if resp.status_code == 429:
                # Rate limit hit
                print(f"Rate limit reached. Waiting {RATE_LIMIT_DELAY} seconds.")
                time.sleep(RATE_LIMIT_DELAY)
                continue
            
            resp.raise_for_status()
            
            # Extract and process Gemini's response
            gemini_data = resp.json()
            text = gemini_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip().lower()
            
            # Check if the response starts with "yes"
            return text == "yes" or text.startswith("yes")
        
        except requests.exceptions.RequestException as e:
            # Log the error
            print(f"Gemini API error (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            
            # Wait before retrying
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            else:
                # Fallback to simple validation if all retries fail
                print("All Gemini API attempts failed. Falling back to simple validation.")
                return correct_answer.lower().strip() == user_answer.lower().strip()

    # Fallback if all attempts fail
    return correct_answer.lower().strip() == user_answer.lower().strip()
@app.route("/")
def home():
    return render_template("index.html")
@app.route("/check_answer", methods=["POST"])
def check_answer():
    data = request.get_json()
    correct_answer = data.get("correctAnswer", "")
    user_answer = data.get("userAnswer", "")
    
    # Get the question number from the request, defaulting to 1 if not provided
    question_number = data.get("questionNumber", 1)
    
    try:
        # Adjust for 0-based indexing
        question_index = int(question_number) - 1
        
        # Validate question index is within range
        if question_index < 0 or question_index >= len(ANSWERS):
            return jsonify({"correct": False, "error": "Invalid question number"}), 400
        
        # Verify the correct answer matches the expected answer for this question
        expected_answer = ANSWERS[question_index]
        if correct_answer.lower().strip() != expected_answer:
            return jsonify({"correct": False, "error": "Incorrect answer for this question"}), 400
        
        # Validate the user's answer using Gemini
        is_correct = validate_answer_with_gemini(correct_answer, user_answer)
        
        return jsonify({"correct": is_correct})
    except (ValueError, TypeError):
        return jsonify({"correct": False, "error": "Invalid question number"}), 400

# Modify to use environment variable for port
if __name__ == "__main__":
    # Check if API key is set
    if not GEMINI_API_KEY:
        print("WARNING: GEMINI_API_KEY is not set. Answer validation will be basic.")
    
    # Use PORT environment variable if set, otherwise default to 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
    