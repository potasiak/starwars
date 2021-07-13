import functools
from typing import Iterable, Optional, Sequence

import dateutil.parser
import petl

from starwars.client import StarWarsClient


def datetime_string_to_date_string(
    datetime_string: Optional[str]
) -> Optional[str]:
    """Convert string with ISO datetime to string with ISO date.

    Args:
        datetime_string: String with ISO datetime.

    Returns:
        String with ISO date.

    """
    if datetime_string is None:
        return None
    date_time = dateutil.parser.isoparse(datetime_string)
    return date_time.date().isoformat()


@functools.lru_cache(maxsize=100)
def get_planet_name(client: StarWarsClient, url: str) -> str:
    """Get planet name from planet URL.

    Args:
        client: Star Wars API client to use.
        url: URL of the planet.

    Returns:
        str: Name of the planet.

    """
    planet = client.get(url)
    return planet.get('name', None)


def add_date_for_edited(table: petl.Table) -> petl.Table:
    """Add date field to table, based on ``edited`` field.

    Args:
        table: ETL table to add the field to.

    Returns:
        ETL table with the date field.

    """
    return petl.addfield(
        table,
        'date',
        lambda row: datetime_string_to_date_string(row.get('edited', None)),
        missing=None,
    )


def convert_homeworld_to_name(table: petl.Table, client: StarWarsClient) -> petl.Table:
    """Converts homeworld URL field to homeworld name.

    Args:
        table: ETL table to convert the field in.
        client: Star Wars API client to use for planet fetching.

    Returns:
        ETL table with converted homeworld field.

    """
    return petl.convert(
        table,
        'homeworld',
        lambda value: get_planet_name(client, value)
    )


def cutout_people_columns(table: petl.Table) -> petl.Table:
    """Cutout unnecessary columns from people table.

    Args:
        table: ETL table to cutout the columns from,

    Returns:
        ETL table without the unnecessary columns.

    """
    return petl.cutout(table, *[
        'starships', 'edited', 'created', 'vehicles', 'films', 'species', 'url'
    ])


def value_counts_without_frequency(
    table: petl.Table,
    fields: Optional[Iterable[str]]
) -> petl.Table:
    """Aggregate table by given fields and add column with value counts.

    Args:
        table: ETL table to aggregate.
        fields: Names of the fields to aggregate the table by.

    Returns:
        ETL table with aggregated value counts for selected fields.

    """
    if not fields:
        return table
    return petl.cutout(
        petl.valuecounts(table, *fields),
        'frequency'
    )


def sort_django_style(table: petl.Table, order_by: Optional[str]) -> petl.Table:
    """Sort table using Django-style notation.

    When ``order_by`` is a column name, the rows are sorted in ascending order.
    When ``order_by`` is a column name with a ``-`` before it, the rows are
    sorted in descending order.

    Args:
         table: ETL table to sort.
         order_by: Django-like order field specification, e.g. ``name``
            or ``-name``.

    Returns:
        ETL table sorted by given column and order.

    """
    if not order_by or order_by not in petl.header(table):
        return table
    reverse = order_by.startswith('-')
    if reverse:
        order_by = order_by[1:]
    return petl.sort(table, key=order_by, reverse=reverse)


def limit_rows(table: petl.Table, limit: int = None) -> petl.Table:
    """Limit returned table rows to given value.

    Args:
        table: ETL table to limit.
        limit: Limit of number of returned rows when iterating over the table.

    Returns:
        ETL table with limited rows number.

    """
    if not limit:
        return table
    return petl.rowslice(table, limit)


def transform_extracted_people_table(
    table: petl.Table,
    client: StarWarsClient
) -> petl.Table:
    """Transform people table extracted from Star Wars API.

    * Add ``date`` field based on ``edited`` column value.
    * Convert homeworld URL to planet name.
    * Cutout unnecessary columns.

    Args:
        table: ETL table to transform.
        client: Star Wars API client to use for getting planet names.

    Returns:
        Transformed ETL table.

    """
    return cutout_people_columns(
        convert_homeworld_to_name(
            add_date_for_edited(table),
            client
        )
    )


def transform_loaded_people_table(
    table: petl.Table,
    aggregate_by: Iterable[str] = None,
    order_by: str = None,
    limit: int = None
) -> petl.Table:
    """Transform people table loaded from a file.

    All transformations are optional:

    * Aggregate table by values of given columns and add a column with counts.
    * Sort table by given field (Django-style).
    * Limit number of returned rows on table iteration.

    Args:
        table: ETL table to transform.
        aggregate_by: Field names to aggregate by. No aggregation is applied
            when ``None``.
        order_by: Django-style field name ordering value, e.g. ``name`` for
            ascending order and ``-name`` for descending order. No sorting
            is applied when ``None``.
        limit: Maximum number of rows that will be returned when iterating over
            the table. No limit when ``None``.

    Returns:
        Transformed ETL table

    """
    return limit_rows(
        sort_django_style(
            value_counts_without_frequency(table, fields=aggregate_by),
            order_by=order_by
        ),
        limit=limit
    )
