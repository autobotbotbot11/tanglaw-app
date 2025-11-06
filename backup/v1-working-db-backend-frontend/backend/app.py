from flask import Flask, send_from_directory
from flask_cors import CORS
from db_config import get_db_connection
from routes import routes

app = Flask(__name__)
CORS(app)


app.register_blueprint(routes)

# serve frontend for quick testing
@app.route('/')
def serve_index():
    return send_from_directory('../frontend', 'index.html')

if __name__ == '__main__':
    app.run(debug=True)
