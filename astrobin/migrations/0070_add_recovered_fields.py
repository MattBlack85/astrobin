# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-10-14 15:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('astrobin', '0069_add_created_to_gear'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='recovered',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='imagerevision',
            name='recovered',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]