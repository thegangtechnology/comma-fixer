import re
from dataclasses import dataclass
from typing import Callable, Optional, TypeAlias

import numpy as np
import pandas as pd

ColumnName: TypeAlias = str
IsValidFunction: TypeAlias = Callable[[str], bool]


@dataclass
class Schema:
    types: dict[ColumnName, any]
    series_types: dict[ColumnName, any]
    is_valid_functions: dict[ColumnName, Callable[[str], IsValidFunction]]
    has_commas: dict[ColumnName, bool]

    @classmethod
    def new_schema(cls) -> "Schema":
        """
        Create a new Schema object.

        Schema can be added to to define the name and type of a column in the
        schema, and how to determine whether an element belongs to that column.

        Used in conjunction with the Fixer class.

        Returns:
            Empty Schema.
        """
        return Schema(dict(), dict(), dict(), dict())

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
        self.types[column_name] = column_type
        if column_type == np.datetime64:
            self.series_types[column_name] = pd.Series(dtype="datetime64[ns]")
        else:
            self.series_types[column_name] = pd.Series(dtype=column_type)
        self.has_commas[column_name] = has_commas

        self.is_valid_functions[column_name] = self.__create_is_valid_function(
            column_type=column_type,
            is_nullable=is_nullable,
            has_commas=has_commas,
            has_spaces=has_spaces,
            format=format,
        )

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
        self.types[column_name] = str
        self.series_types[column_name] = pd.Series(dtype=str)
        self.has_commas[column_name] = has_commas

        self.is_valid_functions[column_name] = self.__create_is_valid_function(
            column_type=str,
            is_nullable=is_nullable,
            has_commas=has_commas,
            has_spaces=has_spaces,
            format=format,
        )

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
        self.types[column_name] = int
        self.series_types[column_name] = pd.Series(dtype=int)
        self.has_commas[column_name] = has_commas

        self.is_valid_functions[column_name] = self.__create_is_valid_function(
            column_type=int,
            is_nullable=is_nullable,
            has_commas=has_commas,
            has_spaces=has_spaces,
            format=format,
        )

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
        self.types[column_name] = float
        self.series_types[column_name] = pd.Series(dtype=float)
        self.has_commas[column_name] = has_commas

        self.is_valid_functions[column_name] = self.__create_is_valid_function(
            column_type=float,
            is_nullable=is_nullable,
            has_commas=has_commas,
            has_spaces=has_spaces,
            format=format,
        )

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
        self.types[column_name] = np.datetime64
        self.series_types[column_name] = pd.Series(dtype="datetime64[ns]")
        self.has_commas[column_name] = has_commas

        self.is_valid_functions[column_name] = self.__create_is_valid_function(
            column_type=np.datetime64,
            is_nullable=is_nullable,
            has_commas=has_commas,
            has_spaces=has_spaces,
            format=format,
        )

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
        return self.is_valid_functions[column_name](token)

    def get_column_names(self) -> list[str]:
        """
        Return a list of column names in the schema.

        Returns:
            List[str]. List containing the name of the columns in the schema.
        """
        return list(self.types.keys())

    def __str__(self) -> str:
        return f"{self.types}"
