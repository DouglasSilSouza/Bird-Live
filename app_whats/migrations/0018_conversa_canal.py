# Generated by Django 4.2.2 on 2023-08-23 19:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_whats', '0017_alter_files_whatsapp_message_file_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversa',
            name='canal',
            field=models.CharField(choices=[('wh', 'WhatsApp'), ('tl', 'Telegram')], default='whatsapp', max_length=20),
            preserve_default=False,
        ),
    ]
