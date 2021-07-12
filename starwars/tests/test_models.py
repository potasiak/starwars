from uuid import uuid4

import pytest

from starwars.models import dataset_destination
from . import factories


@pytest.mark.parametrize(('filename', 'expected_ext'), [
    ('regular.json', '.json'),
    ('multiple.dots.xls', '.xls'),
    ('no_extension', ''),
])
def test_dataset_destination_with_filename(filename, expected_ext):
    # given
    dataset_uuid = uuid4()
    expected_upload_to = f'datasets/%Y/%m/%d/{dataset_uuid!s}{expected_ext!s}'
    dataset_mock = factories.create_dataset_mock(uuid=dataset_uuid)
    # when
    upload_to = dataset_destination(instance=dataset_mock, filename=filename)
    # then
    assert upload_to == expected_upload_to


def test_dataset_destination_without_filename():
    # given
    dataset_uuid = uuid4()
    dataset_mock = factories.create_dataset_mock(uuid=dataset_uuid)
    # when
    upload_to = dataset_destination(instance=dataset_mock)
    # then
    assert upload_to == f'datasets/%Y/%m/%d/{dataset_uuid!s}.csv'
