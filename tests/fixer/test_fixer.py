from unittest.mock import MagicMock

import numpy as np
import pytest

from comma_fixer.fixer import Fixer
from comma_fixer.schema import Schema


@pytest.fixture
def mock_schema():
    schema = Schema.new()
    schema.add_column("col1", str, False, False, False, r"^(?!INVALID$).*$")
    schema.add_column("col2", str, False, False, False, r"^(?!INVALID$).*$")
    schema.add_column("col3", str, False, False, False, r"^(?!INVALID$).*$")
    return schema


@pytest.fixture
def fixer(mock_schema):
    return Fixer.new(mock_schema)


def test_add_valid_row(fixer):
    # Patch __check_valid to simulate valid token split
    fixer._Fixer__check_valid = lambda entry: ["A", "B", "C"]
    res = fixer.process_row("some,data,row")
    assert res == ["A", "B", "C"]


def test_add_invalid_row(fixer):
    fixer._Fixer__check_valid = lambda entry: None
    res = fixer.process_row("bad,data")
    assert res is None


def test_construct_processed_entry_from_path(fixer):
    tokens = ["1", "2", "3"]
    path = [(0, 0), (1, 1), (2, 2)]
    result = fixer._Fixer__construct_processed_entry_from_path(path, tokens, 3, 3)
    assert result == ["1", "2", "3"]


def test_construct_validity_matrix_all_valid(mock_schema):
    # Tokens = 3, Columns = 3
    fixer = Fixer.new(mock_schema)
    entry = "A,B,C"
    matrix = fixer._Fixer__construct_validity_matrix(entry)
    assert matrix.shape == (3, 3)
    assert np.all((matrix == 0) | (matrix == 1))  # only 0 or 1


def test_construct_validity_matrix_with_invalid_token(mock_schema):
    # Simulate one invalid token
    fixer = Fixer.new(mock_schema)
    entry = "A,INVALID,C"
    matrix = fixer._Fixer__construct_validity_matrix(entry)
    assert matrix.shape == (3, 3)
    assert matrix[1].sum() == 3  # All columns invalid for 'INVALID'


def test_check_preceding_zero_in_path():
    fixer = Fixer.new(MagicMock())
    matrix = np.array([[0, 0, 1], [1, 1, 1], [1, 1, 1]])
    # Check for position (1, 1) which has preceding zeros
    assert fixer._Fixer__check_preceding_zero_in_path(matrix, 1, 1) is True
    # Position (2, 2) does not have a preceding 0
    assert fixer._Fixer__check_preceding_zero_in_path(matrix, 2, 2) is False


def test_find_shortest_paths_returns_path():
    fixer = Fixer.new(MagicMock())
    # Valid path in simple 2x2 case
    matrix = np.array([[0, 1], [1, 0]])
    paths = fixer._Fixer__find_shortest_paths(matrix)
    assert isinstance(paths, list)
    assert all(isinstance(p, list) for p in paths)
    assert (0, 0) == paths[0][0]  # Path starts at (0,0)


def test_find_shortest_paths_returns_none_on_no_path():
    fixer = Fixer.new(MagicMock())
    # Blocked matrix (all invalid)
    matrix = np.array([[1, 1], [1, 1]])
    result = fixer._Fixer__find_shortest_paths(matrix)
    assert result is None
