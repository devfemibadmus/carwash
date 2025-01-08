from datetime import datetime
from flask import Flask, request, jsonify
from models import cartype_bp, order_bp, admin_bp, db

app = Flask(__name__)
app.register_blueprint(order_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(cartype_bp)

@app.after_request
def after_request_func(response):
    response.headers.add('Access-Control-Allow-Origin', '*')  # Allow all origins
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, x-csrf-token')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, PATCH, DELETE')
    return response

@app.route('/<path:invalid_path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def catch_all(invalid_path):
    return jsonify({"error": "404 Not Found"}), 404

if __name__ == '__main__':
    app.run(debug=True)

application = app