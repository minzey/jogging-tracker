# Generated by Django 3.2.5 on 2021-08-05 18:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('joggingapi', '0002_jogrecord_jogger_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jogrecord',
            name='weather',
            field=models.CharField(max_length=255),
        ),
    ]
