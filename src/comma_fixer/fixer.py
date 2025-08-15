import logging
from dataclasses import dataclass
from typing import Optional, TypeAlias

import networkx as nx
import numpy as np
from networkx import NetworkXNoPath, NodeNotFound

from comma_fixer.parsed import Parsed
from comma_fixer.schema import Schema

ParsedEntry: TypeAlias = list[str]
Path: TypeAlias = list[tuple[int, int]]
ValidityMatrix: TypeAlias = np.ndarray

logger = logging.getLogger("Fixer Logs")


@dataclass
class Fixer:
    """
    Class for fixing malformed CSV files.

    Contains a dataframe to hold processed entries from
    the CSV file, a Schema object which defines the dataframe,
    and a list of invalid entries (i.e. entries that may contain
    more than one method of grouping to fit into schema).

    Attributes:
        schema (`Schema`): Schema object defining the columns
        of the dataset.
    """

    schema: Schema

    @classmethod
    def new(cls, schema: Schema) -> "Fixer":
        """ "
        Create a new Fixer class with a Schema object.

        Args:
            schema (`Schema`): Schema defining column name, type, and
            validity functions.

        Returns:
            Fixer. Fixer object with initialised DataFrame according to Schema.
        """
        return Fixer(schema)

    def process_row(self, new_entry: str) -> Optional[ParsedEntry]:
        """
        Processes a new row against the columns in the schema.

        If the entry contains a valid parsing, returns it, otherwise
        returns None.

        Args:
            new_entry (str): Row to be processed.

        Returns:
            Optional[ParsedEntry]. Returns processed entry if valid parsing exists,
            and None otherwise.
        """
        return self.__check_valid(new_entry.strip())

    def fix_file(self, filepath: str, skip_first_line: bool = True) -> Parsed:
        """
        Processes a CSV file line by line using schema,
        and identifies invalid entries.

        After processing, prints out the number of valid entries against invalid entries.

        Args:
            filepath (str): Filepath of CSV file to be processed.
            skip_first_line (bool): Whether or not to skip the first line.

        Returns:
            Parsed. Parsed object which holds processed lines, invalid lines, and
            function to export parsed lines to CSV.
        """
        parsed = Parsed.new(schema=self.schema)
        line_count = 0
        with open(filepath) as file:
            for line in file:
                line = line.strip()
                if not skip_first_line:
                    processed_entry = self.process_row(line)
                    if processed_entry is not None:
                        parsed.add_valid_entry(processed_entry)
                    else:
                        parsed.add_invalid_entry(line_index=line_count, entry=line)
                    line_count += 1
                else:
                    skip_first_line = not skip_first_line
        total_entries = line_count - 1 if skip_first_line else line_count
        print(
            f"File has been processed!\nNumber of total entries: {total_entries}\
            \n Number of invalid entries: {len(parsed.invalid_line_numbers)}"
        )
        return parsed

    def __check_valid(self, new_entry: str) -> Optional[ParsedEntry]:
        """
        Checks whether a row is valid and returns the parsed entry if valid.

        Tokenises the row by delimiter and checks which tokens can be placed
        in which columns. If a valid parsing exists, returns it as a list of
        tokens.

        Args:
            new_entry (str): Row to be processed.

        Returns:
            Optional[ParsedEntry]: List of parsed tokens if the row is valid.
        """
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
        path: Path,
        tokens: list[str],
        num_cols: int,
        num_tokens: int,
    ) -> ParsedEntry:
        """
        Constructs a ParsedEntry from a valid path and given tokens.

        Args:
            path (Path): List of tuples of the shortest path that
            creates a parsed entry from the validity matrix.
            tokens (list[str]): List of tokens from splitting entry
            string by the delimiter.
            num_cols (int): Number of columns in schema.
            num_tokens (int): Number of tokens after splitting entry
            string by the delimiter.

        Returns:
            ParsedEntry. List of tokens parsed such that the entry is valid
            according to the schema.
        """
        processed_entry = ["" for _ in range(num_cols)]
        column_names = self.schema.get_column_names()
        previous_col = -1
        for step in path:
            if step[0] < num_tokens and step[1] < num_cols:
                if step[1] != previous_col:
                    if (
                        previous_col >= 0
                        and len(processed_entry[previous_col]) == 0
                        and not self.schema.columns[
                            column_names[previous_col]
                        ].is_nullable()
                    ):
                        logger.warning(
                            "Failed - Parsed null element into non-null column."
                        )
                        return None
                    processed_entry[step[1]] = tokens[step[0]].strip()
                    previous_col = step[1]
                else:
                    if len(processed_entry[step[1]]) == 0:
                        processed_entry[step[1]] = tokens[step[0]].strip()
                    elif len(tokens[step[0]]) != 0:
                        processed_entry[step[1]] = (
                            f"{processed_entry[step[1]]},{tokens[step[0]].strip()}"
                        )
        return processed_entry

    def __construct_validity_matrix(self, new_entry: str) -> ValidityMatrix:
        """
        Constructs a validity matrix from the entry string against the
        columns in schema.

        ValidityMatrix of size number of tokens by number of columns in schema,
        where the number of tokens is obtained from splitting entry string by
        the delimiter.

        Entries in the matrix are either 0 or 1, where 0 denotes that the
        token can be placed in that column, and 1 otherwise.

        Args:
            new_entry (str): String to be processed.

        Returns:
            ValidityMatrix. Matrix of size number of tokens by number of columns in schema.
        """
        tokens = new_entry.split(",")
        num_cols = len(self.schema.get_column_names())
        num_tokens = len(tokens)
        validity_matrix = np.ones((num_tokens, num_cols))
        furthest_col = 0

        for token_index, token in enumerate(tokens):
            first_valid_index = -1
            for column_index, column_name in enumerate(self.schema.get_column_names()):
                preceding_zero = self.__check_preceding_zero_in_path(
                    validity_matrix=validity_matrix,
                    token_index=token_index,
                    column_index=column_index,
                )
                if preceding_zero or token_index == 0:
                    validity_matrix[token_index][column_index] = (
                        0
                        if self.schema.is_token_valid(
                            token=token.strip(), column_name=column_name
                        )
                        else 1
                    )
                    logger.warning(f"[{token_index}][{column_index}] set to {validity_matrix[token_index][column_index]}")
                    if (
                        token_index > 0
                        and not self.schema.columns[column_name].has_commas()
                        and validity_matrix[token_index - 1][column_index] == 0
                    ):
                        validity_matrix[token_index][column_index] = 1
                        logger.warning(f"[{token_index}][{column_index}] changed to {validity_matrix[token_index][column_index]}")
                    elif (
                        len(token) == 0
                        and self.schema.columns[column_name].has_commas()
                    ):
                        validity_matrix[token_index][column_index] = 0
                        logger.warning(f"[{token_index}][{column_index}] changed to {validity_matrix[token_index][column_index]}")
                else:
                    logger.warning(f"[{token_index}][{column_index}] not set")
                    continue
                if (
                    validity_matrix[token_index][column_index] == 0
                    and first_valid_index == -1
                    and token_index == 0
                ):
                    first_valid_index = column_index
                    break
                elif (
                    validity_matrix[token_index][column_index] == 0
                    and column_index > first_valid_index
                ):
                    first_valid_index = column_index
                if token_index != 0 and column_index > furthest_col:
                    logger.warning(f"Break at {column_index}")
                    break
            furthest_col = (
                first_valid_index
                if first_valid_index >= furthest_col + 1
                else furthest_col
            )
        return validity_matrix

    def __check_preceding_zero_in_path(
        self, validity_matrix: ValidityMatrix, token_index: int, column_index: int
    ) -> bool:
        """
        Checks whether the preceding elements in the matrix given an entry are 0,
        resulting in a valid path.

        Given `(token_index, column_index)`, checks whether the preceding elements
        in the path leading to the current element is valid, which creates a valid
        path.

        Preceding elements is the previous token in the same column,
        and the previous token in the prior columnn.

        Args:
            validity_matrix (ValidityMatrix): Matrix to check whether preceding elements
            in path are valid.
            token_index (int): Current token/row being validated.
            column_index (int): Current column being validated.

        Returns:
            Boolean. Returns True if the path to current element is valid, and False otherwise.
        """
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

    def __find_shortest_paths(
        self, validity_matrix: ValidityMatrix
    ) -> Optional[list[Path]]:
        """
        Finds the shortest paths from the constructed validity matrix if one exists using networkx.

        Constructs a networkx directed acyclic graph from the validity matrix and
        finds the shortest paths such that the first token is in the first column, and the
        final token is in the final column.

        Args:
            validity_matrix (ValidityMatrix): Validity matrix constructed from the entry
            to be processed against schema columns.

        Returns:
            Optional[list[Path]]. Returns a list of shortest paths if at least one exists, and
            None otherwise.
        """
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
        logger.warning(validity_matrix)
        try:
            return list(
                nx.all_shortest_paths(
                    G=G,
                    source=(0, 0),
                    target=(num_tokens, num_columns),
                    weight="weight",
                )
            )
        except NetworkXNoPath:
            logger.warning("No paths found")
            return None
        except NodeNotFound:
            logger.warning("Source node (0,0) not found")
            return None
