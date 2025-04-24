from __future__ import annotations

import argparse
import concurrent.futures
import math
import numpy as np
import pymatching
import stim

from concurrent.futures import ProcessPoolExecutor
from util import QubitMapping, Circuit, MeasurementIdentifier, DetectorIdentifier, ObservableIdentifier, SuppressNoise
from surface_code import SurfaceStabilizerPattern, SurfaceSyndromeMeasurement
from surface_code import SurfaceXSyndromeMeasurement, SurfaceZSyndromeMeasurement


TICKS_FOR_SYNDROME_MEASUREMENT = 6
FOUR_WEIGHT = SurfaceStabilizerPattern.FOUR_WEIGHT
TWO_WEIGHT_UP = SurfaceStabilizerPattern.TWO_WEIGHT_UP
TWO_WEIGHT_DOWN = SurfaceStabilizerPattern.TWO_WEIGHT_DOWN
TWO_WEIGHT_LEFT = SurfaceStabilizerPattern.TWO_WEIGHT_LEFT
TWO_WEIGHT_RIGHT = SurfaceStabilizerPattern.TWO_WEIGHT_RIGHT


class SurfaceCodePatch:
    def __init__(self, circuit: Circuit, distance1: int, distance2: int, rounds_for_gap: int) -> None:
        # assert distance1 < distance2
        self.circuit = circuit
        self.distance1 = distance1
        self.distance2 = distance2
        self.rounds_for_gap = rounds_for_gap
        self.syndrome_measurements: dict[tuple[int, int], SurfaceSyndromeMeasurement] = {}
        # Note that `self.circuit` does not recognize this qubit, and hence we use raw Stim APIs to access this qubit.
        # This also means that we do not need to worry about idling noise on the qubit.
        self.boundary_ancilla_id: int = 10000
        self.detector_for_complementary_gap: DetectorIdentifier | None = None
        self.offset = (1, 1)

    def _setup_initial_state(self) -> None:
        m: SurfaceSyndromeMeasurement
        circuit = self.circuit
        stim_circuit = circuit.circuit
        distance1 = self.distance1
        (offset_x, offset_y) = self.offset

        with SuppressNoise(circuit):
            for i in range(distance1):
                for j in range(distance1):
                    x = offset_x + j * 2
                    y = offset_y + i * 2

                    circuit.place_reset_z((x, y))

                    # Weight-two syndrome measurements:
                    if i == 0 and j % 2 == 0 and j < distance1 - 1:
                        m = SurfaceXSyndromeMeasurement(circuit, (x + 1, y - 1), TWO_WEIGHT_DOWN, False)
                        self.syndrome_measurements[(x + 1, y - 1)] = m
                    if i == distance1 - 1 and j % 2 == 1 and j < distance1 - 1:
                        m = SurfaceXSyndromeMeasurement(circuit, (x + 1, y + 1), TWO_WEIGHT_UP, False)
                        self.syndrome_measurements[(x + 1, y + 1)] = m
                    if j == 0 and i % 2 == 1 and i < distance1 - 1:
                        m = SurfaceZSyndromeMeasurement(circuit, (x - 1, y + 1), TWO_WEIGHT_RIGHT, False)
                        self.syndrome_measurements[(x - 1, y + 1)] = m
                    if j == distance1 - 1 and i % 2 == 0 and i < distance1 - 1:
                        m = SurfaceZSyndromeMeasurement(circuit, (x + 1, y + 1), TWO_WEIGHT_LEFT, False)
                        self.syndrome_measurements[(x + 1, y + 1)] = m

                    # Weight-four syndrome measurements:
                    if i < distance1 - 1 and j < distance1 - 1:
                        if (i + j) % 2 == 0:
                            m = SurfaceZSyndromeMeasurement(circuit, (x + 1, y + 1), FOUR_WEIGHT, False)
                        else:
                            m = SurfaceXSyndromeMeasurement(circuit, (x + 1, y + 1), FOUR_WEIGHT, False)
                        self.syndrome_measurements[(x + 1, y + 1)] = m

            for _ in range(TICKS_FOR_SYNDROME_MEASUREMENT * 2):
                for m in self.syndrome_measurements.values():
                    m.run()
                circuit.place_tick()

            stim_circuit.append('QUBIT_COORDS', self.boundary_ancilla_id, (2, -1))
            stim_circuit.append('R', self.boundary_ancilla_id)
            stim_circuit.append('TICK')
            for j in range(distance1):
                x = offset_x + j * 2
                y = offset_y
                control_id = circuit.mapping.get_id(x, y)
                stim_circuit.append('CX', [control_id, self.boundary_ancilla_id])
                stim_circuit.append('TICK')

    def _perform_code_expansion(self) -> None:
        distance1 = self.distance1
        distance2 = self.distance2
        circuit = self.circuit
        (offset_x, offset_y) = self.offset
        syndrome_measurements = self.syndrome_measurements

        for i in range(distance2):
            for j in range(distance2):
                m: SurfaceSyndromeMeasurement
                x = offset_x + j * 2
                y = offset_y + i * 2

                # Initialize data qubits:
                if i < distance1 and j < distance1:
                    pass
                elif i >= j:
                    circuit.place_reset_x((x, y))
                else:
                    circuit.place_reset_z((x, y))

                # Weight-two syndrome measurements:
                if i == 0 and j % 2 == 0 and distance1 - 1 <= j and j < distance2 - 1:
                    self._push(SurfaceXSyndromeMeasurement(circuit, (x + 1, y - 1), TWO_WEIGHT_DOWN, False))
                if i == distance2 - 1 and j % 2 == 1:
                    self._push(SurfaceXSyndromeMeasurement(circuit, (x + 1, y + 1), TWO_WEIGHT_UP, True))
                if j == 0 and i % 2 == 1 and distance1 - 1 <= i and i < distance2 - 1:
                    self._push(SurfaceZSyndromeMeasurement(circuit, (x - 1, y + 1), TWO_WEIGHT_RIGHT, False))
                if j == distance2 - 1 and i % 2 == 0 and i < distance2 - 1:
                    self._push(SurfaceZSyndromeMeasurement(circuit, (x + 1, y + 1), TWO_WEIGHT_LEFT, True))

                # Weight-four syndrome measurements:
                if i >= distance2 - 1 or j >= distance2 - 1:
                    continue
                if i < distance1 - 1 and j < distance1 - 1:
                    continue

                last_measurement: MeasurementIdentifier | None = None
                if (i + j) % 2 == 0:
                    satisfied = i < j
                    if (x + 1, y + 1) in syndrome_measurements:
                        assert j == distance1 - 1
                        m = syndrome_measurements[(x + 1), (y + 1)]
                        assert m.pattern == TWO_WEIGHT_LEFT
                        del syndrome_measurements[(x + 1), (y + 1)]
                        last_measurement = m.last_measurement
                    m = SurfaceZSyndromeMeasurement(circuit, (x + 1, y + 1), FOUR_WEIGHT, satisfied)
                    m.last_measurement = last_measurement
                    self._push(m)
                else:
                    satisfied = j + 1 < i
                    if (x + 1, y + 1) in syndrome_measurements:
                        assert i == distance1 - 1
                        m = syndrome_measurements[(x + 1), (y + 1)]
                        assert m.pattern == TWO_WEIGHT_UP
                        del syndrome_measurements[(x + 1), (y + 1)]
                        last_measurement = m.last_measurement
                    m = SurfaceXSyndromeMeasurement(circuit, (x + 1, y + 1), FOUR_WEIGHT, satisfied)
                    self._push(m)

        assert len(syndrome_measurements) == distance2 * distance2 - 1
        for _ in range(TICKS_FOR_SYNDROME_MEASUREMENT * self.rounds_for_gap):
            for m in syndrome_measurements.values():
                m.run()
            circuit.place_tick()

    def _perform_destructive_z_measurement(self) -> None:
        distance2 = self.distance2
        circuit = self.circuit
        (offset_x, offset_y) = self.offset
        syndrome_measurements = self.syndrome_measurements

        with SuppressNoise(circuit):
            stim_circuit = circuit.circuit
            for j in range(distance2):
                x = offset_x + j * 2
                y = offset_y
                control_id = circuit.mapping.get_id(x, y)
                stim_circuit.append('CX', [control_id, self.boundary_ancilla_id])
            stim_circuit.append('M', self.boundary_ancilla_id)
            stim_circuit.append('DETECTOR', stim.target_rec(-1))
            self.detector_for_complementary_gap = DetectorIdentifier(stim_circuit.num_detectors - 1)
            stim_circuit.append('TICK')

            measurements: dict[tuple[int, int], MeasurementIdentifier] = {}
            last_measurements: dict[tuple[int, int], MeasurementIdentifier | None] = {
                pos: m.last_measurement for (pos, m) in self.syndrome_measurements.items()
            }
            for i in range(distance2):
                for j in range(distance2):
                    x = offset_x + j * 2
                    y = offset_y + i * 2
                    measurements[(x, y)] = circuit.place_measurement_z((x, y))

            for i in range(distance2):
                for j in range(distance2):
                    x = offset_x + j * 2
                    y = offset_y + i * 2

                    # Weight-two syndrome measurements:
                    if j == 0 and i % 2 == 1 and i < distance2 - 1:
                        last = last_measurements[(x - 1, y + 1)]
                        assert last is not None
                        circuit.place_detector([measurements[(x, y)], measurements[(x, y + 2)], last])
                    if j == distance2 - 1 and i % 2 == 0 and i < distance2 - 1:
                        last = last_measurements[(x + 1, y + 1)]
                        assert last is not None
                        circuit.place_detector([measurements[(x, y)], measurements[(x, y + 2)], last])

                    # Weight-four syndrome measurements:
                    if i < distance2 - 1 and j < distance2 - 1 and (i + j) % 2 == 0:
                        last = last_measurements[(x + 1, y + 1)]
                        assert last is not None
                        circuit.place_detector([
                            measurements[(x, y)],
                            measurements[(x + 2, y)],
                            measurements[(x, y + 2)],
                            measurements[(x + 2, y + 2)],
                            last
                        ])
            zs = [measurements[(offset_x + j * 2, offset_y)] for j in range(distance2)]
            circuit.place_observable_include(zs, ObservableIdentifier(0))

    def _push(self, m: SurfaceSyndromeMeasurement) -> None:
        position = m.ancilla_position
        assert position not in self.syndrome_measurements
        self.syndrome_measurements[position] = m

    def build(self) -> None:
        self._setup_initial_state()
        self._perform_code_expansion()
        self._perform_destructive_z_measurement()


