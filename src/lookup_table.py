from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pickle
import sqlite3


@dataclass(frozen=True, init=True, kw_only=True)
class LookupTableKey:
    error_probability: float
    surface_intermediate_distance: int
    surface_final_distance: int
    initial_value: str
    steane_syndrome_extraction_pattern: str
    perfect_initialization: bool
    with_heuristic_post_selection: bool
    with_heuristic_gap_calculation: bool
    full_post_selection: bool
    num_stabilization_rounds_after_surgery: int
    num_epilogue_syndrome_extraction_rounds: int
    gap_threshold: float


def ensure_lookup_tables_table(con: sqlite3.Connection) -> None:
    con.execute('''
        CREATE TABLE IF NOT EXISTS lookup_tables (
            error_probability REAL,
            surface_intermediate_distance INTEGER,
            surface_final_distance INTEGER,
            initial_value TEXT,
            steane_syndrome_extraction_pattern TEXT,
            perfect_initialization BOOLEAN,
            with_heuristic_post_selection BOOLEAN,
            with_heuristic_gap_calculation BOOLEAN,
            full_post_selection BOOLEAN,
            num_stabilization_rounds_after_surgery INTEGER,
            num_epilogue_syndrome_extraction_rounds INTEGER,
            gap_threshold REAL,
            lookup_table_blob BLOB,
            PRIMARY KEY (
                error_probability,
                surface_intermediate_distance,
                surface_final_distance,
                initial_value,
                perfect_initialization,
                with_heuristic_post_selection,
                with_heuristic_gap_calculation,
                full_post_selection,
                num_stabilization_rounds_after_surgery,
                num_epilogue_syndrome_extraction_rounds,
                gap_threshold
            )
        )
    ''')
    con.commit()


def query_lookup_table(con: sqlite3.Connection, key: LookupTableKey) -> LookupTableWithNegativeSamplesOnly | None:
    cur = con.cursor()
    res = cur.execute(
        'SELECT lookup_table_blob from lookup_tables WHERE '
        'error_probability = ? AND '
        'surface_intermediate_distance = ? AND '
        'surface_final_distance = ? AND '
        'initial_value = ? AND '
        'steane_syndrome_extraction_pattern = ? AND '
        'perfect_initialization = ? AND '
        'with_heuristic_post_selection = ? AND '
        'with_heuristic_gap_calculation = ? AND '
        'full_post_selection = ? AND '
        'num_stabilization_rounds_after_surgery = ? AND '
        'num_epilogue_syndrome_extraction_rounds = ? AND '
        'gap_threshold = ?', (
            key.error_probability,
            key.surface_intermediate_distance,
            key.surface_final_distance,
            key.initial_value,
            key.steane_syndrome_extraction_pattern,
            key.perfect_initialization,
            key.with_heuristic_post_selection,
            key.with_heuristic_gap_calculation,
            key.full_post_selection,
            key.num_stabilization_rounds_after_surgery,
            key.num_epilogue_syndrome_extraction_rounds,
            key.gap_threshold
        )
    )

    entry = res.fetchone()
    if entry is None:
        return None
    assert isinstance(entry, tuple)
    assert len(entry) == 1
    assert isinstance(entry[0], bytes)
    lookup_table = pickle.loads(entry[0])
    assert isinstance(lookup_table, LookupTableWithNegativeSamplesOnly)
    return lookup_table


def store_lookup_table(
        con: sqlite3.Connection, key: LookupTableKey, lookup_table: LookupTableWithNegativeSamplesOnly) -> None:
    cur = con.cursor()
    lookup_table_blob = pickle.dumps(lookup_table)

    cur.execute(
        'INSERT OR REPLACE INTO lookup_tables (error_probability, surface_intermediate_distance,'
        'surface_final_distance, initial_value, steane_syndrome_extraction_pattern, perfect_initialization,'
        'with_heuristic_post_selection, with_heuristic_gap_calculation, full_post_selection,'
        'num_stabilization_rounds_after_surgery,'
        'num_epilogue_syndrome_extraction_rounds, gap_threshold,'
        'lookup_table_blob) VALUES '
        '(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (
            key.error_probability,
            key.surface_intermediate_distance,
            key.surface_final_distance,
            key.initial_value,
            key.steane_syndrome_extraction_pattern,
            key.perfect_initialization,
            key.with_heuristic_post_selection,
            key.with_heuristic_gap_calculation,
            key.full_post_selection,
            key.num_stabilization_rounds_after_surgery,
            key.num_epilogue_syndrome_extraction_rounds,
            key.gap_threshold,
            lookup_table_blob
        )
    )
    con.commit()


class LookupTable:
    def __init__(self, gap_threshold: float) -> None:
        self.table: dict[bytes, tuple[int, int]] = {}
        self.gap_threshold = gap_threshold
        self._num_samples: int = 0
        self._reject_nontrivial: bool = False

    def add(self, syndrome: np.ndarray, gap: float, expected: bool) -> None:
        bytes = syndrome.tobytes()
        if bytes not in self.table:
            self.table[bytes] = (0, 0)

        (a, b) = self.table[bytes]
        if not expected or gap < self.gap_threshold:
            b += 1
        else:
            a += 1
        self.table[bytes] = (a, b)
        self._num_samples += 1

    def extend(self, other: LookupTable) -> None:
        assert self.gap_threshold == other.gap_threshold
        for (bytes, (a, b)) in other.table.items():
            if bytes not in self.table:
                self.table[bytes] = (0, 0)
            (a_self, b_self) = self.table[bytes]
            self.table[bytes] = (a_self + a, b_self + b)
        self._num_samples += other._num_samples

    def negative_samples_only(self, min_samples) -> LookupTableWithNegativeSamplesOnly:
        if self._reject_nontrivial:
            return LookupTableWithNegativeSamplesOnly(match_all_nontrivial=True)

        lookup_table = LookupTableWithNegativeSamplesOnly()
        lookup_table.table = {
            bytes: count for (bytes, (a, count)) in self.table.items() if a == 0 and count >= min_samples
        }
        return lookup_table

    def set_reject_nontrivial(self) -> None:
        self._reject_nontrivial = True

    def __len__(self) -> int:
        return len(self.table)

    def num_samples(self) -> int:
        return self._num_samples


class LookupTableWithNegativeSamplesOnly:
    def __init__(self, match_all_nontrivial: bool = False) -> None:
        self.table: dict[bytes, int] = {}
        self.match_all_nontrivial = match_all_nontrivial

    def __len__(self) -> int:
        return len(self.table)

    def __contains__(self, key: object) -> bool:
        if not isinstance(key, bytes):
            return NotImplemented
        if self.match_all_nontrivial:
            return any(key)
        return key in self.table
