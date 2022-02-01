from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from category.models import CategoryImageModel, CategoryModel
from category.serializers import CategoryImageSerializer, CategorySerializer
from django.core.exceptions import BadRequest
from product.models import ProductModel
from product.serializers import ProductSerializer
import os
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser
from rest_framework.decorators import api_view, parser_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
# Create your views here.


class CreateView(generics.CreateAPIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [JWTAuthentication]
    serializer_class = CategorySerializer
    parser_classes = (MultiPartParser, FormParser, FileUploadParser)

    # name = openapi.Parameter('name', openapi.IN_FORM,
    #                          type=openapi.TYPE_STRING, required=True)
    # image = openapi.Parameter('image', openapi.IN_FORM,
    #                           type=openapi.TYPE_FILE, required=True)

    # @swagger_auto_schema(
    #     manual_parameters=[name, image]
    # )
    def post(self, req):
        name = req.data.get('name')
        image = req.FILES.get('image')

        category_data = {
            'name': name,
        }

        category_serializer = self.serializer_class(data=category_data)
        if category_serializer.is_valid():
            category_serializer.save()
            category_image_data = {
                'image_url': image,
                'category_id': category_serializer.data['id']
            }
            category_image_serializer = CategoryImageSerializer(
                data=category_image_data)
            if category_image_serializer.is_valid():
                category_image_serializer.save()
                return Response({'success': True, 'message': 'Category created successfully'}, status=status.HTTP_201_CREATED)
            return Response(category_image_serializer.errors)
        return Response(category_serializer.errors)


class GetView(generics.ListAPIView):
    permission_classes = []
    authentication_classes = []
    serializer_class = CategorySerializer
    serializer_image = CategoryImageSerializer

    def get(self, req):
        categories = CategoryModel.objects.all()
        category_serializer = self.serializer_class(categories, many=True)

        data = []
        for category_index in range(len(category_serializer.data)):
            category_image = CategoryImageModel.objects.filter(
                category_id=category_serializer.data[category_index]['id'])
            if category_image.exists():
                category_image_serializer = self.serializer_image(
                    category_image.get(), many=False)

                data_item = {
                    'name': category_serializer.data[category_index]['name'],
                    'product_count': category_serializer.data[category_index]['product_count'],
                    'slug': category_serializer.data[category_index]['slug'],
                    'created_at': category_serializer.data[category_index]['created_at'],
                    'image_url': os.getenv('URL')+category_image_serializer.data['image_url'],
                }

                data.append(data_item)
        return Response({'success': True, 'count': len(data), 'results': data}, status=status.HTTP_200_OK)


class UpdateView(generics.UpdateAPIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [JWTAuthentication]
    serializer_class = CategorySerializer
    serializer_image = CategoryImageSerializer
    parser_classes = (MultiPartParser, FormParser, FileUploadParser)

    name = openapi.Parameter('name', openapi.IN_FORM,
                             type=openapi.TYPE_STRING, required=True)
    image = openapi.Parameter('image', openapi.IN_FORM,
                              type=openapi.TYPE_FILE, required=True)

    @swagger_auto_schema(
        manual_parameters=[name, image]
    )
    def put(self, req, pk):
        name = req.data.get('name')
        image = req.FILES.get('image')
        if name is not None:
            count = ProductModel.objects.filter(category_id=pk).count()
            data = {
                'name': name,
                'product_count': count if count else 0,
            }
            # önceki image modeli sil ve yenisini oluştur
            category = CategoryModel.objects.get(id=pk)
            if category is not None:
                category_serializer = self.serializer_class(
                    category, data=data)
                if category_serializer.is_valid():
                    category_serializer.save()
                else:
                    return Response(category_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                raise BadRequest('Category is not found')
        else:
            raise BadRequest('Name field is required')

        if image is not None:
            data_i = {
                'image_url': image,
            }
            category_image = CategoryImageModel.objects.get(category_id=pk)
            if category_image is not None:
                category_image_serializer = self.serializer_image(
                    category_image, data=data_i, partial=True)
                if category_image_serializer.is_valid():
                    category_image_serializer.save()
                else:
                    return Response(category_image_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                raise BadRequest('Category image is not found')
        else:
            raise BadRequest('Image field is required')

        return Response({'success': True,
                         'message': 'Category successfully updated'})


class DeleteView(generics.DestroyAPIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [JWTAuthentication]

    def delete(self, req, pk):
        category = CategoryModel.objects.filter(id=pk)
        if category.exists():
            category.delete()
        else:
            raise BadRequest('Category is not found')
        return Response({'success': True, 'message': 'Category successfully deleted'}, status=status.HTTP_200_OK)
