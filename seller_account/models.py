from django.db import models
from django.template.defaultfilters import slugify
# Create your models here.


class SellerAccountModel(models.Model):
    user_id = models.OneToOneField(
        to='Users.User', on_delete=models.CASCADE, null=False, primary_key=True, verbose_name='ID',)
    seller_name = models.CharField(
        max_length=150, null=False, verbose_name='seller name')
    slug = models.SlugField(null=True)
    created_at = models.DateTimeField(
        auto_now_add=True, null=True, verbose_name='created_at')
    updated_at = models.DateTimeField(
        auto_now=True, null=True, verbose_name='updated_at')

    def __str__(self):
        return self.seller_name

    class Meta:
        verbose_name_plural = "Seller Account"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.seller_name)
        super(SellerAccountModel, self).save(*args, **kwargs)
