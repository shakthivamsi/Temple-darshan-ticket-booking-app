# Generated by Django 4.2.23 on 2025-07-10 00:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('temple_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='visit_date',
            field=models.DateField(default='2023-01-01'),
            preserve_default=False,
        ),
    ]
