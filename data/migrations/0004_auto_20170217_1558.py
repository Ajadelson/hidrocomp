# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-17 17:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0003_auto_20170215_2312'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serieoriginal',
            name='serie_temporal_id',
            field=models.IntegerField(),
        ),
    ]