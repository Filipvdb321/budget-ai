from functools import wraps
from flask import request, jsonify, current_app
import jwt
from jwt.algorithms import RSAAlgorithm
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_auth0_public_key():
    """Fetch Auth0 public key from JWKS endpoint."""
    domain = os.getenv('AUTH0_DOMAIN')
    jwks_url = f"https://{domain}/.well-known/jwks.json"
    jwks = requests.get(jwks_url).json()
    # Get the first key (usually there's only one)
    public_key = RSAAlgorithm.from_jwk(jwks['keys'][0])
    return public_key

def requires_auth(f):
    """Decorator to check if request has valid JWT token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', None)
        if not auth_header:
            return jsonify({"message": "No authorization header"}), 401
        
        try:
            # Strip 'Bearer ' from token
            token = auth_header.split(' ')[1]
            # Verify token
            payload = jwt.decode(
                token,
                get_auth0_public_key(),
                algorithms=['RS256'],
                audience=os.getenv('AUTH0_AUDIENCE'),
                issuer=f"https://{os.getenv('AUTH0_DOMAIN')}/"
            )
            # Add user info to request context
            request.auth = {"payload": payload}
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired"}), 401
        except jwt.InvalidTokenError as e:
            current_app.logger.error(f"Invalid token error: {str(e)}")
            return jsonify({"message": "Invalid token"}), 401
        except Exception as e:
            current_app.logger.error(f"Authentication error: {str(e)}")
            return jsonify({"message": "Authentication error"}), 500
            
    return decorated 