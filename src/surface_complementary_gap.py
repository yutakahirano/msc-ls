from __future__ import annotations

import concurrent
import argparse
import enum
import math
import numpy as np
import pymatching
import stim

from concurrent.futures import ProcessPoolExecutor
from enum import auto
from util import QubitMapping, Circuit
from util import MeasurementIdentifier, DetectorIdentifier, ObservableIdentifier, SuppressNoise
from surface_code import SurfaceStabilizerPattern, SurfaceSyndromeMeasurement
from surface_code import SurfaceXSyndromeMeasurement, SurfaceZSyndromeMeasurement


class InitialValue(enum.Enum):
    Plus = auto(),
    Zero = auto(),


# Representing merged two rotated surface code patches.
class SurfacePatch:
    def __init__(self, mapping: QubitMapping, distance: int, initial_value: InitialValue,
                 error_probability: float, full_post_selection: bool) -> None:
        self.mapping = mapping
        self.distance = distance
        self.initial_value = initial_value
        self.error_probability = error_probability
        self.full_post_selection = full_post_selection
        self.circuit = Circuit(mapping, error_probability)
        self.syndrome_measurements: dict[tuple[int, int], SurfaceSyndromeMeasurement] = {}
        self.x_measurements: dict[tuple[int, int], MeasurementIdentifier] = {}
        self.z_measurements: dict[tuple[int, int], MeasurementIdentifier] = {}
        self.offset = (1, 7)
        self.x_detector_for_complementary_gap: DetectorIdentifier | None = None
        self.z_detector_for_complementary_gap: DetectorIdentifier | None = None
        # Note that `self.circuit` does not recognize this qubit, and hence we use raw Stim APIs to access these qubits.
        # This also means that we do not need to worry about idling noise on these qubits.
        self.x_boundary_ancilla_id: int = 10000
        self.z_boundary_ancilla_id: int = 20000
        self.circuit.circuit.append('QUBIT_COORDS', self.x_boundary_ancilla_id, (-5, 0))
        self.circuit.circuit.append('QUBIT_COORDS', self.z_boundary_ancilla_id, (0, -5))

        self._setup_syndrome_measurements()

    def _setup_syndrome_measurements(self) -> None:
        distance = self.distance
        (offset_x, offset_y) = self.offset

        FOUR_WEIGHT = SurfaceStabilizerPattern.FOUR_WEIGHT
        TWO_WEIGHT_UP = SurfaceStabilizerPattern.TWO_WEIGHT_UP
        TWO_WEIGHT_DOWN = SurfaceStabilizerPattern.TWO_WEIGHT_DOWN
        TWO_WEIGHT_LEFT = SurfaceStabilizerPattern.TWO_WEIGHT_LEFT
        TWO_WEIGHT_RIGHT = SurfaceStabilizerPattern.TWO_WEIGHT_RIGHT

        m: SurfaceSyndromeMeasurement

        match self.initial_value:
            case InitialValue.Plus:
                already_satisfied_x = True
                already_satisfied_z = False
            case InitialValue.Zero:
                already_satisfied_x = False
                already_satisfied_z = True

        for i in range(distance):
            for j in range(distance):
                x = offset_x + j * 2
                y = offset_y + i * 2

                # Weight-two syndrome measurements:
                if i == 0 and j % 2 == 0 and j < distance - 1:
                    m = SurfaceXSyndromeMeasurement(self.circuit, (x + 1, y - 1), TWO_WEIGHT_DOWN, already_satisfied_x)
                    self.syndrome_measurements[(x + 1, y - 1)] = m
                if i == distance - 1 and j % 2 == 1:
                    m = SurfaceXSyndromeMeasurement(self.circuit, (x + 1, y + 1), TWO_WEIGHT_UP, already_satisfied_x)
                    self.syndrome_measurements[(x + 1, y + 1)] = m
                if j == 0 and i % 2 == 1:
                    m = SurfaceZSyndromeMeasurement(self.circuit, (x - 1, y + 1), TWO_WEIGHT_RIGHT, already_satisfied_z)
                    self.syndrome_measurements[(x - 1, y + 1)] = m
                if j == distance - 1 and i % 2 == 0 and i < distance - 1:
                    m = SurfaceZSyndromeMeasurement(self.circuit, (x + 1, y + 1), TWO_WEIGHT_LEFT, already_satisfied_z)
                    self.syndrome_measurements[(x + 1, y + 1)] = m

                # Weight-four syndrome measurements:
                if i < distance - 1 and j < distance - 1:
                    if (i + j) % 2 == 0:
                        m = SurfaceZSyndromeMeasurement(self.circuit, (x + 1, y + 1), FOUR_WEIGHT, already_satisfied_z)
                    else:
                        m = SurfaceXSyndromeMeasurement(self.circuit, (x + 1, y + 1), FOUR_WEIGHT, already_satisfied_x)
                    self.syndrome_measurements[(x + 1, y + 1)] = m

        if self.full_post_selection:
            for m in self.syndrome_measurements.values():
                m.set_post_selection(True)

    def run(self) -> None:
        depth_for_surface_code_syndrome_measurement = 6
        distance = self.distance
        circuit = self.circuit
        mapping = self.mapping
        stim_circuit = circuit.circuit

        (offset_x, offset_y) = self.offset

        # Initialize the patch in a noise-free fashion.
        with SuppressNoise(circuit):
            for i in range(distance):
                for j in range(distance):
                    x = offset_x + j * 2
                    y = offset_y + i * 2
                    match self.initial_value:
                        case InitialValue.Plus:
                            circuit.place_reset_x((x, y))
                        case InitialValue.Zero:
                            circuit.place_reset_z((x, y))
            for _ in range(depth_for_surface_code_syndrome_measurement):
                for m in self.syndrome_measurements.values():
                    m.run()
                circuit.place_tick()

        stim_circuit.append('RX', self.x_boundary_ancilla_id)
        stim_circuit.append('CX', [self.x_boundary_ancilla_id, mapping.get_id(offset_x, offset_y)])
        stim_circuit.append('CX', [self.x_boundary_ancilla_id, mapping.get_id(offset_x, offset_y + 2)])
        stim_circuit.append('CX', [self.x_boundary_ancilla_id, mapping.get_id(offset_x, offset_y + 4)])
        stim_circuit.append('R', self.z_boundary_ancilla_id)
        stim_circuit.append('CX', [mapping.get_id(offset_x, offset_y), self.z_boundary_ancilla_id])
        stim_circuit.append('CX', [mapping.get_id(offset_x + 2, offset_y), self.z_boundary_ancilla_id])
        stim_circuit.append('CX', [mapping.get_id(offset_x + 4, offset_y), self.z_boundary_ancilla_id])

        for _ in range(depth_for_surface_code_syndrome_measurement * distance * 2):
            for m in self.syndrome_measurements.values():
                m.run()
            circuit.place_tick()

        for j in range(distance):
            x = offset_x + j * 2
            y = offset_y + 0
            control_id = mapping.get_id(x, y)
            stim_circuit.append('CX', [control_id, self.z_boundary_ancilla_id])
        stim_circuit.append('M', self.z_boundary_ancilla_id)
        stim_circuit.append('DETECTOR', [stim.target_rec(-1)])

        for i in range(distance):
            x = offset_x
            y = offset_y + i * 2
            target_id = mapping.get_id(x, y)
            stim_circuit.append('CX', [self.x_boundary_ancilla_id, target_id])
        stim_circuit.append('MX', self.x_boundary_ancilla_id)
        stim_circuit.append('DETECTOR', [stim.target_rec(-1)])
        self.x_detector_for_complementary_gap = DetectorIdentifier(stim_circuit.num_detectors - 2)
        self.z_detector_for_complementary_gap = DetectorIdentifier(stim_circuit.num_detectors - 1)

        match self.initial_value:
            case InitialValue.Plus:
                self._perform_perfect_destructive_x_measurement()
                measurements = self.x_measurements
                assert len(measurements) == distance * distance
                xs = [measurements[(offset_x, offset_y + i * 2)] for i in range(distance)]
                circuit.place_observable_include(xs, ObservableIdentifier(0))
            case InitialValue.Zero:
                self._perform_perfect_destructive_z_measurement()
                measurements = self.z_measurements
                assert len(measurements) == distance * distance
                zs = [measurements[(offset_x + j * 2, offset_y)] for j in range(distance)]
                circuit.place_observable_include(zs, ObservableIdentifier(0))

    def _perform_perfect_destructive_x_measurement(self) -> None:
        distance = self.distance
        circuit = self.circuit
        (offset_x, offset_y) = self.offset
        post_selection = self.full_post_selection

        last_measurements: dict[tuple[int, int], MeasurementIdentifier | None] = {
            pos: m.last_measurement for (pos, m) in self.syndrome_measurements.items()
        }
        measurements: dict[tuple[int, int], MeasurementIdentifier] = self.x_measurements
        assert len(measurements) == 0

        with SuppressNoise(circuit):
            for i in range(distance):
                for j in range(distance):
                    x = offset_x + j * 2
                    y = offset_y + i * 2
                    id = circuit.place_measurement_x((x, y))
                    measurements[(x, y)] = id

            for i in range(distance):
                for j in range(distance):
                    x = offset_x + j * 2
                    y = offset_y + i * 2

                    # Weight-two syndrome measurements:
                    if i == 0 and j % 2 == 0 and j < distance - 1:
                        last = last_measurements[(x + 1, y - 1)]
                        assert last is not None
                        circuit.place_detector([measurements[(x, y)], measurements[(x + 2, y)], last], post_selection)
                    if i == distance - 1 and j % 2 == 1:
                        last = last_measurements[(x + 1, y + 1)]
                        assert last is not None
                        circuit.place_detector([measurements[(x, y)], measurements[(x + 2, y)], last], post_selection)

                    # Weight-four syndrome measurements:
                    if i < distance - 1 and j < distance - 1 and (i + j) % 2 == 1:
                        last = last_measurements[(x + 1, y + 1)]
                        assert last is not None
                        circuit.place_detector([
                            measurements[(x, y)],
                            measurements[(x + 2, y)],
                            measurements[(x, y + 2)],
                            measurements[(x + 2, y + 2)],
                            last
                        ], post_selection=post_selection)

    def _perform_perfect_destructive_z_measurement(self) -> None:
        distance = self.distance
        circuit = self.circuit
        (offset_x, offset_y) = self.offset
        post_selection = self.full_post_selection

        last_measurements: dict[tuple[int, int], MeasurementIdentifier | None] = {
            pos: m.last_measurement for (pos, m) in self.syndrome_measurements.items()
        }
        measurements: dict[tuple[int, int], MeasurementIdentifier] = self.z_measurements
        assert len(measurements) == 0

        with SuppressNoise(circuit):
            for i in range(distance):
                for j in range(distance):
                    x = offset_x + j * 2
                    y = offset_y + i * 2
                    id = circuit.place_measurement_z((x, y))
                    measurements[(x, y)] = id

            for i in range(distance):
                for j in range(distance):
                    x = offset_x + j * 2
                    y = offset_y + i * 2

                    # Weight-two syndrome measurements:
                    if j == 0 and i % 2 == 1:
                        last = last_measurements[(x - 1, y + 1)]
                        assert last is not None
                        circuit.place_detector([measurements[(x, y)], measurements[(x, y + 2)], last], post_selection)
                    if j == distance - 1 and i % 2 == 0 and i < distance - 1:
                        last = last_measurements[(x + 1, y + 1)]
                        assert last is not None
                        circuit.place_detector([measurements[(x, y)], measurements[(x, y + 2)], last], post_selection)

                    # Weight-four syndrome measurements:
                    if i < distance - 1 and j < distance - 1 and (i + j) % 2 == 0:
                        last = last_measurements[(x + 1, y + 1)]
                        assert last is not None
                        circuit.place_detector([
                            measurements[(x, y)],
                            measurements[(x + 2, y)],
                            measurements[(x, y + 2)],
                            measurements[(x + 2, y + 2)],
                            last
                        ], post_selection)


