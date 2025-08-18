import csv
from dataclasses import dataclass
from typing import TypeAlias

import pandas as pd

from comma_fixer.schema import Schema

InvalidEntry: TypeAlias = tuple[int, str]
ParsedEntry: TypeAlias = list[str]


@dataclass
class Parsed:
    """
    Parsed class produced from calling `fix_file` in Fixer.

    Attributes:
        schema (Schema): Schema of dataset.
        processed (str): CSV of dataset stored as a string.
        invalid_line_numbers (list[InvalidEntry]): List of invalid entries containing line number and entry.
    """

    _schema: Schema
    _processed: str
    _invalid_entries: list[InvalidEntry]

    @classmethod
    def new(
        cls, schema: Schema, processed_csv: str, invalid_entries: list[InvalidEntry]
    ) -> "Parsed":
        """
        Creates an empty Parsed object with specified Schema.

        Args:
            schema (Schema): Schema of dataset.

        Returns:
            Parsed. Parsed object with specified schema.
        """
        return Parsed(
            _schema=schema, _processed=processed_csv, _invalid_entries=invalid_entries
        )

    def export_to_csv_best_effort(self, filepath: str):
        """
        Exports valid entries to CSV at specified filepath.

        Converts valid entries into DataFrame before exporting to CSV.
        """
        processed_to_csv = pd.DataFrame(self._schema.get_series_dict())
        for line_number, line in enumerate(self._processed.split("\n")):
            if (line_number, line) not in self._invalid_entries:
                parsed_csv = list(csv.reader([line]))[0]
                processed_to_csv.loc[len(processed_to_csv)] = parsed_csv
        return processed_to_csv.to_csv(filepath, index=False)

    def print_all_invalid_entries(self):
        """
        Prints all the invalid entries with their line index respective to
        the original CSV file.
        """
        print("Index\tLine entry")
        for invalid_index, invalid_line in self._invalid_entries:
            print(f"{invalid_index}\t{invalid_line}")

    def invalid_entries_count(self) -> int:
        return len(self._invalid_entries)
