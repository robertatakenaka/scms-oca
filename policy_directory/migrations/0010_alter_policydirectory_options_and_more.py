# Generated by Django 4.1.6 on 2023-05-25 10:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("policy_directory", "0009_alter_policydirectory_options"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="policydirectory",
            options={
                "permissions": (
                    ("must_be_moderate", "Must be moderated"),
                    ("can_edit_title", "Can edit title"),
                    ("can_edit_link", "Can edit link"),
                    ("can_edit_description", "Can edit description"),
                    ("can_edit_locations", "Can edit locations"),
                    ("can_edit_institutions", "Can edit institutions"),
                    ("can_edit_thematic_areas", "Can edit thematic_areas"),
                    ("can_edit_practice", "Can edit practice"),
                    ("can_edit_action", "Can edit action"),
                    ("can_edit_classification", "Can edit classification"),
                    ("can_edit_keywords", "Can edit keywords"),
                    ("can_edit_record_status", "Can edit record_status"),
                    ("can_edit_source", "Can edit source"),
                    (
                        "can_edit_institutional_contribution",
                        "Can edit institutional_contribution",
                    ),
                    ("can_edit_notes", "Can edit notes"),
                ),
                "verbose_name": "Policy Data",
                "verbose_name_plural": "Policy Data",
            },
        ),
        migrations.AlterModelOptions(
            name="policydirectoryfile",
            options={"verbose_name_plural": "Policy Data Upload"},
        ),
    ]
