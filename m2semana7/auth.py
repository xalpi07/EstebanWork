import os
from functools import wraps

from flask import request, Response, g

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

jwt_manager = None
db_manager = None


def configure_auth(jwt_mgr, db_mgr):
    global jwt_manager, db_manager
    jwt_manager = jwt_mgr
    db_manager = db_mgr


def get_token_from_header():
    token = request.headers.get("Authorization")
    if token is None:
        return None
    return token.replace("Bearer ", "")


def require_auth(allowed_roles=None):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            token = get_token_from_header()
            if token is None:
                return Response(status=401)

            decoded = jwt_manager.decode(token)
            if decoded is None:
                return Response(status=403)

            user = db_manager.get_user_by_id(decoded["id"])
            if user is None:
                return Response(status=403)

            role = user[3]
            if allowed_roles is not None and role not in allowed_roles:
                return Response(status=403)

            g.current_user = user
            return f(*args, **kwargs)

        return wrapped

    return decorator
