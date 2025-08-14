
from dataclasses import dataclass
from typing import TypeAlias

from comma_fixer.schema import Schema
import pandas as pd
import csv


InvalidEntry: TypeAlias = tuple[int, str]
ParsedEntry: TypeAlias = list[str]

@dataclass
class Parsed:
    schema: Schema
    processed: str
    invalid_line_numbers: list[InvalidEntry]

    @classmethod
    def new(cls, schema) -> 'Parsed':
        return Parsed(schema, "", list())
    
    def add_valid_entry(self, entry: ParsedEntry):
        print(entry)
        processed_entry = ""
        for token in entry:
            if ',' in token:
                if len(processed_entry) != 0:
                    processed_entry = f"{processed_entry},'{token}'"
                else:
                    processed_entry = f"'{token}'"
            else:
                if len(processed_entry) != 0:
                    processed_entry = f"{processed_entry},{token}"
                else:
                    processed_entry = f"{token}"
        print(processed_entry)
        if len(self.processed) != 0:
            self.processed = f"{self.processed}\n{processed_entry}"
        else:
            self.processed = processed_entry
    
    def add_invalid_entry(self, line_index: int, entry: str):
        self.invalid_line_numbers.append(tuple([line_index, entry]))
        if len(self.processed) != 0:
            self.processed = f"{self.processed}\n{entry}"
        else:
            self.processed = entry

    def export_to_csv_best_effort(self, filepath: str):
        processed_to_csv = pd.DataFrame(self.schema.series_types)
        for line_number, line in enumerate(self.processed.split('\n')):
            if (line_number, line) not in self.invalid_line_numbers:
                processed_to_csv.loc[len(processed_to_csv)] = list(csv.reader([line]))[0]
        return processed_to_csv.to_csv(filepath, index=False)
    
    def print_all_invalid_entries(self):
        print(self.invalid_line_numbers)