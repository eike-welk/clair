# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-13 20:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('econdata', '0002_auto_20170501_1855'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='title',
            field=models.CharField(default='', max_length=128, verbose_name='Short description of listing.'),
            preserve_default=False,
        ),
    ]