class UncategorizedSample:
    def __init__(self, gap: float, expected: bool) -> None:
        self.gap = gap
        self.expected = expected


class SimulationResults:
    def __init__(self, lower_threshold: float, upper_threshold: float) -> None:
        self.lower_threshold = lower_threshold
        self.upper_threshold = upper_threshold
        self.num_valid_samples: int = 0
        self.num_wrong_samples: int = 0
        self.num_discarded_samples: int = 0
        self.uncategorized_samples: list[UncategorizedSample] = []

    def append(self, gap: float, expected: bool) -> None:
        if gap < self.lower_threshold:
            self.num_discarded_samples += 1
        elif gap >= self.upper_threshold:
            if expected:
                self.num_valid_samples += 1
            else:
                self.num_wrong_samples += 1
        else:
            self.uncategorized_samples.append(UncategorizedSample(gap, expected))

    def append_discarded(self) -> None:
        self.num_discarded_samples += 1

    def extend(self, other: SimulationResults):
        assert self.lower_threshold == other.lower_threshold
        assert self.upper_threshold == other.upper_threshold

        self.num_valid_samples += other.num_valid_samples
        self.num_wrong_samples += other.num_wrong_samples
        self.num_discarded_samples += other.num_discarded_samples
        self.uncategorized_samples.extend(other.uncategorized_samples)

    def __len__(self):
        return self.num_valid_samples + \
                self.num_wrong_samples + \
                self.num_discarded_samples + len(self.uncategorized_samples)


