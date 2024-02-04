# Generated by Django 4.2.2 on 2023-09-20 03:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_authentication', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cadastro',
            name='cep',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cadastro',
            name='code_area',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cadastro',
            name='complemento',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='cadastro',
            name='cpf_cnpj',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cadastro',
            name='date_birthday',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cadastro',
            name='endereco',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='cadastro',
            name='number',
            field=models.CharField(blank=True, max_length=8, null=True),
        ),
        migrations.AddField(
            model_name='cadastro',
            name='phone',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='cadastro',
            name='type_document',
            field=models.CharField(blank=True, choices=[('cpf', 'CPF'), ('cnpj', 'CNPJ')], max_length=5, null=True),
        ),
        migrations.AlterField(
            model_name='cadastro',
            name='first_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='cadastro',
            name='last_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]