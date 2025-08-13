import logging
from dataclasses import dataclass
from typing import Optional, TypeAlias

import networkx as nx
import numpy as np
import pandas as pd
from networkx import NetworkXNoPath, NodeNotFound

from comma_fixer.schema import Schema

ParsedEntry: TypeAlias = list[str]
Path: TypeAlias = list[tuple[int, int]]
ValidityMatrix: TypeAlias = np.array

logger = logging.getLogger("Fixer Logs")


@dataclass
class Fixer:
    schema: Schema
    processed: pd.DataFrame
    invalid: list[str]

    @classmethod
    def new(cls, schema: Schema) -> "Fixer":
        return Fixer(schema, pd.DataFrame(schema.series_types), list())

    def add_row(self, new_entry: str):
        processed_str = self.__check_valid(new_entry)
        if processed_str is not None:
            row_to_add = len(self.processed)
            self.processed.loc[row_to_add] = processed_str
        else:
            self.invalid.append(new_entry)

    def fix_file(self, filepath: str, skip_first_line: bool = True):
        line_count = 0
        with open(filepath) as file:
            for line in file:
                line = line.strip()
                if not skip_first_line:
                    self.add_row(line)
                else:
                    skip_first_line = not skip_first_line
                line_count += 1

    def __check_valid(self, new_entry: str) -> Optional[ParsedEntry]:
        validity_matrix = self.__construct_validity_matrix(new_entry=new_entry)
        tokens = new_entry.split(",")
        (num_tokens, num_cols) = validity_matrix.shape
        paths = self.__find_shortest_paths(validity_matrix=validity_matrix)

        if paths is not None and len(paths) > 1:
            logger.warning("Multiple paths found -- needs to be resolved")
            return None
        elif paths is not None:
            for path in paths:
                return self.__construct_processed_entry_from_path(
                    path=path, tokens=tokens, num_cols=num_cols, num_tokens=num_tokens
                )
        return None

    def __construct_processed_entry_from_path(
        self,
        path: list[tuple[int, int]],
        tokens: list[str],
        num_cols: int,
        num_tokens: int,
    ) -> list[str]:
        processed_entry = ["" for _ in range(num_cols)]
        for step in path:
            if step[0] < num_tokens and step[1] < num_cols:
                processed_entry[step[1]] = tokens[step[0]]
        return processed_entry

    def __construct_validity_matrix(self, new_entry: str) -> ValidityMatrix:
        tokens = new_entry.split(",")
        num_cols = len(self.schema.get_column_names())
        num_tokens = len(tokens)
        validity_matrix = np.ones((num_tokens, num_cols))
        furthest_col = 0

        for token_index, token in enumerate(tokens):
            first_valid_index = -1
            for column_index, column_name in enumerate(self.schema.get_column_names()):
                preceding_zero = self.__check_preceding_zero_in_path(
                    validity_matrix=validity_matrix, token_index=token_index, column_index=column_index
                )
                if preceding_zero or token_index == 0:
                    validity_matrix[token_index][column_index] = (
                        0
                        if self.schema.is_token_valid(token=token.strip(), column_name=column_name)
                        else 1
                    )
                    if (
                        token_index > 0
                        and not self.schema.has_commas[column_name]
                        and validity_matrix[token_index - 1][column_index] == 0
                    ):
                        validity_matrix[token_index][column_index] = 1
                    elif len(token) == 0 and self.schema.has_commas[column_name]:
                        validity_matrix[token_index][column_index] = 0
                else:
                    continue
                if (
                    validity_matrix[token_index][column_index] == 0
                    and first_valid_index == -1
                ):
                    first_valid_index = column_index
                if token_index != 0 and column_index > furthest_col:
                    break
            furthest_col = (
                first_valid_index
                if first_valid_index >= furthest_col + 1
                else furthest_col
            )
        return validity_matrix

    def __check_preceding_zero_in_path(
        self, validity_matrix: np.array, token_index: int, column_index: int
    ) -> bool:
        if column_index > 0 and token_index > 0:
            if (
                validity_matrix[token_index - 1][column_index - 1] == 0
                or validity_matrix[token_index - 1][column_index] == 0
            ):
                return True
        elif column_index == 0 and token_index > 0:
            if validity_matrix[token_index - 1][column_index] == 0:
                return True
        return False

    def __find_shortest_paths(self, validity_matrix: np.array) -> Optional[list[Path]]:
        (num_tokens, num_columns) = validity_matrix.shape
        G = nx.DiGraph()
        for row in range(num_tokens + 1):
            for column in range(num_columns + 1):
                if row < num_tokens and column < num_columns:
                    if validity_matrix[row][column] != 1:
                        G.add_edge(
                            u_of_edge=(row, column),
                            v_of_edge=(row + 1, column + 1),
                            weight=validity_matrix[row][column],
                        )
                        G.add_edge(
                            u_of_edge=(row, column),
                            v_of_edge=(row + 1, column),
                            weight=validity_matrix[row][column],
                        )
                elif row < num_tokens and column == num_columns - 1:
                    if validity_matrix[row][column] != 1:
                        G.add_edge(
                            u_of_edge=(row, column),
                            v_of_edge=(row + 1, column),
                            weight=validity_matrix[row][column],
                        )
        try:
            return list(
                nx.all_shortest_paths(G=G, source=(0, 0), target=(num_tokens, num_columns), weight="weight")
            )
        except NetworkXNoPath:
            logger.warning("No paths found")
            return None
        except NodeNotFound:
            logger.warning("Source node (0,0) not found")
            return None

    def export_to_csv(self, filepath: str):
        self.processed.to_csv(path_or_buf=filepath)
