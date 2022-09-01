# Generated by Django 1.11.20 on 2019-04-29 03:26

# this file is auto-generated so don't do flake8 on it
# flake8: noqa
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django_celery_beat.validators
import timezone_field.fields


class Migration(migrations.Migration):

    dependencies = [
        ('django_celery_beat', '0009_periodictask_headers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crontabschedule',
            name='day_of_month',
            field=models.CharField(default='*', help_text='Cron Days Of The Month to Run. Use "*" for "all". (Example: "1,15")', max_length=124, validators=[django_celery_beat.validators.day_of_month_validator], verbose_name='Day(s) Of The Month'),
        ),
        migrations.AlterField(
            model_name='crontabschedule',
            name='day_of_week',
            field=models.CharField(default='*', help_text='Cron Days Of The Week to Run. Use "*" for "all". (Example: "0,5")', max_length=64, validators=[django_celery_beat.validators.day_of_week_validator], verbose_name='Day(s) Of The Week'),
        ),
        migrations.AlterField(
            model_name='crontabschedule',
            name='hour',
            field=models.CharField(default='*', help_text='Cron Hours to Run. Use "*" for "all". (Example: "8,20")', max_length=96, validators=[django_celery_beat.validators.hour_validator], verbose_name='Hour(s)'),
        ),
        migrations.AlterField(
            model_name='crontabschedule',
            name='minute',
            field=models.CharField(default='*', help_text='Cron Minutes to Run. Use "*" for "all". (Example: "0,30")', max_length=240, validators=[django_celery_beat.validators.minute_validator], verbose_name='Minute(s)'),
        ),
        migrations.AlterField(
            model_name='crontabschedule',
            name='month_of_year',
            field=models.CharField(default='*', help_text='Cron Months Of The Year to Run. Use "*" for "all". (Example: "0,6")', max_length=64, validators=[django_celery_beat.validators.month_of_year_validator], verbose_name='Month(s) Of The Year'),
        ),
        migrations.AlterField(
            model_name='crontabschedule',
            name='timezone',
            field=timezone_field.fields.TimeZoneField(default='UTC', help_text='Timezone to Run the Cron Schedule on.  Default is UTC.', verbose_name='Cron Timezone'),
        ),
        migrations.AlterField(
            model_name='intervalschedule',
            name='every',
            field=models.IntegerField(help_text='Number of interval periods to wait before running the task again', validators=[django.core.validators.MinValueValidator(1)], verbose_name='Number of Periods'),
        ),
        migrations.AlterField(
            model_name='intervalschedule',
            name='period',
            field=models.CharField(choices=[('days', 'Days'), ('hours', 'Hours'), ('minutes', 'Minutes'), ('seconds', 'Seconds'), ('microseconds', 'Microseconds')], help_text='The type of period between task runs (Example: days)', max_length=24, verbose_name='Interval Period'),
        ),
        migrations.AlterField(
            model_name='periodictask',
            name='args',
            field=models.TextField(blank=True, default='[]', help_text='JSON encoded positional arguments (Example: ["arg1", "arg2"])', verbose_name='Positional Arguments'),
        ),
        migrations.AlterField(
            model_name='periodictask',
            name='crontab',
            field=models.ForeignKey(blank=True, help_text='Crontab Schedule to run the task on.  Set only one schedule type, leave the others null.', null=True, on_delete=django.db.models.deletion.CASCADE, to='django_celery_beat.CrontabSchedule', verbose_name='Crontab Schedule'),
        ),
        migrations.AlterField(
            model_name='periodictask',
            name='date_changed',
            field=models.DateTimeField(auto_now=True, help_text='Datetime that this PeriodicTask was last modified', verbose_name='Last Modified'),
        ),
        migrations.AlterField(
            model_name='periodictask',
            name='description',
            field=models.TextField(blank=True, help_text='Detailed description about the details of this Periodic Task', verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='periodictask',
            name='enabled',
            field=models.BooleanField(default=True, help_text='Set to False to disable the schedule', verbose_name='Enabled'),
        ),
        migrations.AlterField(
            model_name='periodictask',
            name='exchange',
            field=models.CharField(blank=True, default=None, help_text='Override Exchange for low-level AMQP routing', max_length=200, null=True, verbose_name='Exchange'),
        ),
        migrations.AlterField(
            model_name='periodictask',
            name='expires',
            field=models.DateTimeField(blank=True, help_text='Datetime after which the schedule will no longer trigger the task to run', null=True, verbose_name='Expires Datetime'),
        ),
        migrations.AlterField(
            model_name='periodictask',
            name='headers',
            field=models.TextField(blank=True, default='{}', help_text='JSON encoded message headers for the AMQP message.', verbose_name='AMQP Message Headers'),
        ),
        migrations.AlterField(
            model_name='periodictask',
            name='interval',
            field=models.ForeignKey(blank=True, help_text='Interval Schedule to run the task on.  Set only one schedule type, leave the others null.', null=True, on_delete=django.db.models.deletion.CASCADE, to='django_celery_beat.IntervalSchedule', verbose_name='Interval Schedule'),
        ),
        migrations.AlterField(
            model_name='periodictask',
            name='kwargs',
            field=models.TextField(blank=True, default='{}', help_text='JSON encoded keyword arguments (Example: {"argument": "value"})', verbose_name='Keyword Arguments'),
        ),
        migrations.AlterField(
            model_name='periodictask',
            name='last_run_at',
            field=models.DateTimeField(blank=True, editable=False, help_text='Datetime that the schedule last triggered the task to run. Reset to None if enabled is set to False.', null=True, verbose_name='Last Run Datetime'),
        ),
        migrations.AlterField(
            model_name='periodictask',
            name='name',
            field=models.CharField(help_text='Short Description For This Task', max_length=200, unique=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='periodictask',
            name='one_off',
            field=models.BooleanField(default=False, help_text='If True, the schedule will only run the task a single time', verbose_name='One-off Task'),
        ),
        migrations.AlterField(
            model_name='periodictask',
            name='priority',
            field=models.PositiveIntegerField(blank=True, default=None, help_text='Priority Number between 0 and 255. Supported by: RabbitMQ, Redis (priority reversed, 0 is highest).', null=True, validators=[django.core.validators.MaxValueValidator(255)], verbose_name='Priority'),
        ),
        migrations.AlterField(
            model_name='periodictask',
            name='queue',
            field=models.CharField(blank=True, default=None, help_text='Queue defined in CELERY_TASK_QUEUES. Leave None for default queuing.', max_length=200, null=True, verbose_name='Queue Override'),
        ),
        migrations.AlterField(
            model_name='periodictask',
            name='routing_key',
            field=models.CharField(blank=True, default=None, help_text='Override Routing Key for low-level AMQP routing', max_length=200, null=True, verbose_name='Routing Key'),
        ),
        migrations.AlterField(
            model_name='periodictask',
            name='solar',
            field=models.ForeignKey(blank=True, help_text='Solar Schedule to run the task on.  Set only one schedule type, leave the others null.', null=True, on_delete=django.db.models.deletion.CASCADE, to='django_celery_beat.SolarSchedule', verbose_name='Solar Schedule'),
        ),
        migrations.AlterField(
            model_name='periodictask',
            name='start_time',
            field=models.DateTimeField(blank=True, help_text='Datetime when the schedule should begin triggering the task to run', null=True, verbose_name='Start Datetime'),
        ),
        migrations.AlterField(
            model_name='periodictask',
            name='task',
            field=models.CharField(help_text='The Name of the Celery Task that Should be Run.  (Example: "proj.tasks.import_contacts")', max_length=200, verbose_name='Task Name'),
        ),
        migrations.AlterField(
            model_name='periodictask',
            name='total_run_count',
            field=models.PositiveIntegerField(default=0, editable=False, help_text='Running count of how many times the schedule has triggered the task', verbose_name='Total Run Count'),
        ),
        migrations.AlterField(
            model_name='solarschedule',
            name='event',
            field=models.CharField(choices=[('dawn_astronomical', 'dawn_astronomical'), ('dawn_civil', 'dawn_civil'), ('dawn_nautical', 'dawn_nautical'), ('dusk_astronomical', 'dusk_astronomical'), ('dusk_civil', 'dusk_civil'), ('dusk_nautical', 'dusk_nautical'), ('solar_noon', 'solar_noon'), ('sunrise', 'sunrise'), ('sunset', 'sunset')], help_text='The type of solar event when the job should run', max_length=24, verbose_name='Solar Event'),
        ),
        migrations.AlterField(
            model_name='solarschedule',
            name='latitude',
            field=models.DecimalField(decimal_places=6, help_text='Run the task when the event happens at this latitude', max_digits=9, validators=[django.core.validators.MinValueValidator(-90), django.core.validators.MaxValueValidator(90)], verbose_name='Latitude'),
        ),
        migrations.AlterField(
            model_name='solarschedule',
            name='longitude',
            field=models.DecimalField(decimal_places=6, help_text='Run the task when the event happens at this longitude', max_digits=9, validators=[django.core.validators.MinValueValidator(-180), django.core.validators.MaxValueValidator(180)], verbose_name='Longitude'),
        ),
    ]
