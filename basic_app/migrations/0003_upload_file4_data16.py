# Generated by Django 4.2.5 on 2023-10-11 15:22

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('basic_app', '0002_manufacture_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='Upload_File4',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='files4/')),
            ],
            options={
                'verbose_name_plural': 'upload_file2016',
                'db_table': 'upload_file2016',
            },
        ),
        migrations.CreateModel(
            name='Data16',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateField(auto_created=True, default=datetime.date.today, verbose_name='data yaratilgan vaqt')),
                ('sana', models.DateField(default=datetime.date.today)),
                ('country', models.CharField(max_length=255)),
                ('count', models.PositiveIntegerField(default=0)),
                ('file_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='basic_app.upload_file3')),
                ('mark', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='basic_app.mark')),
                ('model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='data16', to='basic_app.model1')),
            ],
            options={
                'verbose_name_plural': 'data2016',
                'db_table': 'data2016',
            },
        ),
    ]