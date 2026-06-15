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


ENTRIES: list[Round] = [
    Round(desc='Encode T', num_qubits=13),
    Round(desc='Stablize', num_qubits=14),
    Round(desc='Check T', num_qubits=15),
    Round(desc='Check T', num_qubits=15),
    Round(desc='Stabilize', num_qubits=454),
    Round(desc='Stabilize', num_qubits=454),
    Round(desc='Stabilize', num_qubits=454),
    Round(desc='Escaped!', num_qubits=454),
    Round(desc='[Wait for gap]', num_qubits=454),
    Round(desc='[Wait for gap]', num_qubits=454),
    Round(desc='[Wait for gap]', num_qubits=454),
    Round(desc='[Wait for gap]', num_qubits=454),
    Round(desc='[Wait for gap]', num_qubits=454),
    Round(desc='[Wait for gap]', num_qubits=454),
    Round(desc='[Wait for gap]', num_qubits=454),
    Round(desc='[Wait for gap]', num_qubits=454),
    Round(desc='[Wait for gap]', num_qubits=454),
    Round(desc='[Wait for gap]', num_qubits=454),
    Round(desc='ready', num_qubits=454),
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

    xs = []
    ys = []
    prev: float = 0
    for (i, round) in enumerate(series):
        xs.append(i)
        ys.append(prev)
        num_qubits = round.num_qubits
        xs.append(i)
        ys.append(num_qubits)
        prev = num_qubits
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
    output_filename = args.out

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.set_xlim(0, len(ENTRIES))
    ax.set_ylabel('#qubits')
    ax.set_ylim(0, max(r.num_qubits for r in ENTRIES) * 1.1)

    plot_series(ax, ENTRIES)

    ax.grid(which='major', color='#BBBBBB')

    # Custom annotations with fixed coordinates:
    # Add arrows
    ax.annotate('', xy=(-0.01, 1.02), xytext=(0.21, 1.02),
                xycoords='axes fraction', arrowprops=dict(arrowstyle='<->', color='darkred'))
    ax.annotate('', xy=(0.21, 1.02), xytext=(1.01, 1.02),
                xycoords='axes fraction', arrowprops=dict(arrowstyle='<->', color='navy'))
    # Add code names
    ax.annotate(
        r'd=3 color',
        xy=(0.1, 1.04),
        xycoords='axes fraction',
        ha='center',
        va='bottom',
        color='darkred',
        fontsize=12
    )
    ax.annotate(
        r'd=15 grafted',
        xy=(0.55, 1.04),
        xycoords='axes fraction',
        ha='center',
        va='bottom',
        color='navy',
        fontsize=12
    )
    # Add a horizontal line representing the qubit count for the rotated surface code.
    ax.plot([0, len(ENTRIES) * 2], [241, 241], label='rotated surface code', color='gray', linestyle='--')

    fig.tight_layout()
    fig.savefig(output_filename)


if __name__ == '__main__':
    main()