def perform_simulation(
        stim_circuit: stim.Circuit,
        num_shots: int,
        x_detector_for_complementary_gap: DetectorIdentifier,
        z_detector_for_complementary_gap: DetectorIdentifier,
        gap_filters: list[tuple[float, float]],
        detectors_for_post_selection: list[DetectorIdentifier]) -> list[SimulationResults]:

    dem = stim_circuit.detector_error_model(decompose_errors=True)
    matcher = pymatching.Matching.from_detector_error_model(dem)

    sampler = stim_circuit.compile_detector_sampler()
    detection_events, observable_flips = sampler.sample(num_shots, separate_observables=True)

    results = [SimulationResults(lower, upper) for (lower, upper) in gap_filters]
    postselection_ids = np.array([id.id for id in detectors_for_post_selection], dtype='uint')

    mask = np.ones_like(detection_events[0], dtype=bool)
    mask[x_detector_for_complementary_gap.id] = False
    mask[z_detector_for_complementary_gap.id] = False

    for shot in range(num_shots):
        syndrome = detection_events[shot]
        if np.any(syndrome[postselection_ids] != 0):
            for rs in results:
                rs.append_discarded()
            continue

        prediction, weight = matcher.decode(syndrome, return_weight=True)
        min_weight = weight
        max_weight = weight

        syndrome[z_detector_for_complementary_gap.id] = not syndrome[z_detector_for_complementary_gap.id]
        c_prediction, c_weight = matcher.decode(syndrome, return_weight=True)
        if c_weight < min_weight:
            prediction = c_prediction
        min_weight = min(min_weight, c_weight)
        max_weight = max(max_weight, c_weight)

        syndrome[x_detector_for_complementary_gap.id] = not syndrome[x_detector_for_complementary_gap.id]
        c_prediction, c_weight = matcher.decode(syndrome, return_weight=True)
        if c_weight < min_weight:
            prediction = c_prediction
        min_weight = min(min_weight, c_weight)
        max_weight = max(max_weight, c_weight)

        syndrome[z_detector_for_complementary_gap.id] = not syndrome[z_detector_for_complementary_gap.id]

        c_prediction, c_weight = matcher.decode(syndrome, return_weight=True)
        if c_weight < min_weight:
            prediction = c_prediction
        min_weight = min(min_weight, c_weight)
        max_weight = max(max_weight, c_weight)

        syndrome[x_detector_for_complementary_gap.id] = not syndrome[x_detector_for_complementary_gap.id]

        actual = observable_flips[shot]
        expected = np.array_equal(actual, prediction)
        gap = max_weight - min_weight

        # Because we *know* that the trivial syndrome is least likely to have logical errors,
        # we increase the gap manually.
        if all(syndrome[mask] == 0):
            gap += 10.0

        for rs in results:
            rs.append(gap, expected)
    return results


