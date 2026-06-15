import argparse
import matplotlib.pyplot as plt
import sinter
import sys

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from sinter import Fit, fit_binomial
from typing import Any


@dataclass
class Task:
    num_valid_cases: int
    num_wrong_cases: int
    num_discarded_cases: int


# See https://docs.google.com/spreadsheets/d/1NV1PXI3OCJHO0QLHeb4nQcJ7v9jxXbYIJyWrJgQPSQg/edit?gid=852091432.
BASELINE: list[Task] = [
    Task(num_valid_cases=572826270, num_wrong_cases=1030983, num_discarded_cases=426142747),
    Task(num_valid_cases=560421558, num_wrong_cases=188085, num_discarded_cases=439390357),
    Task(num_valid_cases=531248572, num_wrong_cases=23654, num_discarded_cases=468727774),
    Task(num_valid_cases=500684164, num_wrong_cases=4790, num_discarded_cases=499311046),
    Task(num_valid_cases=470606449, num_wrong_cases=1853, num_discarded_cases=529391698),
    Task(num_valid_cases=441364648, num_wrong_cases=1049, num_discarded_cases=558634303),
    Task(num_valid_cases=410652368, num_wrong_cases=766, num_discarded_cases=589346866),
    Task(num_valid_cases=380059490, num_wrong_cases=640, num_discarded_cases=619939870),
    Task(num_valid_cases=353224151, num_wrong_cases=577, num_discarded_cases=646775272),
    Task(num_valid_cases=277587287, num_wrong_cases=424, num_discarded_cases=722412289),
]
assert all(t.num_valid_cases + t.num_wrong_cases + t.num_discarded_cases == 1e+9 for t in BASELINE)

# See https://docs.google.com/spreadsheets/d/1NV1PXI3OCJHO0QLHeb4nQcJ7v9jxXbYIJyWrJgQPSQg/edit?gid=509351113#gid=509351113.
WITH_LESS_SINGLE_QUBIT_GATE_ERRORS: list[Task] = [
    Task(num_valid_cases=2302727503, num_wrong_cases=4138001, num_discarded_cases=1693134496),
    Task(num_valid_cases=2239428531, num_wrong_cases=571469, num_discarded_cases=1760000000),
    Task(num_valid_cases=2119923486, num_wrong_cases=76514, num_discarded_cases=1880000000),
    Task(num_valid_cases=1999981432, num_wrong_cases=18568, num_discarded_cases=2000000000),
    Task(num_valid_cases=1879992874, num_wrong_cases=7126, num_discarded_cases=2120000000),
    Task(num_valid_cases=1759995947, num_wrong_cases=4053, num_discarded_cases=2240000000),
    Task(num_valid_cases=1639997011, num_wrong_cases=2989, num_discarded_cases=2360000000),
    Task(num_valid_cases=1519997435, num_wrong_cases=2565, num_discarded_cases=2480000000),
    Task(num_valid_cases=1399997720, num_wrong_cases=2280, num_discarded_cases=2600000000),
    Task(num_valid_cases=1039998374, num_wrong_cases=1626, num_discarded_cases=2960000000),
]
assert all(
    t.num_valid_cases + t.num_wrong_cases + t.num_discarded_cases == 4e+9 for t in WITH_LESS_SINGLE_QUBIT_GATE_ERRORS)

