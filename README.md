# comma-fixer
Python Library for fixing malformed csv files due to excessive commas

# Schema
Create a Schema to define each column's name, type, and what can be inserted into that column (i.e. whether it contains commas, spaces, etc.).

String, integer, float, and datetime type columns can be added to the schema.

```python
schema = Schema.new()
schema.add_str_column("string_column")
schema.add_int_column("integer_column")
```

Adding a column will automatically create a function to check whether an element can be placed into that column - the `is_valid` function.

# Fixer
Create a Fixer to process a CSV file and separate valid entries from invalid entries, according to the specified Schema.

```python
fixer = Fixer.new(schema)
parsed = fixer.fix_file("filepath")
```

`fix_file(filepath)` returns a `Parsed` object, which stores all entries from the original CSV file. Valid, processed entries will
contain quotes on elements containing commas.

Exporting to CSV will only include valid entries, without invalid entries. However, invalid entries can be viewed by calling
`print_invalid_entries()`, which will display their line index respective to the original CSV file that has been read from.

```python
parsed.export_to_csv_best_effort("processed_filepath")
parsed.print_invalid_entries()
```
