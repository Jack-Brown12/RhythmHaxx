from flask import Flask, render_template, jsonify, request
from algorithms import get_map_path_coordinates


app = Flask(__name__)


@app.route('/api/', methods=['POST'])
def index():
        # Get the JSON data from the request
        form = request.get_json()

        # Store info
        starting_point = form["starting_point"]
        scale = form["scaling_factor"]
        points = form["points"]

        coordinates = get_map_path_coordinates(starting_point, scale, points)

        return jsonify(coordinates)


if __name__ == '__main__':
    app.run(debug=True)
   