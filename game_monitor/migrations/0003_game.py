# Generated by Django 4.2.10 on 2024-02-19 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game_monitor', '0002_alter_userphone_phone_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('date', models.DateField()),
                ('home_team', models.CharField(max_length=255)),
                ('away_team', models.CharField(max_length=255)),
                ('home_team_score', models.IntegerField()),
                ('away_team_score', models.IntegerField()),
                ('game_clock', models.CharField(max_length=10)),
                ('period', models.IntegerField()),
            ],
        ),
    ]
