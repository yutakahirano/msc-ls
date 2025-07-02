from __future__ import annotations

import concurrent
import argparse
import enum
import math
import numpy as np
import pymatching
import stim
import sys

import steane_code

from concurrent.futures import ProcessPoolExecutor
from enum import auto
from util import QubitMapping, Circuit, MultiplexingCircuit
from util import MeasurementIdentifier, DetectorIdentifier, ObservableIdentifier, SuppressNoise
from steane_code import SteaneZ0145SyndromeMeasurement, SteaneZ0235SyndromeMeasurement, SteaneZ0246SyndromeMeasurement
from steane_code import STEANE_0, STEANE_1, STEANE_2, STEANE_3, STEANE_4, STEANE_5, STEANE_6
from surface_code import SurfaceStabilizerPattern, SurfaceSyndromeMeasurement
from surface_code import SurfaceXSyndromeMeasurement, SurfaceZSyndromeMeasurement


class InitialValue(enum.Enum):
    Plus = auto(),
    Zero = auto(),
    SPlus = auto(),


# Representing a merged QEC code of the Steane code and the rotated surface code.
class SteanePlusSurfaceCode:
    def __init__(self, mapping: QubitMapping, surface_distance: int, initial_value: InitialValue,
                 perfect_initialization: bool,
                 error_probability: float, full_post_selection: bool) -> None:
        self.mapping = mapping
        self.surface_distance = surface_distance
        self.initial_value = initial_value
        self.perfect_initialization = perfect_initialization
        self.error_probability = error_probability
        self.full_post_selection = full_post_selection
        self.primal_circuit = Circuit(mapping, error_probability)
        self.partially_noiseless_circuit = Circuit(mapping, error_probability)
        noiseless_qubits: list[tuple[int, int]] = []
        for y in range(0, 6):
            for x in range(0, mapping.width):
                if (x + y) % 2 == 0:
                    noiseless_qubits.append((x, y))
        self.partially_noiseless_circuit.mark_qubits_as_noiseless(noiseless_qubits)
        self.circuit = MultiplexingCircuit(self.primal_circuit, self.partially_noiseless_circuit)
        self.surface_syndrome_measurements: dict[tuple[int, int], SurfaceSyndromeMeasurement] = {}
        self.surface_offset_x = 1
        self.surface_offset_y = 7
        self.x_detector_for_complementary_gap: DetectorIdentifier | None = None
        self.z_detector_for_complementary_gap: DetectorIdentifier | None = None
        # Note that `self.circuit` does not recognize this qubit, and hence we use raw Stim APIs to access these qubits.
        # This also means that we do not need to worry about idling noise on these qubits.
        self.x_boundary_ancilla_id: int = 10000
        self.z_boundary_ancilla_id: int = 20000

        self._setup_syndrome_measurements()

    def _setup_syndrome_measurements(self) -> None:
        surface_distance = self.surface_distance
        surface_code_offset_x = self.surface_offset_x
        surface_code_offset_y = self.surface_offset_y

        FOUR_WEIGHT = SurfaceStabilizerPattern.FOUR_WEIGHT
        TWO_WEIGHT_UP = SurfaceStabilizerPattern.TWO_WEIGHT_UP
        TWO_WEIGHT_DOWN = SurfaceStabilizerPattern.TWO_WEIGHT_DOWN
        TWO_WEIGHT_LEFT = SurfaceStabilizerPattern.TWO_WEIGHT_LEFT
        TWO_WEIGHT_RIGHT = SurfaceStabilizerPattern.TWO_WEIGHT_RIGHT

        m: SurfaceSyndromeMeasurement
        for i in range(surface_distance):
            for j in range(surface_distance):
                x = surface_code_offset_x + j * 2
                y = surface_code_offset_y + i * 2

                # Weight-two syndrome measurements:
                if i == 0 and j % 2 == 0 and j < surface_distance - 1:
                    m = SurfaceXSyndromeMeasurement(self.circuit, (x + 1, y - 1), TWO_WEIGHT_DOWN, True)
                    self.surface_syndrome_measurements[(x + 1, y - 1)] = m
                if i == surface_distance - 1 and j % 2 == 1:
                    m = SurfaceXSyndromeMeasurement(self.circuit, (x + 1, y + 1), TWO_WEIGHT_UP, True)
                    self.surface_syndrome_measurements[(x + 1, y + 1)] = m
                if j == 0 and i % 2 == 1:
                    m = SurfaceZSyndromeMeasurement(self.circuit, (x - 1, y + 1), TWO_WEIGHT_RIGHT, False)
                    self.surface_syndrome_measurements[(x - 1, y + 1)] = m
                if j == surface_distance - 1 and i % 2 == 0 and i < surface_distance - 1:
                    m = SurfaceZSyndromeMeasurement(self.circuit, (x + 1, y + 1), TWO_WEIGHT_LEFT, False)
                    self.surface_syndrome_measurements[(x + 1, y + 1)] = m

                # Weight-four syndrome measurements:
                if i < surface_distance - 1 and j < surface_distance - 1:
                    if (i + j) % 2 == 0:
                        m = SurfaceZSyndromeMeasurement(self.circuit, (x + 1, y + 1), FOUR_WEIGHT, False)
                    else:
                        m = SurfaceXSyndromeMeasurement(self.circuit, (x + 1, y + 1), FOUR_WEIGHT, True)
                    self.surface_syndrome_measurements[(x + 1, y + 1)] = m

        if self.full_post_selection:
            for m in self.surface_syndrome_measurements.values():
                m.set_post_selection(True)

    def run(self) -> None:
        SURFACE_SYNDROME_MEASUREMENT_DEPTH = 6
        surface_distance = self.surface_distance
        circuit = self.circuit
        mapping = self.mapping

        surface_offset_x = self.surface_offset_x
        surface_offset_y = self.surface_offset_y

        if self.perfect_initialization:
            for i in range(surface_distance):
                for j in range(surface_distance):
                    x = surface_offset_x + j * 2
                    y = surface_offset_y + i * 2
                    circuit.place_reset_x((x, y))

            SURFACE_DEPTH_OFFSET = 3
            for i in range(SURFACE_DEPTH_OFFSET):
                for m in self.surface_syndrome_measurements.values():
                    m.run()
                circuit.place_tick()

            for stim_circuit in [self.primal_circuit.circuit, self.partially_noiseless_circuit.circuit]:
                match self.initial_value:
                    case InitialValue.Plus:
                        steane_code.perform_perfect_steane_plus_initialization(stim_circuit, mapping)
                    case InitialValue.Zero:
                        steane_code.perform_perfect_steane_zero_initialization(stim_circuit, mapping)
                    case InitialValue.SPlus:
                        steane_code.perform_perfect_steane_s_plus_initialization(stim_circuit, mapping)
        else:
            steane_code.perform_injection(circuit)
            circuit.place_tick()
            steane_code.perform_syndrome_extraction_after_injection(circuit)
            circuit.place_tick()

            g = steane_code.check_generator(circuit)
            tick = 0
            while True:
                if tick == 9:
                    for i in range(surface_distance):
                        for j in range(surface_distance):
                            x = surface_offset_x + j * 2
                            y = surface_offset_y + i * 2
                            circuit.place_reset_x((x, y))
                if tick >= 9:
                    for m in self.surface_syndrome_measurements.values():
                        m.run()
                try:
                    next(g)
                except StopIteration:
                    break
                circuit.place_tick()
                tick += 1

            circuit.place_tick()

        # After the Steane code initialization, we place boundary ancillae for the complementary gap.
        # Note that the exact timing does not matter because `partially_noiseless_circuit` assumes noise-free
        # qubits on the Steane code region.
        for stim_circuit in [self.primal_circuit.circuit, self.partially_noiseless_circuit.circuit]:
            stim_circuit.append('RX', self.x_boundary_ancilla_id)
            stim_circuit.append('CX', [self.x_boundary_ancilla_id, mapping.get_id(*STEANE_1)])
            stim_circuit.append('CX', [self.x_boundary_ancilla_id, mapping.get_id(*STEANE_4)])
            stim_circuit.append('CX', [self.x_boundary_ancilla_id, mapping.get_id(*STEANE_6)])
            stim_circuit.append('R', self.z_boundary_ancilla_id)
            stim_circuit.append('CX', [mapping.get_id(*STEANE_1), self.z_boundary_ancilla_id])
            stim_circuit.append('CX', [mapping.get_id(*STEANE_4), self.z_boundary_ancilla_id])
            stim_circuit.append('CX', [mapping.get_id(*STEANE_6), self.z_boundary_ancilla_id])

        ls_results = steane_code.LatticeSurgeryMeasurements()
        g = steane_code.lattice_surgery_generator(circuit, surface_distance, ls_results)
        performing_first_syndrome_extraction = True

        while True:
            if performing_first_syndrome_extraction and \
                    any([m.is_complete() for m in self.surface_syndrome_measurements.values()]):
                assert all([m.is_complete() for m in self.surface_syndrome_measurements.values()])
                performing_first_syndrome_extraction = False

                # Remove the stabilizers that conflict with the lattice surgery.
                for j in range(surface_distance):
                    x = surface_offset_x + j * 2
                    y = surface_offset_y
                    if j % 2 == 0 and j < surface_distance - 1:
                        del self.surface_syndrome_measurements[(x + 1, y - 1)]

            for m in self.surface_syndrome_measurements.values():
                m.run()

            try:
                next(g)
            except StopIteration:
                assert ls_results.is_complete()
                circuit.place_tick()
                break

            circuit.place_tick()

        self.partially_noiseless_circuit.mark_qubits_as_noiseless([])
        # Let's recover and reconfigure some stabilizers.
        for j in range(surface_distance):
            x = surface_offset_x + j * 2
            y = surface_offset_y
            if j % 2 == 0 and j < surface_distance - 1:
                m = SurfaceXSyndromeMeasurement(
                    self.circuit, (x + 1, y - 1), SurfaceStabilizerPattern.TWO_WEIGHT_DOWN, False)
                self.surface_syndrome_measurements[(x + 1, y - 1)] = m
                m.set_post_selection(self.full_post_selection)

        for _ in range(SURFACE_SYNDROME_MEASUREMENT_DEPTH):
            for m in self.surface_syndrome_measurements.values():
                m.run()
            circuit.place_tick()

        # Place a detector for the six-weight X stabilizer.
        last = self.surface_syndrome_measurements[(surface_offset_x + 1, surface_offset_y - 1)].last_measurement
        assert last is not None
        circuit.place_detector(ls_results.x_0145_measurements() + [last], post_selection=True)

        if not self.full_post_selection:
            for m in self.surface_syndrome_measurements.values():
                m.set_post_selection(False)
            # We perform one-round of syndrome measurements above.
            # Hence, here we perform `(surface_distance - 1)` rounds of syndrome measurments.
            for _ in range(SURFACE_SYNDROME_MEASUREMENT_DEPTH * (surface_distance - 1)):
                for m in self.surface_syndrome_measurements.values():
                    m.run()
                circuit.place_tick()

        for c in [self.primal_circuit, self.partially_noiseless_circuit]:
            stim_circuit = c.circuit
            for j in range(surface_distance):
                x = surface_offset_x + j * 2
                y = surface_offset_y
                control_id = mapping.get_id(x, y)
                stim_circuit.append('CX', [control_id, self.z_boundary_ancilla_id])
            stim_circuit.append('M', self.z_boundary_ancilla_id)
            stim_circuit.append(
                'DETECTOR',
                [stim.target_rec(-1)] + [m.target_rec(c) for m in ls_results.lattice_surgery_zz_measurements()])

            for i in range(surface_distance):
                x = surface_offset_x
                y = surface_offset_y + i * 2
                target_id = mapping.get_id(x, y)
                stim_circuit.append('CX', [self.x_boundary_ancilla_id, target_id])
            stim_circuit.append('MX', self.x_boundary_ancilla_id)
            stim_circuit.append(
                'DETECTOR', [stim.target_rec(-1)] + [m.target_rec(c) for m in ls_results.logical_x_measurements()])
        assert self.primal_circuit.circuit.num_detectors == self.partially_noiseless_circuit.circuit.num_detectors
        self.x_detector_for_complementary_gap = DetectorIdentifier(self.primal_circuit.circuit.num_detectors - 2)
        self.z_detector_for_complementary_gap = DetectorIdentifier(self.primal_circuit.circuit.num_detectors - 1)

        # Perfect verification of the resultant state.
        with SuppressNoise(circuit):
            for _ in range(SURFACE_SYNDROME_MEASUREMENT_DEPTH):
                for m in self.surface_syndrome_measurements.values():
                    m.run()
                circuit.place_tick()

            ms: list[MeasurementIdentifier] = []
            match self.initial_value:
                case InitialValue.Plus:
                    ms.append(circuit.place_mpp(self._logical_x_pauli_string()))
                    ms.extend(ls_results.logical_x_measurements())
                case InitialValue.Zero:
                    ms.append(circuit.place_mpp(self._logical_z_pauli_string()))
                    ms.extend(ls_results.lattice_surgery_zz_measurements())
                case InitialValue.SPlus:
                    ms.append(circuit.place_mpp(self._logical_y_pauli_string()))
                    ms.extend(ls_results.logical_x_measurements())
                    ms.extend(ls_results.lattice_surgery_zz_measurements())
            circuit.place_observable_include(ms, ObservableIdentifier(0))

    def _logical_x_pauli_string(self) -> stim.PauliString:
        surface_distance = self.surface_distance
        mapping = self.mapping
        surface_code_offset_x = self.surface_offset_x
        surface_code_offset_y = self.surface_offset_y

        logical_x: stim.PauliString = stim.PauliString()
        for i in range(surface_distance):
            x = surface_code_offset_x
            y = surface_code_offset_y + i * 2
            logical_x *= stim.PauliString('X{}'.format(mapping.get_id(x, y)))
        return logical_x

    def _logical_z_pauli_string(self) -> stim.PauliString:
        surface_distance = self.surface_distance
        mapping = self.mapping
        surface_code_offset_x = self.surface_offset_x
        surface_code_offset_y = self.surface_offset_y

        logical_z: stim.PauliString = stim.PauliString()
        for j in range(surface_distance):
            x = surface_code_offset_x + j * 2
            y = surface_code_offset_y
            logical_z *= stim.PauliString('Z{}'.format(mapping.get_id(x, y)))
        return logical_z

    def _logical_y_pauli_string(self) -> stim.PauliString:
        return self._logical_x_pauli_string() * self._logical_z_pauli_string()


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
        primal_stim_circuit: stim.Circuit,
        partially_noiseless_stim_circuit: stim.Circuit,
        num_shots: int,
        x_detector_for_complementary_gap: DetectorIdentifier,
        z_detector_for_complementary_gap: DetectorIdentifier,
        gap_filters: list[tuple[float, float]],
        seed: int | None,
        detectors_for_post_selection: list[DetectorIdentifier]) -> list[SimulationResults]:

    # We construct a decoder for `partially_noiseless_stim_circuit`, not to confuse the matching decoder with
    # non-matchable detectors. We perform post-selection for all detectors in the Steane code, so the difference
    # between the two DEMs should be small...
    dem = partially_noiseless_stim_circuit.detector_error_model(decompose_errors=True)
    matcher = pymatching.Matching.from_detector_error_model(dem)

    # However, we construct a sampler from `primal_stim_circuit` because it is *the real* circuit.
    sampler = primal_stim_circuit.compile_detector_sampler(seed=seed)
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
        try:
            c_prediction, c_weight = matcher.decode(syndrome, return_weight=True)
        except ValueError:
            c_prediction = None
            c_weight = math.inf
        if c_weight < min_weight:
            prediction = c_prediction
        min_weight = min(min_weight, c_weight)
        max_weight = max(max_weight, c_weight)

        syndrome[x_detector_for_complementary_gap.id] = not syndrome[x_detector_for_complementary_gap.id]
        try:
            c_prediction, c_weight = matcher.decode(syndrome, return_weight=True)
        except ValueError:
            c_prediction = None
            c_weight = math.inf
        if c_weight < min_weight:
            prediction = c_prediction
        min_weight = min(min_weight, c_weight)
        max_weight = max(max_weight, c_weight)

        syndrome[z_detector_for_complementary_gap.id] = not syndrome[z_detector_for_complementary_gap.id]

        try:
            c_prediction, c_weight = matcher.decode(syndrome, return_weight=True)
        except ValueError:
            c_prediction = None
            c_weight = math.inf
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
        primal_circuit: Circuit,
        partially_noiseless_circuit: Circuit,
        x_detector_for_complementary_gap: DetectorIdentifier,
        z_detector_for_complementary_gap: DetectorIdentifier,
        gap_filters: list[tuple[float, float]],
        num_shots: int,
        parallelism: int,
        num_shots_per_task: int,
        show_progress: bool) -> list[SimulationResults]:
    if num_shots / parallelism < 1000 or parallelism == 1:
        return perform_simulation(
                primal_circuit.circuit,
                partially_noiseless_circuit.circuit,
                num_shots,
                x_detector_for_complementary_gap,
                z_detector_for_complementary_gap,
                gap_filters,
                None,
                primal_circuit.detectors_for_post_selection)

    results = [SimulationResults(lower, upper) for (lower, upper) in gap_filters]
    progress = 0
    with ProcessPoolExecutor(max_workers=parallelism) as executor:
        futures: list[concurrent.futures.Future] = []
        remaining_shots = num_shots

        num_shots_per_task = min(num_shots_per_task, (num_shots + parallelism - 1) // parallelism)
        while remaining_shots > 0:
            seed = None
            num_shots_for_this_task = min(num_shots_per_task, remaining_shots)
            remaining_shots -= num_shots_for_this_task
            future = executor.submit(perform_simulation,
                                     primal_circuit.circuit,
                                     partially_noiseless_circuit.circuit,
                                     num_shots_for_this_task,
                                     x_detector_for_complementary_gap,
                                     z_detector_for_complementary_gap,
                                     gap_filters,
                                     seed,
                                     primal_circuit.detectors_for_post_selection)
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
    if index < 0:
        return 0.0
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
    parser.add_argument('--initial-value', choices=['+', '0', 'S+'], default='+')
    parser.add_argument('--perfect-initialization', action='store_true')
    parser.add_argument('--imperfect-initialization', action='store_true')
    parser.add_argument('--full-post-selection', action='store_true')
    parser.add_argument('--print-circuit', action='store_true')
    parser.add_argument('--show-progress', action='store_true')

    args = parser.parse_args()

    if args.perfect_initialization and args.imperfect_initialization:
        print('Error: Cannot specify both --perfect-initialization and --imperfect-initialization.', file=sys.stderr)
        return

    perfect_initialization: bool = False
    if args.perfect_initialization:
        perfect_initialization = True
    elif args.imperfect_initialization:
        perfect_initialization = False

    print('  num-shots = {}'.format(args.num_shots))
    print('  error-probability = {}'.format(args.error_probability))
    print('  parallelism = {}'.format(args.parallelism))
    print('  max-shots-per-task = {}'.format(args.max_shots_per_task))
    print('  surface-distance = {}'.format(args.surface_distance))
    print('  initial-value = {}'.format(args.initial_value))
    print('  perfect-initialization = {}'.format(perfect_initialization))
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
        case 'S+':
            initial_value = InitialValue.SPlus
        case _:
            assert False
    full_post_selection: bool = args.full_post_selection
    print_circuit: bool = args.print_circuit
    show_progress: bool = args.show_progress

    mapping = QubitMapping(30, 30)
    r = SteanePlusSurfaceCode(
        mapping, surface_distance, initial_value, perfect_initialization, error_probability, full_post_selection)
    primal_circuit = r.primal_circuit
    partially_noiseless_circuit = r.partially_noiseless_circuit
    stim_circuit = primal_circuit.circuit
    r.run()
    if print_circuit:
        print(partially_noiseless_circuit.circuit)

    # Assert that the circuit have deterministic detectors.
    # The primal circuit has a non-graph-like DEM.
    _ = stim_circuit.detector_error_model()
    # The partially noiseless circuit has a graph-like DEM.
    _ = partially_noiseless_circuit.circuit.detector_error_model(decompose_errors=True)

    if num_shots == 0:
        return

    x_detector_for_complementary_gap = r.x_detector_for_complementary_gap
    z_detector_for_complementary_gap = r.z_detector_for_complementary_gap
    assert x_detector_for_complementary_gap is not None
    assert z_detector_for_complementary_gap is not None

    initial_shots = 100_000
    [initial_results] = perform_parallel_simulation(
        primal_circuit,
        partially_noiseless_circuit,
        x_detector_for_complementary_gap,
        z_detector_for_complementary_gap,
        [(0, math.inf)],
        initial_shots,
        parallelism,
        max_shots_per_task,
        show_progress=False)
    initial_results.uncategorized_samples.sort(key=lambda r: r.gap)

    discard_rates = [0, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80]
    gap_filters: list[tuple[float, float]] = construct_gap_filters(discard_rates, initial_results, 0.02)

    assert len(discard_rates) == len(gap_filters)
    for (rate, (low, high)) in zip(discard_rates, gap_filters):
        print('Gap filter for cutoff rate {:4.1f}% is ({:.4f}, {:.4f}).'.format(rate * 100, low, high))

    list_of_results = perform_parallel_simulation(
        primal_circuit,
        partially_noiseless_circuit,
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
