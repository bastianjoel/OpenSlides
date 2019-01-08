# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-02 01:22
from __future__ import unicode_literals

import django.db.models.deletion
import jsonfield.fields
from django.conf import settings
from django.db import migrations, models

import openslides.utils.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("mediafiles", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("prefix", models.CharField(blank=True, max_length=32)),
            ],
            options={"ordering": ["prefix"], "default_permissions": ()},
            bases=(openslides.utils.models.RESTModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name="Motion",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "identifier",
                    models.CharField(
                        blank=True, max_length=255, null=True, unique=True
                    ),
                ),
                ("identifier_number", models.IntegerField(null=True)),
            ],
            options={
                "verbose_name": "Motion",
                "permissions": (
                    ("can_see", "Can see motions"),
                    ("can_create", "Can create motions"),
                    ("can_support", "Can support motions"),
                    ("can_manage", "Can manage motions"),
                ),
                "ordering": ("identifier",),
                "default_permissions": (),
            },
            bases=(openslides.utils.models.RESTModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name="MotionLog",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("message_list", jsonfield.fields.JSONField()),
                ("time", models.DateTimeField(auto_now=True)),
                (
                    "motion",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="log_messages",
                        to="motions.Motion",
                    ),
                ),
                (
                    "person",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ["-time"], "default_permissions": ()},
            bases=(openslides.utils.models.RESTModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name="MotionOption",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                )
            ],
            options={"default_permissions": ()},
            bases=(openslides.utils.models.RESTModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name="MotionPoll",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "votesvalid",
                    openslides.utils.models.MinMaxIntegerField(blank=True, null=True),
                ),
                (
                    "votesinvalid",
                    openslides.utils.models.MinMaxIntegerField(blank=True, null=True),
                ),
                (
                    "votescast",
                    openslides.utils.models.MinMaxIntegerField(blank=True, null=True),
                ),
                (
                    "motion",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="polls",
                        to="motions.Motion",
                    ),
                ),
            ],
            options={"default_permissions": ()},
            bases=(openslides.utils.models.RESTModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name="MotionVersion",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("version_number", models.PositiveIntegerField(default=1)),
                ("title", models.CharField(max_length=255)),
                ("text", models.TextField()),
                ("reason", models.TextField(blank=True, null=True)),
                ("creation_time", models.DateTimeField(auto_now=True)),
                (
                    "motion",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="versions",
                        to="motions.Motion",
                    ),
                ),
            ],
            options={"default_permissions": ()},
            bases=(openslides.utils.models.RESTModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name="MotionVote",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("weight", models.IntegerField(default=1, null=True)),
                ("value", models.CharField(max_length=255, null=True)),
                (
                    "option",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="motions.MotionOption",
                    ),
                ),
            ],
            options={"default_permissions": ()},
            bases=(openslides.utils.models.RESTModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name="State",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("action_word", models.CharField(max_length=255)),
                ("css_class", models.CharField(default="primary", max_length=255)),
                (
                    "required_permission_to_see",
                    models.CharField(blank=True, max_length=255),
                ),
                ("allow_support", models.BooleanField(default=False)),
                ("allow_create_poll", models.BooleanField(default=False)),
                ("allow_submitter_edit", models.BooleanField(default=False)),
                ("versioning", models.BooleanField(default=False)),
                ("leave_old_version_active", models.BooleanField(default=False)),
                ("dont_set_identifier", models.BooleanField(default=False)),
                ("next_states", models.ManyToManyField(to="motions.State")),
            ],
            options={"default_permissions": ()},
            bases=(openslides.utils.models.RESTModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name="Workflow",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                (
                    "first_state",
                    models.OneToOneField(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="motions.State",
                    ),
                ),
            ],
            options={"default_permissions": ()},
            bases=(openslides.utils.models.RESTModelMixin, models.Model),
        ),
        migrations.AddField(
            model_name="state",
            name="workflow",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="states",
                to="motions.Workflow",
            ),
        ),
        migrations.AddField(
            model_name="motionoption",
            name="poll",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="motions.MotionPoll"
            ),
        ),
        migrations.AddField(
            model_name="motion",
            name="active_version",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="active_version",
                to="motions.MotionVersion",
            ),
        ),
        migrations.AddField(
            model_name="motion",
            name="attachments",
            field=models.ManyToManyField(blank=True, to="mediafiles.Mediafile"),
        ),
        migrations.AddField(
            model_name="motion",
            name="category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="motions.Category",
            ),
        ),
        migrations.AddField(
            model_name="motion",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="amendments",
                to="motions.Motion",
            ),
        ),
        migrations.AddField(
            model_name="motion",
            name="state",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="motions.State",
            ),
        ),
        migrations.AddField(
            model_name="motion",
            name="submitters",
            field=models.ManyToManyField(
                blank=True,
                related_name="motion_submitters",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="motion",
            name="supporters",
            field=models.ManyToManyField(
                blank=True,
                related_name="motion_supporters",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="motion",
            name="tags",
            field=models.ManyToManyField(blank=True, to="core.Tag"),
        ),
        migrations.AlterUniqueTogether(
            name="motionversion", unique_together=set([("motion", "version_number")])
        ),
    ]
