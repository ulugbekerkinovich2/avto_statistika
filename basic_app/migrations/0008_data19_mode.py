# Generated by Django 4.2.5 on 2023-12-18 15:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('basic_app', '0007_alter_upload_file5_options_alter_upload_file5_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='data19',
            name='mode',
            field=models.CharField(max_length=20, null=True),
        ),
    ]