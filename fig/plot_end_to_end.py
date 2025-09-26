import argparse
import matplotlib.pyplot as plt
import sys

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any


@dataclass
class Task:
    num_valid_cases: int
    num_wrong_cases: int
    num_discarded_cases: int


# See https://docs.google.com/spreadsheets/d/1NV1PXI3OCJHO0QLHeb4nQcJ7v9jxXbYIJyWrJgQPSQg/edit?gid=852091432.
SERIES_WITH_DISTANCE_3: list[Task] = [
    Task(num_valid_cases=585382708, num_wrong_cases=2356325, num_discarded_cases=412260967),
    Task(num_valid_cases=560533083, num_wrong_cases=371375, num_discarded_cases=439095542),
    Task(num_valid_cases=530475973, num_wrong_cases=174315, num_discarded_cases=469349712),
    Task(num_valid_cases=501101451, num_wrong_cases=36901, num_discarded_cases=498861648),
    Task(num_valid_cases=470855594, num_wrong_cases=7748, num_discarded_cases=529136658),
    Task(num_valid_cases=440143568, num_wrong_cases=4480, num_discarded_cases=559851952),
    Task(num_valid_cases=410029905, num_wrong_cases=1718, num_discarded_cases=589968377),
    Task(num_valid_cases=380044801, num_wrong_cases=1041, num_discarded_cases=619954158),
    Task(num_valid_cases=350524797, num_wrong_cases=712, num_discarded_cases=649474491),
    Task(num_valid_cases=324261648, num_wrong_cases=601, num_discarded_cases=675737751),
]
assert all(t.num_valid_cases + t.num_wrong_cases + t.num_discarded_cases == 1e+9 for t in SERIES_WITH_DISTANCE_3)

# See https://docs.google.com/spreadsheets/d/1NV1PXI3OCJHO0QLHeb4nQcJ7v9jxXbYIJyWrJgQPSQg/edit?gid=852091432.
SERIES_WITH_DISTANCE_5: list[Task] = [
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
assert all(t.num_valid_cases + t.num_wrong_cases + t.num_discarded_cases == 1e+9 for t in SERIES_WITH_DISTANCE_5)

# See https://docs.google.com/spreadsheets/d/1NV1PXI3OCJHO0QLHeb4nQcJ7v9jxXbYIJyWrJgQPSQg/edit?gid=1169353086.
SERIES_WITH_MSC: list[Task] = [
    Task(num_valid_cases=536496810, num_wrong_cases=1220667, num_discarded_cases=462282523),
    Task(num_valid_cases=534970499, num_wrong_cases=645878, num_discarded_cases=464383623),
    Task(num_valid_cases=532980098, num_wrong_cases=379606, num_discarded_cases=466640296),
    Task(num_valid_cases=530257590, num_wrong_cases=250557, num_discarded_cases=469491853),
    Task(num_valid_cases=520547331, num_wrong_cases=110895, num_discarded_cases=479341774),
    Task(num_valid_cases=514861412, num_wrong_cases=72048, num_discarded_cases=485066540),
    Task(num_valid_cases=499549590, num_wrong_cases=38143, num_discarded_cases=500412267),
    Task(num_valid_cases=479219642, num_wrong_cases=20206, num_discarded_cases=520760152),
    Task(num_valid_cases=446223229, num_wrong_cases=8677, num_discarded_cases=553768094),
    Task(num_valid_cases=387244834, num_wrong_cases=1910, num_discarded_cases=612753256),
    Task(num_valid_cases=358000034, num_wrong_cases=1063, num_discarded_cases=641998903),
    Task(num_valid_cases=326373831, num_wrong_cases=670, num_discarded_cases=673625499),
    Task(num_valid_cases=289314224, num_wrong_cases=453, num_discarded_cases=710685323),
    Task(num_valid_cases=237737154, num_wrong_cases=299, num_discarded_cases=762262547),
]
assert all(t.num_valid_cases + t.num_wrong_cases + t.num_discarded_cases == 1e+9 for t in SERIES_WITH_MSC)


def plot_series(
        ax: plt.Axes,
        seriese: Iterable[Task],
        *,
        label: str,
        color: str,
        marker: str) -> None:
    xs: list[float] = []
    ys: list[float] = []
    for task in seriese:
        num_shots = task.num_valid_cases + task.num_wrong_cases + task.num_discarded_cases
        x = (task.num_valid_cases + task.num_wrong_cases) / num_shots
        y = (task.num_wrong_cases) / (task.num_valid_cases + task.num_wrong_cases)
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

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.set_xlabel('Distillation success probability')
    ax.set_xlim(0.2, 0.6)

    ax.set_yscale('log')
    ax.set_ylabel('Logical error probability')
    ax.set_ylim(1e-6, 1e-3)

    plot_series(ax, SERIES_WITH_DISTANCE_3, label='MSC-LS, 3⇒11', color='C0', marker='o')
    plot_series(ax, SERIES_WITH_DISTANCE_5, label='MSC-LS, 5⇒11', color='C1', marker='v')
    plot_series(ax, SERIES_WITH_MSC, label='MSC', color='C2', marker='*')

    ax.grid(which='major', color='#000000')
    ax.grid(which='minor', color='#DDDDDD')
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_filename)

if __name__ == '__main__':
    main()
