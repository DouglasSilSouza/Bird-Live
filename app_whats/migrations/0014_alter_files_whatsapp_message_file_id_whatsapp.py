# Generated by Django 4.2.2 on 2023-06-25 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_whats', '0013_files_whatsapp_message_file_id_whatsapp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='files_whatsapp_message',
            name='file_id_whatsapp',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
