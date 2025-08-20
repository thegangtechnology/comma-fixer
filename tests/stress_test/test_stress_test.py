import logging
import time

import numpy as np
import pytest

from comma_fixer.column import Column
from comma_fixer.fixer import Fixer
from comma_fixer.schema import Schema

logger = logging.getLogger("Stress Test Logs")


def run_shortest_path_on_n_tokens_by_n_columns(
    fixer: Fixer, n_token: int, n_col: int, seed: int
):
    if n_col > n_token:
        print("Invalid n_token x n_col size!")
        return

    np.random.seed(seed)

    v_tc = np.random.randint(2, size=(n_token, n_col))
    np.fill_diagonal(v_tc, 0)
    start = time.time()
    _ = fixer._Fixer__find_shortest_paths(v_tc)
    end = time.time()
    logger.info(f"{end-start}")
    return end - start


@pytest.mark.stress_test
class TestShortestPath:
    seed = 33_550_336

    def test_50_tokens_by_40_columns(self):
        fixer = Fixer.new(
            Schema.new(
                columns=[
                    Column.numeric(name=f"col_{x}", has_commas=True) for x in range(40)
                ]
            )
        )
        execution_time = run_shortest_path_on_n_tokens_by_n_columns(
            fixer, 50, 40, self.seed
        )
        assert execution_time < 1

    def test_100_tokens_by_100_columns(self):
        fixer = Fixer.new(
            Schema.new(
                columns=[
                    Column.numeric(name=f"col_{x}", has_commas=True) for x in range(100)
                ]
            )
        )
        execution_time = run_shortest_path_on_n_tokens_by_n_columns(
            fixer, 100, 100, self.seed
        )
        assert execution_time < 1

    def test_60_tokens_by_30_columns(self):
        fixer = Fixer.new(
            Schema.new(
                columns=[
                    Column.numeric(name=f"col_{x}", has_commas=True) for x in range(30)
                ]
            )
        )
        execution_time = run_shortest_path_on_n_tokens_by_n_columns(
            fixer, 60, 30, self.seed
        )
        assert execution_time < 1

    def test_1000_tokens_by_1000_columns(self):
        fixer = Fixer.new(
            Schema.new(
                columns=[
                    Column.numeric(name=f"col_{x}", has_commas=True)
                    for x in range(1000)
                ]
            )
        )
        execution_time = run_shortest_path_on_n_tokens_by_n_columns(
            fixer, 1000, 1000, self.seed
        )
        assert execution_time < 20
