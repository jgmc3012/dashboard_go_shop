from django.db import models

import logging

from collections import defaultdict
from django.apps import apps

class Token(models.Model):
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    expiration = models.DateTimeField()
    app_id = models.BigIntegerField(default=0)


class BulkCreateManager(object):
    """
    This helper class keeps track of ORM objects to be created for multiple
    model classes, and automatically creates those objects with `bulk_create`
    when the number of objects accumulated for a given model class exceeds
    `chunk_size`.
    Upon completion of the loop that's `add()`ing objects, the developer must
    call `done()` to ensure the final set of objects is created for all models.
    """

    def __init__(self, chunk_size=100):
        self._create_queues = defaultdict(list)
        self._update_queues = defaultdict(list)
        self._update_fields = defaultdict(set)
        self.chunk_size = chunk_size

    def _commit_create(self, model_class):
        model_key = model_class._meta.label
        logging.info(f'Insertando {len(self._create_queues[model_key])} registros')
        model_class.objects.bulk_create(self._create_queues[model_key])
        self._create_queues[model_key] = []

    def _commit_update(self, model_class):
        model_key = model_class._meta.label
        logging.info(f'Actualizando {len(self._update_queues[model_key])} registros')
        model_class.objects.bulk_update(
            self._update_queues[model_key],
            self._update_fields[model_key]
        )
        self._update_queues[model_key] = []

    def add(self, obj):
        """
        Add an object to the queue to be created, and call bulk_create if we
        have enough objs.
        """
        model_class = type(obj)
        model_key = model_class._meta.label
        self._create_queues[model_key].append(obj)
        if len(self._create_queues[model_key]) >= self.chunk_size:
            self._commit_create(model_class)

    def update(self, obj, fields:set):
        """
        Add an object to the queue to be created, and call bulk_create if we
        have enough objs.
        """
        model_class = type(obj)
        model_key = model_class._meta.label
        self._update_queues[model_key].append(obj)
        self._update_fields[model_key] |= fields
        if len(self._update_queues[model_key]) >= self.chunk_size:
            self._commit_update(model_class)

    def done(self):
        """
        Always call this upon completion to make sure the final partial chunk
        is saved.
        """
        for model_name, objs in self._create_queues.items():
            if len(objs) > 0:
                self._commit_create(apps.get_model(model_name))

        for model_name, objs in self._update_queues.items():
            if len(objs) > 0:
                self._commit_update(apps.get_model(model_name))