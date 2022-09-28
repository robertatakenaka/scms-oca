# Generated by Django 3.2.12 on 2022-09-26 13:49

from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('usefulmodels', '0004_alter_country_options'),
        ('taggit', '0004_alter_taggeditem_content_type_alter_taggeditem_tag'),
        ('institution', '0003_alter_institution_institution_type'),
        ('location', '0003_alter_location_country'),
        ('indicator', '0005_indicator_chronology'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='creator',
        ),
        migrations.RemoveField(
            model_name='post',
            name='updated_by',
        ),
        migrations.RemoveIndex(
            model_name='indicator',
            name='indicator_i_name_bf54a8_idx',
        ),
        migrations.RemoveField(
            model_name='indicator',
            name='chronology',
        ),
        migrations.RemoveField(
            model_name='indicator',
            name='geographic_context',
        ),
        migrations.RemoveField(
            model_name='indicator',
            name='institutional_context',
        ),
        migrations.RemoveField(
            model_name='indicator',
            name='name',
        ),
        migrations.RemoveField(
            model_name='indicator',
            name='post',
        ),
        migrations.RemoveField(
            model_name='indicator',
            name='thematic_area',
        ),
        migrations.RemoveField(
            model_name='versioning',
            name='record_status',
        ),
        migrations.AddField(
            model_name='indicator',
            name='classification',
            field=models.CharField(blank=True, choices=[('', ''), ('encontro', 'encontro'), ('conferência', 'conferência'), ('congresso', 'congresso'), ('workshop', 'workshop'), ('seminário', 'seminário'), ('outros', 'outros')], max_length=255, null=True, verbose_name='Classificação'),
        ),
        migrations.AddField(
            model_name='indicator',
            name='description',
            field=models.TextField(blank=True, max_length=1000, null=True, verbose_name='Descrição'),
        ),
        migrations.AddField(
            model_name='indicator',
            name='end_date',
            field=models.DateField(blank=True, max_length=255, null=True, verbose_name='Data de fim'),
        ),
        migrations.AddField(
            model_name='indicator',
            name='institutions',
            field=models.ManyToManyField(blank=True, to='institution.Institution', verbose_name='Instituição'),
        ),
        migrations.AddField(
            model_name='indicator',
            name='keywords',
            field=taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Palavra-chave'),
        ),
        migrations.AddField(
            model_name='indicator',
            name='link',
            field=models.URLField(default='', verbose_name='Link'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='indicator',
            name='locations',
            field=models.ManyToManyField(blank=True, to='location.Location', verbose_name='Localização'),
        ),
        migrations.AddField(
            model_name='indicator',
            name='record_status',
            field=models.CharField(blank=True, choices=[('', ''), ('WIP', 'WIP'), ('TO MODERATE', 'TO MODERATE'), ('PUBLISHED', 'PUBLISHED')], max_length=255, null=True, verbose_name='Record status'),
        ),
        migrations.AddField(
            model_name='indicator',
            name='source',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Origem'),
        ),
        migrations.AddField(
            model_name='indicator',
            name='start_date',
            field=models.DateField(blank=True, max_length=255, null=True, verbose_name='Data de início'),
        ),
        migrations.AddField(
            model_name='indicator',
            name='thematic_areas',
            field=models.ManyToManyField(blank=True, to='usefulmodels.ThematicArea', verbose_name='Área temática'),
        ),
        migrations.AddField(
            model_name='indicator',
            name='title',
            field=models.CharField(default='', max_length=255, verbose_name='Título'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='indicator',
            name='action',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='usefulmodels.action', verbose_name='Ação'),
        ),
        migrations.AlterField(
            model_name='indicator',
            name='practice',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='usefulmodels.practice', verbose_name='Practice'),
        ),
        migrations.AddIndex(
            model_name='indicator',
            index=models.Index(fields=['title'], name='indicator_i_title_96c026_idx'),
        ),
        migrations.AddIndex(
            model_name='indicator',
            index=models.Index(fields=['start_date'], name='indicator_i_start_d_618ee6_idx'),
        ),
        migrations.AddIndex(
            model_name='indicator',
            index=models.Index(fields=['end_date'], name='indicator_i_end_dat_0cdcf7_idx'),
        ),
        migrations.DeleteModel(
            name='Post',
        ),
    ]
