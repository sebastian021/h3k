# Generated by Django 5.0.4 on 2025-02-26 23:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('league', '0006_teamstat_clean_sheet_away_teamstat_clean_sheet_home_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='league',
            old_name='league_name',
            new_name='symbol',
        ),
    ]
