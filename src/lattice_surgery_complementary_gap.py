from __future__ import annotations

import concurrent
import concurrent.futures
import argparse
import enum
import math
import numpy as np
import pymatching
import re
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


class SteaneSyndromeExtractionPattern(enum.Enum):
    XZZ = auto(),
    ZXZ = auto(),
    ZZ = auto(),


# Representing a merged QEC code of the Steane code and the rotated surface code.
class SteanePlusSurfaceCode:
    def __init__(self, mapping: QubitMapping, surface_distance: int, initial_value: InitialValue,
                 steane_syndrome_extraction_pattern: SteaneSyndromeExtractionPattern, perfect_initialization: bool,
                 error_probability: float, with_heulistic_post_selection: bool,
                 full_post_selection: bool, num_epilogue_syndrome_extraction_rounds: int) -> None:
        self.mapping = mapping
        self.surface_distance = surface_distance
        self.initial_value = initial_value
        self.steane_syndrome_extraction_pattern = steane_syndrome_extraction_pattern
        self.perfect_initialization = perfect_initialization
        self.error_probability = error_probability
        self.with_heulistic_post_selection = with_heulistic_post_selection
        self.full_post_selection = full_post_selection
        self.num_epilogue_syndrome_extraction_rounds = num_epilogue_syndrome_extraction_rounds
        self.primal_circuit = Circuit(mapping, error_probability)
        self.partially_noiseless_circuit = Circuit(mapping, error_probability)
        noiseless_qubits: list[tuple[int, int]] = []
        for y in range(0, 16):
            for x in range(0, mapping.width):
                if (x + y) % 2 == 0:
                    noiseless_qubits.append((x, y))
        self.partially_noiseless_circuit.mark_qubits_as_noiseless(noiseless_qubits)
        self.circuit = MultiplexingCircuit(self.primal_circuit, self.partially_noiseless_circuit)
        self.surface_syndrome_measurements: dict[tuple[int, int], SurfaceSyndromeMeasurement] = {}
        self.surface_offset_x = 1
        self.surface_offset_y = 17
        self.detector_for_complementary_gap: DetectorIdentifier | None = None

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
                        if self.with_heulistic_post_selection and i < 4 and j < 5:
                            m.set_post_selection(True)
                    else:
                        m = SurfaceXSyndromeMeasurement(self.circuit, (x + 1, y + 1), FOUR_WEIGHT, True)
                        if self.with_heulistic_post_selection and i < 4 and j < 5:
                            m.set_post_selection(True)
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
            for stim_circuit in [self.primal_circuit.circuit, self.partially_noiseless_circuit.circuit]:
                match self.initial_value:
                    case InitialValue.Plus:
                        steane_code.perform_perfect_steane_plus_initialization(stim_circuit, mapping)
                    case InitialValue.Zero:
                        steane_code.perform_perfect_steane_zero_initialization(stim_circuit, mapping)
                    case InitialValue.SPlus:
                        steane_code.perform_perfect_steane_s_plus_initialization(stim_circuit, mapping)
            circuit.place_tick()
        else:
            steane_code.perform_injection(circuit)
            circuit.place_tick()

            steane_code.perform_zx_syndrome_extraction_after_injection(circuit)
            circuit.place_tick()

            steane_code.perform_check(circuit)
            circuit.place_tick()

        ls_results = steane_code.LatticeSurgeryMeasurements()
        match self.steane_syndrome_extraction_pattern:
            case SteaneSyndromeExtractionPattern.XZZ:
                g = steane_code.lattice_surgery_generator_xzz(circuit, surface_distance, ls_results)
                SURFACE_SYNDROME_EXTRACTION_OFFSET = 3
            case SteaneSyndromeExtractionPattern.ZXZ:
                g = steane_code.lattice_surgery_generator_zxz(circuit, surface_distance, ls_results)
                SURFACE_SYNDROME_EXTRACTION_OFFSET = 0
            case SteaneSyndromeExtractionPattern.ZZ:
                g = steane_code.lattice_surgery_generator_zz(circuit, surface_distance, ls_results)
                SURFACE_SYNDROME_EXTRACTION_OFFSET = 0
        tick = 0

        while True:
            if tick == SURFACE_SYNDROME_EXTRACTION_OFFSET:
                for i in range(surface_distance):
                    for j in range(surface_distance):
                        x = surface_offset_x + j * 2
                        y = surface_offset_y + i * 2
                        circuit.place_reset_x((x, y))
                # Remove the stabilizers that conflict with the lattice surgery.
                for j in range(surface_distance):
                    x = surface_offset_x + j * 2
                    y = surface_offset_y
                    if j % 2 == 0 and j < surface_distance - 1:
                        del self.surface_syndrome_measurements[(x + 1, y - 1)]

            if tick >= SURFACE_SYNDROME_EXTRACTION_OFFSET:
                for m in self.surface_syndrome_measurements.values():
                    m.run()

            try:
                next(g)
            except StopIteration:
                assert ls_results.is_complete()
                circuit.place_tick()
                break

            circuit.place_tick()
            tick += 1

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
        # Hence, here we perform `(num_epilogue_syndrome_extraction_rounds - 1)` rounds of syndrome measurments.
        for _ in range(SURFACE_SYNDROME_MEASUREMENT_DEPTH * (self.num_epilogue_syndrome_extraction_rounds - 1)):
            for m in self.surface_syndrome_measurements.values():
                m.run()
            circuit.place_tick()

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
            self.detector_for_complementary_gap = circuit.place_detector(ms)
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


