# Generated by Django 2.1.5 on 2019-04-22 15:58

import django.core.validators
from django.db import migrations, models
import noteable.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ABCSong',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=50)),
                ('time_sig', models.CharField(default='4/4', max_length=5)),
                ('length', models.CharField(default='1/4', max_length=5)),
                ('key', models.CharField(default='Dmaj', max_length=4)),
                ('song', models.CharField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('recording', models.FileField(upload_to='recordings/', validators=[noteable.validators.validate_wav_extension])),
                ('tempo', models.IntegerField(default=100, validators=[django.core.validators.MaxValueValidator(120), django.core.validators.MinValueValidator(20)])),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Sheet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sheet', models.FileField(upload_to='sheets/', validators=[noteable.validators.validate_pdf_extension])),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
