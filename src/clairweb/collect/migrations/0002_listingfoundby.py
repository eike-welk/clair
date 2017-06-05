# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-16 19:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('econdata', '0003_listing_title'),
        ('collect', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ListingFoundBy',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='Internal unique ID.')),
                ('listing', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='econdata.Listing', verbose_name='The listing that was found by the model')),
                ('task', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='collect.SearchTask', verbose_name='The task that found the model')),
            ],
        ),
    ]