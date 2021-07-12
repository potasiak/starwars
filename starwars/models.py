from __future__ import annotations

import pathlib
from uuid import uuid4

from django.db import models
from django.utils import timezone


def dataset_destination(instance: Dataset, filename: str = None) -> str:
    """Determine dataset upload destination path.

    When the ``filename`` is not specified, the file is saved with a ``.csv``
    extension.

    Args:
        instance (Dataset): instance of a dataset the file is uploaded for.
        filename (str, optional): original name of the file.

    Returns:
        str: file upload destination path.

    """
    file_extension = pathlib.Path(filename).suffix if filename else '.csv'
    return f'datasets/%Y/%m/%d/{instance.uuid!s}{file_extension!s}'


class Dataset(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid4)
    date = models.DateTimeField(default=timezone.now)
    file = models.FileField(upload_to=dataset_destination)

    class Meta:
        ordering = ('-date',)
