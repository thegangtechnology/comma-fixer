import re
from dataclasses import dataclass
from typing import Callable, Optional, TypeAlias

import numpy as np
import pandas as pd

from comma_fixer.column import Column

ColumnName: TypeAlias = str
"""
    TypeAlias for string
"""
IsValidFunction: TypeAlias = Callable[[str], bool]
"""
    TypeAlias for Callable[[str], bool]
"""


@dataclass
class Schema:
    """
    Class containing information on a dataset's columns.

    Stores the column type, functions for checking whether an
    element can be placed in the column, and whether the column
    allows commas.

    Attributes:
        types (dict[ColumnName, any]): Dictionary containing the
        types associated with each column.
        series_types (dict[ColumnName, any]): Dictionary containing
        the panda.Series types associated with each column for initialising a DataFrame.
        is_valid_functions (dict[ColumnName, IsValidFunction]): Dictionary containing
        functions to determine whether a token can be placed in a column.
        has_commas (dict[ColumnName, bool]): Dictionary containing
        booleans on whether a column can contain commas.
    """

    columns: dict[ColumnName, Column]
    series_types: dict[ColumnName, type]

    @classmethod
    def new(cls) -> "Schema":
        """
        Create a new Schema object.

        Schema can be added to to define the name and type of a column in the
        schema, and how to determine whether an element belongs to that column.

        Used in conjunction with the Fixer class.

        Returns:
            Empty Schema.
        """
        return Schema(dict(), dict())

    def __create_is_valid_function(
        self,
        column_type: type,
        is_nullable: bool,
        has_commas: bool,
        has_spaces: bool,
        format: Optional[str] = None,
    ) -> IsValidFunction:
        """
        Create a function to verify whether an element belongs within a column.

        Function is created based on the arguments passed in.

        Args:
            column_type (type): Python type or numpy.dtype of elements in column.
            is_nullable (bool): Whether elements in column can be nullable.
            has_commas (bool): Whether elements in column can contain commas.
            has_spaces (bool): Whether elements in column can contain spaces.
            format (Optional[str]): RegEx formatting for text columns (optional).

        Returns:
            Callable[[str], bool]. Function which takes in a string and returns
            whether the element belongs in a given column.
        """

        def is_valid(input: str) -> bool:
            if len(input) == 0:
                return is_nullable

            try:
                parsed_input = column_type(input)

                if column_type == str:
                    if " " in parsed_input and not has_spaces:
                        return False
                    if "," in parsed_input and not has_commas:
                        return False
                    if format is not None:
                        if re.match(format, parsed_input) is None:
                            return False
                return True
            except ValueError:
                return False

        return is_valid

    def add_column(
        self,
        column_name: str,
        column_type: type,
        is_nullable: bool,
        has_commas: bool,
        has_spaces: bool,
        format: Optional[str] = None,
    ):
        """
        Add a new column to the schema with a specific column type.

        Additionally creates an `is_valid` function for the column.

        Args:
            column_name (str): Name of column in schema.
            column_type (type): Python type or numpy.dtype of elements in column.
            is_nullable (bool): Whether elements in column can be nullable.
            has_commas (bool): Whether elements in column can contain commas.
            has_spaces (bool): Whether elements in column can contain spaces.
            format (Optional[str]): RegEx formatting for text columns (optional).
        """

        is_valid = self.__create_is_valid_function(
            column_type=column_type,
            is_nullable=is_nullable,
            has_commas=has_commas,
            has_spaces=has_spaces,
            format=format,
        )

        new_column = Column.new(
            name=column_name,
            data_type=column_type,
            is_nullable=is_nullable,
            has_commas=has_commas,
            has_spaces=has_spaces,
            format=format,
            is_valid=is_valid,
        )
        if column_type == np.datetime64:
            self.series_types[column_name] = pd.Series(dtype="datetime64[ns]")
        else:
            self.series_types[column_name] = pd.Series(dtype=column_type)
        self.columns[column_name] = new_column

    def add_str_column(
        self,
        column_name: str,
        is_nullable: bool,
        has_commas: bool,
        has_spaces: bool,
        format: Optional[str] = None,
    ):
        """
        Add a new string type column to the schema.

        Additionally creates an `is_valid` function for the column.

        Args:
            column_name (str): Name of column in schema.
            is_nullable (bool): Whether elements in column can be nullable.
            has_commas (bool): Whether elements in column can contain commas.
            has_spaces (bool): Whether elements in column can contain spaces.
            format (Optional[str]): RegEx formatting for text columns (optional).
        """
        data_type = str
        is_valid = self.__create_is_valid_function(
            column_type=data_type,
            is_nullable=is_nullable,
            has_commas=has_commas,
            has_spaces=has_spaces,
            format=format,
        )

        new_column = Column.new(
            name=column_name,
            data_type=data_type,
            is_nullable=is_nullable,
            has_commas=has_commas,
            has_spaces=has_spaces,
            format=format,
            is_valid=is_valid,
        )
        self.series_types[column_name] = pd.Series(dtype=data_type)
        self.columns[column_name] = new_column

    def add_int_column(
        self,
        column_name: str,
        is_nullable: bool = False,
        has_commas: bool = False,
        has_spaces: bool = False,
        format: Optional[str] = None,
    ):
        """
        Add a new integer type column to the schema.

        Additionally creates an `is_valid` function for the column.

        Args:
            column_name (str): Name of column in schema.
            is_nullable (bool): Whether elements in column can be nullable.
            has_commas (bool): Whether elements in column can contain commas.
            has_spaces (bool): Whether elements in column can contain spaces.
            format (Optional[str]): RegEx formatting for text columns (optional).
        """
        data_type = int
        is_valid = self.__create_is_valid_function(
            column_type=data_type,
            is_nullable=is_nullable,
            has_commas=has_commas,
            has_spaces=has_spaces,
            format=format,
        )

        new_column = Column.new(
            name=column_name,
            data_type=data_type,
            is_nullable=is_nullable,
            has_commas=has_commas,
            has_spaces=has_spaces,
            format=format,
            is_valid=is_valid,
        )
        self.series_types[column_name] = pd.Series(dtype=data_type)
        self.columns[column_name] = new_column

    def add_float_column(
        self,
        column_name: str,
        is_nullable: bool = False,
        has_commas: bool = False,
        has_spaces: bool = False,
        format: Optional[str] = None,
    ):
        """
        Add a new float type column to the schema.

        Additionally creates an `is_valid` function for the column.

        Args:
            column_name (str): Name of column in schema.
            is_nullable (bool): Whether elements in column can be nullable.
            has_commas (bool): Whether elements in column can contain commas.
            has_spaces (bool): Whether elements in column can contain spaces.
            format (Optional[str]): RegEx formatting for text columns (optional).
        """
        data_type = float
        is_valid = self.__create_is_valid_function(
            column_type=data_type,
            is_nullable=is_nullable,
            has_commas=has_commas,
            has_spaces=has_spaces,
            format=format,
        )

        new_column = Column.new(
            name=column_name,
            data_type=data_type,
            is_nullable=is_nullable,
            has_commas=has_commas,
            has_spaces=has_spaces,
            format=format,
            is_valid=is_valid,
        )
        self.series_types[column_name] = pd.Series(dtype=data_type)
        self.columns[column_name] = new_column

    def add_datetime_column(
        self,
        column_name: str,
        is_nullable: bool = False,
        has_commas: bool = False,
        has_spaces: bool = False,
        format: Optional[str] = None,
    ):
        """
        Add a new datetime type column to the schema.

        Additionally creates an `is_valid` function for the column.

        Args:
            column_name (str): Name of column in schema.
            is_nullable (bool): Whether elements in column can be nullable.
            has_commas (bool): Whether elements in column can contain commas.
            has_spaces (bool): Whether elements in column can contain spaces.
            format (Optional[str]): RegEx formatting for text columns (optional).
        """
        data_type = np.datetime64
        is_valid = self.__create_is_valid_function(
            column_type=data_type,
            is_nullable=is_nullable,
            has_commas=has_commas,
            has_spaces=has_spaces,
            format=format,
        )

        new_column = Column.new(
            name=column_name,
            data_type=data_type,
            is_nullable=is_nullable,
            has_commas=has_commas,
            has_spaces=has_spaces,
            format=format,
            is_valid=is_valid,
        )
        self.series_types[column_name] = pd.Series(dtype="datetime64[ns]")
        self.columns[column_name] = new_column

    def is_token_valid(self, token: str, column_name: str) -> bool:
        """
        Check whether a string token is valid for a specified column.

        Calls the specified column's `is_valid` function to check
        whether the element can be placed in that column.

        Args:
            token (str): String token to be validated
            column_name (str): Column the token is validated against

        Returns:
            bool. Returns True if the token can be placed within the
            specified column, False otherwise.
        """
        return self.columns[column_name].is_valid(token)

    def get_column_names(self) -> list[str]:
        """
        Return a list of column names in the schema.

        Returns:
            List[str]. List containing the name of the columns in the schema.
        """
        return list(self.columns.keys())

    def __str__(self) -> str:
        return f"{self.types}"

    def schema_info(self):
        """
        Prints out information about the current schema.
        """
        schema_df = pd.DataFrame(
            columns=["name", "type", "nullable", "has commas", "has spaces", "format"]
        )
        for column_name, column in list(self.columns.items()):
            schema_df.loc[len(schema_df)] = [
                column_name,
                column.get_type().__name__,
                column.is_nullable(),
                column.has_commas(),
                column.has_spaces(),
                column.get_format(),
            ]
        return schema_df.style
