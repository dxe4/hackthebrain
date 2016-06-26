# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='WaveData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('alpha', models.FloatField()),
                ('beta', models.FloatField()),
                ('beta_theta_ratio', models.FloatField()),
                ('beta_alpha_theta_ratio', models.FloatField()),
            ],
        ),
    ]
