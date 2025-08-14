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
    schema: Schema
    processed: str
    invalid_line_numbers: list[InvalidEntry]

    @classmethod
    def new(cls, schema) -> "Parsed":
        """
        Creates an empty Parsed object with specified Schema.

        Args:
            schema (Schema): Schema of dataset.

        Returns:
            Parsed. Parsed object with specified schema.
        """
        return Parsed(schema, "", list())

    def add_valid_entry(self, entry: ParsedEntry):
        """
        Adds a valid entry to the string representation of the CSV with 
        quotes around elements containing commas.

        Args:
            entry (ParsedEntry): List of tokens to be added.
        """
        processed_entry = ""
        for token in entry:
            if "," in token:
                if len(processed_entry) != 0:
                    processed_entry = f"{processed_entry},'{token}'"
                else:
                    processed_entry = f"'{token}'"
            else:
                if len(processed_entry) != 0:
                    processed_entry = f"{processed_entry},{token}"
                else:
                    processed_entry = f"{token}"
        if len(self.processed) != 0:
            self.processed = f"{self.processed}\n{processed_entry}"
        else:
            self.processed = processed_entry

    def add_invalid_entry(self, line_index: int, entry: str):
        """
        Adds invalid entries to string representation of the CSV, 
        and the list of invalid entries.

        Args:
            line_index (int): Index of invalid entry in original CSV file.
            entry (str): String of invalid entry.
        """
        self.invalid_line_numbers.append(tuple([line_index, entry]))
        if len(self.processed) != 0:
            self.processed = f"{self.processed}\n{entry}"
        else:
            self.processed = entry

    def export_to_csv_best_effort(self, filepath: str):
        """
        Exports valid entries to CSV at specified filepath.

        Converts valid entries into DataFrame before exporting to CSV.
        """
        processed_to_csv = pd.DataFrame(self.schema.series_types)
        for line_number, line in enumerate(self.processed.split("\n")):
            if (line_number, line) not in self.invalid_line_numbers:
                processed_to_csv.loc[len(processed_to_csv)] = list(csv.reader([line]))[
                    0
                ]
        return processed_to_csv.to_csv(filepath, index=False)

    def print_all_invalid_entries(self):
        """
        Prints all the invalid entries with their line index respective to 
        the original CSV file.
        """
        print(self.invalid_line_numbers)
