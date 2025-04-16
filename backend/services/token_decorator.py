from flask import request, g
from functools import wraps

from ..utilities import Utility

standardize_response = Utility.standardize_response

def token_required():
    """
    Decorator to check if the request has a valid access token.
    """
    from ..models import AccessToken

    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            token = kwargs.get('token') or request.args.get('token') or request.headers.get('Authorization')
            if not token:
                return standardize_response(status='error', message="Token is missing", code=401)
            
            access_token = AccessToken.get_by_token(token)

            # TODO: Add logging

            # Inject context
            g.event_uuid = access_token.event_uuid

            return f(*args, **kwargs)
        return wrapped
    return decorator