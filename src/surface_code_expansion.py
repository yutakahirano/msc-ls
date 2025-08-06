from __future__ import annotations

import argparse
import concurrent.futures
import enum
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


class ExpansionPattern(enum.Enum):
    DOWNWARD = enum.auto(),
    UPWARD = enum.auto(),


class SurfaceCodePatch:
    def __init__(self, circuit: Circuit,
                 distance1: int, distance2: int, rounds_for_gap: int, pattern: ExpansionPattern) -> None:
        assert distance1 <= distance2
        self.circuit = circuit
        self.distance1 = distance1
        self.distance2 = distance2
        self.rounds_for_gap = rounds_for_gap
        self.syndrome_measurements: dict[tuple[int, int], SurfaceSyndromeMeasurement] = {}
        self.detector_for_complementary_gap: DetectorIdentifier | None = None
        self.pattern = pattern
        match pattern:
            case ExpansionPattern.DOWNWARD:
                self.offset = (1, 1)
            case ExpansionPattern.UPWARD:
                self.offset = (1, 1 + 2 * (distance2 - distance1))

    def _setup_initial_state(self) -> None:
        m: SurfaceSyndromeMeasurement
        circuit = self.circuit
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

    def _setup_syndrome_measurements_upward(self) -> None:
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
                if j < distance1 and i >= distance2 - distance1:
                    pass
                elif i + j < distance2 - 1:
                    circuit.place_reset_x((x, y))
                else:
                    circuit.place_reset_z((x, y))

                # Weight-two syndrome measurements:
                if i == 0 and j % 2 == 0 and j < distance2 - 1:
                    self._push(SurfaceXSyndromeMeasurement(circuit, (x + 1, y - 1), TWO_WEIGHT_DOWN, True))
                if i == distance2 - 1 and j % 2 == 1 and distance1 - 1 <= j and j < distance2 - 1:
                    self._push(SurfaceXSyndromeMeasurement(circuit, (x + 1, y + 1), TWO_WEIGHT_UP, False))
                if j == 0 and i % 2 == 1 and i < (distance2 - distance1):
                    self._push(SurfaceZSyndromeMeasurement(circuit, (x - 1, y + 1), TWO_WEIGHT_RIGHT, False))
                if j == distance2 - 1 and i % 2 == 0 and i < distance2 - 1:
                    self._push(SurfaceZSyndromeMeasurement(circuit, (x + 1, y + 1), TWO_WEIGHT_LEFT, True))

                # Weight-four syndrome measurements:
                if i >= distance2 - 1 or j >= distance2 - 1:
                    continue
                if i >= distance2 - distance1 and j < distance1 - 1:
                    continue

                last_measurement: MeasurementIdentifier | None = None
                if (i + j) % 2 == 0:
                    satisfied = i + j >= distance2 - 1
                    if (x + 1, y + 1) in syndrome_measurements:
                        assert j == distance1 - 1
                        assert satisfied
                        m = syndrome_measurements[(x + 1), (y + 1)]
                        del syndrome_measurements[(x + 1), (y + 1)]
                        assert isinstance(m, SurfaceZSyndromeMeasurement)
                        assert m.pattern == TWO_WEIGHT_LEFT
                        last_measurement = m.last_measurement
                        assert last_measurement is not None
                        satisfied = False
                    m = SurfaceZSyndromeMeasurement(circuit, (x + 1, y + 1), FOUR_WEIGHT, satisfied)
                    m.last_measurement = last_measurement
                    self._push(m)
                else:
                    satisfied = i + j < distance2 - 2
                    if (x + 1, y + 1) in syndrome_measurements:
                        assert i == distance2 - distance1 - 1
                        assert satisfied
                        m = syndrome_measurements[(x + 1), (y + 1)]
                        del syndrome_measurements[(x + 1), (y + 1)]
                        assert isinstance(m, SurfaceXSyndromeMeasurement)
                        assert m.pattern == TWO_WEIGHT_DOWN
                        last_measurement = m.last_measurement
                        assert last_measurement is not None
                        satisfied = False
                    m = SurfaceXSyndromeMeasurement(circuit, (x + 1, y + 1), FOUR_WEIGHT, satisfied)
                    m.last_measurement = last_measurement
                    self._push(m)

    def _setup_syndrome_measurements_downward(self) -> None:
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
                        assert satisfied
                        m = syndrome_measurements[(x + 1), (y + 1)]
                        del syndrome_measurements[(x + 1), (y + 1)]
                        assert isinstance(m, SurfaceZSyndromeMeasurement)
                        assert m.pattern == TWO_WEIGHT_LEFT
                        last_measurement = m.last_measurement
                        satisfied = False
                    m = SurfaceZSyndromeMeasurement(circuit, (x + 1, y + 1), FOUR_WEIGHT, satisfied)
                    m.last_measurement = last_measurement
                    self._push(m)
                else:
                    satisfied = j < i
                    if (x + 1, y + 1) in syndrome_measurements:
                        assert i == distance1 - 1
                        assert satisfied
                        m = syndrome_measurements[(x + 1), (y + 1)]
                        del syndrome_measurements[(x + 1), (y + 1)]
                        assert isinstance(m, SurfaceXSyndromeMeasurement)
                        assert m.pattern == TWO_WEIGHT_UP
                        last_measurement = m.last_measurement
                        satisfied = False
                    m = SurfaceXSyndromeMeasurement(circuit, (x + 1, y + 1), FOUR_WEIGHT, satisfied)
                    m.last_measurement = last_measurement
                    self._push(m)

    def _perform_code_expansion(self) -> None:
        if self.distance1 == self.distance2:
            return

        match self.pattern:
            case ExpansionPattern.DOWNWARD:
                self._setup_syndrome_measurements_downward()
            case ExpansionPattern.UPWARD:
                (offset_x, offset_y) = self.offset
                self.offset = (offset_x, offset_y - 2 * (self.distance2 - self.distance1))
                (offset_x, offset_y) = self.offset
                self._setup_syndrome_measurements_upward()

        assert len(self.syndrome_measurements) == self.distance2 * self.distance2 - 1

    def _perform_logical_z_measurement(self) -> None:
        distance2 = self.distance2
        circuit = self.circuit
        (offset_x, offset_y) = self.offset

        with SuppressNoise(circuit):
            for _ in range(TICKS_FOR_SYNDROME_MEASUREMENT * 2):
                for m in self.syndrome_measurements.values():
                    m.run()
                circuit.place_tick()

            pauli_string = stim.PauliString()
            match self.pattern:
                case ExpansionPattern.DOWNWARD:
                    for j in range(distance2):
                        x = offset_x + j * 2
                        y = offset_y
                        pauli_string *= stim.PauliString('Z{}'.format(circuit.mapping.get_id(x, y)))
                case ExpansionPattern.UPWARD:
                    for j in range(distance2):
                        x = offset_x + j * 2
                        y = offset_y + (distance2 - 1) * 2
                        pauli_string *= stim.PauliString('Z{}'.format(circuit.mapping.get_id(x, y)))
            zs = [circuit.place_mpp(pauli_string)]
            circuit.place_observable_include(zs)
            self.detector_for_complementary_gap = circuit.place_detector(zs)

    def _push(self, m: SurfaceSyndromeMeasurement) -> None:
        position = m.ancilla_position
        assert position not in self.syndrome_measurements
        self.syndrome_measurements[position] = m

    def build(self) -> None:
        self._setup_initial_state()
        self._perform_code_expansion()
        for _ in range(TICKS_FOR_SYNDROME_MEASUREMENT * self.rounds_for_gap):
            for m in self.syndrome_measurements.values():
                m.run()
            self.circuit.place_tick()

        self._perform_logical_z_measurement()


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
        detector_for_complementary_gap: DetectorIdentifier,
        gap_filters: list[tuple[float, float]],
        detectors_for_post_selection: list[DetectorIdentifier]) -> list[SimulationResults]:

    dem = stim_circuit.detector_error_model(decompose_errors=True)
    matcher = pymatching.Matching.from_detector_error_model(dem)
    sampler = stim_circuit.compile_detector_sampler()

    detection_events, observable_flips = sampler.sample(num_shots, separate_observables=True)

    results = [SimulationResults(lower, upper) for (lower, upper) in gap_filters]
    postselection_ids = np.array([id.id for id in detectors_for_post_selection], dtype='uint')

    for shot in range(num_shots):
        syndrome = detection_events[shot]
        if np.any(syndrome[postselection_ids] != 0):
            for rs in results:
                rs.append_discarded()
            continue

        prediction, weight = matcher.decode(syndrome, return_weight=True)

        syndrome[detector_for_complementary_gap.id] = not syndrome[detector_for_complementary_gap.id]
        c_prediction, c_weight = matcher.decode(syndrome, return_weight=True)
        syndrome[detector_for_complementary_gap.id] = not syndrome[detector_for_complementary_gap.id]

        if weight > c_weight:
            prediction = c_prediction

        actual = observable_flips[shot]
        expected = np.array_equal(actual, prediction)
        gap = abs(weight - c_weight)
        for rs in results:
            rs.append(gap, expected)
    return results


