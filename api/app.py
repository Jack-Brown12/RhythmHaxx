from flask import Flask, jsonify, request, send_from_directory
from algorithms import get_map_path_coordinates,JasonAlgorithm
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__, static_folder='build', static_url_path='')

@app.route('/api/config', methods=['GET'])
def get_config():
    maps_api_key = os.environ.get('PUBLIC_MAPS_API_KEY')

    if not maps_api_key:
        return jsonify({"error": "Maps API key not configured on server."}), 500

    return jsonify({
        "mapsApiKey": maps_api_key
    })


@app.route('/api/mapify', methods=['POST'])
def mapify_route():
    form = request.get_json()
    response = JasonAlgorithm(form["points"])
    return jsonify(response)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


if __name__ == "__main__":
    app.run()
