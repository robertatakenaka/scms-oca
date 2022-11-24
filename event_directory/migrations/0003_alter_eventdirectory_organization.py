# Generated by Django 3.2.12 on 2022-11-19 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('institution', '0004_institution_source'),
        ('event_directory', '0002_alter_eventdirectory_record_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventdirectory',
            name='organization',
            field=models.ManyToManyField(blank=True, help_text='Instituições responsáveis pela organização do evento.', to='institution.Institution', verbose_name='Instituição'),
        ),
    ]
