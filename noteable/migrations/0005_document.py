# Generated by Django 2.1.5 on 2019-03-28 19:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('noteable', '0004_record'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=255)),
                ('document', models.FileField(upload_to='documents/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
