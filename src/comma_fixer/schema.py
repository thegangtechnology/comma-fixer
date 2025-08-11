from dataclasses import dataclass
import re
from typing import Callable, Optional, TypeAlias

ColumnName: TypeAlias = str

@dataclass
class Schema:
    types: dict[ColumnName, any]
    is_valid_functions: dict[ColumnName, Callable[[str], bool]]
    has_commas: dict[ColumnName, bool]

    @classmethod
    def new_schema(cls) -> 'Schema':
        return Schema(dict(), dict(), dict())
    
    def add_column(self, column_name: str, column_type: type, is_nullable: bool, has_commas: bool, has_spaces: bool, format: Optional[str] = None): 
        self.types[column_name] = column_type
        self.has_commas[column_name] = has_commas

        def is_valid(input: str) -> bool:
            if len(input) == 0:
                return is_nullable
            
            try:
                parsed_input = column_type(input)

                if column_type == str:
                    if ' ' in parsed_input and not has_spaces: 
                        return False
                    if ',' in parsed_input and not has_commas:
                        return False
                    if format != None:
                        if re.match(format, parsed_input) == None:
                            return False
                return True
            except:
                return False
        
        self.is_valid_functions[column_name] = is_valid
    
    def is_token_valid(self, token: str, column_name: str) -> bool:
        return self.is_valid_functions[column_name](token)
    
    def __str__(self) -> str:
        return f"{self.type}"