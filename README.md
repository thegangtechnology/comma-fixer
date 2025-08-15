# comma-fixer
Python Library for fixing malformed csv files due to excessive commas

# Quickstart

The library can be imported like so:

```python
from comma_fixer.column import Column
from comma_fixer.schema import Schema
from comma_fixer.fixer import Fixer
```

# Schema
Create a Schema to define each column's name, type, and what can be inserted into that column (i.e. whether it contains commas, spaces, etc.).

String, integer, float, and datetime type columns can be added to the schema. Each column will automatically generate a function to 
check whether a token fits within a column.

```python
schema = Schema.new(columns=[
    Column.string(name="username", is_nullable=False, has_commas=False, has_spaces=False),
    Column.string(name="email", is_nullable=True, has_commas=False, has_spaces=False, format=r"[a-zA-Z0-9\.-]+@[a-z]+(\.[a-z]+)+")
    Column.numeric(name="age")
    Column.datetime(name="birthdate")
    Column.float(name="height")
])
schema.info()
```

Custom columns that are not of the type {string, integer, float, datetime} can also be created, but a pandas.Series must also be given 
as part of the arguments. This is to ensure that a pandas.Series object can be created from the specified type, and will allow a 
DataFrame to be initialised from the Schema object when exporting to a CSV file.

```python
Column.new(name="has_car", data_type=bool, series_type=pd.Series(dtype=bool), is_nullable=False, has_commas=False, has_spaces=False)
```

Once a schema is created, it can no longer be added to or editted. Schemas can be viewed with `.info()`, which will display 
each column's attributes.

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
