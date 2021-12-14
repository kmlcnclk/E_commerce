from django.db import models
# from djongo.models.fields import ObjectIdField
from django.contrib.auth.models import AbstractUser
import uuid
# # Create your models here.


class User(AbstractUser):
    # id = ObjectIdField(verbose_name='ID')
    id = models.UUIDField(
        auto_created=True, verbose_name='ID', default=uuid.uuid4, primary_key=True)
    username = models.CharField(
        unique=True, null=False, max_length=150, verbose_name='username')
    first_name = models.CharField(
        null=False, max_length=150, verbose_name='first name')
    last_name = models.CharField(
        null=False, max_length=150, verbose_name='last name')
    email = models.EmailField(null=False, unique=True,
                              max_length=150, verbose_name='email')
    password = models.CharField(
        null=False, max_length=200, verbose_name='password')
    slug = models.SlugField(null=True)
    created_at = models.DateTimeField(
        auto_now_add=True, null=True, verbose_name='created_at')
    updated_at = models.DateTimeField(
        auto_now=True, null=True, verbose_name='updated_at')

    def __str__(self):
        return self.username

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email',
                       'password', 'first_name', 'last_name', ]


class CartModel(models.Model):
    id = models.UUIDField(
        auto_created=True, verbose_name='ID', default=uuid.uuid4, primary_key=True)
    user_id = models.ForeignKey(
        to='Users.User', on_delete=models.CASCADE, null=False, verbose_name='User ID',)
    total_price = models.BigIntegerField(
        null=False, default=0, verbose_name='Total Price')
    cart_count = models.BigIntegerField(
        null=False, default=0, verbose_name='Cart Count')

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = "Carts"


class CartItemModel(models.Model):
    id = models.UUIDField(
        auto_created=True, verbose_name='ID', default=uuid.uuid4, primary_key=True)
    cart_id = models.ForeignKey(
        to='CartModel', on_delete=models.CASCADE, null=False, verbose_name='Cart ID',)
    product_id = models.ForeignKey(
        to='product.ProductModel', on_delete=models.CASCADE, null=False, verbose_name='Product ID',)
    count = models.BigIntegerField(
        null=False, default=1, verbose_name='Count')

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = "Cart Items"
