import pytest

from comma_fixer.schema import Schema  # Replace with your actual module name


@pytest.fixture
def schema() -> Schema:
    schema = Schema.new()
    schema.add_datetime_column(
        "datetime", is_nullable=False, has_commas=False, has_spaces=False
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
