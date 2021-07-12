from __future__ import annotations

from typing import Callable, ContextManager, Mapping

import requests
from requests import HTTPError


class TooManyRequests(HTTPError):
    pass


class StarWarsClient(ContextManager):
    """Client for Star Wars API.

    Args:
        base_url: Base URL for Star Wars API, e.g. https://swapi.dev/api/
        session_maker: Callable without arguments that returns a requests
            session instance.

    """

    def __init__(self, session_maker: Callable[[], requests.Session] = None):
        self.session_maker = session_maker
        if self.session_maker is None:
            self.session_maker = self.default_session_maker
        self._session = None

    def __enter__(self) -> StarWarsClient:
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, traceback):
        self.close()

    @property
    def session(self) -> requests.Session:
        """Requests session instance.

        Returns:
            Requests session instance.

        Raises:
            AssertionError: when session is not open.

        """
        assert self._session is not None, 'session is not open'
        return self._session

    def open(self):
        """Open new requests session.

        Raises:
            AssertionError: when session is already open.

        """
        assert self._session is None, 'session is already open'
        self._session = self.session_maker()

    def close(self):
        """Close current requests session.

        Raises:
            AssertionError: when session is not open.

        """
        self.session.close()
        self._session = None

    def default_session_maker(self) -> requests.Session:
        """Get a plain requests session.

        Returns:
            Plain requests session.

        """
        return requests.session()

    def get(self, url: str, **kwargs) -> Mapping:
        """Get JSON data from given endpoint.

        Args:
            url: Full endpoint URL.
            kwargs: Additional arguments to be passed to requests.get()
                function.

        Returns:
            JSON object extracted from response.

        Raises:
            TooManyRequests: when rate limit has been exceeded.
            requests.ResponseError: when any other response error occurred.

        """
        response = self.session.get(url, **kwargs)
        if response.status_code == 429:
            raise TooManyRequests(response=response)
        response.raise_for_status()
        return response.json()
