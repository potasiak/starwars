from unittest.mock import Mock, patch

import petl
import pytest

from starwars.client import StarWarsClient
from starwars.transforms import (
    add_date_for_edited,
    convert_homeworld_to_name,
    cutout_people_columns,
    datetime_string_to_date_string,
    get_planet_name,
    limit_rows, sort_django_style,
    transform_extracted_people_table,
    transform_loaded_people_table,
    value_counts_without_frequency,
)


class DummyTable(petl.Table):
    def __iter__(self):
        yield (
            'name', 'homeworld', 'starships', 'edited', 'created', 'vehicles',
            'films', 'species', 'url'
        )
        yield (
            'Test 1', 'http://swapi/api/planet/1/', [], '2021-06-12T12:34:56Z',
            '2021-06-12T12:34:56Z', [], [], [], 'http://swapi/api/people/1/'
        )
        yield (
            'Test 2', 'http://swapi/api/planet/2/', [], '2021-06-12T12:34:56Z',
            '2021-06-12T12:34:56Z', [], [], [], 'http://swapi/api/people/2/'
        )


@pytest.fixture
def client_mock():
    return Mock(spec_set=StarWarsClient)


def test_datetime_string_to_date_string_when_none():
    # given
    datetime_string = None
    # when
    date_string = datetime_string_to_date_string(datetime_string)
    # then
    assert date_string is None


@pytest.mark.parametrize(('datetime_string', 'expected_date_string'), [
    ('2021', '2021-01-01'),
    ('2021-06', '2021-06-01'),
    ('2021-06-12', '2021-06-12'),
    ('2021-06-12T12', '2021-06-12'),
    ('2021-06-12T12:34', '2021-06-12'),
    ('2021-06-12T12:34:56', '2021-06-12'),
    ('2021-06-12T12:34:56.987654', '2021-06-12'),
    ('2021-06-12T12:34:56.987654Z', '2021-06-12'),
    ('2021-06-12T12:34:56.987654+01:23', '2021-06-12'),
])
def test_datetime_string_to_date_string(datetime_string, expected_date_string):
    # when
    date_string = datetime_string_to_date_string(datetime_string)
    # then
    assert date_string == expected_date_string


def test_get_planet_name_no_name(client_mock):
    # given
    client_mock.get.return_value = {}
    # when
    planet_name = get_planet_name(client=client_mock, url='https://swapi/')
    # then
    assert planet_name is None


def test_get_planet_name(client_mock):
    # given
    expected_planet_name = 'Tatooine'
    client_mock.get.return_value = {'name': expected_planet_name}
    # when
    planet_name = get_planet_name(client=client_mock, url='https://swapi/')
    # then
    assert planet_name == expected_planet_name


def test_add_date_for_edited():
    # given
    expected_date = '2021-06-12'
    table = DummyTable()
    # when
    transformed_table = add_date_for_edited(table)
    # then
    assert 'date' in petl.header(transformed_table)
    first_row = next(iter(petl.dicts(transformed_table)))
    assert first_row['date'] == expected_date


@patch('starwars.transforms.get_planet_name')
def test_convert_homeworld_to_name(get_planet_name_mock, client_mock):
    # given
    planet_name = 'Tatooine'
    get_planet_name_mock.return_value = planet_name
    table = DummyTable()
    # when
    transformed_table = convert_homeworld_to_name(table, client_mock)
    # then
    assert 'homeworld' in petl.header(transformed_table)
    first_row = next(iter(petl.dicts(transformed_table)))
    assert first_row['homeworld'] == planet_name


def test_cutout_people_columns():
    # given
    expected_cutout_columns = [
        'starships', 'edited', 'created', 'vehicles', 'films', 'species', 'url'
    ]
    table = DummyTable()
    # when
    transformed_table = cutout_people_columns(table)
    # then
    header = petl.header(transformed_table)
    assert all(col not in header for col in expected_cutout_columns)


def test_value_counts_without_frequency_no_fields():
    # given
    table = DummyTable()
    # when
    transformed_table = value_counts_without_frequency(table, [])
    # then
    assert transformed_table == table


@pytest.mark.parametrize(('column', 'counts'), [
    ('homeworld', 1),
    ('edited', 2),
])
def test_value_counts_without_frequency(column, counts):
    # given
    table = DummyTable()
    # when
    transformed_table = value_counts_without_frequency(table, [column])
    # then
    first_row = next(iter(petl.dicts(transformed_table)))
    assert first_row['count'] == counts


def test_sort_django_style_no_order_by():
    # given
    table = DummyTable()
    # when
    transformed_table = sort_django_style(table, order_by=None)
    # then
    assert transformed_table == table


def test_sort_django_style_ascending():
    # given
    table = DummyTable()
    # when
    transformed_table = sort_django_style(table, order_by='name')
    # then
    first_row = next(iter(petl.dicts(transformed_table)))
    assert first_row['name'] == 'Test 1'


def test_sort_django_style_descending():
    # given
    table = DummyTable()
    # when
    transformed_table = sort_django_style(table, order_by='-name')
    # then
    first_row = next(iter(petl.dicts(transformed_table)))
    assert first_row['name'] == 'Test 2'


def test_limit_rows_no_limit():
    # given
    table = DummyTable()
    # when
    transformed_table = limit_rows(table, limit=None)
    # then
    assert transformed_table == table


def test_limit_rows():
    # given
    table = DummyTable()
    # when
    transformed_table = limit_rows(table, limit=1)
    # then
    assert len(petl.data(transformed_table)) == 1


@patch('starwars.transforms.cutout_people_columns')
@patch('starwars.transforms.convert_homeworld_to_name')
@patch('starwars.transforms.add_date_for_edited')
def test_transform_extracted_people_table(
    add_date_for_edited_mock,
    convert_homeworld_to_name_mock,
    cutout_people_columns_mock,
    client_mock
):
    # given
    table = DummyTable()
    add_date_for_edited_mock.return_value = table
    convert_homeworld_to_name_mock.return_value = table
    cutout_people_columns_mock.return_value = table
    # when
    transformed_table = transform_extracted_people_table(table, client_mock)
    # then
    assert transformed_table == table
    add_date_for_edited_mock.assert_called_once_with(table)
    convert_homeworld_to_name_mock.assert_called_once_with(table, client_mock)
    cutout_people_columns_mock.assert_called_once_with(table)


@patch('starwars.transforms.limit_rows')
@patch('starwars.transforms.sort_django_style')
@patch('starwars.transforms.value_counts_without_frequency')
def test_transform_loaded_people_table(
    value_counts_without_frequency_mock,
    sort_django_style_mock,
    limit_rows_mock
):
    # given
    table = DummyTable()
    value_counts_without_frequency_mock.return_value = table
    sort_django_style_mock.return_value = table
    limit_rows_mock.return_value = table
    fields = Mock()
    order_by = Mock()
    limit = Mock()
    # when
    transformed_table = transform_loaded_people_table(
        table,
        aggregate_by=fields,
        order_by=order_by,
        limit=limit,
    )
    # then
    assert transformed_table == table
    value_counts_without_frequency_mock.assert_called_once_with(
        table,
        fields=fields
    )
    sort_django_style_mock.assert_called_once_with(
        table,
        order_by=order_by
    )
    limit_rows_mock.assert_called_once_with(table, limit=limit)
