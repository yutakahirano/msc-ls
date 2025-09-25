import argparse
import matplotlib.pyplot as plt
import sinter
import sys

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any


@dataclass
class Task:
    num_valid_cases: int
    num_wrong_cases: int
    num_discarded_cases: int


def translate_to_sinter_tasks(tasks: list[Task]) -> list[sinter.TaskStats]:
    sinter_tasks: list[sinter.TaskStats] = []
    for i, task in enumerate(tasks):
        sinter_tasks.append(sinter.TaskStats(
            shots=task.num_valid_cases + task.num_wrong_cases + task.num_discarded_cases,
            discards=task.num_discarded_cases,
            errors=task.num_wrong_cases,
            strong_id=f'task_{i}',
            decoder='',
            json_metadata={'d': task.d},
        ))
    return sinter_tasks


# See https://docs.google.com/spreadsheets/d/1NV1PXI3OCJHO0QLHeb4nQcJ7v9jxXbYIJyWrJgQPSQg/edit?gid=731228931.
SERIES_WITH_DISTANCE_3: list[Task] = [
    Task(num_valid_cases=585382708, num_wrong_cases=2356325, num_discarded_cases=412260967),
    Task(num_valid_cases=559636384, num_wrong_cases=363616, num_discarded_cases=440000000),
    Task(num_valid_cases=529830847, num_wrong_cases=169153, num_discarded_cases=470000000),
    Task(num_valid_cases=499969948, num_wrong_cases=30052, num_discarded_cases=500000000),
    Task(num_valid_cases=469992533, num_wrong_cases=7467, num_discarded_cases=530000000),
    Task(num_valid_cases=439995525, num_wrong_cases=4475, num_discarded_cases=560000000),
    Task(num_valid_cases=409998283, num_wrong_cases=1717, num_discarded_cases=590000000),
    Task(num_valid_cases=379998960, num_wrong_cases=1040, num_discarded_cases=620000000),
    Task(num_valid_cases=349999289, num_wrong_cases=711, num_discarded_cases=650000000),
    Task(num_valid_cases=319999407, num_wrong_cases=593, num_discarded_cases=680000000),
]

# See https://docs.google.com/spreadsheets/d/1NV1PXI3OCJHO0QLHeb4nQcJ7v9jxXbYIJyWrJgQPSQg/edit?gid=731228931.
SERIES_WITH_DISTANCE_5: list[Task] = [
    Task(num_valid_cases=572826270, num_wrong_cases=1030983, num_discarded_cases=426142747),
    Task(num_valid_cases=559816359, num_wrong_cases=183641, num_discarded_cases=440000000),
    Task(num_valid_cases=529977864, num_wrong_cases=22136, num_discarded_cases=470000000),
    Task(num_valid_cases=499995242, num_wrong_cases=4758, num_discarded_cases=500000000),
    Task(num_valid_cases=469998161, num_wrong_cases=1839, num_discarded_cases=530000000),
    Task(num_valid_cases=439998960, num_wrong_cases=1040, num_discarded_cases=560000000),
    Task(num_valid_cases=409999237, num_wrong_cases=763, num_discarded_cases=590000000),
    Task(num_valid_cases=379999360, num_wrong_cases=640, num_discarded_cases=620000000),
    Task(num_valid_cases=349999430, num_wrong_cases=570, num_discarded_cases=650000000),
    Task(num_valid_cases=319999490, num_wrong_cases=510, num_discarded_cases=680000000),
    Task(num_valid_cases=289999551, num_wrong_cases=449, num_discarded_cases=710000000),
    Task(num_valid_cases=259999603, num_wrong_cases=397, num_discarded_cases=740000000),
]

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
    ax.set_xlabel('Distillation success rate')
    ax.set_xlim(0.2, 0.6)

    ax.set_yscale('log')
    ax.set_ylabel('Logical error rate')
    ax.set_ylim(1e-6, 1e-3)

    plot_series(ax, SERIES_WITH_DISTANCE_3, label='MSC-LS, 3⇒11', color='C0', marker='o')
    plot_series(ax, SERIES_WITH_DISTANCE_5, label='MSC-LS, 5⇒11', color='C1', marker='v')
    plot_series(ax, SERIES_WITH_MSC, label='MSC', color='C2', marker='*')

    ax.grid(which='major', color='#000000')
    ax.grid(which='minor', color='#DDDDDD')
    ax.legend()
    fig.savefig(output_filename)
    plt.show()


if __name__ == '__main__':
    main()
