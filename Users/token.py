
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from django.core.exceptions import BadRequest
from rest_framework.response import Response
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken, OutstandingToken
# from rest_framework.authtoken.models import Token


def add_token_to_blacklist(req_token, message):
    token = RefreshToken(req_token)
    token.blacklist()
    return {
        'success': True,
        'message': message
    }


def add_token_from_user_to_blacklist(token, message):
    real_token = TokenBackend(
        algorithm='HS256').decode(token, verify=False)
    user_id = real_token['user_id']

    tokens = OutstandingToken.objects.filter(user_id=user_id)
    for token in tokens:
        t, _ = BlacklistedToken.objects.get_or_create(token=token)

    return {
        'success': True,
        'message': message,
    }


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


def verify_token(token):
    state = AccessToken.verify(token)
    if state:
        return True
    else:
        raise AuthenticationFailed('Invalid token, try again')
