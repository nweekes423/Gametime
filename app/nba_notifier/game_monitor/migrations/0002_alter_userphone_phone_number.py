# Generated by Django 4.2.10 on 2024-02-11 16:53

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("game_monitor", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userphone",
            name="phone_number",
            field=models.CharField(
                blank=True,
                max_length=17,
                validators=[
                    django.core.validators.RegexValidator(
                        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
                        regex="^\\+?1?\\d{9,15}$",
                    )
                ],
            ),
        ),
    ]