def perform_parallel_simulation(
        circuit: Circuit,
        x_detector_for_complementary_gap: DetectorIdentifier,
        z_detector_for_complementary_gap: DetectorIdentifier,
        gap_filters: list[tuple[float, float]],
        num_shots: int,
        parallelism: int,
        num_shots_per_task: int,
        show_progress: bool) -> list[SimulationResults]:
    if num_shots / parallelism < 1000 or parallelism == 1:
        return perform_simulation(
                circuit.circuit,
                num_shots,
                x_detector_for_complementary_gap,
                z_detector_for_complementary_gap,
                gap_filters,
                circuit.detectors_for_post_selection)

    results = [SimulationResults(lower, upper) for (lower, upper) in gap_filters]
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
                                     x_detector_for_complementary_gap,
                                     z_detector_for_complementary_gap,
                                     gap_filters,
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
                        assert len(results) == len(future.result())
                        assert len(results) > 0
                        for i in range(len(results)):
                            results[i].extend(future.result()[i])
                        progress += len(future.result()[0])
                    else:
                        new_futures.append(future)
                futures = new_futures
            if show_progress:
                print()
        finally:
            for future in futures:
                future.cancel()
    return results


def find_gap_threshold(results: SimulationResults, rate: float) -> float:
    assert results.lower_threshold == 0
    assert results.upper_threshold == math.inf
    num_discarded = results.num_discarded_samples
    total = len(results)
    if rate * total <= num_discarded:
        return 0.0

    index = min(len(results.uncategorized_samples) - 1, int(round(rate * total)) - num_discarded)
    gap = results.uncategorized_samples[index].gap
    return gap


