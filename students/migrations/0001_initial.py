# Generated by Django 5.1.3 on 2024-11-22 16:30

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
                ('name', models.CharField(default='SomeName', max_length=255)),
                ('dob', models.DateField(blank=True, null=True)),
                ('registration_date', models.DateField(auto_now_add=True)),
            ],
        ),
    ]
