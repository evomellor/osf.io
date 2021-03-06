# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-10-28 15:14
from __future__ import unicode_literals

from django.db import migrations
import osf.utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('osf', '0012_auto_20161028_0908'),
    ]

    operations = [
        migrations.AlterField(
            model_name='externalaccount',
            name='display_name',
            field=osf.utils.fields.EncryptedTextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='externalaccount',
            name='oauth_key',
            field=osf.utils.fields.EncryptedTextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='externalaccount',
            name='oauth_secret',
            field=osf.utils.fields.EncryptedTextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='externalaccount',
            name='profile_url',
            field=osf.utils.fields.EncryptedTextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='externalaccount',
            name='refresh_token',
            field=osf.utils.fields.EncryptedTextField(blank=True, null=True),
        ),
    ]