def construct_gap_filters(
        discard_rates: list[float],
        results: SimulationResults,
        uncategorized_samples_rate: float) -> list[tuple[float, float]]:
    assert results.lower_threshold == 0
    assert results.upper_threshold == math.inf
    gap_filters: list[tuple[float, float]] = []
    num_samples = len(results)

    for rate in discard_rates:
        lower_rate = rate - uncategorized_samples_rate / 2
        upper_rate = rate + uncategorized_samples_rate / 2

        # Complementary gap distribution can have spikes, and these multiplications are protections for them.
        lower_threshold = find_gap_threshold(results, lower_rate) * 0.999
        upper_threshold = find_gap_threshold(results, upper_rate) * 1.001
        gap_filters.append((lower_threshold, upper_threshold))
    return gap_filters


def main() -> None:
    parser = argparse.ArgumentParser(description='description')
    parser.add_argument('--num-shots', type=int, default=1000)
    parser.add_argument('--error-probability', type=float, default=0)
    parser.add_argument('--parallelism', type=int, default=1)
    parser.add_argument('--max-shots-per-task', type=int, default=2 ** 20)
    parser.add_argument('--surface-distance', type=int, default=3)
    parser.add_argument('--initial-value', choices=['+', '0'], default='+')
    parser.add_argument('--full-post-selection', action='store_true')
    parser.add_argument('--print-circuit', action='store_true')
    parser.add_argument('--show-progress', action='store_true')

    args = parser.parse_args()

    print('  num-shots = {}'.format(args.num_shots))
    print('  error-probability = {}'.format(args.error_probability))
    print('  parallelism = {}'.format(args.parallelism))
    print('  max-shots-per-task = {}'.format(args.max_shots_per_task))
    print('  surface-distance = {}'.format(args.surface_distance))
    print('  initial-value = {}'.format(args.initial_value))
    print('  full-post-selection = {}'.format(args.full_post_selection))
    print('  print-circuit = {}'.format(args.print_circuit))
    print('  show-progress = {}'.format(args.show_progress))

    num_shots: int = args.num_shots
    error_probability: float = args.error_probability
    parallelism: int = args.parallelism
    max_shots_per_task: int = args.max_shots_per_task
    surface_distance: int = args.surface_distance
    match args.initial_value:
        case '+':
            initial_value = InitialValue.Plus
        case '0':
            initial_value = InitialValue.Zero
        case _:
            assert False
    full_post_selection: bool = args.full_post_selection
    print_circuit: bool = args.print_circuit
    show_progress: bool = args.show_progress

    mapping = QubitMapping(30, 30)
    r = SurfacePatch(mapping, surface_distance, initial_value, error_probability, full_post_selection)
    stim_circuit = r.circuit.circuit
    r.run()
    if print_circuit:
        print(stim_circuit)

    # Check whether all the detectors and observables are deterministic.
    stim_circuit.detector_error_model(decompose_errors=True)

    if num_shots == 0:
        return

    x_detector_for_complementary_gap = r.x_detector_for_complementary_gap
    z_detector_for_complementary_gap = r.z_detector_for_complementary_gap
    assert x_detector_for_complementary_gap is not None
    assert z_detector_for_complementary_gap is not None

    initial_shots = 100_000
    [initial_results] = perform_parallel_simulation(
        r.circuit,
        x_detector_for_complementary_gap,
        z_detector_for_complementary_gap,
        [(0, math.inf)],
        initial_shots,
        parallelism,
        max_shots_per_task,
        show_progress=False)
    initial_results.uncategorized_samples.sort(key=lambda r: r.gap)

    discard_rates = [0.25, 0.30, 0.35]
    gap_filters: list[tuple[float, float]] = construct_gap_filters(discard_rates, initial_results, 0.02)
    assert len(discard_rates) == len(gap_filters)
    for (rate, (low, high)) in zip(discard_rates, gap_filters):
        print('Gap filter for cutoff rate {:4.1f}% is ({:.4f}, {:.4f}).'.format(rate * 100, low, high))

    list_of_results = perform_parallel_simulation(
        r.circuit,
        x_detector_for_complementary_gap,
        z_detector_for_complementary_gap,
        gap_filters,
        num_shots,
        parallelism,
        max_shots_per_task,
        show_progress)

    for results in list_of_results:
        results.uncategorized_samples.sort(key=lambda r: r.gap)

    for (rate, results) in zip(discard_rates, list_of_results):
        num_valid = results.num_valid_samples
        num_wrong = results.num_wrong_samples
        num_discarded = results.num_discarded_samples

        num_to_be_discarded = round(len(results) * rate)

        for sample in results.uncategorized_samples:
            if num_discarded < num_to_be_discarded:
                num_discarded += 1
            elif sample.expected:
                num_valid += 1
            else:
                num_wrong += 1

        print('Discard {:.1f}% samples, VALID = {}, WRONG = {}, DISCARDED = {}'.format(
            rate * 100, num_valid, num_wrong, num_discarded))
        print('WRONG / (VALID + WRONG) = {:.3e}'.format(num_wrong / (num_valid + num_wrong)))
        print()


if __name__ == '__main__':
    main()
