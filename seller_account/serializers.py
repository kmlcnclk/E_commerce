from rest_framework import serializers
from .models import SellerAccountModel


class SellerAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerAccountModel
        fields = '__all__'
