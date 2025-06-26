from __future__ import annotations

import concurrent
import copy
import argparse
import math
import numpy as np
import pymatching
import stim

import steane_code

from concurrent.futures import ProcessPoolExecutor
from enum import auto
from util import QubitMapping, Circuit, MultiplexingCircuit
from util import MeasurementIdentifier, DetectorIdentifier, ObservableIdentifier, SuppressNoise
from steane_code import SteaneZ0145SyndromeMeasurement, SteaneZ0235SyndromeMeasurement, SteaneZ0246SyndromeMeasurement
from steane_code import STEANE_0, STEANE_1, STEANE_2, STEANE_3, STEANE_4, STEANE_5, STEANE_6
from surface_code import SurfaceStabilizerPattern, SurfaceSyndromeMeasurement
from surface_code import SurfaceXSyndromeMeasurement, SurfaceZSyndromeMeasurement


class CircuitsWithAdditionalProperties:
    def __init__(
            self,
            circuit: Circuit) -> None:
        self.circuit = circuit


class SimulationResults:
    def __init__(self) -> None:
        self.num_valid_samples: int = 0
        self.num_wrong_samples: int = 0
        self.num_discarded_samples: int = 0

    def append(self, expected: bool) -> None:
        if expected:
            self.num_valid_samples += 1
        else:
            self.num_wrong_samples += 1

    def append_discarded(self) -> None:
        self.num_discarded_samples += 1

    def extend(self, other: SimulationResults):
        self.num_valid_samples += other.num_valid_samples
        self.num_wrong_samples += other.num_wrong_samples
        self.num_discarded_samples += other.num_discarded_samples

    def __len__(self):
        return self.num_valid_samples + \
                self.num_wrong_samples + \
                self.num_discarded_samples


def perform_simulation(
        circuits: CircuitsWithAdditionalProperties,
        num_shots: int,
        seed: int | None):
    stim_circuit = circuits.circuit.circuit

    sampler = stim_circuit.compile_detector_sampler(seed=seed)
    detection_events, observable_flips = sampler.sample(num_shots, separate_observables=True)

    results = SimulationResults()
    postselection_ids = np.array([id.id for id in circuits.circuit.detectors_for_post_selection], dtype='uint')

    for shot in range(num_shots):
        syndrome = detection_events[shot]
        if np.any(syndrome[postselection_ids] != 0):
            results.append_discarded()
            continue

        expected = bool(np.all(observable_flips[shot] == 0))
        results.append(expected)

    return results


def perform_parallel_simulation(
        circuits: CircuitsWithAdditionalProperties,
        num_shots: int,
        parallelism: int,
        num_shots_per_task: int,
        show_progress: bool) -> SimulationResults:
    if num_shots / parallelism < 1000 or parallelism == 1:
        return perform_simulation(
                circuits,
                num_shots,
                None)

    progress = 0
    results = SimulationResults()
    with ProcessPoolExecutor(max_workers=parallelism) as executor:
        futures: list[concurrent.futures.Future] = []
        remaining_shots = num_shots

        num_shots_per_task = min(num_shots_per_task, (num_shots + parallelism - 1) // parallelism)
        while remaining_shots > 0:
            seed = None
            num_shots_for_this_task = min(num_shots_per_task, remaining_shots)
            remaining_shots -= num_shots_for_this_task
            future = executor.submit(perform_simulation,
                                     circuits,
                                     num_shots_for_this_task,
                                     seed)
            futures.append(future)
        try:
            while len(futures) > 0:
                import sys
                if show_progress:
                    print('Progress: {}% ({}/{})\r'.format(
                        round((progress / num_shots) * 100), progress, num_shots), end='')
                concurrent.futures.wait(futures, timeout=None, return_when=concurrent.futures.FIRST_COMPLETED)
                new_futures = []
                for future in futures:
                    if future.done():
                        results.extend(future.result())
                        progress = len(results)
                    else:
                        new_futures.append(future)
                futures = new_futures
            if show_progress:
                print()
        finally:
            for future in futures:
                future.cancel()
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description='description')
    parser.add_argument('--num-shots', type=int, default=1000)
    parser.add_argument('--error-probability', type=float, default=0)
    parser.add_argument('--parallelism', type=int, default=1)
    parser.add_argument('--max-shots-per-task', type=int, default=2 ** 20)
    parser.add_argument('--intermediate-surface-distance', type=int, default=3)
    parser.add_argument('--final-surface-distance', type=int, default=None)
    parser.add_argument('--full-post-selection', action='store_true')
    parser.add_argument('--print-circuit', action='store_true')
    parser.add_argument('--show-progress', action='store_true')

    args = parser.parse_args()

    print('  num-shots = {}'.format(args.num_shots))
    print('  error-probability = {}'.format(args.error_probability))
    print('  parallelism = {}'.format(args.parallelism))
    print('  max-shots-per-task = {}'.format(args.max_shots_per_task))
    print('  intermediate-surface-distance = {}'.format(args.intermediate_surface_distance))
    print('  final-surface-distance = {}'.format(args.final_surface_distance))
    print('  full-post-selection = {}'.format(args.full_post_selection))
    print('  print-circuit = {}'.format(args.print_circuit))
    print('  show-progress = {}'.format(args.show_progress))

    num_shots: int = args.num_shots
    error_probability: float = args.error_probability
    parallelism: int = args.parallelism
    max_shots_per_task: int = args.max_shots_per_task
    intermediate_surface_distance: int = args.intermediate_surface_distance
    final_distance: int = \
        args.final_surface_distance if args.final_surface_distance is not None else intermediate_surface_distance
    full_post_selection: bool = args.full_post_selection
    print_circuit: bool = args.print_circuit
    show_progress: bool = args.show_progress

    assert final_distance >= intermediate_surface_distance

    mapping = QubitMapping(30, 30)
    circuit = Circuit(mapping, error_probability)

    steane_code.perform_injection(circuit)
    circuit.place_tick()
    circuit.circuit.append('SWAP', [
        mapping.get_id(*steane_code.STEANE_1_INJECTION), mapping.get_id(*steane_code.STEANE_1_CHECK)
    ])

    steane_code.perform_check(circuit)
    with SuppressNoise(circuit):
        circuit.place_tick()
        steane_code.perform_tomography_after_check_stage(circuit)

    if print_circuit:
        print(circuit.circuit)

    if num_shots == 0:
        return

    results = perform_parallel_simulation(
        CircuitsWithAdditionalProperties(circuit),
        num_shots,
        parallelism,
        max_shots_per_task,
        show_progress)

    num_valid = results.num_valid_samples
    num_wrong = results.num_wrong_samples
    num_discarded = results.num_discarded_samples

    print('VALID = {}, WRONG = {}, DISCARDED = {}'.format(num_valid, num_wrong, num_discarded))
    print('(VALID + WRONG) / TOTAL = {:.3f}'.format(
        (num_valid + num_wrong) / (num_valid + num_wrong + num_discarded)))
    print('WRONG / (VALID + WRONG) = {:.3e}'.format(num_wrong / (num_valid + num_wrong)))
    print()


if __name__ == '__main__':
    main()
