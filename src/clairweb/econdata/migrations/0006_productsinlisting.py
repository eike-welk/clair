# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-06-10 23:13
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('econdata', '0005_auto_20170520_2232'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductsInListing',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='Internal unique ID of each record.')),
                ('is_training_data', models.BooleanField(default=False, verbose_name='If true this record is used for training the product recognition algortithms.')),
                ('listing', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='econdata.Listing', verbose_name='ID of listing from which the price is taken.')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='econdata.Product', verbose_name='ID of product for which the price is recorded.')),
            ],
        ),
    ]