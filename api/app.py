import os

from dotenv import load_dotenv

from flask import Flask, jsonify, request
from flask_cors import CORS

from time import time

from algorithms import JasonAlgorithm


load_dotenv()

app = Flask(__name__, static_folder='build', static_url_path='')

origins = [o.strip() for o in os.getenv("FRONTEND_ORIGINS", "").split(",") if o.strip()]
CORS(app, resources={r"/api/*": {"origins": origins}})

rate_limits = {}
MAX_REQUESTS = 10
TIME_WINDOW = 60

def is_rate_limited(ip: str) -> bool:
    now = time()
    window = rate_limits.get(ip, [])

    window = [t for t in window if now - t < TIME_WINDOW]
    if len(window) >= MAX_REQUESTS:
        rate_limits[ip] = window
        return True
    
    window.append(now)
    rate_limits[ip] = window
    return False

@app.route('/api/mapify', methods=['POST'])
def mapify_route():
    ip = request.remote_addr or "unknown"
    if not is_rate_limited(ip):
        return jsonify({
            "error": "Too many requests",
            "message": f"Rate limit exceeded (max {MAX_REQUESTS}/minute)"
        }), 429
    
    if not request.is_json:
        return jsonify({
            "error": "Invalid request",
            "message": "Expected JSON payload"
        }), 400

    form = request.get_json(silent=True) or {}

    if form.get("points") is None:
        return jsonify({
            "error": "Invalid request",
            "message": "Missing 'points' in request data"
        }), 400

    response = JasonAlgorithm(form["points"])
    return jsonify(response)


if __name__ == "__main__":
    app.run()
