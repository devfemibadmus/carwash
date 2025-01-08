from functools import wraps
from google.oauth2 import id_token
from .helper import gcloud_client_id, jsonify, CustomSession, route
from google.auth.transport import requests

session_manager = CustomSession()

class UserSessionManager:
    active_sessions = {}

    @staticmethod
    def login_user(user_id, session_id):
        if user_id in UserSessionManager.active_sessions:
            old_session_id = UserSessionManager.active_sessions[user_id]
            session_manager.delete_session(old_session_id)
        UserSessionManager.active_sessions[user_id] = session_id

    @staticmethod
    def logout_user(user_id):
        if user_id in UserSessionManager.active_sessions:
            session_id = UserSessionManager.active_sessions.pop(user_id)
            session_manager.delete_session(session_id)

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_data = session_manager.get_session(session.sid)
        if not session_data or 'token' not in session_data:
            return jsonify({'status': 'failure', 'message': 'Admin login required'}), 403
        token = session_data['token']
        try:
            idinfo = id_token.verify_oauth2_token(token, requests.Request())
        except ValueError:
            return jsonify({'status': 'failure', 'message': 'Invalid Google token'}), 400
        return f(*args, **kwargs)
    return decorated_function

@route('/admin/google', methods=['POST'])
def google_auth(request):
    data = request.get_json()
    token = data.get('token')
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), gcloud_client_id)
        user_id = idinfo['sub']
        session_id = session_manager.create_session({'user_id': user_id, 'token': token})
        UserSessionManager.login_user(user_id, session_id)
        return jsonify({'status': 'success', 'message': 'User authenticated'})
    except ValueError:
        return jsonify({'status': 'failure', 'message': 'Invalid Google token'}), 400

@route('/admin/logout', methods=['POST'])
def logout(request):
    session_data = session_manager.get_session(session.sid)
    if session_data and 'user_id' in session_data:
        user_id = session_data['user_id']
        UserSessionManager.logout_user(user_id)
        session_manager.delete_session(session.sid)
        return jsonify({'status': 'success', 'message': 'User logged out'})
    return jsonify({'status': 'failure', 'message': 'User not logged in'}), 400

@route('/admin/check', methods=['GET'])
def check_login(request):
    session_data = session_manager.get_session(session.sid)
    if session_data and 'user_id' in session_data:
        return jsonify({'status': 'success', 'message': 'Yes, you are logged in'}), 200
    else:
        return jsonify({'status': 'failure', 'message': 'No, you are not logged in'}), 401

