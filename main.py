from models import *
import functions_framework
from models.helper import route, jsonify

@functions_framework.http
def carwash(request):
    if request.method == 'OPTIONS':
        response = jsonify({"message": "Preflight OK"})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response, 200
    for func in globals().values():
        if callable(func) and hasattr(func, '_route_path'):
            if func._route_path == request.path and ('*' in func._route_methods or request.method in func._route_methods):
                response = func(request)
                if isinstance(response, tuple):
                    content, status_code = response
                    response = content
                else:
                    status_code = 200
                response.headers['Access-Control-Allow-Origin'] = '*'
                response.headers['Access-Control-Allow-Methods'] = '*'
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
                return response, status_code
    response = jsonify({"message": "This is a test mode. Below are the available routes:", "routes": [{"path": "/cartype", "method": "POST", "description": "Create a new car type."}, {"path": "/cartype", "method": "GET", "description": "Retrieve all car types."}, {"path": "/cartype", "method": "PUT", "description": "Update a car type."}, {"path": "/cartype", "method": "DELETE", "description": "Delete a car type."}, {"path": "/order", "method": "POST", "description": "Create a new order."}, {"path": "/orders", "method": "GET", "description": "Retrieve all orders."}, {"path": "/payment/verify", "method": "POST", "description": "Verify payment status."}]})
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response, 404