# See https://docs.google.com/spreadsheets/d/1NV1PXI3OCJHO0QLHeb4nQcJ7v9jxXbYIJyWrJgQPSQg/edit?gid=509351113#gid=509351113.
WITH_LESS_TWO_QUBIT_GATE_ERRORS: list[Task] = [
    Task(num_valid_cases=2416165930, num_wrong_cases=2689817, num_discarded_cases=1581144253),
    Task(num_valid_cases=2239966364, num_wrong_cases=33636, num_discarded_cases=1760000000),
    Task(num_valid_cases=2119993366, num_wrong_cases=6634, num_discarded_cases=1880000000),
    Task(num_valid_cases=1999995913, num_wrong_cases=4087, num_discarded_cases=2000000000),
    Task(num_valid_cases=1879997215, num_wrong_cases=2785, num_discarded_cases=2120000000),
    Task(num_valid_cases=1639997900, num_wrong_cases=2100, num_discarded_cases=2360000000),
    Task(num_valid_cases=1519998056, num_wrong_cases=1944, num_discarded_cases=2480000000),
    Task(num_valid_cases=1279998365, num_wrong_cases=1635, num_discarded_cases=2720000000),
]
assert all(
    t.num_valid_cases + t.num_wrong_cases + t.num_discarded_cases == 4e+9 for t in WITH_LESS_TWO_QUBIT_GATE_ERRORS)

# See https://docs.google.com/spreadsheets/d/1NV1PXI3OCJHO0QLHeb4nQcJ7v9jxXbYIJyWrJgQPSQg/edit?gid=509351113#gid=509351113.
WITH_LESS_RESET_ERRORS: list[Task] = [
    Task(num_valid_cases=2334105755, num_wrong_cases=4013358, num_discarded_cases=1661880887),
    Task(num_valid_cases=2239776733, num_wrong_cases=223267, num_discarded_cases=1760000000),
    Task(num_valid_cases=2119954772, num_wrong_cases=45228, num_discarded_cases=1880000000),
    Task(num_valid_cases=1999984575, num_wrong_cases=15425, num_discarded_cases=2000000000),
    Task(num_valid_cases=1879994282, num_wrong_cases=5718, num_discarded_cases=2120000000),
    Task(num_valid_cases=1759996551, num_wrong_cases=3449, num_discarded_cases=2240000000),
    Task(num_valid_cases=1639997300, num_wrong_cases=2700, num_discarded_cases=2360000000),
    Task(num_valid_cases=1519997704, num_wrong_cases=2296, num_discarded_cases=2480000000),
    Task(num_valid_cases=1399997900, num_wrong_cases=2100, num_discarded_cases=2600000000),
    Task(num_valid_cases=1159998260, num_wrong_cases=1740, num_discarded_cases=2840000000),
]
assert all(
    t.num_valid_cases + t.num_wrong_cases + t.num_discarded_cases == 4e+9 for t in WITH_LESS_RESET_ERRORS)

# See https://docs.google.com/spreadsheets/d/1NV1PXI3OCJHO0QLHeb4nQcJ7v9jxXbYIJyWrJgQPSQg/edit?gid=509351113#gid=509351113.
WITH_LESS_MEASUREMENT_ERRORS: list[Task] = [
    Task(num_valid_cases=2326439583, num_wrong_cases=4098197, num_discarded_cases=1669462220),
    Task(num_valid_cases=2239708695, num_wrong_cases=291305, num_discarded_cases=1760000000),
    Task(num_valid_cases=2119949118, num_wrong_cases=50882, num_discarded_cases=1880000000),
    Task(num_valid_cases=1999984007, num_wrong_cases=15993, num_discarded_cases=2000000000),
    Task(num_valid_cases=1879994134, num_wrong_cases=5866, num_discarded_cases=2120000000),
    Task(num_valid_cases=1759996454, num_wrong_cases=3546, num_discarded_cases=2240000000),
    Task(num_valid_cases=1639997318, num_wrong_cases=2682, num_discarded_cases=2360000000),
    Task(num_valid_cases=1519997694, num_wrong_cases=2306, num_discarded_cases=2480000000),
    Task(num_valid_cases=1399997931, num_wrong_cases=2069, num_discarded_cases=2600000000),
    Task(num_valid_cases=1039998495, num_wrong_cases=1505, num_discarded_cases=2960000000),
]
assert all(
    t.num_valid_cases + t.num_wrong_cases + t.num_discarded_cases == 4e+9 for t in WITH_LESS_MEASUREMENT_ERRORS)