class SimulationResults:
    class Bucket:
        def __init__(self) -> None:
            self.num_valid_samples: int = 0
            self.num_wrong_samples: int = 0

    def __init__(self) -> None:
        self.buckets: list[SimulationResults.Bucket] = []
        self.num_discarded_samples: int = 0

    def ensure_bucket(self, gap: float) -> SimulationResults.Bucket:
        int_gap = int(gap)
        if len(self.buckets) > int_gap:
            return self.buckets[int_gap]
        self.buckets.extend([SimulationResults.Bucket() for _ in range(int_gap - len(self.buckets) + 1)])
        assert len(self.buckets) == int_gap + 1
        return self.buckets[int_gap]

    def append(self, gap: float, expected: bool) -> None:
        bucket = self.ensure_bucket(gap)

        if expected:
            bucket.num_valid_samples += 1
        else:
            bucket.num_wrong_samples += 1

    def append_discarded(self) -> None:
        self.num_discarded_samples += 1

    def extend(self, other: SimulationResults) -> None:
        self.buckets.extend([SimulationResults.Bucket() for _ in range(len(other.buckets) - len(self.buckets))])
        assert len(self.buckets) >= len(other.buckets)

        self.num_discarded_samples += other.num_discarded_samples
        for (i, bucket) in enumerate(other.buckets):
            self.buckets[i].num_valid_samples += bucket.num_valid_samples
            self.buckets[i].num_wrong_samples += bucket.num_wrong_samples

    def __len__(self) -> int:
        return sum([b.num_valid_samples + b.num_wrong_samples for b in self.buckets]) + self.num_discarded_samples


def perform_simulation(
        primal_stim_circuit: stim.Circuit,
        partially_noiseless_stim_circuit: stim.Circuit,
        num_shots: int,
        detector_for_complementary_gap: DetectorIdentifier,
        seed: int | None,
        detectors_for_post_selection: list[DetectorIdentifier]) -> SimulationResults:

    # We construct a decoder for `partially_noiseless_stim_circuit`, not to confuse the matching decoder with
    # non-matchable detectors. We perform post-selection for all detectors in the Steane code, so the difference
    # between the two DEMs should be small...
    dem = partially_noiseless_stim_circuit.detector_error_model(decompose_errors=True)
    matcher = pymatching.Matching.from_detector_error_model(dem)

    # However, we construct a sampler from `primal_stim_circuit` because it is *the real* circuit.
    sampler = primal_stim_circuit.compile_detector_sampler(seed=seed)
    detection_events, observable_flips = sampler.sample(num_shots, separate_observables=True)

    results = SimulationResults()
    postselection_ids = np.array([id.id for id in detectors_for_post_selection], dtype='uint')

    mask = np.ones_like(detection_events[0], dtype=bool)
    mask[detector_for_complementary_gap.id] = False

    for shot in range(num_shots):
        syndrome = detection_events[shot]
        if np.any(syndrome[postselection_ids] != 0):
            results.append_discarded()
            continue

        prediction, weight = matcher.decode(syndrome, return_weight=True)
        min_weight = weight
        max_weight = weight

        syndrome[detector_for_complementary_gap.id] = not syndrome[detector_for_complementary_gap.id]
        try:
            c_prediction, c_weight = matcher.decode(syndrome, return_weight=True)
        except ValueError:
            c_prediction = None
            c_weight = math.inf
        if c_weight < min_weight:
            prediction = c_prediction
        min_weight = min(min_weight, c_weight)
        max_weight = max(max_weight, c_weight)

        syndrome[detector_for_complementary_gap.id] = not syndrome[detector_for_complementary_gap.id]

        actual = observable_flips[shot]
        assert isinstance(prediction, np.ndarray)
        expected = np.array_equal(actual, prediction)
        gap = max_weight - min_weight

        # Because we *know* that the trivial syndrome is least likely to have logical errors,
        # we increase the gap manually.
        if all(syndrome[mask] == 0):
            gap += 10.0

        gap *= 100

        results.append(gap, expected)

    return results


