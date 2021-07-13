import uuid
from datetime import datetime

import petl
from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.safestring import mark_safe

from starwars.client import StarWarsClient
from starwars.models import Dataset
from starwars.services import fetch_dataset
from starwars.transforms import transform_loaded_people_table


def index(request):
    datasets = Dataset.objects.only('uuid', 'date').all()
    return render(request, 'index.html', {'datasets': datasets})


def details(request, dataset_uuid: uuid.UUID):
    dataset = get_object_or_404(Dataset, uuid=dataset_uuid)

    fields = request.GET.getlist('field', [])
    order_by = request.GET.get('order_by', None)
    limit = request.GET.get('limit', settings.DATASET_DEFAULT_PER_PAGE)
    try:
        limit = int(limit)
    except ValueError:
        limit = settings.DATASET_DEFAULT_PER_PAGE
    next_limit = limit + settings.DATASET_DEFAULT_PER_PAGE

    table = petl.fromcsv(dataset.file)
    transformed_table = transform_loaded_people_table(
        table,
        aggregate_by=fields,
        order_by=order_by,
        limit=limit
    )
    return render(request, 'details.html', {
        'dataset': dataset,
        'available_fields': petl.header(table),
        'fields': fields,
        'header': petl.header(transformed_table),
        'data': petl.data(transformed_table),
        'next_limit': next_limit
    })


def fetch(request):
    client = StarWarsClient()
    try:
        time_start = datetime.now()
        dataset = fetch_dataset(client)
        time_end = datetime.now()

        fetch_time = (time_end - time_start).total_seconds()

        dataset_url = reverse("details", args=(dataset.uuid,))
        messages.success(request, mark_safe(
            f'Fetched dataset <a href="{dataset_url}">{dataset.uuid!s}</a> '
            f'in <b>{round(fetch_time, 2)}s</b>'
        ))
    except Exception as e:
        messages.error(request, f'Could not fetch dataset: {e!s}')
    return redirect('index')

