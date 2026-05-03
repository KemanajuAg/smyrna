import os
import json
import urllib.request
from flask import Blueprint, render_template, request, jsonify, send_from_directory

main = Blueprint("main", __name__, static_folder="static", static_url_path="/static")

@main.route("/")
def home():
    return render_template("home.html")

@main.route("/blog")
def blog():
    return render_template("blog.html")

@main.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(os.path.join(os.path.dirname(__file__), 'static'), filename)

@main.route("/api/generate", methods=["POST"])
def generate():
    try:
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            return jsonify({"error": "NO API KEY FOUND"}), 500

        data = request.get_json()
        topic = data.get("topic", "")
        lang = data.get("lang", "English")

        system_prompt = "You are a historian. Write a blog article in " + lang + ". Respond ONLY with raw JSON: {\"title\": \"title here\", \"body\": \"4 paragraphs separated by two newlines\"}"

        payload = json.dumps({
            "model": "claude-sonnet-4-5",
            "max_tokens": 1000,
            "system": system_prompt,
            "messages": [{"role": "user", "content": "Write about: " + topic}]
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

        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            text = "".join(b.get("text", "") for b in result.get("content", []))
            clean = text.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(clean)
            return jsonify(parsed)

    except Exception as e:
        return jsonify({"error": "DETAIL: " + str(e)}), 500
