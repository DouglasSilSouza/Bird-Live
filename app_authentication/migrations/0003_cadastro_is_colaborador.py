# Generated by Django 4.2.2 on 2023-10-09 23:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_authentication', '0002_cadastro_cep_cadastro_code_area_cadastro_complemento_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cadastro',
            name='is_colaborador',
            field=models.BooleanField(default=False),
        ),
    ]