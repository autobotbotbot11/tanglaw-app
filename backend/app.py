# app.py
from flask import Flask, send_from_directory
from flask_cors import CORS
from routes import api

app = Flask(__name__, static_folder="../frontend", static_url_path="/")
CORS(app)

# register API blueprint
app.register_blueprint(api)

# serve frontend files for quick manual testing
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def static_proxy(path):
    # serve other frontend files
    return send_from_directory(app.static_folder, path)

if __name__ == "__main__":
    # debug True for development only
    app.run(host="0.0.0.0", port=5000, debug=True)
