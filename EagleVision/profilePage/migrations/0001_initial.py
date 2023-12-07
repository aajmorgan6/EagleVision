# Generated by Django 4.2.5 on 2023-12-07 18:01

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SystemConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('system_open', models.BooleanField(default=True)),
                ('semester_code', models.CharField(max_length=6)),
                ('semester_name', models.CharField(max_length=50)),
            ],
        ),
    ]
