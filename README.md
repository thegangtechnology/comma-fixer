# comma-fixer
Python Library for fixing malformed csv files due to excessive commas

# Schema
Create a Schema to define each column's name, type, and what can be inserted into that column (i.e. whether it contains commas, spaces, etc.).

String, integer, float, and datetime type columns can be added to the schema.

```python
schema = Schema.new_schema()
schema.add_str_column("string_column")
schema.add_int_column("integer_column")
```

Adding a column will automatically create a function to check whether an element can be placed into that column - the `is_valid` function.

# Fixer
Create a Fixer to process a CSV file and separate valid entries from invalid entries, according to the specified Schema.

```python
fixer = Fixer.new(schema)
fixer.fix_file("filepath")
```

After running `fix_file`, valid entries will be placed in a DataFrame, whilst invalid entries 
will be placed in a list to either be manually processed by the user, or to be processed via 
Machine Learning classification.

```python
fixer.export_to_csv("processed_filepath")
```

Calling `export_to_csv` will export the items in the processed DataFrame to a CSV file.