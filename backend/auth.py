"""
auth.py - Authentication and authorization utilities
"""

from functools import wraps
from flask import session, redirect, url_for, jsonify, request
from models import get_db, query_to_dict
from werkzeug.security import check_password_hash


def login_user(username, password):
    """Authenticate a user. Returns user dict on success, None on failure."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    user = dict(row)
    if check_password_hash(user['password_hash'], password):
        return user
    return None


def login_required(f):
    """Decorator: require user to be logged in (session-based)."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'error': '未登录，请先登录'}), 401
            return redirect(url_for('serve_index'))
        return f(*args, **kwargs)
    return decorated


def role_required(*roles):
    """Decorator: require user to have one of the specified roles."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'user_id' not in session:
                if request.path.startswith('/api/'):
                    return jsonify({'error': '未登录，请先登录'}), 401
                return redirect(url_for('serve_index'))
            if session.get('role') not in roles:
                return jsonify({'error': '权限不足'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


def get_current_user():
    """Get current logged-in user from session."""
    if 'user_id' not in session:
        return None
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
    user = query_to_dict(cursor.fetchone())
    conn.close()
    return user
