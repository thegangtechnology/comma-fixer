import pytest

from comma_fixer.column import Column
from comma_fixer.schema import Schema


@pytest.fixture
def schema() -> Schema:
    schema = Schema.new(
        columns=[
            Column.datetime(
                "datetime", is_nullable=False, has_commas=False, has_spaces=False
            )
        ]
    )
    return schema


@pytest.mark.parametrize(
    "value, expected",
    [
        ("2025-05-31", True),
        ("13 August 2025", False),
        ("13.05.2025", False),
        ("10/06/2025", False),
        ("2025-06-10", True),
        ("today", True),
        ("Not a date!", False),
    ],
)
def test_datetime_column(schema, value, expected):
    assert schema.is_token_valid(value, "datetime") == expected
