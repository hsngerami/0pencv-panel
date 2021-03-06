# Generated by Django 3.1.2 on 2020-10-15 16:41

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Movement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_picture', models.ImageField(upload_to='', verbose_name='Start Picture')),
                ('end_picture', models.ImageField(upload_to='', verbose_name='End Picture')),
                ('datetime', models.DateTimeField(auto_now=True, verbose_name='Date and Time')),
            ],
        ),
    ]
