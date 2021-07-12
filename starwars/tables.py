import petl

from starwars.client import StarWarsClient


class PeopleTable(petl.Table):
    """ETL table for people objects from Star Wars API.

    Args:
        client: Star Wars API client.

    """
    def __init__(self, client: StarWarsClient, initial_url: str):
        self.client = client
        self.initial_url = initial_url

    def __iter__(self):
        next_url = self.initial_url
        header_returned = False
        with self.client as client:
            while next_url:
                people_page = client.get(next_url)
                for person in people_page.get('results', []):
                    if not header_returned:
                        yield tuple(person.keys())
                        header_returned = True
                    yield tuple(person.values())
                next_url = people_page.get('next', None)

