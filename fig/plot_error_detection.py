import argparse
import matplotlib.pyplot as plt
import sinter
import sys

from dataclasses import dataclass


@dataclass
class Task:
    p: float
    num_valid_cases: int
    num_wrong_cases: int
    num_discarded_cases: int
    initial: str


def translate_to_sinter_tasks(tasks: list[Task]) -> list[sinter.TaskStats]:
    sinter_tasks: list[sinter.TaskStats] = []
    for i, task in enumerate(tasks):
        sinter_tasks.append(sinter.TaskStats(
            shots=task.num_valid_cases + task.num_wrong_cases + task.num_discarded_cases,
            discards=task.num_discarded_cases,
            errors=task.num_wrong_cases,
            strong_id=f'task_{i}',
            decoder='',
            json_metadata={'p': task.p, 'initial': task.initial},
        ))
    return sinter_tasks


# See https://docs.google.com/spreadsheets/d/1NV1PXI3OCJHO0QLHeb4nQcJ7v9jxXbYIJyWrJgQPSQg/edit?gid=573444527.
TASKS: list[Task] = [
    Task(p=0.0020, initial='+', num_valid_cases=96722196, num_wrong_cases=509, num_discarded_cases=859646376),
    Task(p=0.0017, initial='+', num_valid_cases=155851217, num_wrong_cases=510, num_discarded_cases=937011719),
    Task(p=0.0014, initial='+', num_valid_cases=263549536, num_wrong_cases=505, num_discarded_cases=1047309558),
    Task(p=0.0012, initial='+', num_valid_cases=419539630, num_wrong_cases=505, num_discarded_cases=1239946393),
    Task(p=0.0010, initial='+', num_valid_cases=809219250, num_wrong_cases=502, num_discarded_cases=1736300599),
    Task(p=0.0008, initial='+', num_valid_cases=1440893234, num_wrong_cases=509, num_discarded_cases=3604366998),
    Task(p=0.0006, initial='+', num_valid_cases=3330619080, num_wrong_cases=505, num_discarded_cases=3294338114),
    Task(p=0.0005, initial='+', num_valid_cases=5885297276, num_wrong_cases=504, num_discarded_cases=4553544149),

    Task(p=0.0020, initial='0', num_valid_cases=451671623, num_wrong_cases=507, num_discarded_cases=3987786450),
    Task(p=0.0017, initial='0', num_valid_cases=828257983, num_wrong_cases=506, num_discarded_cases=4951067831),
    Task(p=0.0014, initial='0', num_valid_cases=1451634144, num_wrong_cases=502, num_discarded_cases=5738772485),
    Task(p=0.0012, initial='0', num_valid_cases=2298262210, num_wrong_cases=503, num_discarded_cases=6760344250),
    Task(p=0.0010, initial='0', num_valid_cases=3983127409, num_wrong_cases=502, num_discarded_cases=8508944398),
    Task(p=0.0008, initial='0', num_valid_cases=7990797620, num_wrong_cases=502, num_discarded_cases=19941125736),
    Task(p=0.0006, initial='0', num_valid_cases=17745122390, num_wrong_cases=503, num_discarded_cases=17489165475),
    Task(p=0.0005, initial='0', num_valid_cases=33332089798, num_wrong_cases=502, num_discarded_cases=25703016900),
]


def main() -> None:
    parser = argparse.ArgumentParser(description='description')
    parser.add_argument('--out', type=str, default=None)

    args = parser.parse_args()
    if args.out is None:
        print('The output filename should be specified via --out.', file=sys.stderr)
        sys.exit(1)
    output_filename: str = args.out

    stats = translate_to_sinter_tasks(TASKS)

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.set_xscale('log')
    ax.set_xlabel('Physical error probability')
    ax.set_xlim(0.0005 / 1.05, 0.0020 * 1.05)

    ax.set_yscale('log')
    ax.set_ylabel('Logical error probability')
    ax.set_ylim(1e-8, 1e-5)

    def group_func(m: sinter.AnonTaskStats) -> dict[str, str]:
        match m.json_metadata['initial']:
            case '+': label = 'Initial value = + (detecting Z errors)'
            case '0': label = 'Initial value = 0 (detecting X errors)'
            case _: raise ValueError(m.json_metadata['initial'])
        return {
            'label': label,
        }

    sinter.plot_error_rate(
        ax=ax,
        stats=stats,
        x_func=lambda m: m.json_metadata['p'],
        group_func=group_func,
    )

    ax.grid(which='major', color='#000000')
    ax.grid(which='minor', color='#DDDDDD')
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_filename)


if __name__ == '__main__':
    main()
