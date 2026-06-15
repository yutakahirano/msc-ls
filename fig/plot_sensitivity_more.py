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
WITH_MORE_SINGLE_QUBIT_GATE_ERRORS: list[Task] = [
    Task(num_valid_cases=1137078058, num_wrong_cases=2046653, num_discarded_cases=860875289),
    Task(num_valid_cases=1119578315, num_wrong_cases=421685, num_discarded_cases=880000000),
    Task(num_valid_cases=1059940000, num_wrong_cases=60000, num_discarded_cases=940000000),
    Task(num_valid_cases=999988809, num_wrong_cases=11191, num_discarded_cases=1000000000),
    Task(num_valid_cases=939995937, num_wrong_cases=4063, num_discarded_cases=1060000000),
    Task(num_valid_cases=879997750, num_wrong_cases=2250, num_discarded_cases=1120000000),
    Task(num_valid_cases=819998340, num_wrong_cases=1660, num_discarded_cases=1180000000),
    Task(num_valid_cases=759998583, num_wrong_cases=1417, num_discarded_cases=1240000000),
    Task(num_valid_cases=699998745, num_wrong_cases=1255, num_discarded_cases=1300000000),
    Task(num_valid_cases=519999075, num_wrong_cases=925, num_discarded_cases=1480000000),
]
assert all(
    t.num_valid_cases + t.num_wrong_cases + t.num_discarded_cases == 2e+9 for t in WITH_MORE_SINGLE_QUBIT_GATE_ERRORS)

# See https://docs.google.com/spreadsheets/d/1NV1PXI3OCJHO0QLHeb4nQcJ7v9jxXbYIJyWrJgQPSQg/edit?gid=509351113#gid=509351113.
WITH_MORE_TWO_QUBIT_GATE_ERRORS: list[Task] = [
    Task(num_valid_cases=1056720129, num_wrong_cases=3375687, num_discarded_cases=939904184),
    Task(num_valid_cases=1056682565, num_wrong_cases=3317435, num_discarded_cases=940000000),
    Task(num_valid_cases=999764666, num_wrong_cases=235334, num_discarded_cases=1000000000),
    Task(num_valid_cases=939944126, num_wrong_cases=55874, num_discarded_cases=1060000000),
    Task(num_valid_cases=879982803, num_wrong_cases=17197, num_discarded_cases=1120000000),
    Task(num_valid_cases=819993590, num_wrong_cases=6410, num_discarded_cases=1180000000),
    Task(num_valid_cases=759996573, num_wrong_cases=3427, num_discarded_cases=1240000000),
    Task(num_valid_cases=699997713, num_wrong_cases=2287, num_discarded_cases=1300000000),
    Task(num_valid_cases=639998254, num_wrong_cases=1746, num_discarded_cases=1360000000),
    Task(num_valid_cases=579998530, num_wrong_cases=1470, num_discarded_cases=1420000000),
    Task(num_valid_cases=519998714, num_wrong_cases=1286, num_discarded_cases=1480000000),
    Task(num_valid_cases=399999023, num_wrong_cases=977, num_discarded_cases=1600000000),
]
assert all(
    t.num_valid_cases + t.num_wrong_cases + t.num_discarded_cases == 2e+9 for t in WITH_MORE_TWO_QUBIT_GATE_ERRORS)

# See https://docs.google.com/spreadsheets/d/1NV1PXI3OCJHO0QLHeb4nQcJ7v9jxXbYIJyWrJgQPSQg/edit?gid=509351113#gid=509351113.
WITH_MORE_RESET_ERRORS: list[Task] = [
    Task(num_valid_cases=1113906667, num_wrong_cases=2195633, num_discarded_cases=883897700),
    Task(num_valid_cases=1059895950, num_wrong_cases=104050, num_discarded_cases=940000000),
    Task(num_valid_cases=999976707, num_wrong_cases=23293, num_discarded_cases=1000000000),
    Task(num_valid_cases=939994215, num_wrong_cases=5785, num_discarded_cases=1060000000),
    Task(num_valid_cases=879996586, num_wrong_cases=3414, num_discarded_cases=1120000000),
    Task(num_valid_cases=819997841, num_wrong_cases=2159, num_discarded_cases=1180000000),
    Task(num_valid_cases=759998307, num_wrong_cases=1693, num_discarded_cases=1240000000),
    Task(num_valid_cases=699998555, num_wrong_cases=1445, num_discarded_cases=1300000000),
    Task(num_valid_cases=639998710, num_wrong_cases=1290, num_discarded_cases=1360000000),
    Task(num_valid_cases=459999098, num_wrong_cases=902, num_discarded_cases=1540000000),
]
assert all(
    t.num_valid_cases + t.num_wrong_cases + t.num_discarded_cases == 2e+9 for t in WITH_MORE_RESET_ERRORS)

