# Generated by Django 3.1.7 on 2021-03-16 06:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wine", "0007_auto_20210308_1903"),
    ]

    operations = [
        migrations.AlterField(
            model_name="wine",
            name="libraries",
            field=models.ManyToManyField(
                related_name="wines", to="wine.Library"
            ),
        ),
    ]
