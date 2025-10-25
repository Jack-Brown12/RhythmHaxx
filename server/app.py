from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

@app.route('/api/', methods=['POST'])
def index():
        form = request.get_json()
        form_key = form["sigma"]
        print(form_key)
        blah = {"key": "value"}
        return jsonify(blah)
#blah["key"]


if __name__ == '__main__':
    app.run(debug=True)

   