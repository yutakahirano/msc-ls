import argparse
import matplotlib.pyplot as plt
import sys

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any


@dataclass
class Entry:
    num_valid_cases: int
    num_wrong_cases: int
    num_discarded_cases: int
    cost: float


# See https://docs.google.com/spreadsheets/d/1NV1PXI3OCJHO0QLHeb4nQcJ7v9jxXbYIJyWrJgQPSQg/edit?gid=852091432.
SERIES_WITHOUT_TABLE: list[Entry] = [
    Entry(num_valid_cases=572826270, num_wrong_cases=1030983, num_discarded_cases=426142747, cost=3720.513),
    Entry(num_valid_cases=560421558, num_wrong_cases=188085, num_discarded_cases=439390357, cost=3808.431),
    Entry(num_valid_cases=531248572, num_wrong_cases=23654, num_discarded_cases=468727774, cost=4018.737),
    Entry(num_valid_cases=500684164, num_wrong_cases=4790, num_discarded_cases=499311046, cost=4264.211),
    Entry(num_valid_cases=470606449, num_wrong_cases=1853, num_discarded_cases=529391698, cost=4536.774),
    Entry(num_valid_cases=441364648, num_wrong_cases=1049, num_discarded_cases=558634303, cost=4837.357),
    Entry(num_valid_cases=410652368, num_wrong_cases=766, num_discarded_cases=589346866, cost=5199.141),
    Entry(num_valid_cases=353224151, num_wrong_cases=577, num_discarded_cases=646775272, cost=6044.434),
    Entry(num_valid_cases=277587287, num_wrong_cases=424, num_discarded_cases=722412289, cost=7691.419),
]
assert all(t.num_valid_cases + t.num_wrong_cases + t.num_discarded_cases == 1e+9 for t in SERIES_WITHOUT_TABLE)

# See https://docs.google.com/spreadsheets/d/1NV1PXI3OCJHO0QLHeb4nQcJ7v9jxXbYIJyWrJgQPSQg/edit?gid=852091432.
SERIES_WITH_TABLE: list[Entry] = [
    Entry(num_valid_cases=572826270, num_wrong_cases=1030983, num_discarded_cases=426142747, cost=3720.513),
    Entry(num_valid_cases=560421450, num_wrong_cases=188054, num_discarded_cases=439390496, cost=3793.356),
    Entry(num_valid_cases=531248476, num_wrong_cases=23647, num_discarded_cases=468727877, cost=3949.97),
    Entry(num_valid_cases=500684014, num_wrong_cases=4789, num_discarded_cases=499311197, cost=4101.854),
    Entry(num_valid_cases=470606282, num_wrong_cases=1853, num_discarded_cases=529391865, cost=4247.582),
    Entry(num_valid_cases=441364569, num_wrong_cases=1049, num_discarded_cases=558634382, cost=4420.644),
    Entry(num_valid_cases=410652298, num_wrong_cases=766, num_discarded_cases=589346936, cost=4612.832),
    Entry(num_valid_cases=353224101, num_wrong_cases=577, num_discarded_cases=646775322, cost=5127.45),
    Entry(num_valid_cases=277587287, num_wrong_cases=424, num_discarded_cases=722412289, cost=5089.845),
]
assert all(t.num_valid_cases + t.num_wrong_cases + t.num_discarded_cases == 1e+9 for t in SERIES_WITH_TABLE)

# See https://docs.google.com/spreadsheets/d/1NV1PXI3OCJHO0QLHeb4nQcJ7v9jxXbYIJyWrJgQPSQg/edit?gid=1135421454.
SERIES_MSC: list[Entry] = [
    Entry(num_valid_cases=536496810, num_wrong_cases=1220667, num_discarded_cases=462282523, cost=6861.56875),
    Entry(num_valid_cases=534970499, num_wrong_cases=645878, num_discarded_cases=464383623, cost=6877.763073),
    Entry(num_valid_cases=532980098, num_wrong_cases=379606, num_discarded_cases=466640296, cost=6919.658916),
    Entry(num_valid_cases=530257590, num_wrong_cases=250557, num_discarded_cases=469491853, cost=6961.067716),
    Entry(num_valid_cases=520547331, num_wrong_cases=110895, num_discarded_cases=479341774, cost=7082.811246),
    Entry(num_valid_cases=514861412, num_wrong_cases=72048, num_discarded_cases=485066540, cost=7168.038949),
    Entry(num_valid_cases=499549590, num_wrong_cases=38143, num_discarded_cases=500412267, cost=7366.662187),
    Entry(num_valid_cases=479219642, num_wrong_cases=20206, num_discarded_cases=520760152, cost=7690.52653),
    Entry(num_valid_cases=446223229, num_wrong_cases=8677, num_discarded_cases=553768094, cost=8264.581607),
    Entry(num_valid_cases=387244834, num_wrong_cases=1910, num_discarded_cases=612753256, cost=9475.572636),
    Entry(num_valid_cases=358000034, num_wrong_cases=1063, num_discarded_cases=641998903, cost=10322.42352),
    Entry(num_valid_cases=326373831, num_wrong_cases=670, num_discarded_cases=673625499, cost=11332.66964),
    Entry(num_valid_cases=289314224, num_wrong_cases=453, num_discarded_cases=710685323, cost=12789.12827),
    Entry(num_valid_cases=237737154, num_wrong_cases=299, num_discarded_cases=762262547, cost=15524.6264),
]
assert all(t.num_valid_cases + t.num_wrong_cases + t.num_discarded_cases == 1e+9 for t in SERIES_MSC)


def plot_series(
        ax: plt.Axes,
        seriese: Iterable[Entry],
        *,
        label: str,
        color: str,
        marker: str) -> None:
    xs: list[float] = []
    ys: list[float] = []
    for entry in seriese:
        x = entry.cost
        y = (entry.num_wrong_cases) / (entry.num_valid_cases + entry.num_wrong_cases)
        xs.append(x)
        ys.append(y)

    ax.plot(xs, ys, label=label, color=color, marker=marker)


def main() -> None:
    parser = argparse.ArgumentParser(description='description')
    parser.add_argument('--out', type=str, default=None)

    args = parser.parse_args()
    if args.out is None:
        print('The output filename should be specified via --out.', file=sys.stderr)
        sys.exit(1)
    output_filename: str = args.out

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.set_xlabel('Spacetime overhead of distillation (qubit·rounds)', fontsize=12)
    ax.set_xlim(0, 16000)

    ax.set_yscale('log')
    ax.set_ylabel('Logical error probability', fontsize=12)
    ax.set_ylim(1e-6, 1e-4)

    plot_series(ax, SERIES_WITHOUT_TABLE, label='MSC-LS without table', color='C0', marker='o')
    plot_series(ax, SERIES_WITH_TABLE, label='MSC-LS with table', color='C1', marker='v')
    plot_series(ax, SERIES_MSC, label='MSC', color='C2', marker='*')

    ax.grid(which='major', color='#000000')
    ax.grid(which='minor', color='#DDDDDD')
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_filename)


if __name__ == '__main__':
    main()
