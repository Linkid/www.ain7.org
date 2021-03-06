# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-30 23:26
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('annuaire', '0002_auto_20160331_0126'),
        ('groups', '0001_initial'),
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventOrganizer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('send_email_for_new_subscriptions', models.BooleanField(default=False, verbose_name="email en cas d'inscription")),
            ],
        ),
        migrations.CreateModel(
            name='NewsItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_change_at', models.DateTimeField(blank=True, editable=False, verbose_name='Modifi\xe9 pour la derni\xe8re fois \xe0')),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('title', models.CharField(max_length=100, unique=True, verbose_name='titre')),
                ('body', models.TextField(verbose_name='corps')),
                ('shorttext', models.CharField(blank=True, max_length=500, null=True, verbose_name='Texte court')),
                ('image', models.ImageField(blank=True, null=True, upload_to=b'data', verbose_name='image')),
                ('creation_date', models.DateTimeField(default=datetime.datetime.today, editable=False, verbose_name='date')),
                ('date', models.DateTimeField(blank=True, null=True, verbose_name='date')),
                ('location', models.CharField(blank=True, max_length=60, null=True, verbose_name='Lieu')),
                ('status', models.IntegerField(blank=True, choices=[(0, 'projet'), (1, 'confirm\xe9'), (2, 'annul\xe9')], null=True, verbose_name='\xe9tat')),
                ('contact_email', models.EmailField(blank=True, max_length=50, null=True, verbose_name='email de contact')),
                ('link', models.CharField(blank=True, max_length=60, null=True, verbose_name='lien externe')),
                ('pictures_gallery', models.CharField(blank=True, max_length=100, null=True, verbose_name='Galerie photos')),
                ('rsvp_question', models.CharField(blank=True, max_length=100, null=True, verbose_name='question suppl\xe9mentaire')),
                ('rsvp_begin', models.DateField(blank=True, null=True, verbose_name='d\xe9but des inscriptions')),
                ('rsvp_end', models.DateField(blank=True, null=True, verbose_name='fin des inscriptions')),
                ('rsvp_multiple', models.BooleanField(default=True)),
                ('groups', models.ManyToManyField(blank=True, related_name='events', to='groups.Group', verbose_name='groupes')),
                ('last_change_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='last_changed_newsitem', to='annuaire.Person', verbose_name='Auteur de la derni\xe8re modification')),
                ('package', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.Package')),
            ],
            options={
                'ordering': ['-creation_date'],
                'verbose_name': 'actualit\xe9',
            },
        ),
        migrations.CreateModel(
            name='RSVPAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('yes', models.BooleanField(default=False)),
                ('no', models.BooleanField(default=False)),
                ('maybe', models.BooleanField(default=False)),
                ('number', models.IntegerField(default=1, verbose_name='Nombre de personnes')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rsvpanswers_created', to='annuaire.Person')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='news.NewsItem')),
                ('payment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.Payment')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annuaire.Person')),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rsvpanswers_updated', to='annuaire.Person')),
            ],
        ),
        migrations.AddField(
            model_name='eventorganizer',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event_organizers', to='news.NewsItem', verbose_name='\xe9v\xe9nement'),
        ),
        migrations.AddField(
            model_name='eventorganizer',
            name='organizer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='organized_events', to='annuaire.Person', verbose_name='organisateur'),
        ),
    ]
