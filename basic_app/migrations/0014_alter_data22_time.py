# Generated by Django 4.2.5 on 2024-03-23 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('basic_app', '0013_alter_data23_file_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='data22',
            name='time',
            field=models.DateTimeField(auto_created=True, blank=True, null=True, verbose_name='data yaratilgan vaqti'),
        ),
    ]
