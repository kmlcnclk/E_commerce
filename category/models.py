from django.db import models
from django.template.defaultfilters import slugify
from product.models import ProductModel
import uuid
# Create your models here.


class CategoryModel(models.Model):
    id = models.UUIDField(
        auto_created=True, verbose_name='ID', default=uuid.uuid4, primary_key=True)
    name = models.CharField(null=False, max_length=200, unique=True)
    product_count = models.BigIntegerField(
        null=False, default=0, verbose_name='product_count')
    slug = models.SlugField(null=True)
    created_at = models.DateTimeField(
        auto_now_add=True, null=True, verbose_name='created_at')

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(CategoryModel, self).save(*args, **kwargs)


class CategoryImageModel(models.Model):
    id = models.UUIDField(
        auto_created=True, verbose_name='ID', default=uuid.uuid4, primary_key=True)
    image_url = models.ImageField(upload_to='category-images', null=False)
    category_id = models.ForeignKey(
        to='CategoryModel', on_delete=models.CASCADE, null=False)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = "Category Images"
