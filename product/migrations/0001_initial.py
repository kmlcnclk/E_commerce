# Generated by Django 3.2.9 on 2021-12-05 10:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('category', '0001_initial'),
        ('seller_account', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductModel',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300, verbose_name='name')),
                ('price', models.FloatField(verbose_name='price')),
                ('like_count', models.BigIntegerField(default=0, verbose_name='like_count')),
                ('slug', models.SlugField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='created_at')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='updated_at')),
                ('category_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='category.categorymodel')),
                ('seller_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='seller_account.selleraccountmodel')),
            ],
            options={
                'verbose_name_plural': 'Products',
            },
        ),
        migrations.CreateModel(
            name='ProductImageModel',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_url', models.ImageField(upload_to='product-images')),
                ('product_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.productmodel')),
            ],
            options={
                'verbose_name_plural': 'Product Images',
            },
        ),
        migrations.CreateModel(
            name='LikeModel',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='category.categorymodel')),
                ('product_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.productmodel')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Likes',
            },
        ),
    ]
