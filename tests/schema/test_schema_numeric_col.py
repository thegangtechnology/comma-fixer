import pytest

from comma_fixer.schema import Schema  # Replace with your actual module name


@pytest.fixture
def schema() -> Schema:
    schema = Schema.new()
    schema.add_int_column("int", is_nullable=False, has_commas=False, has_spaces=False)
    schema.add_float_column(
        "float", is_nullable=False, has_commas=False, has_spaces=False
    )
    return schema


@pytest.mark.parametrize(
    "value, expected",
    [
        ("1", True),
        ("1.0", False),
        ("3.5", False),
        ("abc", False),
        ("12345", True),
        ("abc123", False),
        ("x", False),
        ("3.1415", False),
    ],
)
def test_int_column(schema, value, expected):
    assert schema.is_token_valid(value, "int") == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("1", True),
        ("1.0", True),
        ("3.5", True),
        ("abc", False),
        ("12345", True),
        ("abc123", False),
        ("x", False),
        ("3.1415", True),
    ],
)
def test_float_column(schema, value, expected):
    assert schema.is_token_valid(value, "float") == expected