# See https://docs.google.com/spreadsheets/d/1NV1PXI3OCJHO0QLHeb4nQcJ7v9jxXbYIJyWrJgQPSQg/edit?gid=509351113#gid=509351113.
WITH_MORE_MEASUREMENT_ERRORS: list[Task] = [
    Task(num_valid_cases=1119568140, num_wrong_cases=2139619, num_discarded_cases=878292241),
    Task(num_valid_cases=1118395968, num_wrong_cases=1604032, num_discarded_cases=880000000),
    Task(num_valid_cases=1059910290, num_wrong_cases=89710, num_discarded_cases=940000000),
    Task(num_valid_cases=999981888, num_wrong_cases=18112, num_discarded_cases=1000000000),
    Task(num_valid_cases=939994676, num_wrong_cases=5324, num_discarded_cases=1060000000),
    Task(num_valid_cases=879996671, num_wrong_cases=3329, num_discarded_cases=1120000000),
    Task(num_valid_cases=819997854, num_wrong_cases=2146, num_discarded_cases=1180000000),
    Task(num_valid_cases=759998302, num_wrong_cases=1698, num_discarded_cases=1240000000),
    Task(num_valid_cases=699998547, num_wrong_cases=1453, num_discarded_cases=1300000000),
    Task(num_valid_cases=639998699, num_wrong_cases=1301, num_discarded_cases=1360000000),
    Task(num_valid_cases=459999100, num_wrong_cases=900, num_discarded_cases=1540000000),
]
assert all(
    t.num_valid_cases + t.num_wrong_cases + t.num_discarded_cases == 2e+9 for t in WITH_MORE_MEASUREMENT_ERRORS)

# See https://docs.google.com/spreadsheets/d/1NV1PXI3OCJHO0QLHeb4nQcJ7v9jxXbYIJyWrJgQPSQg/edit?gid=509351113#gid=509351113.
WITH_MORE_IDLE_ERRORS: list[Task] = [
    Task(num_valid_cases=995761423, num_wrong_cases=2490447, num_discarded_cases=1001748130),
    Task(num_valid_cases=939876682, num_wrong_cases=123318, num_discarded_cases=1060000000),
    Task(num_valid_cases=879970774, num_wrong_cases=29226, num_discarded_cases=1120000000),
    Task(num_valid_cases=819992709, num_wrong_cases=7291, num_discarded_cases=1180000000),
    Task(num_valid_cases=759995710, num_wrong_cases=4290, num_discarded_cases=1240000000),
    Task(num_valid_cases=699997244, num_wrong_cases=2756, num_discarded_cases=1300000000),
    Task(num_valid_cases=639997796, num_wrong_cases=2204, num_discarded_cases=1360000000),
    Task(num_valid_cases=579998124, num_wrong_cases=1876, num_discarded_cases=1420000000),
    Task(num_valid_cases=399998743, num_wrong_cases=1257, num_discarded_cases=1600000000),
]
assert all(
    t.num_valid_cases + t.num_wrong_cases + t.num_discarded_cases == 2e+9 for t in WITH_MORE_IDLE_ERRORS)



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
    ax.set_ylim(1e-6, 1e-3)

    plot_series(ax, BASELINE, label='uniform ($1.0 × 10^{-3}$)', color='C1', marker='v')
    plot_series(ax, WITH_MORE_SINGLE_QUBIT_GATE_ERRORS, label='single-qubit gate error probability=$1.5 × 10^{-3}$', color='C2', marker='*')
    plot_series(ax, WITH_MORE_TWO_QUBIT_GATE_ERRORS, label='two-qubit gate error probability=$1.5 × 10^{-3}$', color='C3', marker='o')
    plot_series(ax, WITH_MORE_RESET_ERRORS, label='reset error probability=$1.5 × 10^{-3}$', color='C4', marker='s')
    plot_series(ax, WITH_MORE_MEASUREMENT_ERRORS, label='measurement error probability=$1.5 × 10^{-3}$', color='C5', marker='D')
    plot_series(ax, WITH_MORE_IDLE_ERRORS, label='idling error probability=$1.5 × 10^{-3}$', color='C6', marker='P')

    ax.grid(which='major', color='#000000')
    ax.grid(which='minor', color='#DDDDDD')
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_filename)


if __name__ == '__main__':
    main()
