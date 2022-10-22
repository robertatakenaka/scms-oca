# Generated by Django 3.2.12 on 2022-10-21 20:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('policy_directory', '0002_alter_policydirectory_record_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='policydirectory',
            name='date',
            field=models.DateField(blank=True, max_length=255, null=True, verbose_name='Data'),
        ),
        migrations.AddIndex(
            model_name='policydirectory',
            index=models.Index(fields=['title'], name='policy_dire_title_102ac0_idx'),
        ),
        migrations.AddIndex(
            model_name='policydirectory',
            index=models.Index(fields=['date'], name='policy_dire_date_4e898a_idx'),
        ),
        migrations.AddIndex(
            model_name='policydirectory',
            index=models.Index(fields=['practice'], name='policy_dire_practic_bb3966_idx'),
        ),
        migrations.AddIndex(
            model_name='policydirectory',
            index=models.Index(fields=['action'], name='policy_dire_action__2bf591_idx'),
        ),
        migrations.AddIndex(
            model_name='policydirectory',
            index=models.Index(fields=['classification'], name='policy_dire_classif_df2c1a_idx'),
        ),
        migrations.AddIndex(
            model_name='policydirectory',
            index=models.Index(fields=['source'], name='policy_dire_source_8639c0_idx'),
        ),
        migrations.AddIndex(
            model_name='policydirectory',
            index=models.Index(fields=['record_status'], name='policy_dire_record__322c90_idx'),
        ),
    ]
