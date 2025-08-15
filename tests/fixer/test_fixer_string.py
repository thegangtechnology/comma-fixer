from comma_fixer.column import Column
from comma_fixer.fixer import Fixer
from comma_fixer.schema import Schema


def test_multiple_single_string_columns():
    schema = Schema.new(
        columns=[
            Column.string("name", False, False, False),
            Column.string("username", False, False, False),
            Column.string("cat_name", False, False, False),
            Column.string("cat_colour", False, False, False),
        ]
    )
    fixer = Fixer.new(schema=schema)
    assert ["john", "john", "chanom", "orange"] == fixer.process_row(
        "john,john,chanom,orange"
    )
    assert fixer.process_row(",john,chanom,orange") is None
    assert fixer.process_row(",,,") is None
    assert fixer.process_row("john,john,chanom,chayen,orange") is None


def test_one_comma_column():
    schema = Schema.new(
        columns=[
            Column.string("name", False, False, False),
            Column.string("username", False, False, False),
            Column.string("cat_names", False, True, False),
            Column.string("cat_group_name", False, False, False),
        ]
    )
    fixer = Fixer.new(schema=schema)
    assert ["john", "john", "chanom,chayen,olieang", "orange"] == fixer.process_row(
        "john,john,chanom,chayen,olieang,orange"
    )
    assert fixer.process_row(",john,chanom,orange") is None
    assert fixer.process_row(",,,") is None
    assert fixer.process_row("john,john,chanom,chayen,") is None


def test_one_space_column():
    schema = Schema.new(
        columns=[
            Column.string("name", False, False, True),
            Column.string("username", False, False, False),
            Column.string("cat_name", False, False, False),
            Column.string("cat_group_name", False, False, False),
        ]
    )
    fixer = Fixer.new(schema=schema)
    assert ["john appleseed", "john", "chanom", "orange"] == fixer.process_row(
        "john appleseed,john,chanom,orange"
    )
    assert ["john", "john", "chanom", "orange"] == fixer.process_row(
        "john,john,chanom,orange"
    )
    assert fixer.process_row(" ,john,chanom,orange") is None
    assert fixer.process_row(",john,chanom,orange") is None
    assert fixer.process_row(",,,") is None
    assert fixer.process_row("john,john,chanom,") is None


def test_one_space_one_comma_column():
    schema = Schema.new(
        columns=[
            Column.string("name", False, False, True),
            Column.string("username", False, False, False),
            Column.string("cat_names", False, True, False),
            Column.string("cat_group_name", False, False, False),
        ]
    )
    fixer = Fixer.new(schema=schema)
    assert [
        "john appleseed",
        "john",
        "chanom,chayen,olieang",
        "orange",
    ] == fixer.process_row("john appleseed,john,chanom,chayen,olieang,orange")
    assert ["john", "john", "chanom,chayen,olieang", "orange"] == fixer.process_row(
        "john,john,chanom,chayen,olieang,orange"
    )
    assert ["john", "john", "chanom", "orange"] == fixer.process_row(
        "john,john,chanom,orange"
    )
    assert fixer.process_row("john,john,,,orange") is None
    assert fixer.process_row(" ,john,chanom,orange") is None
    assert fixer.process_row(",john,chanom,orange") is None
    assert fixer.process_row(",,,") is None
    assert fixer.process_row("john,john,chanom,") is None


def test_two_non_consecutive_comma_columns():
    schema = Schema.new(
        columns=[
            Column.string("cat_names", False, True, False),
            Column.string("cat_group_name", False, False, False, format=r"^[a-z]{3}$"),
            Column.string("cat_colours", False, True, False),
        ]
    )
    fixer = Fixer.new(schema=schema)
    assert ["chanom", "cat", "orange"] == fixer.process_row("chanom,cat,orange")
    assert ["chanom,chayen", "cat", "orange"] == fixer.process_row(
        "chanom,chayen,cat,orange"
    )
    assert ["chanom,chayen", "cat", "orange,orange"] == fixer.process_row(
        "chanom,chayen,cat,orange,orange"
    )
    assert ["chanom", "cat", "orange,orange"] == fixer.process_row(
        "chanom,,cat,orange,orange"
    )
    assert ["chanom", "cat", "orange,orange"] == fixer.process_row(
        ",chanom,cat,orange,orange"
    )
    assert ["chanom,chayen", "cat", "orange,orange"] == fixer.process_row(
        "chanom,,chayen,cat,orange,orange"
    )
    assert fixer.process_row(",cat,") is None
    assert fixer.process_row(",,") is None
    assert fixer.process_row(",,cat,") is None
    assert fixer.process_row(",,cat,meow,meow,meow") is None


def test_two_consecutive_comma_columns():
    schema = Schema.new(
        columns=[
            Column.string("cat_names", False, True, False),
            Column.string("cat_colours", False, True, False),
        ]
    )
    fixer = Fixer.new(schema=schema)
    assert ["chanom", "orange"] == fixer.process_row("chanom,orange")
    assert fixer.process_row("chanom,chayen,orange") is None
    assert fixer.process_row("chanom,chayen,cat,orange,orange") is None
    assert fixer.process_row("chanom,,cat,orange,orange") is None
    assert fixer.process_row(",chanom,cat,orange,orange") is None
    assert fixer.process_row("chanom,,chayen,cat,orange,orange") is None
    assert fixer.process_row(",,orange") is None
    assert fixer.process_row(",,") is None
    assert fixer.process_row(",,,meow,meow,meow") is None
