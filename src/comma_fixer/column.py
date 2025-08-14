from dataclasses import dataclass
from typing import Callable, Optional, TypeAlias

IsValidFunction: TypeAlias = Callable[[str], bool]
"""
    TypeAlias for Callable[[str], bool]
"""


@dataclass
class Column:
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
        return self._data_type

    def is_nullable(self) -> bool:
        return self._nullable

    def has_commas(self) -> bool:
        return self._has_commas

    def has_spaces(self) -> bool:
        return self._has_spaces

    def get_format(self) -> Optional[str]:
        return self._format

    def is_valid(self, token: str) -> bool:
        return self._is_valid(token)
