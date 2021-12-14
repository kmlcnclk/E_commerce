from django.contrib import admin
from .models import ProductModel, ProductImageModel, LikeModel
# Register your models here.


admin.site.register(ProductModel)
admin.site.register(ProductImageModel)
admin.site.register(LikeModel)
