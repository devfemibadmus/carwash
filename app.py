from datetime import datetime
from flask import Flask, request, jsonify
from models import cartype_bp, order_bp, admin_bp, db

from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["*","null"])
app.register_blueprint(cartype_bp)
app.register_blueprint(order_bp)
app.register_blueprint(admin_bp)

@app.route('/<path:invalid_path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def catch_all(invalid_path):
    return jsonify({"error": "404 Not Found"}), 404

if __name__ == '__main__':
    app.run(debug=True)

