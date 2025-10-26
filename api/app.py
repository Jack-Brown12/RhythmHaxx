from flask import Flask, jsonify, request, send_from_directory
from algorithms import get_map_path_coordinates
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__, static_folder='build', static_url_path='')

@app.route('/api/mapify', methods=['POST'])
def mapify_route():
    form = request.get_json()
    response = get_map_path_coordinates(form["points"])
    return jsonify(response)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')
