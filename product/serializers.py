from rest_framework import serializers
from .models import LikeModel, ProductImageModel, ProductModel


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductModel
        fields = '__all__'


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImageModel
        fields = '__all__'


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikeModel
        fields = '__all__'
