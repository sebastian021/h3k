# Generated by Django 5.0.4 on 2025-02-10 09:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('league', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Table',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rank', models.IntegerField()),
                ('points', models.IntegerField()),
                ('goals_diff', models.IntegerField()),
                ('group', models.CharField(max_length=100)),
                ('form', models.CharField(max_length=50)),
                ('status', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=100)),
                ('played', models.IntegerField()),
                ('win', models.IntegerField()),
                ('draw', models.IntegerField()),
                ('lose', models.IntegerField()),
                ('goals_for', models.IntegerField()),
                ('goals_against', models.IntegerField()),
                ('last_update', models.DateTimeField()),
                ('league', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='league.league')),
                ('season', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='league.season')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='league.team')),
            ],
        ),
    ]
