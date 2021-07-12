from unittest.mock import Mock, patch

import pytest
import requests
import responses
from requests import HTTPError

from starwars.client import StarWarsClient, TooManyRequests

TEST_URL = 'http://swapi/api'


@pytest.fixture
def test_client():
    with StarWarsClient() as client:
        yield client


def test_get_calls_requests_session_get(test_client):
    # given
    session_mock = Mock(spec_set=requests.Session())
    test_client._session = session_mock
    # when
    test_client.get(TEST_URL)
    # then
    session_mock.get.assert_called_with(TEST_URL)


def test_get_calls_requests_session_get_with_kwargs(test_client):
    # given
    session_mock = Mock(spec_set=requests.Session())
    test_client._session = session_mock
    kwargs = {'params': {'page': 1}}
    # when
    test_client.get(TEST_URL, **kwargs)
    # then
    session_mock.get.assert_called_with(TEST_URL, **kwargs)


@responses.activate
def test_get_raise_too_many_requests_on_http_429(test_client):
    # given
    responses.add(responses.GET, TEST_URL, status=429)
    # then
    with pytest.raises(TooManyRequests):
        # when
        test_client.get(TEST_URL)


@responses.activate
@pytest.mark.parametrize('status_code', [400, 499, 500, 599])
def test_get_raise_response_error_on_http_error(status_code, test_client):
    # given
    responses.add(responses.GET, TEST_URL, status=status_code)
    # then
    with pytest.raises(HTTPError):
        # when
        test_client.get(TEST_URL)


@responses.activate
def test_get_returns_json_payload(test_client):
    # given
    payload = {'test': True}
    responses.add(responses.GET, TEST_URL, json=payload)
    # when
    result = test_client.get(TEST_URL)
    # then
    assert result == payload
