# Generated by Django 4.1.6 on 2023-07-16 23:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("article", "0007_alter_affiliation_name"),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name="affiliation",
            name="article_aff_name_d033b1_idx",
        ),
    ]
