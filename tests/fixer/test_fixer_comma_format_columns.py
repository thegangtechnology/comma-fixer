from comma_fixer.column import Column
from comma_fixer.fixer import Fixer
from comma_fixer.schema import Schema


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


def test_two_consecutive_comma_columns_with_regex():
    schema = Schema.new(
        columns=[
            Column.string("cat_names", False, True, False, format=r"[a-z]+,?"),
            Column.string("cat_ages", False, True, False, format=r"[0-9]+,?"),
        ]
    )
    fixer = Fixer.new(schema=schema)
    assert fixer.process_row("chanom,1") == ["chanom", "1"]
    assert fixer.process_row("chanom,chayen,1") == ["chanom,chayen", "1"]
    assert fixer.process_row("chanom,chayen,1,2") == ["chanom,chayen", "1,2"]
    # Although they are fake commas, unable to determine "which" belongs to which column
    assert fixer.process_row("chayen,,3,") is None
    assert fixer.process_row(",,1,2,3,") is None
    assert fixer.process_row("1,2,3,4,5") is None
    assert fixer.process_row("chanom,chayen,milky") is None
