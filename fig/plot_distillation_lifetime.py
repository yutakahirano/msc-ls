import argparse
import collections
import math
import sys

from dataclasses import dataclass
from matplotlib import pyplot as plt


@dataclass
class Round:
    desc: str
    num_qubits: int
    round_success_rate: float


WITHOUT_LOOKUP_TABLE: list[Round] = [
    Round(desc='Encode T', num_qubits=14, round_success_rate=1.0),
    Round(desc='Stablize', num_qubits=16, round_success_rate=0.846),
    Round(desc='Check T', num_qubits=16, round_success_rate=0.967),
    Round(desc='Check T', num_qubits=16, round_success_rate=0.932),
    Round(desc='Perform LS', num_qubits=66, round_success_rate=0.979),
    Round(desc='Perform LS', num_qubits=66, round_success_rate=0.838),
    Round(desc='Perform LS', num_qubits=66, round_success_rate=0.918),
    Round(desc='Expand', num_qubits=241, round_success_rate=1.0),
    Round(desc='Stabilize', num_qubits=241, round_success_rate=1.0),
    Round(desc='Stabilize', num_qubits=241, round_success_rate=1.0),
    Round(desc='Stabilize', num_qubits=241, round_success_rate=1.0),
    Round(desc='[Wait for gap]', num_qubits=241, round_success_rate=1.0),
    Round(desc='[Wait for gap]', num_qubits=241, round_success_rate=1.0),
    Round(desc='[Wait for gap]', num_qubits=241, round_success_rate=1.0),
    Round(desc='[Wait for gap]', num_qubits=241, round_success_rate=1.0),
    Round(desc='[Wait for gap]', num_qubits=241, round_success_rate=1.0),
    Round(desc='[Wait for gap]', num_qubits=241, round_success_rate=1.0),
    Round(desc='[Wait for gap]', num_qubits=241, round_success_rate=1.0),
    Round(desc='[Wait for gap]', num_qubits=241, round_success_rate=1.0),
    Round(desc='[Wait for gap]', num_qubits=241, round_success_rate=1.0),
    Round(desc='[Wait for gap]', num_qubits=241, round_success_rate=0.616),
    Round(desc='ready', num_qubits=241, round_success_rate=1.0),
]

WITH_LOOKUP_TABLE: list[Round] = [
    Round(desc='Encode T', num_qubits=14, round_success_rate=1.0),
    Round(desc='Stablize', num_qubits=16, round_success_rate=0.846),
    Round(desc='Check T', num_qubits=16, round_success_rate=0.967),
    Round(desc='Check T', num_qubits=16, round_success_rate=0.932),
    Round(desc='Perform LS', num_qubits=66, round_success_rate=0.979),
    Round(desc='Perform LS', num_qubits=66, round_success_rate=0.838),
    Round(desc='Perform LS', num_qubits=66, round_success_rate=0.764),
    Round(desc='Expand', num_qubits=241, round_success_rate=1.0),
    Round(desc='Stabilize', num_qubits=241, round_success_rate=1.0),
    Round(desc='Stabilize', num_qubits=241, round_success_rate=1.0),
    Round(desc='Stabilize', num_qubits=241, round_success_rate=1.0),
    Round(desc='[Wait for gap]', num_qubits=241, round_success_rate=1.0),
    Round(desc='[Wait for gap]', num_qubits=241, round_success_rate=1.0),
    Round(desc='[Wait for gap]', num_qubits=241, round_success_rate=1.0),
    Round(desc='[Wait for gap]', num_qubits=241, round_success_rate=1.0),
    Round(desc='[Wait for gap]', num_qubits=241, round_success_rate=1.0),
    Round(desc='[Wait for gap]', num_qubits=241, round_success_rate=1.0),
    Round(desc='[Wait for gap]', num_qubits=241, round_success_rate=1.0),
    Round(desc='[Wait for gap]', num_qubits=241, round_success_rate=1.0),
    Round(desc='[Wait for gap]', num_qubits=241, round_success_rate=1.0),
    Round(desc='[Wait for gap]', num_qubits=241, round_success_rate=0.739),
    Round(desc='ready', num_qubits=241, round_success_rate=1.0),
]


def desc(n: float) -> str:
    power = math.floor(math.log10(n))
    while 10**(power + 1) <= n:
        power += 1
    base = round(n / 10**power * 10) / 10
    base = str(base).ljust(3, '0')
    return fr'${base} \cdot 10^{{{power}}}$'


def plot_series(
        ax: plt.Axes,
        series: list[Round],
        *,
        label: str | None = None) -> None:
    labels = [r.desc for r in series]
    ax.set_xticks(range(len(labels) + 1), [''] * (len(labels) + 1))
    ax.set_xticks([i + 0.5 for i in range(len(labels))], labels, rotation=90, minor=True)
    ax.xaxis.set_tick_params(length=0, which='minor')

    xs: list[float] = [0]
    ys: list[float] = [1]
    prob = 1.0
    for (i, round) in enumerate(series):
        xs.append(i + 1)
        ys.append(prob)
        prob *= round.round_success_rate
        xs.append(i + 1)
        ys.append(prob)

    ax.plot(xs, ys, label='Survival Probability', color='C0')
    ax.fill_between(xs, [0 for _ in ys], ys, alpha=0.2, color='C0')

    xs = []
    ys = []
    max_qubits = max(r.num_qubits for r in series)
    prev: float = 0
    for (i, round) in enumerate(series):
        xs.append(i)
        ys.append(prev)
        num_qubits = round.num_qubits
        xs.append(i)
        ys.append(num_qubits / max_qubits)
        prev = num_qubits / max_qubits
    xs.append(len(series))
    ys.append(prev)

    ax.fill_between(xs, [0 for _ in ys], ys, alpha=0.2, color='C1')
    ax.plot(xs, ys, label='Qubits Activated', color='C1')


def main():
    parser = argparse.ArgumentParser(description='description')
    parser.add_argument('--out', type=str, default=None)

    args = parser.parse_args()
    if args.out is None:
        print('The output filename should be specified via --out.', file=sys.stderr)
        sys.exit(1)
    if '{}' not in args.out:
        print('The output filename should contain a placeholder mark "{}".', file=sys.stderr)
        sys.exit(1)
    output_filename_without = args.out.format('without-lookup-table')
    output_filename_with = args.out.format('with-lookup-table')

    caption_without = (
        'MSC-LS without the lookup table\n'
        '$d_{{intermediate}} = 5$, $d_{{final}} = 11$, $gap = 15.48$\n'
        '(expected qubit·rounds=6044)'
    )
    caption_with = (
        'MSC-LS with the lookup table\n'
        '$d_{{intermediate}} = 5$, $d_{{final}} = 11$, $gap = 15.48$\n'
        '(expected qubit·rounds=5127)'
    )
    output_filename = args.out.format('comparison')
    settings = [
        (WITHOUT_LOOKUP_TABLE, output_filename_without, caption_without),
        (WITH_LOOKUP_TABLE, output_filename_with, caption_with),
    ]

    for (series, filename, caption) in settings:
        fig, ax = plt.subplots(figsize=(6, 5))
        ax.set_title(caption)
        ax.set_xlim(0, len(series))
        ax.set_ylabel('Proportion')
        ax.set_ylim(0, 1.01)

        plot_series(ax, series)

        ax.grid(which='major', color='#BBBBBB')
        ax.legend()

        fig.tight_layout()
        fig.savefig(filename)


if __name__ == '__main__':
    main()
