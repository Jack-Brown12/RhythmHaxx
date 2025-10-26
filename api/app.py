from flask import Flask, jsonify, request
from algorithms import get_map_path_coordinates
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route('/api/mapify', methods=['POST'])
def mapify_route():
    form = request.get_json()

    response = get_map_path_coordinates(form["points"])

    return jsonify(response)
