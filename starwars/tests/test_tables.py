from unittest.mock import Mock, call, patch

import petl
import pytest
import requests

from starwars.client import StarWarsClient
from starwars.tables import PeopleTable

TEST_URL = 'http://swapi/api/people/'


def create_people_page(**kwargs):
    page = {
        "count": 2,
        "next": None,
        "previous": None,
        "results": [
            {
                "name": "Luke Skywalker",
                "height": "172",
                "mass": "77",
            },
            {
                "name": "C-3PO",
                "height": "167",
                "mass": "75",
            }
        ]
    }
    page.update(kwargs)
    return page


@pytest.fixture
def test_client():
    return StarWarsClient()


@pytest.fixture
def people_table(test_client):
    return PeopleTable(client=test_client, initial_url=TEST_URL)


def test_people_table_returns_header(people_table, test_client):
    # given
    expected_header = ('name', 'height', 'mass')
    with patch.object(test_client, 'get') as get_mock:
        get_mock.return_value = create_people_page()
        # when
        header = petl.header(people_table)
        # then
        assert header == expected_header


def test_people_table_returns_rows(people_table, test_client):
    # given
    expected_rows = [
        ('Luke Skywalker', '172', '77'),
        ('C-3PO', '167', '75')
    ]
    with patch.object(test_client, 'get') as get_mock:
        get_mock.return_value = create_people_page()
        # when
        data = petl.data(people_table)
        # then
        assert len(data) == 2
        assert all(row in expected_rows for row in data)


def test_people_table_queries_next_page(people_table, test_client):
    # given
    next_page_url = f'{TEST_URL}?page=2'
    first_page = create_people_page(next=next_page_url)
    second_page = create_people_page()
    with patch.object(test_client, 'get') as get_mock:
        get_mock.side_effect = [first_page, second_page]
        # when
        data = petl.data(people_table)
        # then
        assert len(data) == 4
        get_mock.assert_has_calls([
            call(TEST_URL),
            call(next_page_url)
        ])
