from dataclasses import dataclass
from typing import Callable, Optional, TypeAlias

IsValidFunction: TypeAlias = Callable[[str], bool]
"""
    TypeAlias for Callable[[str], bool]
"""


@dataclass
class Column:
    """
    Column class which contains information about a column's types and 
    what elements can be inserted into the column.

    Attributes:
        _name (str): Name of column.
        _data_type (type): Column type.
        _nullable (bool): Whether elements in column can be null.
        _has_commas (bool): Whether elements in column can contain commas.
        _has_spaces (bool): Whether elements in column can contain spaces.
        _format (Optional[str]): RegEx formatting for elements in column if needed.
        _is_valid (IsValidFunction): Function used to check if an element can be placed in column.
    """
    _name: str
    _data_type: type
    _nullable: bool
    _has_commas: bool
    _has_spaces: bool
    _format: Optional[str]
    _is_valid: IsValidFunction

    @classmethod
    def new(
        cls,
        name: str,
        data_type: type,
        is_nullable: bool,
        has_commas: bool,
        has_spaces: bool,
        format: Optional[str],
        is_valid: IsValidFunction,
    ) -> "Column":
        """
        Creates a Column with supplied arguments and returns it.

        Args:
            name (str): Name of column.
            data_type (type): Column type.
            nullable (bool): Whether elements in column can be null.
            has_commas (bool): Whether elements in column can contain commas.
            has_spaces (bool): Whether elements in column can contain spaces.
            format (Optional[str]): RegEx formatting for elements in column if needed.
            is_valid (IsValidFunction): Function used to check if an element can be placed in column.

        Returns:
            Column. Column object with specified values.
        """
        return Column(
            _name=name,
            _data_type=data_type,
            _nullable=is_nullable,
            _has_commas=has_commas,
            _has_spaces=has_spaces,
            _format=format,
            _is_valid=is_valid,
        )

    def get_type(self) -> type:
        """
        Returns data type of column.
        """
        return self._data_type

    def is_nullable(self) -> bool:
        """
        Returns whether elements in column can be null.
        """
        return self._nullable

    def has_commas(self) -> bool:
        """
        Returns whether elements in column can contain commas.
        """
        return self._has_commas

    def has_spaces(self) -> bool:
        """
        Returns whether elements in column can contain spaces.
        """
        return self._has_spaces

    def get_format(self) -> Optional[str]:
        """
        Returns RegEx formatting of elements in column if needed.
        """
        return self._format

    def is_valid(self, token: str) -> bool:
        """
        Returns whether elements can be placed in this column.
        """
        return self._is_valid(token)
