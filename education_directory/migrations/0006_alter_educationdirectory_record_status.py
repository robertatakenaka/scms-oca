# Generated by Django 4.1.6 on 2023-04-24 14:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("education_directory", "0005_alter_educationdirectory_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="educationdirectory",
            name="record_status",
            field=models.CharField(
                blank=True,
                choices=[
                    ("", ""),
                    ("WIP", "WIP"),
                    ("TO MODERATE", "TO MODERATE"),
                    ("PUBLISHED", "PUBLISHED"),
                    ("NOT PUBLISHED", "NOT PUBLISHED"),
                ],
                max_length=255,
                null=True,
                verbose_name="Record status",
            ),
        ),
    ]
