# Generated by Django 5.0.1 on 2024-02-03 09:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_authentication', '0005_cadastro_bairro'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cadastro',
            name='cep',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]