class SimulationResult:
    def __init__(self, weight: float, complementary_weight: float, expected: bool) -> None:
        self.weight = weight
        self.complementary_weight = complementary_weight
        self.expected = expected

    def gap(self) -> float:
        return abs(self.complementary_weight - self.weight)


class SimulationResults:
    def __init__(self, cutoff_gap: float):
        self.cutoff_gap = cutoff_gap
        self.num_valid_samples_with_large_gap: int = 0
        self.num_wrong_samples_with_large_gap: int = 0
        self.num_discarded_samples: int = 0
        self.samples_with_small_gap: list[SimulationResult] = []

    def append(self, weight: float, complementary_weight: float, expected: bool) -> None:
        r = SimulationResult(weight, complementary_weight, expected)
        if r.gap() > self.cutoff_gap:
            if expected:
                self.num_valid_samples_with_large_gap += 1
            else:
                self.num_wrong_samples_with_large_gap += 1
            return
        self.samples_with_small_gap.append(r)

    def append_discarded(self) -> None:
        self.num_discarded_samples += 1

    def extend(self, other: SimulationResults):
        assert self.cutoff_gap == other.cutoff_gap

        self.num_valid_samples_with_large_gap += other.num_valid_samples_with_large_gap
        self.num_wrong_samples_with_large_gap += other.num_wrong_samples_with_large_gap
        self.num_discarded_samples += other.num_discarded_samples
        self.samples_with_small_gap.extend(other.samples_with_small_gap)

    def __len__(self):
        return self.num_valid_samples_with_large_gap + \
                self.num_wrong_samples_with_large_gap + \
                self.num_discarded_samples + len(self.samples_with_small_gap)


