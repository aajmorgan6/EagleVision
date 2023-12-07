# Generated by Django 4.2.5 on 2023-12-07 18:01

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=50, verbose_name='username')),
                ('majors', models.CharField(max_length=200, verbose_name='majors')),
                ('minors', models.CharField(blank=True, max_length=200, null=True, verbose_name='minors')),
                ('grad_year', models.CharField(max_length=4, null=True, verbose_name='graduation year')),
                ('grad_sem', models.CharField(max_length=10, null=True, verbose_name='graduation semester')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('eagle_id', models.CharField(default='', max_length=8, unique=True, verbose_name='eagleid')),
                ('is_superuser', models.BooleanField(default=False)),
                ('is_student', models.BooleanField(default=True)),
            ],
        ),
    ]