# See https://docs.google.com/spreadsheets/d/1NV1PXI3OCJHO0QLHeb4nQcJ7v9jxXbYIJyWrJgQPSQg/edit?gid=509351113#gid=509351113.
WITH_LESS_IDLE_ERRORS: list[Task] = [
    Task(num_valid_cases=2513447019, num_wrong_cases=3544831, num_discarded_cases=1483008150),
    Task(num_valid_cases=2239983296, num_wrong_cases=16704, num_discarded_cases=1760000000),
    Task(num_valid_cases=2119994168, num_wrong_cases=5832, num_discarded_cases=1880000000),
    Task(num_valid_cases=1999996940, num_wrong_cases=3060, num_discarded_cases=2000000000),
    Task(num_valid_cases=1879997800, num_wrong_cases=2200, num_discarded_cases=2120000000),
    Task(num_valid_cases=1759998157, num_wrong_cases=1843, num_discarded_cases=2240000000),
    Task(num_valid_cases=1639998362, num_wrong_cases=1638, num_discarded_cases=2360000000),
    Task(num_valid_cases=1519998505, num_wrong_cases=1495, num_discarded_cases=2480000000),
    Task(num_valid_cases=1279998781, num_wrong_cases=1219, num_discarded_cases=2720000000),
]
assert all(
    t.num_valid_cases + t.num_wrong_cases + t.num_discarded_cases == 4e+9 for t in WITH_LESS_IDLE_ERRORS)


def plot_series(
        ax: plt.Axes,
        series: Iterable[Task],
        *,
        label: str,
        color: str,
        marker: str) -> None:
    xs: list[float] = []
    ys_low: list[float] = []
    ys_best: list[float] = []
    ys_high: list[float] = []

    for task in series:
        num_shots = task.num_valid_cases + task.num_wrong_cases + task.num_discarded_cases
        r: sinter.Fit = sinter.fit_binomial(num_shots=task.num_valid_cases + task.num_wrong_cases,
                                            num_hits=task.num_wrong_cases, max_likelihood_factor=1e3)

        x = (task.num_valid_cases + task.num_wrong_cases) / num_shots
        xs.append(x)
        ys_low.append(r.low)
        ys_best.append(r.best)
        ys_high.append(r.high)

    ax.plot(xs, ys_best, label=label, color=color, marker=marker)
    ax.fill_between(xs, ys_low, ys_high, alpha=0.2, color=color, zorder=-1)


def main() -> None:
    parser = argparse.ArgumentParser(description='description')
    parser.add_argument('--out', type=str, default=None)

    args = parser.parse_args()
    if args.out is None:
        print('The output filename should be specified via --out.', file=sys.stderr)
        sys.exit(1)
    output_filename: str = args.out

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.set_xlabel('Distillation success probability')
    ax.set_xlim(0.2, 0.6)

    ax.set_yscale('log')
    ax.set_ylabel('Logical error probability')
    ax.set_ylim(1e-7, 1e-3)

    plot_series(ax, BASELINE, label='uniform ($1.0 × 10^{-3}$)', color='C1', marker='v')
    plot_series(ax, WITH_LESS_SINGLE_QUBIT_GATE_ERRORS, label='single-qubit gate error probability=$6.7 × 10^{-4}$', color='C2', marker='*')
    plot_series(ax, WITH_LESS_TWO_QUBIT_GATE_ERRORS, label='two-qubit gate error probability=$6.7 × 10^{-4}$', color='C3', marker='o')
    plot_series(ax, WITH_LESS_RESET_ERRORS, label='reset error probability=$6.7 × 10^{-4}$', color='C4', marker='s')
    plot_series(ax, WITH_LESS_MEASUREMENT_ERRORS, label='measurement error probability=$6.7 × 10^{-4}$', color='C5', marker='D')
    plot_series(ax, WITH_LESS_IDLE_ERRORS, label='idling error probability=$6.7 × 10^{-4}$', color='C6', marker='P')

    ax.grid(which='major', color='#000000')
    ax.grid(which='minor', color='#DDDDDD')
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_filename)


if __name__ == '__main__':
    main()
