import argparse
import matplotlib.pyplot as plt
import sinter
import sys

from collections.abc import Iterable
from dataclasses import dataclass

@dataclass
class Entry:
    num_entries: int
    num_discarded_samples: int


ENTRIES: list[Entry] = [
    Entry(num_entries=0, num_discarded_samples=0),
    Entry(num_entries=2500, num_discarded_samples=767344106),
    Entry(num_entries=5000, num_discarded_samples=807902076),
    Entry(num_entries=7500, num_discarded_samples=833411934),
    Entry(num_entries=10000, num_discarded_samples=851685640),
    Entry(num_entries=12500, num_discarded_samples=864895584),
    Entry(num_entries=15000, num_discarded_samples=875625895),
    Entry(num_entries=17500, num_discarded_samples=884179939),
    Entry(num_entries=20000, num_discarded_samples=891438926),
    Entry(num_entries=22500, num_discarded_samples=897480017),
    Entry(num_entries=25000, num_discarded_samples=902538866),
    Entry(num_entries=27500, num_discarded_samples=907115141),
    Entry(num_entries=30000, num_discarded_samples=911307645),
    Entry(num_entries=32500, num_discarded_samples=914921390),
    Entry(num_entries=35000, num_discarded_samples=918063792),
    Entry(num_entries=37500, num_discarded_samples=920879041),
    Entry(num_entries=40000, num_discarded_samples=923429284),
    Entry(num_entries=42500, num_discarded_samples=925807976),
    Entry(num_entries=45000, num_discarded_samples=928017247),
    Entry(num_entries=47500, num_discarded_samples=929989478),
    Entry(num_entries=50000, num_discarded_samples=931825649),
    Entry(num_entries=52500, num_discarded_samples=933582595),
    Entry(num_entries=55000, num_discarded_samples=935260820),
    Entry(num_entries=57500, num_discarded_samples=936842465),
    Entry(num_entries=60000, num_discarded_samples=938324966),
    Entry(num_entries=62500, num_discarded_samples=939688558),
    Entry(num_entries=65000, num_discarded_samples=940910724),
    Entry(num_entries=67500, num_discarded_samples=942034575),
    Entry(num_entries=70000, num_discarded_samples=943072426),
    Entry(num_entries=72500, num_discarded_samples=944039501),
    Entry(num_entries=75000, num_discarded_samples=944946436),
    Entry(num_entries=77500, num_discarded_samples=945796863),
    Entry(num_entries=80000, num_discarded_samples=946600280),
    Entry(num_entries=82500, num_discarded_samples=947363866),
    Entry(num_entries=85000, num_discarded_samples=948084630),
    Entry(num_entries=87500, num_discarded_samples=948759860),
    Entry(num_entries=90000, num_discarded_samples=949397520),
    Entry(num_entries=92500, num_discarded_samples=950007970),
    Entry(num_entries=95000, num_discarded_samples=950596128),
    Entry(num_entries=97500, num_discarded_samples=951163029),
    Entry(num_entries=100000, num_discarded_samples=951708499),
    Entry(num_entries=102500, num_discarded_samples=952229841),
    Entry(num_entries=105000, num_discarded_samples=952724612),
    Entry(num_entries=107500, num_discarded_samples=953192544),
    Entry(num_entries=110000, num_discarded_samples=953638053),
    Entry(num_entries=112500, num_discarded_samples=954065806),
    Entry(num_entries=115000, num_discarded_samples=954479193),
    Entry(num_entries=117500, num_discarded_samples=954879859),
    Entry(num_entries=120000, num_discarded_samples=955268925),
    Entry(num_entries=122500, num_discarded_samples=955646836),
    Entry(num_entries=125000, num_discarded_samples=956013981),
    Entry(num_entries=127500, num_discarded_samples=956370859),
    Entry(num_entries=130000, num_discarded_samples=956717518),
    Entry(num_entries=132500, num_discarded_samples=957053945),
    Entry(num_entries=135000, num_discarded_samples=957379713),
    Entry(num_entries=137500, num_discarded_samples=957695555),
    Entry(num_entries=140000, num_discarded_samples=958002074),
    Entry(num_entries=142500, num_discarded_samples=958300155),
    Entry(num_entries=145000, num_discarded_samples=958589977),
    Entry(num_entries=147500, num_discarded_samples=958872349),
    Entry(num_entries=150000, num_discarded_samples=959147583),
    Entry(num_entries=152500, num_discarded_samples=959416264),
    Entry(num_entries=155000, num_discarded_samples=959678560),
    Entry(num_entries=157500, num_discarded_samples=959934670),
    Entry(num_entries=159410, num_discarded_samples=960126518),
]


def plot_series(
    ax: plt.Axes,
    seriese: Iterable[Entry],
    *,
    label: str | None = None,
    color: str | None = None,
    marker: str | None = None,
    linewidth: int | None = None) -> None:
    xs: list[float] = []
    ys: list[float] = []
    for entry in seriese:
        num_entries = entry.num_entries
        coverage = entry.num_discarded_samples / 1e10
        xs.append(coverage)
        ys.append(num_entries)

    ax.plot(xs, ys, label=label, color=color, marker=marker, linewidth=linewidth)


def main() -> None:
    parser = argparse.ArgumentParser(description='description')
    parser.add_argument('--out', type=str, default=None)

    args = parser.parse_args()
    if args.out is None:
        print('The output filename should be specified via --out.', file=sys.stderr)
        sys.exit(1)
    output_filename: str = args.out

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.set_xlabel('Coverage', fontsize=16)
    ax.set_xlim(0, 0.1)

    ax.set_ylabel('#entries', fontsize=16)
    ax.set_ylim(0, 160_000)

    plot_series(ax, ENTRIES, label='', color='C0', linewidth=2)

    ax.grid(which='major', color='#000000')
    ax.grid(which='minor', color='#DDDDDD')
    ax.legend()
    fig.savefig(output_filename)
    plt.show()


if __name__ == '__main__':
    main()
