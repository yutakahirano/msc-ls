import argparse
import sqlite3
import sys

from lookup_table import LookupTableKey, LookupTableWithNegativeSamplesOnly
from lookup_table import ensure_lookup_tables_table, query_lookup_table


def main() -> None:
    parser = argparse.ArgumentParser(description='description')
    parser.add_argument('--error-probability', type=float, default=0)
    parser.add_argument('--surface-intermediate-distance', type=int, default=None)
    parser.add_argument('--surface-final-distance', type=int, default=3)
    parser.add_argument('--initial-value', choices=['+', '0', 'S+'], default='+')
    parser.add_argument('--steane-syndrome-extraction-pattern', choices=['XZZ', 'ZXZ', 'ZZ'], default='ZXZ',)
    parser.add_argument('--perfect-initialization', action='store_true')
    parser.add_argument('--imperfect-initialization', action='store_true')
    parser.add_argument('--with-heuristic-post-selection', action='store_true')
    parser.add_argument('--with-heuristic-gap-calculation', action='store_true')
    parser.add_argument('--full-post-selection', action='store_true')
    parser.add_argument('--num-epilogue-syndrome-extraction-rounds', type=int, default=10)
    parser.add_argument('--gap-threshold', type=float)
    parser.add_argument('--interval', type=int, default=1)

    args = parser.parse_args()

    if args.perfect_initialization and args.imperfect_initialization:
        print('Error: Cannot specify both --perfect-initialization and --imperfect-initialization.', file=sys.stderr)
        return

    perfect_initialization: bool = False
    if args.perfect_initialization:
        perfect_initialization = True
    elif args.imperfect_initialization:
        perfect_initialization = False

    print('  error-probability = {}'.format(args.error_probability))
    print('  surface-intermediate-distance = {}'.format(args.surface_intermediate_distance))
    print('  surface-final-distance = {}'.format(args.surface_final_distance))
    print('  initial-value = {}'.format(args.initial_value))
    print('  steane-syndrome-extraction-pattern = {}'.format(args.steane_syndrome_extraction_pattern))
    print('  perfect-initialization = {}'.format(perfect_initialization))
    print('  with-heuristic-post-selection = {}'.format(args.with_heuristic_post_selection))
    print('  with-heuristic-gap-calculation = {}'.format(args.with_heuristic_gap_calculation))
    print('  full-post-selection = {}'.format(args.full_post_selection))
    print('  num-epilogue-syndrome-extraction-rounds = {}'.format(args.num_epilogue_syndrome_extraction_rounds))
    print('  gap-threshold = {}'.format(args.gap_threshold))
    print('  interval = {}'.format(args.interval))

    error_probability: float = args.error_probability
    surface_final_distance: int = args.surface_final_distance
    surface_intermediate_distance: int = args.surface_intermediate_distance or surface_final_distance
    initial_value: str
    match args.initial_value:
        case '+':
            initial_value = 'Plus'
        case '0':
            initial_value = 'Zero'
        case 'S+':
            initial_value = 'SPlus'
        case _:
            raise ValueError(f"Invalid initial value: {args.initial_value}")
    steane_syndrome_extraction_pattern: str = args.steane_syndrome_extraction_pattern
    gap_threshold: float = args.gap_threshold

    with_heuristic_post_selection: bool = args.with_heuristic_post_selection
    with_heuristic_gap_calculation: bool = args.with_heuristic_gap_calculation
    full_post_selection: bool = args.full_post_selection
    num_epilogue_syndrome_extraction_rounds: int = args.num_epilogue_syndrome_extraction_rounds
    interval = args.interval

    lookup_table_key = LookupTableKey(
        error_probability=error_probability,
        surface_intermediate_distance=surface_intermediate_distance,
        surface_final_distance=surface_final_distance,
        initial_value=initial_value,
        steane_syndrome_extraction_pattern=steane_syndrome_extraction_pattern,
        perfect_initialization=perfect_initialization,
        with_heuristic_post_selection=with_heuristic_post_selection,
        with_heuristic_gap_calculation=with_heuristic_gap_calculation,
        full_post_selection=full_post_selection,
        num_epilogue_syndrome_extraction_rounds=num_epilogue_syndrome_extraction_rounds,
        gap_threshold=gap_threshold)

    lookup_table: LookupTableWithNegativeSamplesOnly | None = None
    with sqlite3.connect('lookup_table.db') as lookup_table_con:
        ensure_lookup_tables_table(lookup_table_con)

        lookup_table = query_lookup_table(lookup_table_con, lookup_table_key)
    if lookup_table is None:
        print('Lookup table is not found.', file=sys.stderr)
        return

    print('#entries = {}'.format(len(lookup_table)))
    ls: list[int] = [count for (bytes, count) in lookup_table.table.items()]
    ls.sort(reverse=True)

    sum = 0
    for (i, count) in enumerate(ls):
        if i % interval == 0:
            print('{:8d} {:12d}'.format(i, sum))
        sum += count

    print('{:8d} {:12d}'.format(len(ls), sum))


if __name__ == '__main__':
    main()
