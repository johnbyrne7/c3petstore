# dummy authorization functions

from werkzeug.exceptions import Unauthorized

testToken = {"sub": "1234567890", "name": "John Doe", "scopes": []}


def decode_token(token, *args, **kwargs) -> dict:
    #  implement method to decode pass auth token and return a decoded user token
    #   mocked sample provded here; only requirement is to pass something
    if token:
        return testToken

    raise Unauthorized


def token_info(access_token) -> dict:
    return decode_token(access_token)


def validate_scope(required_scopes, token_scopes):
    return True

    # Possible implementation:
    # return len(set(required_scopes) & set(token_scopes)) > 0


def validate_apiscope(required_scopes, token_scopes):
    return True


def validate_apitoken(token, required_scopes) -> dict:
    return testToken
