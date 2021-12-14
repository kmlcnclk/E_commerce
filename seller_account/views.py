from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from .serializers import SellerAccountSerializer
from .models import SellerAccountModel
from django.conf import settings
from rest_framework import status
from django.core.exceptions import BadRequest
import jwt
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
# Create your views here.


class CreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = SellerAccountSerializer
    parser_classes = (FormParser,)

    user_id = openapi.Parameter('user_id', openapi.IN_FORM,
                                type=openapi.TYPE_STRING, required=False)
    seller_name = openapi.Parameter('seller_name', openapi.IN_FORM,
                                    type=openapi.TYPE_STRING, required=True)

    @swagger_auto_schema(
        manual_parameters=[user_id, seller_name]
    )
    def post(self, req):
        access = req.headers.get('AUTHORIZATION').split(' ')[1]
        payload = jwt.decode(
            access, settings.SECRET_KEY, algorithms=['HS256'])
        seller_name = req.data.get('seller_name')
        user_id = payload['user_id']
        seller_account = SellerAccountModel.objects.filter(user_id=user_id)
        if seller_account.exists():
            raise BadRequest('You already have a seller account')
        data = {
            'seller_name': seller_name,
            'user_id': user_id,
        }
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'message': 'Seller Account successfully created'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors)


class GetView(generics.ListAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = SellerAccountSerializer

    def get(self, req):
        access = req.headers.get('AUTHORIZATION').split(' ')[1]
        payload = jwt.decode(
            access, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']
        seller_account = SellerAccountModel.objects.filter(user_id=user_id)
        if seller_account.exists():
            seller_account_serializer = self.serializer_class(
                seller_account.get())
            if seller_account_serializer.data is not None:
                return Response(seller_account_serializer.data, status=status.HTTP_200_OK)
            else:
                Response(seller_account_serializer.errors)
        else:
            raise BadRequest('You haven\'t a seller acount')


class UpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = SellerAccountSerializer

    def put(self, req):
        seller_name = req.data.get('seller_name')
        if seller_name is not None:
            access = req.headers.get('AUTHORIZATION').split(' ')[1]
            payload = jwt.decode(
                access, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload['user_id']
            seller_account = SellerAccountModel.objects.filter(user_id=user_id)
            if seller_account.exists():
                data = {
                    'seller_name': seller_name,
                }
                seller_account_serializer = self.serializer_class(
                    seller_account.get(), data=data, partial=True)
                if seller_account_serializer.is_valid():
                    seller_account_serializer.save()
                else:
                    return Response(seller_account_serializer.errors)
            else:
                raise BadRequest('You haven\'t a seller account')
        else:
            raise BadRequest('Seller name field is required')
        return Response({'success': True, 'message': 'Seller account successfully updated'}, status=status.HTTP_200_OK)


class DeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def delete(self, req):
        access = req.headers.get('AUTHORIZATION').split(' ')[1]
        payload = jwt.decode(
            access, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']
        seller_account = SellerAccountModel.objects.filter(user_id=user_id)
        if seller_account.exists():
            seller_account.delete()
        else:
            raise BadRequest('You haven\'t a seller account')
        return Response({'success': True, 'message': 'Seller account successfully deleted'}, status=status.HTTP_200_OK)
