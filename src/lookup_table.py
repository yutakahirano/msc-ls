from __future__ import annotations

import numpy as np
import pickle
import sqlite3


class LookupTableKey:
    def __init__(self, *, error_probability: float, surface_intermediate_distance: int, surface_final_distance: int,
                 initial_value: str, perfect_initialization: bool, with_heulistic_post_selection: bool,
                 full_post_selection: bool, num_epilogue_syndrome_extraction_rounds: int,
                 gap_threshold: float) -> None:
        self.error_probability = error_probability
        self.surface_intermediate_distance = surface_intermediate_distance
        self.surface_final_distance = surface_final_distance
        self.initial_value = initial_value
        self.perfect_initialization = perfect_initialization
        self.with_heulistic_post_selection = with_heulistic_post_selection
        self.full_post_selection = full_post_selection
        self.num_epilogue_syndrome_extraction_rounds = num_epilogue_syndrome_extraction_rounds
        self.gap_threshold = gap_threshold

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LookupTableKey):
            return NotImplemented
        return (
            self.error_probability == other.error_probability and
            self.surface_intermediate_distance == other.surface_intermediate_distance and
            self.surface_final_distance == other.surface_final_distance and
            self.initial_value == other.initial_value and
            self.perfect_initialization == other.perfect_initialization and
            self.with_heulistic_post_selection == other.with_heulistic_post_selection and
            self.full_post_selection == other.full_post_selection and
            self.num_epilogue_syndrome_extraction_rounds == other.num_epilogue_syndrome_extraction_rounds and
            self.gap_threshold == other.gap_threshold
        )


def ensure_lookup_tables_table(con: sqlite3.Connection) -> None:
    con.execute('''
        CREATE TABLE IF NOT EXISTS lookup_tables (
            error_probability REAL,
            surface_intermediate_distance INTEGER,
            surface_final_distance INTEGER,
            initial_value TEXT,
            perfect_initialization BOOLEAN,
            with_heulistic_post_selection BOOLEAN,
            full_post_selection BOOLEAN,
            num_epilogue_syndrome_extraction_rounds INTEGER,
            gap_threshold REAL,
            lookup_table_blob BLOB,
            PRIMARY KEY (
                error_probability,
                surface_intermediate_distance,
                surface_final_distance,
                initial_value,
                perfect_initialization,
                with_heulistic_post_selection,
                full_post_selection,
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
        'perfect_initialization = ? AND '
        'with_heulistic_post_selection = ? AND '
        'full_post_selection = ? AND '
        'num_epilogue_syndrome_extraction_rounds = ? AND '
        'gap_threshold = ?', (
            key.error_probability,
            key.surface_intermediate_distance,
            key.surface_final_distance,
            key.initial_value,
            key.perfect_initialization,
            key.with_heulistic_post_selection,
            key.full_post_selection,
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
        'INSERT INTO lookup_tables (error_probability, surface_intermediate_distance, surface_final_distance, '
        'initial_value, perfect_initialization, with_heulistic_post_selection, full_post_selection, '
        'num_epilogue_syndrome_extraction_rounds, gap_threshold, lookup_table_blob) VALUES '
        '(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (
            key.error_probability,
            key.surface_intermediate_distance,
            key.surface_final_distance,
            key.initial_value,
            key.perfect_initialization,
            key.with_heulistic_post_selection,
            key.full_post_selection,
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
        lookup_table = LookupTableWithNegativeSamplesOnly()
        lookup_table.table = {
            bytes: count for (bytes, (a, count)) in self.table.items() if a == 0 and count >= min_samples
        }
        return lookup_table

    def __len__(self) -> int:
        return len(self.table)

    def num_samples(self) -> int:
        return self._num_samples


class LookupTableWithNegativeSamplesOnly:
    def __init__(self) -> None:
        self.table: dict[bytes, int] = {}

    def __len__(self) -> int:
        return len(self.table)

    def __contains__(self, key: object) -> bool:
        if not isinstance(key, bytes):
            return NotImplemented
        return key in self.table
