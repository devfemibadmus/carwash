from models import *
import functions_framework
from models.helper import route, jsonify

@functions_framework.http
def carwash(request):
    for func in globals().values():
        if callable(func) and hasattr(func, '_route_path'):
            if func._route_path == request.path and request.method in func._route_methods:
                return func(request)
    return jsonify({"error": "Route not found"}), 404


