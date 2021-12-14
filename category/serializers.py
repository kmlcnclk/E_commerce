from rest_framework import serializers
from .models import CategoryImageModel, CategoryModel


class CategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CategoryModel
        fields = '__all__'

class CategoryImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = CategoryImageModel
        fields = '__all__'

