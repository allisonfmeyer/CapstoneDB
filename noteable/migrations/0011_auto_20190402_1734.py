# Generated by Django 2.1.5 on 2019-04-02 21:34

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('noteable', '0010_auto_20190402_1734'),
    ]

    operations = [
        migrations.AlterField(
            model_name='record',
            name='tempo',
            field=models.IntegerField(default=100, validators=[django.core.validators.MaxValueValidator(120), django.core.validators.MinValueValidator(20)]),
        ),
    ]