# Generated by Django 3.1.5 on 2021-01-09 20:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20210109_2018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='his_followers',
            field=models.OneToOneField(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='his_followers', to='core.followers'),
        ),
    ]
