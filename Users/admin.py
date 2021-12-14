from rest_framework_simplejwt import token_blacklist
from django.contrib import admin
from .models import User
# from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import CartItemModel, CartModel
# Register your models here.

admin.site.register(User, UserAdmin)
admin.site.register(CartModel)
admin.site.register(CartItemModel)
