from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from category.serializers import CategorySerializer
from category.models import CategoryModel
from .serializers import LikeSerializer, ProductSerializer, ProductImageSerializer
from .models import LikeModel, ProductModel, ProductImageModel
from django.core.exceptions import BadRequest, ValidationError
from rest_framework import status
import jwt
from django.conf import settings
import json
import os
from rest_framework.permissions import IsAuthenticated

# Create your views here.


class CreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = ProductSerializer
    serializer_image = ProductImageSerializer

    def post(self, req):
        name = req.data.get('name')
        price = req.data.get('price')
        image = req.data.get('image')
        category_id = req.data.get('category_id')
        access = req.headers.get('AUTHORIZATION').split(' ')[1]
        payload = jwt.decode(
            access, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']
        data = {
            'name': name,
            'price': price,
            'category_id': category_id,
            'seller_id': user_id
        }

        product_serializer = self.serializer_class(data=data)
        if product_serializer.is_valid():
            product_serializer.save()
            category = CategoryModel.objects.filter(id=category_id)
            if category.exists():
                cs = CategorySerializer(category.get())
                if cs.data is not None:
                    cs_data = {
                        # 'name': cs.data['name'],
                        'product_count': cs.data['product_count']+1,
                    }
                    category_serializer = CategorySerializer(
                        category.get(), data=cs_data, partial=True)  # bunu diğer yerlere uyarla , partial=True bunun sayesinde sadece değişen yeri güncelliyoruz.
                    if category_serializer.is_valid():
                        category_serializer.save()
                    else:
                        return Response(category_serializer.errors)
                else:
                    return Response(cs.errors)
            else:
                raise BadRequest('Category is not found')
            product_image_data = {
                'image_url': image,
                'product_id': product_serializer.data['id'],
            }
            product_image_serializer = self.serializer_image(
                data=product_image_data)
            if product_image_serializer.is_valid():
                product_image_serializer.save()
                return Response({'success': True, 'message': 'Product successfully created'}, status=status.HTTP_201_CREATED)
            return Response(product_image_serializer.errors)
        return Response(product_serializer.errors)


class GetView(generics.ListAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = ProductSerializer
    serializer_image = ProductImageSerializer

    def get(self, req, pk):
        product = ProductModel.objects.filter(id=pk)
        if product.exists():
            product_serializer = self.serializer_class(
                product.get(), many=False)
            if product_serializer is not None:
                product_image = ProductImageModel.objects.filter(
                    product_id=pk)
                if product_image.exists():
                    product_image_serializer = self.serializer_image(
                        product_image.get(), many=False)
                    if product_image_serializer is not None:
                        data = {
                            'name': product_serializer.data['name'],
                            'price': product_serializer.data['price'],
                            'slug': product_serializer.data['slug'],
                            'seller_id': product_serializer.data['seller_id'],
                            'category_id': product_serializer.data['category_id'],
                            'created_at': product_serializer.data['created_at'],
                            'updated_at': product_serializer.data['updated_at'],
                            'image_url': os.getenv('URL') + product_image_serializer.data['image_url'],
                        }
                        return Response(data, status=status.HTTP_200_OK)
                    else:
                        return Response(product_image_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                else:
                    raise BadRequest('Product image is not found')
            else:
                return Response(product_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            raise BadRequest('Product is not found')


class UpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = ProductSerializer
    serializer_image = ProductImageSerializer

    def put(self, req, pk):
        name = req.data.get('name')
        image = req.data.get('image')
        price = req.data.get('price')
        category_id = req.data.get('category_id')
        access = req.headers.get('AUTHORIZATION').split(' ')[1]
        payload = jwt.decode(
            access, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']
        if (name or price or category_id) is not None and user_id is not None:
            product = ProductModel.objects.filter(id=pk, seller_id=user_id)
            if product.exists():
                ps = self.serializer_class(
                    product.get())
                if ps.data is not None:
                    data = {
                        'name': name if name else ps.data['name'],
                        'price': price if price else ps.data['price'],
                        'category_id': category_id if category_id else ps.data['category_id'],
                        # 'seller_id': ps.data['seller_id'],
                    }
                    product_serializer = self.serializer_class(
                        product.get(), data=data, partial=True)
                    if product_serializer.is_valid():
                        product_serializer.save()
                    else:
                        return Response(product_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response(ps.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                raise BadRequest('Product is not found')
        else:
            raise BadRequest(
                'Name, Price and Category or User ID field is not found')

        if image is not None:
            product = ProductModel.objects.filter(id=pk, seller_id=user_id)
            if product.exists():
                data = {
                    'image_url': image,
                }
                product_image = ProductImageModel.objects.filter(product_id=pk)
                if product_image.exists():
                    product_image_serializer = self.serializer_image(
                        product_image.get(), data=data, partial=True)
                    if product_image_serializer.is_valid():
                        product_image_serializer.save()
                    else:
                        return Response(product_image_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                else:
                    raise BadRequest('Product image is not found')
            else:
                raise BadRequest(
                    'You have not this product or There is no such this product')
        else:
            raise BadRequest('Image field is required')
        return Response({'success': True,
                         'message': 'Product successfully updated'})


class DeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def delete(self, req, pk):
        access = req.headers.get('AUTHORIZATION').split(' ')[1]
        payload = jwt.decode(
            access, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']
        if user_id is not None:
            product = ProductModel.objects.filter(id=pk, seller_id=user_id)
            if product.exists():
                p_s = ProductSerializer(product.get())
                if p_s.data:
                    category = CategoryModel.objects.filter(
                        id=p_s.data['category_id'])
                    if category.exists():
                        cs = CategorySerializer(category.get())
                        if cs.data is not None:
                            cs_data = {
                                'product_count': cs.data['product_count']-1,
                            }
                            category_serializer = CategorySerializer(
                                category.get(), data=cs_data, partial=True)  # bunu diğer yerlere uyarla , partial=True bunun sayesinde sadece değişen yeri güncelliyoruz.
                            if category_serializer.is_valid():
                                category_serializer.save()
                            else:
                                return Response(category_serializer.errors)
                        else:
                            return Response(cs.errors)
                    else:
                        raise BadRequest('Category is not found')
                else:
                    raise BadRequest('Category is not found')
                product.delete()
            else:
                raise BadRequest(
                    'Product is not found or You have not this product')
        return Response({'success': True, 'message': 'Product successfully deleted'}, status=status.HTTP_200_OK)


class LikeView(generics.CreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = LikeSerializer

    def post(self, req, pk):
        product = ProductModel.objects.filter(id=pk)
        if product.exists():
            product_serializer = ProductSerializer(product.get())
            if product_serializer.data is not None:
                access = req.headers.get('AUTHORIZATION').split(' ')[1]
                payload = jwt.decode(
                    access, settings.SECRET_KEY, algorithms=['HS256'])
                user_id = payload['user_id']
                like_current = LikeModel.objects.filter(
                    user_id=user_id, product_id=product_serializer.data['id'], category_id=product_serializer.data['category_id'])
                if like_current.exists():
                    raise BadRequest('You already like this product')
                data = {
                    'user_id': user_id,
                    'product_id': product_serializer.data['id'],
                    'category_id': product_serializer.data['category_id']
                }
                like_serializer = self.serializer_class(data=data)
                if like_serializer.is_valid():
                    like_serializer.save()
                    p_data = {
                        'like_count': product_serializer.data['like_count']+1
                    }
                    p_s = ProductSerializer(
                        product.get(), data=p_data, partial=True)
                    if p_s.is_valid():
                        p_s.save()
                        return Response({'success': True, 'message': 'You liked this product'}, status=status.HTTP_201_CREATED)
                    else:
                        return Response(p_s.errors)
                else:
                    raise ValidationError('Internal Server Error')
            else:
                return Response(product_serializer.errors)
        else:
            raise BadRequest('Product is not found')


class UnlikeView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = LikeModel

    def delete(self, req, pk):
        product = ProductModel.objects.filter(id=pk)
        if product.exists():
            product_serializer = ProductSerializer(product.get())
            if product_serializer.data is not None:
                access = req.headers.get('AUTHORIZATION').split(' ')[1]
                payload = jwt.decode(
                    access, settings.SECRET_KEY, algorithms=['HS256'])
                user_id = payload['user_id']
                like_current = LikeModel.objects.filter(
                    user_id=user_id, product_id=product_serializer.data['id'], category_id=product_serializer.data['category_id'])
                if like_current.exists():
                    like_current.delete()
                    p_data = {
                        'like_count': product_serializer.data['like_count']-1
                    }
                    p_s = ProductSerializer(
                        product.get(), data=p_data, partial=True)
                    if p_s.is_valid():
                        p_s.save()
                        return Response({'success': True, 'message': 'You got the like back'}, status=status.HTTP_201_CREATED)
                    else:
                        return Response(p_s.errors)
                else:
                    raise BadRequest('You don\'t like this product yet')
            else:
                return Response(product_serializer.errors)
        else:
            raise BadRequest('Product is not found')

# pagination yap ve drf sitedeki logini araştırıp farklı bir proje oluşturarak yap


class GetProductsView(generics.ListAPIView):
    queryset = ProductModel.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filter_fields = ('name',)
    search_fields = ('name',)
