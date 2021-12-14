from rest_framework.permissions import BasePermission, SAFE_METHODS
from dotenv import load_dotenv
from rest_framework_simplejwt.tokens import AccessToken

from Users.token import verify_token
# from .models import User
from django.contrib.auth.models import User
import jwt
from rest_framework.exceptions import AuthenticationFailed
import os

load_dotenv()


class CIsAuthenticated(BasePermission):
    # message = "You are not a user"

    def has_permission(self, request, view):
    
        # if request.COOKIES.get('access'):
        #     token = request.COOKIES.get('access')

        # if request.headers.get('Authorization'):
        #     token = request.headers.get('Authorization')

        # if not token:
        #     raise AuthenticationFailed('Unauthenticated!')

        # try:
        #     access = token.split(' ')[1]

        #     payload = jwt.decode(access, os.getenv(
        #         "SECRET_KEY"), algorithms=['HS256'])
        # except jwt.ExpiredSignatureError:
        #     raise AuthenticationFailed('Unauthenticated')

        # user = User.objects.filter(_id=payload['_id'])

        # if user.exists():
        # return True

        raise AuthenticationFailed("asd")
    def has_object_permission(self, request, view):

        raise AuthenticationFailed("asd")
