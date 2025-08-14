import pytest

from comma_fixer.schema import Schema  # Replace with your actual module name


@pytest.fixture
def schema() -> Schema:
    schema = Schema.new_schema()
    schema.add_str_column(
        "str_space_comma", is_nullable=False, has_commas=True, has_spaces=True
    )
    schema.add_str_column(
        "str_space", is_nullable=False, has_commas=False, has_spaces=True
    )
    schema.add_str_column(
        "str_comma", is_nullable=False, has_commas=True, has_spaces=False
    )
    schema.add_str_column(
        "str_no_space_no_comma", is_nullable=False, has_commas=False, has_spaces=False
    )
    schema.add_str_column(
        "str_null_space_comma", is_nullable=True, has_commas=True, has_spaces=True
    )
    return schema


@pytest.mark.parametrize(
    "value, expected",
    [
        ("This is a test message with spaces", True),
        ("This is a test message with spaces, and commas", True),
        ("ThisIsATestMessageWithNoSpaces", True),
        ("This is a test message with spaces and a period.", True),
        ("", False),
        (",", True),
        ("tabby,black,orange", True),
        ("cat sr, cat jr, cat", True),
        (",,", True),
        (" ", True),
    ],
)
def test_str_column_with_spaces_and_commas(schema, value, expected):
    assert schema.is_token_valid(value, "str_space_comma") == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("This is a test message with spaces", True),
        ("This is a test message with spaces, and commas", False),
        ("ThisIsATestMessageWithNoSpaces", True),
        ("This is a test message with spaces and a period.", True),
        ("", False),
        (",", False),
        ("tabby,black,orange", False),
        ("cat sr, cat jr, cat", False),
        (",,", False),
        (" ", True),
    ],
)
def test_str_column_with_space(schema, value, expected):
    assert schema.is_token_valid(value, "str_space") == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("This is a test message with spaces", False),
        ("This is a test message with spaces, and commas", False),
        ("ThisIsATestMessageWithNoSpaces", True),
        ("This is a test message with spaces and a period.", False),
        ("", False),
        (",", True),
        ("tabby,black,orange", True),
        ("cat sr, cat jr, cat", False),
        (",,", True),
        (" ", False),
    ],
)
def test_str_column_with_commas(schema, value, expected):
    assert schema.is_token_valid(value, "str_comma") == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("This is a test message with spaces", False),
        ("This is a test message with spaces, and commas", False),
        ("ThisIsATestMessageWithNoSpaces", True),
        ("This is a test message with spaces and a period.", False),
        ("", False),
        (",", False),
        ("tabby,black,orange", False),
        ("cat sr, cat jr, cat", False),
        (",,", False),
        (" ", False),
    ],
)
def test_str_column_with_no_space_no_commas(schema, value, expected):
    assert schema.is_token_valid(value, "str_no_space_no_comma") == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("This is a test message with spaces", True),
        ("This is a test message with spaces, and commas", True),
        ("ThisIsATestMessageWithNoSpaces", True),
        ("This is a test message with spaces and a period.", True),
        ("", True),
        (",", True),
        ("tabby,black,orange", True),
        ("cat sr, cat jr, cat", True),
        (",,", True),
        (" ", True),
    ],
)
def test_str_column_with_null_space_commas(schema, value, expected):
    assert schema.is_token_valid(value, "str_null_space_comma") == expected
