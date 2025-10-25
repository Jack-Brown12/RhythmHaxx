from flask import Flask, jsonify, request
from dotenv import load_dotenv
from algorithms import get_map_path_coordinates
from flask_cors import CORS, cross_origin

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Enable CORS
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/api/', methods=['POST'])
def index():
        # Get the JSON data from the request
        form = request.get_json()

        # Store info
        starting_point = form["starting_point"]
        scale = form["scaling_factor"]
        points = form["points"]

        coordinates = get_map_path_coordinates(starting_point, scale, points, use_MAPBOX=True)

        return jsonify(coordinates)


if __name__ == '__main__':
    app.run(debug=True)
   