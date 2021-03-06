import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'dev-ju3r18pc.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'https://jackstewart.net/authentication'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

## Auth Header
'''
@Implement get_token_auth_header() method
    it should attempt to get the header from the request
        it should raise an AuthError if no header is present
    it should attempt to split bearer and the token
        it should raise an AuthError if the header is malformed
    return the token part of the header
'''
def get_token_auth_header():
    print(request.headers)
    auth_value = request.headers.get('Authorization', None)
    if auth_value:
        # Partially derived from Auth0 quick start docs (https://auth0.com/docs/quickstart/backend/python/01-authorization)
        auth_array = auth_value.split(" ")
        if auth_array[0].lower() != 'bearer':
            raise AuthError({
                    "code": "invalid_header",
                    "description": "Authorization header missing 'Bearer' prefix"
                },
                401
            )
        elif len(auth_array) == 1:
            raise AuthError({
                "code": "invalid_header",
                "description": "Missing authorization token"
                },
                401
            )
        elif len(auth_array) > 2:
            raise AuthError({
                "code": "invalid_header",
                "description": "Authorization header elements exceed those in Bearer token format"
                },
                401
            )
        auth_token = auth_array[1]
        if auth_token.lower() == 'bearer':
            raise AuthError({
                "code": "invalid_header",
                "description": "Bearer token values not in correct order"
                },
                401
            )
            print(auth_token)
            return auth_token
    else:
        raise AuthError('Authorization error', 401)

'''
@TODO implement check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded JWT payload
    it should raise an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission string is not in the payload permissions array
    return true otherwise
'''
def check_permissions(permission, payload):
    # TODO Add all possible permissions values to `all_permissions`
    # all_permissions = []
    # payload_permissions = 0
    # for permission in all_permissions:
    #     if permission in payload:
    #         payload_permissions += 1
    #     else:
    #         pass
    print(permission, payload)
    if payload_permissions <= 0:
        AuthError('Permissions not provided', 401)
    elif permission not in payload:
        AuthError('Unauthorized request', 401)
    else:
        return True

'''
@TODO implement verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)
    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims
    return the decoded payload
    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''
def verify_decode_jwt(token):
    # References Python Quick Start: https://auth0.com/docs/quickstart/backend/python/01-authorization
    jsonurl = urlopen("https://"+AUTH0_DOMAIN+"/.well-known/jwks.json")
    # Store the web key set as a Python object
    jwks = json.loads(jsonurl.read())
    try:
        unverified_header = jwt.get_unverified_header(token)
        print(unverified_header)
    except jwt.JWTError:
        raise AuthError({
            "code": "invalid_header",
            "description": "Use a valid RS256 signed JWT"
            },
            401
        )
    rsa_key = {}
    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms = ALGORITHMS,
                audience = API_AUDIENCE,
                issuer = "https://"+AUTH0_DOMAIN+"/"
            )
        except jwt.ExpiredSignatureError:
            raise AuthError({
                "code": "token_expired",
                "description": "Expired token"
                },
                401
            )
        except jwt.JWTClaimsError:
            raise AuthError({
                "code": "invalid_claims",
                "description": "Incorrect values for audience and/or issuer."
                },
                401
            )
        except Exception:
            raise AuthError({
                "code": "invalid_header",
                "description": "Unable to parse authentication token."
                },
                401
            )
        _request_ctx_stack.top.current_user = payload
        return f(*args, **kwargs)
    print(payload)
    return payload

'''
@TODO implement @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''
def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)
        return wrapper
    return requires_auth_decorator