def perform_parallel_simulation(
        circuit: Circuit,
        detector_for_complementary_gap: DetectorIdentifier,
        gap_filters: list[tuple[float, float]],
        num_shots: int,
        parallelism: int,
        num_shots_per_task: int,
        show_progress: bool) -> list[SimulationResults]:
    if num_shots / parallelism < 1000 or parallelism == 1:
        return perform_simulation(
                circuit.circuit,
                num_shots,
                detector_for_complementary_gap,
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
                                     detector_for_complementary_gap,
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
    parser.add_argument('--distance1', type=int, default=3)
    parser.add_argument('--distance2', type=int, default=7)
    parser.add_argument('--expansion-pattern', type=str, choices=list(['UPWARD', 'DOWNWARD']), default='DOWNWARD')
    parser.add_argument('--threshold-gap', type=float)
    parser.add_argument('--rounds-for-gap', type=int, default=7)
    parser.add_argument('--show-progress', action='store_true')
    parser.add_argument('--print-circuit', action='store_true')

    args = parser.parse_args()

    print('  num-shots = {}'.format(args.num_shots))
    print('  error-probability = {}'.format(args.error_probability))
    print('  parallelism = {}'.format(args.parallelism))
    print('  max-shots-per-task = {}'.format(args.max_shots_per_task))
    print('  distance1 = {}'.format(args.distance1))
    print('  distance2 = {}'.format(args.distance2))
    print('  expansion-pattern = {}'.format(args.expansion_pattern))
    print('  threshold-gap = {}'.format(args.threshold_gap))
    print('  rounds-for-gap = {}'.format(args.rounds_for_gap))
    print('  show-progress = {}'.format(args.show_progress))
    print('  print-circuit = {}'.format(args.print_circuit))

    num_shots: int = args.num_shots
    error_probability: float = args.error_probability
    parallelism: int = args.parallelism
    max_shots_per_task: int = args.max_shots_per_task
    distance1: int = args.distance1
    distance2: int = args.distance2
    expansion_pattern: ExpansionPattern = args.expansion_pattern
    match args.expansion_pattern:
        case 'UPWARD':
            expansion_pattern = ExpansionPattern.UPWARD
        case 'DOWNWARD':
            expansion_pattern = ExpansionPattern.DOWNWARD
        case _:
            raise ValueError(f'Invalid expansion pattern: {args.expansion_pattern}')
    threshold_gap: float | None = args.threshold_gap
    rounds_for_gap: int = args.rounds_for_gap
    show_progress: bool = args.show_progress
    print_circuit: bool = args.print_circuit

    mapping = QubitMapping(30, 30)
    circuit = Circuit(mapping, error_probability)
    patch = SurfaceCodePatch(circuit, distance1, distance2, rounds_for_gap, expansion_pattern)

    patch.build()

    if print_circuit:
        print(circuit.circuit)

    # Assert that the circuit has deterministic observables.
    _ = circuit.circuit.detector_error_model()
    # Assert that the circuit has a graph-like dem.
    _ = circuit.circuit.detector_error_model(decompose_errors=True)

    detector_for_complementary_gap = patch.detector_for_complementary_gap
    assert detector_for_complementary_gap is not None

    if num_shots == 0:
        return

    if threshold_gap is not None:
        [results] = perform_parallel_simulation(
            circuit,
            detector_for_complementary_gap,
            [(threshold_gap, threshold_gap)],
            num_shots,
            parallelism,
            max_shots_per_task,
            show_progress)
        assert len(results.uncategorized_samples) == 0
        num_valid = results.num_valid_samples
        num_wrong = results.num_wrong_samples
        num_discarded = results.num_discarded_samples
        print('VALID = {}, WRONG = {}, DISCARDED = {}'.format(num_valid, num_wrong, num_discarded))
        print('WRONG / (VALID + WRONG) = {:.3e}'.format(num_wrong / (num_valid + num_wrong)))
        return

    initial_shots = 100_000
    [initial_results] = perform_parallel_simulation(
        circuit,
        detector_for_complementary_gap,
        [(0, math.inf)],
        initial_shots,
        parallelism,
        max_shots_per_task,
        show_progress=False)
    initial_results.uncategorized_samples.sort(key=lambda r: r.gap)

    discard_rates = [0, 0.01, 0.02, 0.05, 0.1, 0.15, 0.2]
    gap_filters: list[tuple[float, float]] = construct_gap_filters(discard_rates, initial_results, 0.02)
    assert len(discard_rates) == len(gap_filters)
    for (rate, (low, high)) in zip(discard_rates, gap_filters):
        print('Gap filter for cutoff rate {:4.1f}% is ({:.4f}, {:.4f}).'.format(rate * 100, low, high))

    list_of_results = perform_parallel_simulation(
        circuit,
        detector_for_complementary_gap,
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
