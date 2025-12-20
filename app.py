import os
import time
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

ANSWERS = [
    "DTCLV",
    "159",
    "98",
    "TQRG",
    "Sunday",
    "Maggi",
    "Ottawa",
    "Modi & Putin",
    "Battery",
    "147",
    "YA",
    "34",
    "32U65"
]

GEMINI_KEYS = [
    os.environ.get("GEMINI_API_KEY"),
    os.environ.get("GEMINI_API_KEY_2")
]

MODEL = "gemini-2.5-flash"

def gemini_url(key):
    return f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={key}"

def validate_with_gemini(correct, user):
    prompt = f'''
Respond ONLY with YES or NO.

Correct Answer: "{correct}"
User Answer: "{user}"
'''

    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    for key in GEMINI_KEYS:
        if not key:
            continue
        try:
            r = requests.post(
                gemini_url(key),
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            if r.status_code == 429:
                time.sleep(2)
                continue
            r.raise_for_status()
            text = r.json()["candidates"][0]["content"]["parts"][0]["text"].lower()
            return text.startswith("yes")
        except:
            continue

    return correct.lower().strip() == user.lower().strip()

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok"})

@app.route("/check_answer", methods=["POST"])
def check_answer():
    data = request.get_json()
    meth = None
    qn = int(data.get("questionNumber", 1)) - 1
    if qn < 0 or qn >= len(ANSWERS):
        print({"error": "Invalid question number", "question": qn + 1})
        return jsonify({"correct": False}), 400
    correct = ANSWERS[qn]
    user = data.get("userAnswer", "")

    if user.lower().strip() == correct.lower().strip():
        meth = "default"
        print({
            "question": f"Q{qn+1}",
            "correct": correct,
            "user": user,
            "method": meth,
            "result": True
        })
        return jsonify({"correct": True})
    result = validate_with_gemini(correct, user)
    meth = "gemini"

    print({
        "question": f"Q{qn+1}",
        "correct": correct,
        "user": user,
        "method": meth,
        "result": result
    })
    return jsonify({"correct": result})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
