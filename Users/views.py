from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.exceptions import TokenError
from .models import CartItemModel, CartModel, User
# from django.contrib.auth.models import User
from .serializers import CartItemSerializer, CartSerializer, UserSerializer
from django.contrib.auth.hashers import make_password, check_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .token import get_tokens_for_user, add_token_to_blacklist
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import generics
from django.contrib.auth.models import update_last_login
from django.core.exceptions import BadRequest
import jwt
from django.conf import settings
from product.models import ProductModel
from product.serializers import ProductSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser


# req.headers.get('AUTHORIZATION')
# Create your views here.


class RegisterView(generics.CreateAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = UserSerializer

    def post(self, req):
        data = JSONParser().parse(req)
        hashPassword = make_password(data['password'])
        data['password'] = hashPassword
        user_serializer = self.serializer_class(data=data)
        if user_serializer.is_valid():
            user_serializer.save()
            user = User.objects.filter(username=data['username'])
            if user.exists():
                update_last_login(None, user.get())
                token = get_tokens_for_user(user.get())
                response = Response()
                response.set_cookie(key='access', value=token['access'],
                                    httponly=True)
                response.set_cookie(key='refresh', value=token['refresh'],
                                    httponly=True)
                response.status_code = 201
                response.data = {
                    'success': True,
                    'token': token,
                }
                # userın passwordunu almaya çalış login kısmında kontrol et falan sadece password al falan.
                user_serializer = self.serializer_class(user.get(), many=False)
                if user_serializer.data is not None:
                    cart_data = {
                        'user_id': user_serializer.data['id']}
                    cart_serializer = CartSerializer(data=cart_data)
                    if cart_serializer.is_valid():
                        cart_serializer.save()
                    else:
                        return Response(cart_serializer.errors)
                else:
                    return Response(user_serializer.errors)
                return response
            return Response({'error': {'message': 'Internal Server Error'}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(user_serializer.errors)


class LoginView(generics.GenericAPIView):
    authentication_classes = []
    permission_classes = []
    # parser_classes = (FormParser,)

    # serializer_class = UserSerializer

    # username_param_config = openapi.Parameter(
    #     'username', in_=openapi.IN_FORM, description='Please entry username ', type=openapi.TYPE_STRING)
    # password_param_config = openapi.Parameter(
    #     'password', in_=openapi.IN_FORM, description='Please entry password ', type=openapi.TYPE_STRING)

    # @swagger_auto_schema(request_body=openapi.Schema(
    #     type=openapi.TYPE_OBJECT,
    #     properties={
    #         'username': openapi.Schema(type=openapi.TYPE_STRING, description='Please entry username'),
    #         'password': openapi.Schema(type=openapi.TYPE_STRING, description='Please entry password'),
    #     }
    # ))
    username = openapi.Parameter('username', openapi.IN_FORM,
                                 type=openapi.TYPE_STRING, required=True)
    password = openapi.Parameter('password', openapi.IN_FORM,
                                 type=openapi.TYPE_STRING, required=True)

    @swagger_auto_schema(
        manual_parameters=[username, password]
    )
    def post(self, req):
        username = req.data.get('username')
        password = req.data.get('password')
        # data = JSONParser().parse(req)
        user = User.objects.filter(username=username)
        if user.exists():
            password_state = check_password(
                password, user.get().password)
            if password_state == False:
                return Response({'error': {'message': "The password entered isn't the same as the current password"}}, status=status.HTTP_400_BAD_REQUEST)

            update_last_login(None, user.get())
            token = get_tokens_for_user(user.get())
            response = Response()
            response.set_cookie(
                key='access', value=token['access'], httponly=True)
            response.set_cookie(
                key='refresh', value=token['refresh'], httponly=True)
            response.status_code = 200
            response.data = {
                'success': True,
                'token': token
            }
            return response
        return Response({'error': {'message': 'There is no such user with username'}}, status=status.HTTP_400_BAD_REQUEST)

# eğer kullanıcı logout yaparsa access tokenı db de açtığın access token alanına ekle ve herhangi bir işlem yapılırken orda var mı yokmu diye bak


class LogoutView(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = None

    req_body = openapi.Schema(type=openapi.TYPE_OBJECT,
                              properties={
                                  'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Please entry refresh')
                              })

    @swagger_auto_schema(request_body=req_body)
    def post(self, req):
        refresh = req.data.get('refresh')
        if refresh is not None:
            result = add_token_to_blacklist(refresh, 'Logout successfully')

            response = Response()
            response.delete_cookie('access')
            response.delete_cookie('refresh')
            response.status_code = 200
            response.data = result

            return response
        raise BadRequest('Refresh is not found')


class UserDelete(generics.DestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = None

    def delete(self, req):
        access = req.headers.get('AUTHORIZATION').split(' ')[1]
        payload = jwt.decode(
            access, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']
        if user_id is not None and access is not None:
            user = User.objects.filter(id=user_id)
            if user.exists():
                user.delete()

                response = Response()
                response.delete_cookie('access')
                response.delete_cookie('refresh')
                response.status_code = 200
                response.data = {
                    'success': True,
                    'message': 'User successfully deleted',
                }

                return response
            else:
                raise BadRequest('User ID is not found')
        else:
            raise BadRequest('User ID is not found')


class CartView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class_1 = CartSerializer
    serializer_class_2 = CartItemSerializer

    def get(self, req):
        access = req.headers.get('AUTHORIZATION').split(' ')[1]
        payload = jwt.decode(
            access, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']
        if user_id is not None:
            cart = CartModel.objects.filter(user_id=user_id)
            if cart.exists():
                cart_serializer = self.serializer_class_1(
                    cart.get(), many=False)
                if cart_serializer.data is not None:
                    current_cart_item = CartItemModel.objects.filter(
                        cart_id=cart_serializer.data['id'],)
                    if current_cart_item.exists():
                        current_cart_item_serializer = self.serializer_class_2(
                            current_cart_item.all(), many=True)
                        if current_cart_item_serializer.data is not None:
                            return Response({'success': True,
                                             'cart_count': cart_serializer.data['cart_count'],
                                             'total_price': cart_serializer.data['total_price'],
                                             'data': current_cart_item_serializer.data},
                                            status=status.HTTP_200_OK)
                        else:
                            return Response(current_cart_item_serializer.errors)
                    else:
                        return Response({'success': True, 'message': 'There are no items in your cart yet'}, status=status.HTTP_200_OK)
                else:
                    return Response(cart_serializer.errors)
            else:
                raise BadRequest('Cart is not defined')
        else:
            raise BadRequest('User ID not defined')


class AddToCartView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class_1 = CartSerializer
    serializer_class_2 = CartItemSerializer

    def post(self, req):
        product_id = req.data.get('product_id')
        access = req.headers.get('AUTHORIZATION').split(' ')[1]
        payload = jwt.decode(
            access, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']
        if product_id is not None and user_id is not None:
            cart = CartModel.objects.filter(user_id=user_id)
            if cart.exists():
                cart_serializer = self.serializer_class_1(
                    cart.get(), many=False)
                if cart_serializer.data is not None:
                    product = ProductModel.objects.filter(id=product_id)
                    if product.exists():
                        product_serializer = ProductSerializer(
                            product.get(), many=False)
                        if product_serializer.data is not None:
                            cart_item = CartItemModel.objects.filter(
                                product_id=product_id, cart_id=cart_serializer.data['id'])
                            if cart_item.exists():
                                current_cart_item_serializer = self.serializer_class_2(
                                    cart_item.get(), many=False)
                                if current_cart_item_serializer.data is not None:
                                    cart_item_data = {
                                        'count': current_cart_item_serializer.data['count']+1
                                    }
                                    new_cart_item_serializer = self.serializer_class_2(
                                        cart_item.get(), data=cart_item_data, partial=True)
                                    if new_cart_item_serializer.is_valid():
                                        new_cart_item_serializer.save()
                                        cart_data = {
                                            'total_price': cart_serializer.data['total_price']+product_serializer.data['price'],
                                            'cart_count': cart_serializer.data['cart_count']+1,
                                        }
                                        new_cart_serializer = self.serializer_class_1(
                                            cart.get(), data=cart_data, partial=True)
                                        if new_cart_serializer.is_valid():
                                            new_cart_serializer.save()
                                            return Response({'success': True, 'message': 'The product has been successfully added to your cart'}, status=status.HTTP_201_CREATED)
                                        else:
                                            return Response(new_cart_serializer.errors)
                                    else:
                                        return Response(new_cart_item_serializer.errors)
                                else:
                                    return Response(current_cart_item_serializer.errors)
                            else:
                                cart_item_data = {
                                    'cart_id': cart_serializer.data['id'],
                                    'product_id': product_id
                                }
                                cart_item_serializer = self.serializer_class_2(
                                    data=cart_item_data)
                                if cart_item_serializer.is_valid():
                                    cart_item_serializer.save()
                                    cart_data = {
                                        'total_price': cart_serializer.data['total_price']+product_serializer.data['price'],
                                        'cart_count': cart_serializer.data['cart_count']+1,
                                    }
                                    new_cart_serializer = self.serializer_class_1(
                                        cart.get(), data=cart_data, partial=True)
                                    if new_cart_serializer.is_valid():
                                        new_cart_serializer.save()
                                        return Response({'success': True, 'message': 'The product has been successfully added to your cart'}, status=status.HTTP_201_CREATED)
                                    else:
                                        return Response(new_cart_serializer.errors)
                                else:
                                    return Response(cart_item_serializer.errors)
                        else:
                            return Response(product_serializer.errors)
                    else:
                        raise BadRequest('Product is not found')
                else:
                    return Response(cart_serializer.errors)
            else:
                raise BadRequest('Cart is not defined')
        else:
            raise BadRequest('Product ID or User ID not defined')


class IncreaseToCartView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class_1 = CartSerializer
    serializer_class_2 = CartItemSerializer

    def put(self, req):
        product_id = req.data.get('product_id')
        access = req.headers.get('AUTHORIZATION').split(' ')[1]
        payload = jwt.decode(
            access, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']
        if product_id is not None and user_id is not None:
            cart = CartModel.objects.filter(user_id=user_id)
            if cart.exists():
                cart_serializer = self.serializer_class_1(
                    cart.get(), many=False)
                if cart_serializer.data is not None:
                    product = ProductModel.objects.filter(id=product_id)
                    if product.exists():
                        product_serializer = ProductSerializer(
                            product.get(), many=False)
                        if product_serializer.data is not None:
                            current_cart_item = CartItemModel.objects.filter(
                                cart_id=cart_serializer.data['id'], product_id=product_id)
                            if current_cart_item.exists():
                                current_cart_item_serializer = self.serializer_class_2(
                                    current_cart_item.get(), many=False)
                                if current_cart_item_serializer.data is not None:
                                    cart_item_data = {
                                        'count': current_cart_item_serializer.data['count']+1
                                    }
                                    new_cart_item_serializer = self.serializer_class_2(
                                        current_cart_item.get(), data=cart_item_data, partial=True)
                                    if new_cart_item_serializer.is_valid():
                                        new_cart_item_serializer.save()
                                        cart_data = {
                                            'total_price': cart_serializer.data['total_price']+product_serializer.data['price'],
                                            'cart_count': cart_serializer.data['cart_count']+1,
                                        }
                                        new_cart_serializer = self.serializer_class_1(
                                            cart.get(), data=cart_data, partial=True)
                                        if new_cart_serializer.is_valid():
                                            new_cart_serializer.save()
                                            return Response({'success': True, 'message': 'Cart item successfully updated'}, status=status.HTTP_201_CREATED)
                                        else:
                                            return Response(new_cart_serializer.errors)
                                    else:
                                        return Response(new_cart_item_serializer.errors)
                                else:
                                    return Response(current_cart_item_serializer.errors)
                            else:
                                raise BadRequest(
                                    'You don\'t have this product in your cart')
                        else:
                            return Response(product_serializer.errors)
                    else:
                        raise BadRequest('Product is not found')
                else:
                    return Response(cart_serializer.errors)
            else:
                raise BadRequest('Cart is not defined')
        else:
            raise BadRequest('Product ID or User ID not defined')


class DecreaseToCartView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class_1 = CartSerializer
    serializer_class_2 = CartItemSerializer

    def put(self, req):
        product_id = req.data.get('product_id')
        access = req.headers.get('AUTHORIZATION').split(' ')[1]
        payload = jwt.decode(
            access, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']
        if product_id is not None and user_id is not None:
            cart = CartModel.objects.filter(user_id=user_id)
            if cart.exists():
                cart_serializer = self.serializer_class_1(
                    cart.get(), many=False)
                if cart_serializer.data is not None:
                    product = ProductModel.objects.filter(id=product_id)
                    if product.exists():
                        product_serializer = ProductSerializer(
                            product.get(), many=False)
                        if product_serializer.data is not None:
                            current_cart_item = CartItemModel.objects.filter(
                                cart_id=cart_serializer.data['id'], product_id=product_id)
                            if current_cart_item.exists():
                                current_cart_item_serializer = self.serializer_class_2(
                                    current_cart_item.get(), many=False)
                                if current_cart_item_serializer.data is not None:
                                    if current_cart_item_serializer.data['count']-1 <= 0:
                                        current_cart_item.delete()
                                        cart_data = {
                                            'total_price': cart_serializer.data['total_price']-product_serializer.data['price'],
                                            'cart_count': cart_serializer.data['cart_count']-1,
                                        }
                                        new_cart_serializer = self.serializer_class_1(
                                            cart.get(), data=cart_data, partial=True)
                                        if new_cart_serializer.is_valid():
                                            new_cart_serializer.save()
                                            return Response({'success': True, 'message': 'Cart item successfully deleted'}, status=status.HTTP_201_CREATED)
                                        else:
                                            return Response(new_cart_serializer.errors)
                                    else:
                                        cart_item_data = {
                                            'count': current_cart_item_serializer.data['count']-1
                                        }
                                        new_cart_item_serializer = self.serializer_class_2(
                                            current_cart_item.get(), data=cart_item_data, partial=True)
                                        if new_cart_item_serializer.is_valid():
                                            new_cart_item_serializer.save()
                                            cart_data = {
                                                'total_price': cart_serializer.data['total_price']-product_serializer.data['price'],
                                                'cart_count': cart_serializer.data['cart_count']-1,
                                            }
                                            new_cart_serializer = self.serializer_class_1(
                                                cart.get(), data=cart_data, partial=True)
                                            if new_cart_serializer.is_valid():
                                                new_cart_serializer.save()
                                                return Response({'success': True, 'message': 'Cart item successfully updated'}, status=status.HTTP_201_CREATED)
                                            else:
                                                return Response(new_cart_serializer.errors)
                                        else:
                                            return Response(new_cart_item_serializer.errors)
                                else:
                                    return Response(current_cart_item_serializer.errors)
                            else:
                                raise BadRequest(
                                    'You don\'t have this product in your cart')
                        else:
                            return Response(product_serializer.errors)
                    else:
                        raise BadRequest('Product is not found')
                else:
                    return Response(cart_serializer.errors)
            else:
                raise BadRequest('Cart is not defined')
        else:
            raise BadRequest('Product ID or User ID not defined')


class DeleteToCartView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class_1 = CartSerializer
    serializer_class_2 = CartItemSerializer

    def delete(self, req):
        product_id = req.data.get('product_id')
        access = req.headers.get('AUTHORIZATION').split(' ')[1]
        payload = jwt.decode(
            access, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']
        if product_id is not None and user_id is not None:
            cart = CartModel.objects.filter(user_id=user_id)
            if cart.exists():
                cart_serializer = self.serializer_class_1(
                    cart.get(), many=False)
                if cart_serializer.data is not None:
                    product = ProductModel.objects.filter(id=product_id)
                    if product.exists():
                        product_serializer = ProductSerializer(
                            product.get(), many=False)
                        if product_serializer.data is not None:
                            current_cart_item = CartItemModel.objects.filter(
                                cart_id=cart_serializer.data['id'], product_id=product_id)
                            if current_cart_item.exists():
                                current_cart_item_serializer = self.serializer_class_2(
                                    current_cart_item.get(), many=False)
                                if current_cart_item_serializer.data is not None:
                                    current_cart_item.delete()
                                    cart_data = {
                                        'total_price': cart_serializer.data['total_price']-(product_serializer.data['price']*current_cart_item_serializer.data['count']),
                                        'cart_count': cart_serializer.data['cart_count']-current_cart_item_serializer.data['count'],
                                    }
                                    new_cart_serializer = self.serializer_class_1(
                                        cart.get(), data=cart_data, partial=True)
                                    if new_cart_serializer.is_valid():
                                        new_cart_serializer.save()
                                        return Response({'success': True, 'message': 'Cart item successfully deleted'}, status=status.HTTP_201_CREATED)
                                    else:
                                        return Response(new_cart_serializer.errors)
                                else:
                                    return Response(current_cart_item_serializer.errors)
                            else:
                                raise BadRequest(
                                    'You don\'t have this product in your cart')
                        else:
                            return Response(product_serializer.errors)
                    else:
                        raise BadRequest('Product is not found')
                else:
                    return Response(cart_serializer.errors)
            else:
                raise BadRequest('Cart is not defined')
        else:
            raise BadRequest('Product ID or User ID not defined')
