# Generated by Django 4.2.2 on 2023-06-26 22:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_whats', '0015_alter_files_whatsapp_message_file_id_whatsapp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='files_whatsapp_message',
            name='file_message',
            field=models.BinaryField(),
        ),
    ]
