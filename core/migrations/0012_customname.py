# Generated by Django 3.2 on 2022-06-05 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_profile_cover_img'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomName',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=100)),
                ('fullname', models.CharField(max_length=100)),
            ],
        ),
    ]
