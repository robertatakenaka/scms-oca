# Generated by Django 3.2.12 on 2022-10-28 12:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('usefulmodels', '0004_alter_country_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='state',
            name='region',
            field=models.CharField(blank=True, choices=[('', ''), ('Norte', 'Norte'), ('Nordeste', 'Nordeste'), ('Centro-oeste', 'Centro-Oeste'), ('Sudeste', 'Sudeste'), ('Sul', 'Sul'), ('ALL', 'ALL'), ('NOT APPLICABLE', 'NOT_APPLICABLE'), ('UNDEFINED', 'UNDEFINED')], max_length=255, null=True, verbose_name='Região'),
        ),
        migrations.CreateModel(
            name='ActionAndPractice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('classification', models.CharField(blank=True, choices=[('', ''), ('curso livre', 'curso livre'), ('disciplina de graduação', 'disciplina de graduação'), ('disciplina de lato sensu', 'disciplina de lato sensu'), ('disciplina de stricto sensu', 'disciplina de stricto sensu'), ('encontro', 'encontro'), ('conferência', 'conferência'), ('congresso', 'congresso'), ('workshop', 'workshop'), ('seminário', 'seminário'), ('outros', 'outros'), ('portal', 'Portal'), ('plataforma', 'Plataforma'), ('servidor', 'Servidor'), ('repositório', 'Repositório'), ('serviço', 'Serviço'), ('promoção', 'promoção'), ('posicionamento', 'posicionamento'), ('mandato', 'mandato'), ('geral', 'geral'), ('outras', 'Outras')], max_length=255, null=True, verbose_name='Classificação')),
                ('action', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='usefulmodels.action', verbose_name='Ação')),
                ('practice', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='usefulmodels.practice', verbose_name='Practice')),
            ],
        ),
        migrations.AddIndex(
            model_name='actionandpractice',
            index=models.Index(fields=['practice'], name='usefulmodel_practic_b91105_idx'),
        ),
        migrations.AddIndex(
            model_name='actionandpractice',
            index=models.Index(fields=['action'], name='usefulmodel_action__48c3a3_idx'),
        ),
        migrations.AddIndex(
            model_name='actionandpractice',
            index=models.Index(fields=['classification'], name='usefulmodel_classif_4a4920_idx'),
        ),
    ]
