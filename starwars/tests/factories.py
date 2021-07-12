from unittest.mock import Mock

from starwars.models import Dataset


def create_dataset_mock(**kwargs) -> Mock:
    """Creates a mock with dataset spec and given attributes.

    Args:
        kwargs: attributes to assign to the dataset mock.

    Returns:
        mock of dataset: a mock that simulates dataset model instance.

    """
    dataset_mock = Mock(spec_set=Dataset())
    for key, value in kwargs.items():
        setattr(dataset_mock, key, value)
    return dataset_mock
