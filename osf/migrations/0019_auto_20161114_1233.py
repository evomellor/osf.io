# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-11-14 18:33
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('osf', '0018_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='preprintservice',
            name='node',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='preprints', to='osf.AbstractNode'),
        ),
    ]
