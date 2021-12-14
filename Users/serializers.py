from rest_framework import serializers
from rest_framework.utils import json
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CartItemModel, CartModel, User
from rest_framework_simplejwt.exceptions import TokenError
# from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
# from rest_framework.parsers import JSONParser
# from django.contrib.auth.hashers import make_password, check_password
# from .token import get_tokens_for_user
# from rest_framework.response import Response


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}
        }


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartModel
        fields = '__all__'


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItemModel
        fields = '__all__'

# class RegisterSerializer(serializers.ModelSerializer):
#     access = serializers.CharField(max_length=255, read_only=True)
#     refresh = serializers.CharField(max_length=255, read_only=True)

#     class Meta:
#         model = User
#         fields = '__all__'

    # def validate(self, data):
    #     username = data.get("username", None)
    #     password = data.get("password", None)
    #     first_name = data.get("first_name", None)
    #     last_name = data.get("last_name", None)
    #     email = data.get("email", None)
    #     user = self.create(data)
    #     if user is not None:
    #         try:
    #             current_user = User.objects.filter(username=username)
    #             if current_user.exists():
    #                 refresh = RefreshToken.for_user(current_user.get())
    #                 update_last_login(None, current_user.get())
    #         except User.DoesNotExist:
    #             raise serializers.ValidationError(
    #                 'User with given email and password does not exists'
    #             )
    #         return {
    #             'access': str(refresh.access_token),
    #             'refresh': str(refresh),
    #         }

    # def create(self, req):
    #     data = JSONParser().parse(req)
    #     hashPassword = make_password(data['password'])
    #     data['password'] = hashPassword
    #     user_serializer = UserSerializer(data=data)
    #     if user_serializer.is_valid():
    #         user_serializer.save()
    #         user = User.objects.filter(username=data['username'])
    #         if user.exists():
    #             update_last_login(None, user.get())
    #             token = get_tokens_for_user(user.get())
    #             return token
    #         return Response({'error': {'message': 'Internal Server Error'}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    #     return user_serializer.errors


# class LoginSerializer(serializers.ModelSerializer):
#     token = serializers.CharField(max_length=255, read_only=True)

#     class Meta:
#         model = User
#         field = '__all__'

#     def validate(self, data):
#         username = data.get("username", None)
#         password = data.get("password", None)
#         user = authenticate(username=username, password=password)
#         if user is None:
#             raise serializers.ValidationError(
#                 'A user with this username and password is not found.'
#             )
#         try:
#             current_user = User.objects.filter(username=username)
#             if current_user.exists():
#                 refresh = RefreshToken.for_user(current_user.get())
#                 update_last_login(None, user)
#         except User.DoesNotExist:
#             raise serializers.ValidationError(
#                 'User with given email and password does not exists'
#             )
#         return {
#             'access': str(refresh.access_token),
#             'refresh': str(refresh),
#         }


# class LogoutSerializer(serializers.Serializer):

#     refresh = serializers.CharField()

#     default_error_messages = {'bad_token': 'Token is expired or invalid'}

#     def validate(self, attrs):
#         self.token = attrs['refresh']
#         return attrs

#     def save(self, **kwargs):

#         try:
#             RefreshToken(self.token).blacklist()
#         except TokenError:
#             self.fail('bad_token')