def perform_simulation(
        stim_circuit: stim.Circuit,
        num_shots: int,
        detector_for_complementary_gap: DetectorIdentifier,
        cutoff_gap: float,
        detectors_for_post_selection: list[DetectorIdentifier]) -> SimulationResults:

    dem = stim_circuit.detector_error_model(decompose_errors=True)
    matcher = pymatching.Matching.from_detector_error_model(dem)
    sampler = stim_circuit.compile_detector_sampler()

    detection_events, observable_flips = sampler.sample(num_shots, separate_observables=True)

    results = SimulationResults(cutoff_gap)

    for shot in range(num_shots):
        syndrome = detection_events[shot]
        discard = False
        for id in detectors_for_post_selection:
            if syndrome[id.id] != 0:
                discard = True
                break
        if discard:
            results.append_discarded()
            continue

        prediction, weight = matcher.decode(syndrome, return_weight=True)

        syndrome[detector_for_complementary_gap.id] = not syndrome[detector_for_complementary_gap.id]
        c_prediction, complementary_weight = matcher.decode(syndrome, return_weight=True)
        syndrome[detector_for_complementary_gap.id] = not syndrome[detector_for_complementary_gap.id]

        if weight > complementary_weight:
            prediction = c_prediction

        actual = observable_flips[shot]
        expected = np.array_equal(actual, prediction)
        results.append(weight, complementary_weight, expected)
    return results


