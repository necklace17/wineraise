# Generated by Django 3.1.7 on 2021-03-06 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wine", "0003_auto_20210306_1018"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="wine",
            name="library",
        ),
        migrations.AddField(
            model_name="wine",
            name="library",
            field=models.ManyToManyField(to="wine.Library"),
        ),
        migrations.AlterField(
            model_name="wine",
            name="name",
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
