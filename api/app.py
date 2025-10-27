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

@app.route('/api/mapify', methods=['POST'])
def mapify_route():
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
