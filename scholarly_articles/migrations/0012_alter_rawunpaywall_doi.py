# Generated by Django 3.2.12 on 2022-09-22 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scholarly_articles', '0011_auto_20220922_1336'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rawunpaywall',
            name='doi',
            field=models.CharField(max_length=100, verbose_name='DOI'),
        ),
    ]
