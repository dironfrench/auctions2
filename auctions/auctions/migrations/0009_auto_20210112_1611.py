# Generated by Django 2.2.14 on 2021-01-12 22:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0008_auto_20210112_1509'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='desc',
            field=models.TextField(),
        ),
    ]