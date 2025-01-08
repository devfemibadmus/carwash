from functools import wraps
from firebase_admin import auth
import requests, os, json, uuid
from google.cloud import firestore
from datetime import datetime, timedelta
from flask import jsonify

db = firestore.Client()

stripe_api_key = os.getenv('STRIPE_API_KEY')
endpoint_secret = os.getenv('ENDPOINT_SECRET')
RECAPTCHA_SECRET_KEY = os.getenv('RECAPTCHA_SECRET_KEY')
gcloud_client_id = os.getenv('GCLOUD_CLIENT_ID')

def route(path, methods=['GET']):
    def decorator(f):
        f._route_path = path
        f._route_methods = methods
        def wrapper(request, *args, **kwargs):
            response = f(request, *args, **kwargs)
            if isinstance(response, tuple):
                content, status_code = response
                response = content
            else:
                status_code = 200
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
            return response, status_code
        return wrapper
    return decorator

def validate_recaptcha(action_name):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            recaptcha_token = request.json.get('recaptcha_token')
            if not recaptcha_token:
                return jsonify({"error": "Recaptcha token is missing"}), 400
            response = requests.post(
                f"https://recaptchaenterprise.googleapis.com/v1/projects/dev-femi-badmus/assessments?key={RECAPTCHA_SECRET_KEY}",
                json={
                    "event": {
                        "token": recaptcha_token,
                        "expectedAction": action_name,
                        "siteKey": "6LcqVbEqAAAAAH1KgZju7V7Vzexy9e2zSm69MMh4"
                    }
                }
            )
            result = response.json()
            if response.status_code != 200 or not result.get("tokenProperties", {}).get("valid", False) or result.get("tokenProperties", {}).get("action") != action_name or result.get("riskAnalysis", {}).get("score", 0) < 0.5:
                return jsonify({"error": "Recaptcha validation failed"}), 403
            return f(*args, **kwargs)
        return wrapped
    return decorator

class CustomSession:
    def __init__(self):
        self.sessions = {}

    def _generate_session_id(self):
        return str(uuid.uuid4())

    def create_session(self, data, expires_in=3600):
        session_id = self._generate_session_id()
        expiration_time = datetime.utcnow() + timedelta(seconds=expires_in)
        self.sessions[session_id] = {
            'data': data,
            'expires_at': expiration_time
        }
        return session_id

    def get_session(self, session_id):
        session = self.sessions.get(session_id)
        if session and session['expires_at'] > datetime.utcnow():
            return session['data']
        return None

    def delete_session(self, session_id):
        if session_id in self.sessions:
            del self.sessions[session_id]

    def is_session_valid(self, session_id):
        session = self.sessions.get(session_id)
        return session and session['expires_at'] > datetime.utcnow()

