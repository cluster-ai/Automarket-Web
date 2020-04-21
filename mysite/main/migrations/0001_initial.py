# Generated by Django 3.0.5 on 2020-04-21 22:54

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DemoKey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name_plural': 'Demo Keys',
            },
        ),
        migrations.CreateModel(
            name='HistoricalData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('index_id', models.CharField(max_length=200)),
                ('file_name', models.CharField(max_length=200)),
                ('file_path', models.CharField(max_length=200)),
                ('symbol_id', models.CharField(max_length=200)),
                ('exchange_id', models.CharField(max_length=200)),
                ('asset_id_quote', models.CharField(max_length=200)),
                ('asset_id_base', models.CharField(max_length=200)),
                ('period_id', models.CharField(max_length=200)),
                ('time_increment', models.PositiveIntegerField()),
                ('data_points', models.PositiveIntegerField()),
                ('data_start', models.CharField(max_length=200)),
                ('data_end', models.CharField(max_length=200)),
            ],
            options={
                'verbose_name_plural': 'Historical Data',
            },
        ),
    ]
