import pytest

from comma_fixer.column import Column
from comma_fixer.schema import Schema

def test_new_schema_is_empty():
    schema = Schema.new([])
    assert schema.columns == {}
    assert schema.get_series_dict() == {}


def test_add_column_basic_str():
    schema = Schema.new(columns=
        [
            Column.string("name", is_nullable=False, has_commas=False, has_spaces=False)
        ])
    assert "name" in schema.columns
    assert schema.columns["name"].get_type() == str


def test_is_token_valid_str_no_commas_or_spaces():
    schema = Schema.new(columns=
        [
            Column.string("username", is_nullable=False, has_commas=False, has_spaces=False)
        ])
    assert schema.is_token_valid("User123", "username")
    assert not schema.is_token_valid("User 123", "username")
    assert not schema.is_token_valid("User,123", "username")


def test_is_token_valid_str_with_commas_and_spaces():
    schema = Schema.new(columns=
        [
            Column.string("address", is_nullable=False, has_commas=True, has_spaces=True)
        ])
    assert schema.is_token_valid("123 Main St, Apt 4B", "address")


def test_is_token_valid_nullable_field():
    schema = Schema.new(columns=
        [
            Column.string("middle_name", is_nullable=True, has_commas=False, has_spaces=False)
        ])
    assert schema.is_token_valid("", "middle_name")


def test_is_token_valid_non_nullable_field():
    schema = Schema.new(columns=
        [
            Column.string("last_name", is_nullable=False, has_commas=False, has_spaces=False)
        ])
    assert not schema.is_token_valid("", "last_name")


def test_format_matching():
    schema = Schema.new(columns=
        [
            Column.string("zipcode", is_nullable=False, has_commas=False, has_spaces=False, format=r"^\d{5}$")
        ])
    assert schema.is_token_valid("12345", "zipcode")
    assert not schema.is_token_valid("1234a", "zipcode")
    assert not schema.is_token_valid("123", "zipcode")


def test_non_string_type_int():
    schema = Schema.new(columns=
        [
            Column.numeric("age", is_nullable=False, has_commas=False, has_spaces=False)
        ])
    assert schema.is_token_valid("25", "age")
    assert not schema.is_token_valid("twenty", "age")
    assert not schema.is_token_valid("", "age")


def test_nullable_int():
    schema = Schema.new(columns=
        [
            Column.numeric("score", is_nullable=True, has_commas=False, has_spaces=False)
        ])
    assert schema.is_token_valid("", "score")
    assert schema.is_token_valid("100", "score")


def test_invalid_column():
    schema = Schema.new(columns=[])
    with pytest.raises(KeyError):
        schema.is_token_valid("something", "nonexistent")


def test_get_column_names():
    schema = Schema.new(columns=[
        Column.string("col1", True, False, False),
        Column.numeric("col2", True, False, False)
    ])
    assert set(schema.get_column_names()) == {"col1", "col2"}