def perform_parallel_simulation(
        circuit: Circuit,
        detector_for_complementary_gap: DetectorIdentifier,
        cutoff_gap: float,
        num_shots: int,
        parallelism: int,
        num_shots_per_task: int,
        show_progress: bool) -> SimulationResults:
    if num_shots / parallelism < 1000 or parallelism == 1:
        return perform_simulation(
                circuit.circuit,
                num_shots,
                detector_for_complementary_gap,
                cutoff_gap,
                circuit.detectors_for_post_selection)

    results = SimulationResults(cutoff_gap)
    progress = 0
    with ProcessPoolExecutor(max_workers=parallelism) as executor:
        futures: list[concurrent.futures.Future] = []
        remaining_shots = num_shots

        num_shots_per_task = min(num_shots_per_task, (num_shots + parallelism - 1) // parallelism)
        while remaining_shots > 0:
            num_shots_for_this_task = min(num_shots_per_task, remaining_shots)
            remaining_shots -= num_shots_for_this_task
            future = executor.submit(perform_simulation,
                                     circuit.circuit,
                                     num_shots_for_this_task,
                                     detector_for_complementary_gap,
                                     cutoff_gap,
                                     circuit.detectors_for_post_selection)
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
                        progress += len(future.result())
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
    parser.add_argument('--distance1', type=int, default=3)
    parser.add_argument('--distance2', type=int, default=7)
    parser.add_argument('--rounds-for-gap', type=int, default=7)
    parser.add_argument('--cutoff-gap', type=float, default=100.0)
    parser.add_argument('--show-progress', action='store_true')
    parser.add_argument('--print-circuit', action='store_true')

    args = parser.parse_args()

    print('  num-shots = {}'.format(args.num_shots))
    print('  error-probability = {}'.format(args.error_probability))
    print('  parallelism = {}'.format(args.parallelism))
    print('  max-shots-per-task = {}'.format(args.max_shots_per_task))
    print('  distance1 = {}'.format(args.distance1))
    print('  distance2 = {}'.format(args.distance2))
    print('  rounds-for-gap = {}'.format(args.rounds_for_gap))
    print('  cutoff-gap = {}'.format(args.cutoff_gap))
    print('  show-progress = {}'.format(args.show_progress))
    print('  print-circuit = {}'.format(args.print_circuit))

    num_shots: int = args.num_shots
    error_probability: float = args.error_probability
    parallelism: int = args.parallelism
    max_shots_per_task: int = args.max_shots_per_task
    distance1: int = args.distance1
    distance2: int = args.distance2
    rounds_for_gap: int = args.rounds_for_gap
    cutoff_gap: float = args.cutoff_gap
    show_progress: bool = args.show_progress
    print_circuit: bool = args.print_circuit

    mapping = QubitMapping(30, 30)
    circuit = Circuit(mapping, error_probability)
    patch = SurfaceCodePatch(circuit, distance1, distance2, rounds_for_gap)

    patch.build()

    detector_for_complementary_gap = patch.detector_for_complementary_gap
    assert detector_for_complementary_gap is not None

    if print_circuit:
        print(circuit.circuit)

    if num_shots == 0:
        return

    results = perform_parallel_simulation(
        circuit,
        detector_for_complementary_gap,
        cutoff_gap,
        num_shots,
        parallelism,
        max_shots_per_task,
        show_progress)

    print('#VALID with large gap = {}, #WRONG with large gap = {}'.format(
        results.num_valid_samples_with_large_gap, results.num_wrong_samples_with_large_gap
    ))
    results.samples_with_small_gap.sort(key=lambda r: r.gap())

    discard_rates = [0, 0.001, 0.01, 0.02, 0.05, 0.1, 0.15, 0.2]
    for rate in discard_rates:
        num_discarded = max(
            min(int(rate * len(results)), len(results.samples_with_small_gap)), results.num_discarded_samples)
        max_gap = -math.inf

        num_valid = results.num_valid_samples_with_large_gap
        num_wrong = results.num_wrong_samples_with_large_gap

        num_discarded_by_complementary_gap = num_discarded - results.num_discarded_samples
        if num_discarded_by_complementary_gap:
            max_gap = results.samples_with_small_gap[num_discarded_by_complementary_gap - 1].gap()
        for r in results.samples_with_small_gap[num_discarded_by_complementary_gap:]:
            if r.expected:
                num_valid += 1
            else:
                num_wrong += 1
        print('Discard {:.1f}% samples, VALID = {}, WRONG = {}, DISCARDED = {}'.format(
            rate * 100, num_valid, num_wrong, num_discarded))
        print('max gap = {}'.format(max_gap))
        print('WRONG / (VALID + WRONG) = {:.3e}'.format(num_wrong / (num_valid + num_wrong)))
        print()


if __name__ == '__main__':
    main()
