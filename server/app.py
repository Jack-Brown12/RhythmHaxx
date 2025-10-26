from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

from algorithms import get_map_path_coordinates

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Enable CORS
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/api/mapify/', methods=['POST'])
def index():
    # Get the JSON data from the request
    form = request.get_json()

    # Store info
    points = form["points"]

    coordinates = get_map_path_coordinates(points)

    return jsonify(coordinates)


if __name__ == '__main__':
    app.run(debug=True)