def perform_parallel_simulation(
        primal_circuit: Circuit,
        partially_noiseless_circuit: Circuit,
        detector_for_complementary_gap: DetectorIdentifier,
        num_shots: int,
        parallelism: int,
        num_shots_per_task: int,
        show_progress: bool) -> SimulationResults:
    if num_shots / parallelism < 1000 or parallelism == 1:
        return perform_simulation(
                primal_circuit.circuit,
                partially_noiseless_circuit.circuit,
                num_shots,
                detector_for_complementary_gap,
                None,
                primal_circuit.detectors_for_post_selection)

    results = SimulationResults()
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
                                     detector_for_complementary_gap,
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
    parser.add_argument('--surface-distance', type=int, default=3)
    parser.add_argument('--initial-value', choices=['+', '0', 'S+'], default='+')
    parser.add_argument('--steane-syndrome-extraction-pattern', choices=['XZZ', 'ZXZ', 'ZZ'], default='ZXZ',)
    parser.add_argument('--perfect-initialization', action='store_true')
    parser.add_argument('--imperfect-initialization', action='store_true')
    parser.add_argument('--with-heulistic-post-selection', action='store_true')
    parser.add_argument('--full-post-selection', action='store_true')
    parser.add_argument('--num-epilogue-syndrome-extraction-rounds', type=int, default=10)
    parser.add_argument('--discard-rates', type=str, default='0')
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
    print('  steane-syndrome-extraction-pattern = {}'.format(args.steane_syndrome_extraction_pattern))
    print('  perfect-initialization = {}'.format(perfect_initialization))
    print('  with-heulistic-post-selection = {}'.format(args.with_heulistic_post_selection))
    print('  full-post-selection = {}'.format(args.full_post_selection))
    print('  num-epilogue-syndrome-extraction-rounds = {}'.format(args.num_epilogue_syndrome_extraction_rounds))
    print('  discard-rates = {}'.format(args.discard_rates))
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
    match args.steane_syndrome_extraction_pattern:
        case 'XZZ':
            steane_syndrome_extraction_pattern = SteaneSyndromeExtractionPattern.XZZ
        case 'ZXZ':
            steane_syndrome_extraction_pattern = SteaneSyndromeExtractionPattern.ZXZ
        case 'ZZ':
            steane_syndrome_extraction_pattern = SteaneSyndromeExtractionPattern.ZZ
        case _:
            assert False
    if not re.compile(r'^\d+(\.\d+)?(,\d+(\.\d+)?)*$').match(args.discard_rates):
        print('Error: --discard-rates must be a comma-separated list of numbers.', file=sys.stderr)
        return
    discard_rates = [float(x) for x in args.discard_rates.split(',')]

    with_heulistic_post_selection: bool = args.with_heulistic_post_selection
    full_post_selection: bool = args.full_post_selection
    num_epilogue_syndrome_extraction_rounds: int = args.num_epilogue_syndrome_extraction_rounds
    print_circuit: bool = args.print_circuit
    show_progress: bool = args.show_progress

    if not perfect_initialization and initial_value != InitialValue.SPlus:
        print('perfect-initialization=False is supported only for S+ initial value.', file=sys.stderr)
        return

    mapping = QubitMapping(30, 30)
    r = SteanePlusSurfaceCode(
        mapping, surface_distance, initial_value, steane_syndrome_extraction_pattern,
        perfect_initialization, error_probability, with_heulistic_post_selection, full_post_selection,
        num_epilogue_syndrome_extraction_rounds)
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

    detector_for_complementary_gap = r.detector_for_complementary_gap
    assert detector_for_complementary_gap is not None

    results = perform_parallel_simulation(
        primal_circuit,
        partially_noiseless_circuit,
        detector_for_complementary_gap,
        num_shots,
        parallelism,
        max_shots_per_task,
        show_progress)

    num_discarded = results.num_discarded_samples
    num_samples = len(results)
    num_valid = sum([b.num_valid_samples for b in results.buckets])
    num_wrong = sum([b.num_wrong_samples for b in results.buckets])
    bucket_index = 0
    for rate in discard_rates:
        while num_discarded < round(num_samples * rate) and bucket_index < len(results.buckets):
            bucket = results.buckets[bucket_index]
            num_valid -= bucket.num_valid_samples
            num_wrong -= bucket.num_wrong_samples
            num_discarded += bucket.num_valid_samples + bucket.num_wrong_samples
            bucket_index += 1

        print('Discard {:.1f}% samples, VALID = {}, WRONG = {}, DISCARDED = {}, bucket_index = {}'.format(
            rate * 100, num_valid, num_wrong, num_discarded, bucket_index))
        if num_valid + num_wrong == 0:
            print('WRONG / (VALID + WRONG) = nan')
        else:
            print('WRONG / (VALID + WRONG) = {:.3e}'.format(num_wrong / (num_valid + num_wrong)))
        print('(VALID + WRONG) / SHOTS = {:.3f}'.format((num_valid + num_wrong) / num_samples))
        print()


if __name__ == '__main__':
    main()
