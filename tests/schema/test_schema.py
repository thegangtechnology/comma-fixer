import pytest
from comma_fixer.schema import Schema

@pytest.fixture
def schema():
    return Schema.new_schema()

def test_new_schema_is_empty(schema):
    assert schema.types == {}
    assert schema.is_valid_functions == {}
    assert schema.has_commas == {}


def test_add_column_basic_str(schema):
    schema.add_column("name", str, is_nullable=False, has_commas=False, has_spaces=False)
    assert "name" in schema.types
    assert schema.types["name"] == str
    assert not schema.has_commas["name"]


def test_is_token_valid_str_no_commas_or_spaces(schema):
    schema.add_column("username", str, is_nullable=False, has_commas=False, has_spaces=False)
    assert schema.is_token_valid("User123", "username")
    assert not schema.is_token_valid("User 123", "username")
    assert not schema.is_token_valid("User,123", "username")


def test_is_token_valid_str_with_commas_and_spaces(schema):
    schema.add_column("address", str, is_nullable=False, has_commas=True, has_spaces=True)
    assert schema.is_token_valid("123 Main St, Apt 4B", "address")


def test_is_token_valid_nullable_field(schema):
    schema.add_column("middle_name", str, is_nullable=True, has_commas=False, has_spaces=False)
    assert schema.is_token_valid("", "middle_name")


def test_is_token_valid_non_nullable_field(schema):
    schema.add_column("last_name", str, is_nullable=False, has_commas=False, has_spaces=False)
    assert not schema.is_token_valid("", "last_name")


def test_format_matching(schema):
    schema.add_column("zipcode", str, is_nullable=False, has_commas=False, has_spaces=False, format=r'^\d{5}$')
    assert schema.is_token_valid("12345", "zipcode")
    assert not schema.is_token_valid("1234a", "zipcode")
    assert not schema.is_token_valid("123", "zipcode")


def test_non_string_type_int(schema):
    schema.add_column("age", int, is_nullable=False, has_commas=False, has_spaces=False)
    assert schema.is_token_valid("25", "age")
    assert not schema.is_token_valid("twenty", "age")
    assert not schema.is_token_valid("", "age")


def test_nullable_int(schema):
    schema.add_column("score", int, is_nullable=True, has_commas=False, has_spaces=False)
    assert schema.is_token_valid("", "score")
    assert schema.is_token_valid("100", "score")


def test_invalid_column(schema):
    with pytest.raises(KeyError):
        schema.is_token_valid("something", "nonexistent")
