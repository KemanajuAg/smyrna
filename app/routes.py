import os
import json
import urllib.request
from flask import Blueprint, render_template, request, jsonify

main = Blueprint("main", __name__)

@main.route("/")
def home():
    return render_template("home.html")

@main.route("/blog")
def blog():
    return render_template("blog.html")

@main.route("/api/generate", methods=["POST"])
def generate():
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return jsonify({"error": "API key not configured"}), 500

    data = request.get_json()
    topic = data.get("topic", "")
    lang = data.get("lang", "English")

    payload = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 1000,
        "system": f"You are a passionate historian and writer for 'Smyrna', a blog about Ancient Anatolia and Greek History. Write richly detailed, evocative blog articles in {lang}. Respond ONLY with a raw JSON object (no markdown, no backticks): {{\"title\": \"compelling article title\", \"body\": \"4 rich paragraphs separated by \\n\\n\"}}",
        "messages": [{"role": "user", "content": f"Write a compelling, well-researched blog article about: {topic}"}]
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            text = "".join(b.get("text", "") for b in result.get("content", []))
            clean = text.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(clean)
            return jsonify(parsed)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
