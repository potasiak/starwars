import petl
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import transaction

from starwars.client import StarWarsClient
from starwars.models import Dataset
from starwars.tables import PeopleTable
from starwars.transforms import transform_extracted_people_table


def fetch_table_csv(client: StarWarsClient) -> bytes:
    table = PeopleTable(client, initial_url=settings.DATASET_FETCH_URL)
    transformed_table = transform_extracted_people_table(table, client)
    source = petl.MemorySource()
    petl.tocsv(transformed_table, source)
    return source.getvalue()


@transaction.atomic
def fetch_dataset(client: StarWarsClient) -> Dataset:
    dataset = Dataset.objects.create()
    csv_table = fetch_table_csv(client)
    dataset.file.save(
        name=f'{dataset.uuid!s}.csv',
        content=ContentFile(csv_table),
    )
    return dataset
