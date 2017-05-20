# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-20 22:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('econdata', '0003_listing_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='description',
            field=models.TextField(blank=True, default='', verbose_name='Long description of the listing.'),
        ),
        migrations.AlterField(
            model_name='listing',
            name='id_site',
            field=models.CharField(max_length=44, verbose_name="the listing's ID on the remote site."),
        ),
        migrations.AlterField(
            model_name='listing',
            name='title',
            field=models.CharField(max_length=128, verbose_name='Short description of the listing.'),
        ),
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(blank=True, default='', verbose_name='Description of the product. Any text.'),
        ),
    ]
