import requests, os
from functools import wraps
from firebase_admin import auth
from google.cloud import firestore
from flask import Blueprint, request, jsonify

db = firestore.Client()

admin_bp = Blueprint('admin_bp', __name__)
order_bp = Blueprint('order_bp', __name__)
cartype_bp = Blueprint('cartype_bp', __name__)
os.getenv('SAMPLE_ENV_VAR')

stripe_api_key = os.getenv('STRIPE_API_KEY')
endpoint_secret = os.getenv('ENDPOINT_SECRET')
RECAPTCHA_SECRET_KEY = os.getenv('RECAPTCHA_SECRET_KEY')
gcloud_client_id = os.getenv('GCLOUD_CLIENT_ID')


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

