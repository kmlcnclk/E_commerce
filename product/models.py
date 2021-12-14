from django.db import models
from django.template.defaultfilters import slugify
import uuid

# Create your models here.


class ProductModel(models.Model):
    id = models.UUIDField(
        auto_created=True, verbose_name='ID', default=uuid.uuid4, primary_key=True)
    name = models.CharField(null=False, max_length=300, verbose_name='name')
    price = models.FloatField(verbose_name='price', null=False)
    like_count = models.BigIntegerField(
        null=False, default=0, verbose_name='like_count')
    slug = models.SlugField(null=True)
    seller_id = models.ForeignKey(
        to='seller_account.SellerAccountModel', on_delete=models.CASCADE, null=False)
    category_id = models.ForeignKey(
        to='category.CategoryModel', on_delete=models.CASCADE, null=False)
    created_at = models.DateTimeField(
        auto_now_add=True, null=True, verbose_name='created_at')
    updated_at = models.DateTimeField(
        auto_now=True, null=True, verbose_name='updated_at')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Products"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(ProductModel, self).save(*args, **kwargs)


class ProductImageModel(models.Model):
    id = models.UUIDField(
        auto_created=True, verbose_name='ID', default=uuid.uuid4, primary_key=True)
    image_url = models.ImageField(upload_to='product-images', null=False)
    product_id = models.ForeignKey(
        to='ProductModel', on_delete=models.CASCADE, null=False)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = "Product Images"


class LikeModel(models.Model):
    id = models.UUIDField(
        auto_created=True, verbose_name='ID', default=uuid.uuid4, primary_key=True)
    user_id = models.ForeignKey(
        to='Users.User', on_delete=models.CASCADE, null=False)
    product_id = models.ForeignKey(
        to='product.ProductModel', on_delete=models.CASCADE, null=False)
    category_id = models.ForeignKey(
        to='category.CategoryModel', on_delete=models.CASCADE, null=False)

    def __str__(self):
        return str(self.user_id)

    class Meta:
        verbose_name_plural = "Likes"
