# Generated by Django 4.1.6 on 2023-07-24 09:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("institution", "0006_institutionsource_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="institutionsource",
            name="country_code",
            field=models.CharField(
                blank=True, max_length=50, null=True, verbose_name="Country code"
            ),
        ),
        migrations.AddField(
            model_name="institutionsource",
            name="type",
            field=models.CharField(
                blank=True, max_length=255, null=True, verbose_name="type"
            ),
        ),
    ]
