# Generated by Django 3.2.12 on 2022-09-06 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scholarly_articles', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='rawunpaywall',
            index=models.Index(fields=['doi'], name='scholarly_a_doi_e75c1d_idx'),
        ),
        migrations.AddIndex(
            model_name='rawunpaywall',
            index=models.Index(fields=['year'], name='scholarly_a_year_c2349f_idx'),
        ),
        migrations.AddIndex(
            model_name='rawunpaywall',
            index=models.Index(fields=['resource_type'], name='scholarly_a_resourc_0d5bcb_idx'),
        ),
    ]
