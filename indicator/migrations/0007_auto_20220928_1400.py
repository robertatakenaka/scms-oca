# Generated by Django 3.2.12 on 2022-09-28 14:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event_directory', '0002_alter_eventdirectory_record_status'),
        ('education_directory', '0002_alter_educationdirectory_record_status'),
        ('policy_directory', '0003_alter_policydirectory_date'),
        ('infrastructure_directory', '0002_alter_infrastructuredirectory_record_status'),
        ('indicator', '0006_auto_20220926_1349'),
    ]

    operations = [
        migrations.AddField(
            model_name='versioning',
            name='seq',
            field=models.IntegerField(blank=True, null=True, verbose_name='Sequential number'),
        ),
        migrations.AlterField(
            model_name='indicator',
            name='link',
            field=models.URLField(blank=True, null=True, verbose_name='Link'),
        ),
        migrations.AlterField(
            model_name='indicator',
            name='record_status',
            field=models.CharField(blank=True, choices=[('', ''), ('CURRENT', 'CURRENT'), ('DEACTIVATED', 'DEACTIVATED')], max_length=255, null=True, verbose_name='Record status'),
        ),
        migrations.CreateModel(
            name='Results',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('education_results', models.ManyToManyField(blank=True, to='education_directory.EducationDirectory')),
                ('event_results', models.ManyToManyField(blank=True, to='event_directory.EventDirectory')),
                ('infrastructure_results', models.ManyToManyField(blank=True, to='infrastructure_directory.InfrastructureDirectory')),
                ('policy_results', models.ManyToManyField(blank=True, to='policy_directory.PolicyDirectory')),
            ],
        ),
        migrations.AddField(
            model_name='indicator',
            name='results',
            field=models.ManyToManyField(blank=True, to='indicator.Results', verbose_name='Results'),
        ),
    ]
