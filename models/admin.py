from functools import wraps
from .helper import admin_bp
from google.oauth2 import id_token
from .helper import gcloud_client_id
from google.auth.transport import requests
from flask import request, jsonify, session


# Class to manage user sessions
class UserSessionManager:
    active_sessions = {}

    @staticmethod
    def login_user(user_id, session_id):
        if user_id in UserSessionManager.active_sessions:
            old_session_id = UserSessionManager.active_sessions[user_id]
            session.pop(old_session_id, None)
        UserSessionManager.active_sessions[user_id] = session_id

    @staticmethod
    def logout_user(user_id):
        if user_id in UserSessionManager.active_sessions:
            session_id = UserSessionManager.active_sessions.pop(user_id)
            session.pop(session_id, None)

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = session.get('token')
        if not token:
            return jsonify({'status': 'failure', 'message': 'Admin login required'}), 403
        try:
            idinfo = id_token.verify_oauth2_token(token, requests.Request())
        except ValueError:
            return jsonify({'status': 'failure', 'message': 'Invalid Google token'}), 400
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/admin/google', methods=['POST'])
def google_auth():
    data = request.get_json()
    token = data.get('token')
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), gcloud_client_id)
        user_id = idinfo['sub']
        UserSessionManager.login_user(user_id, session.sid)
        session['user_id'] = user_id
        session['token'] = token
        return jsonify({'status': 'success', 'message': 'User authenticated'})
    except ValueError:
        return jsonify({'status': 'failure', 'message': 'Invalid Google token'}), 400

@admin_bp.route('/admin/logout', methods=['POST'])
def logout():
    user_id = session.get('user_id')
    if user_id:
        UserSessionManager.logout_user(user_id)
        session.clear()
        return jsonify({'status': 'success', 'message': 'User logged out'})
    return jsonify({'status': 'failure', 'message': 'User not logged in'}), 400

@admin_bp.route('/admin/check', methods=['GET'])
def check_login():
    if 'user_id' in session:
        return jsonify({'status': 'success', 'message': 'Yes, you are logged in'}), 200
    else:
        return jsonify({'status': 'failure', 'message': 'No, you are not logged in'}), 401
