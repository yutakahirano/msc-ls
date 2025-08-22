from __future__ import annotations

import argparse
import enum
import numpy as np
import pymatching
import sinter

import steane_code

from enum import auto
from util import QubitMapping, Circuit, MeasurementIdentifier, ObservableIdentifier
from steane_code import SteaneZ0145SyndromeMeasurement, SteaneZ0235SyndromeMeasurement, SteaneZ0246SyndromeMeasurement
from steane_code import STEANE_0, STEANE_1, STEANE_2, STEANE_3, STEANE_4, STEANE_5, STEANE_6
from surface_code import SurfaceStabilizerPattern, SurfaceSyndromeMeasurement
from surface_code import SurfaceXSyndromeMeasurement, SurfaceZSyndromeMeasurement


class InitialValue(enum.Enum):
    Plus = auto(),
    Zero = auto(),


class SteaneSyndromeExtractionPattern(enum.Enum):
    XZZ = auto(),
    ZXZ = auto(),
    ZZ = auto(),


# Representing a merged QEC code of the Steane code and the rotated surface code.
class SteanePlusSurfaceCode:
    def __init__(self, mapping: QubitMapping, surface_distance: int, initial_value: InitialValue,
                 steane_syndrome_extraction_pattern: SteaneSyndromeExtractionPattern,
                 error_probability: float, full_post_selection: bool) -> None:
        self.mapping = mapping
        self.surface_distance = surface_distance
        self.initial_value = initial_value
        self.steane_syndrome_extraction_pattern = steane_syndrome_extraction_pattern
        self.error_probability = error_probability
        self.full_post_selection = full_post_selection
        self.circuit = Circuit(mapping, error_probability)
        self.surface_syndrome_measurements: dict[tuple[int, int], SurfaceSyndromeMeasurement] = {}
        self.surface_x_measurements: dict[tuple[int, int], MeasurementIdentifier] = {}
        self.surface_z_measurements: dict[tuple[int, int], MeasurementIdentifier] = {}
        self.surface_offset_x = 1
        self.surface_offset_y = 17

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
                if i == surface_distance - 1 and j % 2 == 1 and j < surface_distance - 1:
                    m = SurfaceXSyndromeMeasurement(self.circuit, (x + 1, y + 1), TWO_WEIGHT_UP, True)
                    self.surface_syndrome_measurements[(x + 1, y + 1)] = m
                if j == 0 and i % 2 == 1 and i < surface_distance - 1:
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
                    if i + j <= surface_distance // 2 and (i + j) % 2 == 1:
                        m.set_post_selection(True)

        if self.full_post_selection:
            for m in self.surface_syndrome_measurements.values():
                m.set_post_selection(True)

    def run(self) -> None:
        SURFACE_SYNDROME_MEASUREMENT_DEPTH = 6
        surface_distance = self.surface_distance
        circuit = self.circuit

        surface_offset_x = self.surface_offset_x
        surface_offset_y = self.surface_offset_y

        for i in range(surface_distance):
            for j in range(surface_distance):
                x = surface_offset_x + j * 2
                y = surface_offset_y + i * 2
                circuit.place_reset_x((x, y))

        SURFACE_DEPTH_OFFSET: int
        match self.steane_syndrome_extraction_pattern:
            case SteaneSyndromeExtractionPattern.XZZ:
                SURFACE_DEPTH_OFFSET = 3
            case SteaneSyndromeExtractionPattern.ZXZ:
                SURFACE_DEPTH_OFFSET = 6
            case SteaneSyndromeExtractionPattern.ZZ:
                SURFACE_DEPTH_OFFSET = 6
        for i in range(SURFACE_DEPTH_OFFSET):
            for m in self.surface_syndrome_measurements.values():
                m.run()
            circuit.place_tick()

        match self.initial_value:
            case InitialValue.Plus:
                steane_code.perform_perfect_steane_plus_initialization(circuit.circuit, self.mapping)
            case InitialValue.Zero:
                steane_code.perform_perfect_steane_zero_initialization(circuit.circuit, self.mapping)
        ls_results = steane_code.LatticeSurgeryMeasurements()
        match self.steane_syndrome_extraction_pattern:
            case SteaneSyndromeExtractionPattern.XZZ:
                g = steane_code.lattice_surgery_generator_xzz(circuit, surface_distance, ls_results)
            case SteaneSyndromeExtractionPattern.ZXZ:
                g = steane_code.lattice_surgery_generator_zxz(circuit, surface_distance, True, ls_results)
            case SteaneSyndromeExtractionPattern.ZZ:
                g = steane_code.lattice_surgery_generator_zz(circuit, surface_distance, ls_results)

        tick = SURFACE_DEPTH_OFFSET
        while True:
            if tick == SURFACE_SYNDROME_MEASUREMENT_DEPTH:
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
            tick += 1

        for m in self.surface_syndrome_measurements.values():
            assert m.is_complete()

        # Let's recover and reconfigure some stabilizers.
        for j in range(surface_distance):
            x = surface_offset_x + j * 2
            y = surface_offset_y
            if j % 2 == 0 and j < surface_distance - 1:
                m = SurfaceXSyndromeMeasurement(
                    self.circuit, (x + 1, y - 1), SurfaceStabilizerPattern.TWO_WEIGHT_DOWN, False)
                self.surface_syndrome_measurements[(x + 1, y - 1)] = m
                m.set_post_selection(self.full_post_selection)
        self.surface_syndrome_measurements[(surface_offset_x + 1, surface_offset_y - 1)].last_measurement = \
            ls_results.x_ab_measurement()

        for i in range(SURFACE_SYNDROME_MEASUREMENT_DEPTH):
            for m in self.surface_syndrome_measurements.values():
                m.run()
            circuit.place_tick()

        if not self.full_post_selection:
            # We perform one-round of syndrome measurements above.
            # Hence, here we perform `(surface_distance - 1)` rounds of syndrome measurments.
            for i in range(SURFACE_SYNDROME_MEASUREMENT_DEPTH * (surface_distance - 1)):
                for m in self.surface_syndrome_measurements.values():
                    m.run()
                circuit.place_tick()

        match self.initial_value:
            case InitialValue.Plus:
                self._perform_destructive_x_measurement()
                measurements = self.surface_x_measurements
                assert len(measurements) == surface_distance * surface_distance
                xs = [
                    measurements[(surface_offset_x, surface_offset_y + i * 2)] for i in range(surface_distance)
                ] + ls_results.logical_x_measurements()
                circuit.place_observable_include(xs, ObservableIdentifier(0))
            case InitialValue.Zero:
                self._perform_destructive_z_measurement()
                measurements = self.surface_z_measurements
                assert len(measurements) == surface_distance * surface_distance
                zs = [
                    measurements[
                        (surface_offset_x + j * 2, surface_offset_y + 2 * 0)
                    ] for j in range(surface_distance)
                ] + ls_results.lattice_surgery_zz_measurements()
                circuit.place_observable_include(zs, ObservableIdentifier(0))

    def run_surface_only(self) -> None:
        depth_for_surface_code_syndrome_measurement = 6
        surface_distance = self.surface_distance
        circuit = self.circuit

        surface_code_offset_x = self.surface_offset_x
        surface_code_offset_y = self.surface_offset_y

        for i in range(surface_distance):
            for j in range(surface_distance):
                x = surface_code_offset_x + j * 2
                y = surface_code_offset_y + i * 2
                # Data qubits:
                circuit.place_reset_x((x, y))

        for _ in range(depth_for_surface_code_syndrome_measurement * surface_distance):
            for m in self.surface_syndrome_measurements.values():
                m.run()
            circuit.place_tick()

        self._perform_destructive_x_measurement()
        measurements = self.surface_x_measurements

        xs = [measurements[(surface_code_offset_x, surface_code_offset_y + i * 2)] for i in range(surface_distance)]
        circuit.place_observable_include(xs, ObservableIdentifier(0))

    def _perform_destructive_x_measurement(self) -> None:
        surface_distance = self.surface_distance
        circuit = self.circuit
        surface_code_offset_x = self.surface_offset_x
        surface_code_offset_y = self.surface_offset_y
        post_selection = self.full_post_selection

        last_measurements: dict[tuple[int, int], MeasurementIdentifier | None] = {
            pos: m.last_measurement for (pos, m) in self.surface_syndrome_measurements.items()
        }
        measurements: dict[tuple[int, int], MeasurementIdentifier] = self.surface_x_measurements
        assert len(measurements) == 0

        for i in range(surface_distance):
            for j in range(surface_distance):
                x = surface_code_offset_x + j * 2
                y = surface_code_offset_y + i * 2
                id = circuit.place_measurement_x((x, y))
                measurements[(x, y)] = id

        for i in range(surface_distance):
            for j in range(surface_distance):
                x = surface_code_offset_x + j * 2
                y = surface_code_offset_y + i * 2

                # Weight-two syndrome measurements:
                if i == 0 and j % 2 == 0 and j < surface_distance - 1:
                    last = last_measurements[(x + 1, y - 1)]
                    assert last is not None
                    circuit.place_detector([measurements[(x, y)], measurements[(x + 2, y)], last], post_selection)
                if i == surface_distance - 1 and j % 2 == 1:
                    last = last_measurements[(x + 1, y + 1)]
                    assert last is not None
                    circuit.place_detector([measurements[(x, y)], measurements[(x + 2, y)], last], post_selection)

                # Weight-four syndrome measurements:
                if i < surface_distance - 1 and j < surface_distance - 1 and (i + j) % 2 == 1:
                    last = last_measurements[(x + 1, y + 1)]
                    assert last is not None
                    circuit.place_detector([
                        measurements[(x, y)],
                        measurements[(x + 2, y)],
                        measurements[(x, y + 2)],
                        measurements[(x + 2, y + 2)],
                        last
                    ], post_selection=post_selection)

    def _perform_destructive_z_measurement(self) -> None:
        surface_distance = self.surface_distance
        circuit = self.circuit
        surface_code_offset_x = self.surface_offset_x
        surface_code_offset_y = self.surface_offset_y
        post_selection = self.full_post_selection

        last_measurements: dict[tuple[int, int], MeasurementIdentifier | None] = {
            pos: m.last_measurement for (pos, m) in self.surface_syndrome_measurements.items()
        }
        measurements: dict[tuple[int, int], MeasurementIdentifier] = self.surface_z_measurements
        assert len(measurements) == 0

        for i in range(surface_distance):
            for j in range(surface_distance):
                x = surface_code_offset_x + j * 2
                y = surface_code_offset_y + i * 2
                id = circuit.place_measurement_z((x, y))
                measurements[(x, y)] = id

        for i in range(surface_distance):
            for j in range(surface_distance):
                x = surface_code_offset_x + j * 2
                y = surface_code_offset_y + i * 2

                # Weight-two syndrome measurements:
                if j == 0 and i % 2 == 1:
                    last = last_measurements[(x - 1, y + 1)]
                    assert last is not None
                    circuit.place_detector([measurements[(x, y)], measurements[(x, y + 2)], last], post_selection)
                if j == surface_distance - 1 and i % 2 == 0 and i < surface_distance - 1:
                    last = last_measurements[(x + 1, y + 1)]
                    assert last is not None
                    circuit.place_detector([measurements[(x, y)], measurements[(x, y + 2)], last], post_selection)

                # Weight-four syndrome measurements:
                if i < surface_distance - 1 and j < surface_distance - 1 and (i + j) % 2 == 0:
                    last = last_measurements[(x + 1, y + 1)]
                    assert last is not None
                    circuit.place_detector([
                        measurements[(x, y)],
                        measurements[(x + 2, y)],
                        measurements[(x, y + 2)],
                        measurements[(x + 2, y + 2)],
                        last
                    ], post_selection)


def main() -> None:
    parser = argparse.ArgumentParser(description='description')
    parser.add_argument('--max-shots', type=int, default=1000)
    parser.add_argument('--max-errors', type=int, default=100)
    parser.add_argument('--error-probability', type=float, default=0)
    parser.add_argument('--parallelism', type=int, default=1)
    parser.add_argument('--surface-distance', type=int, default=3)
    parser.add_argument('--initial-value', choices=['+', '0'], default='+')
    parser.add_argument('--steane-syndrome-extraction-pattern', choices=['XZZ', 'ZXZ', 'ZZ'], default='ZXZ')
    parser.add_argument('--perfect-initialization', action='store_true',)
    parser.add_argument('--full-post-selection', action='store_true')
    parser.add_argument('--print-circuit', action='store_true')

    args = parser.parse_args()

    print('  max-shots = {}'.format(args.max_shots))
    print('  max-errors = {}'.format(args.max_errors))
    print('  error-probability = {}'.format(args.error_probability))
    print('  parallelism = {}'.format(args.parallelism))
    print('  surface-distance = {}'.format(args.surface_distance))
    print('  initial-value = {}'.format(args.initial_value))
    print('  full-post-selection = {}'.format(args.full_post_selection))
    print('  print-circuit = {}'.format(args.print_circuit))

    max_shots: int = args.max_shots
    max_errors: int = args.max_errors
    error_probability: float = args.error_probability
    parallelism: int = args.parallelism
    surface_distance: int = args.surface_distance
    match args.initial_value:
        case '+':
            initial_value = InitialValue.Plus
        case '0':
            initial_value = InitialValue.Zero
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
    full_post_selection: bool = args.full_post_selection
    print_circuit: bool = args.print_circuit

    mapping = QubitMapping(30, 30)
    r = SteanePlusSurfaceCode(
        mapping, surface_distance, initial_value, steane_syndrome_extraction_pattern,
        error_probability, full_post_selection)
    circuit = r.circuit
    stim_circuit = circuit.circuit
    r.run()
    # r.run_surface_only()
    if print_circuit:
        print(stim_circuit)

    use_sinter = True
    if use_sinter:
        # Note that Sinter has a bug regarding `postselection_mask`.
        # See https://github.com/quantumlib/Stim/issues/887. We use Sinter 1.13 to avoid the issue.
        postselection_mask = np.zeros(stim_circuit.num_detectors, dtype='uint8')
        for id in circuit.detectors_for_post_selection:
            postselection_mask[id.id] = 1
        postselection_mask = np.packbits(postselection_mask, bitorder='little')

        task = sinter.Task(circuit=stim_circuit, postselection_mask=postselection_mask)
        collected_stats: list[sinter.TaskStats] = sinter.collect(
            num_workers=parallelism,
            tasks=[task],
            decoders=['pymatching'],
            max_shots=max_shots,
            max_errors=max_errors,
            max_batch_size=1_000_000,
        )
        num_wrong = collected_stats[0].errors
        num_discarded = collected_stats[0].discards
        num_valid = collected_stats[0].shots - num_wrong - num_discarded
    else:
        num_shots = args.max_shots
        dem = stim_circuit.detector_error_model(decompose_errors=True)
        matcher = pymatching.Matching.from_detector_error_model(dem)
        sampler = stim_circuit.compile_detector_sampler()
        detection_events, observable_flips = sampler.sample(num_shots, separate_observables=True)

        num_valid = 0
        num_wrong = 0
        num_discarded = 0

        for shot in range(num_shots):
            syndrome = detection_events[shot]
            actual = matcher.decode(syndrome)
            prediction = observable_flips[shot]

            discard = False
            for id in circuit.detectors_for_post_selection:
                if syndrome[id.id] != 0:
                    discard = True
                    break
            if discard:
                num_discarded += 1
                continue
            if np.array_equal(actual, prediction):
                num_valid += 1
            else:
                num_wrong += 1

    print('VALID = {}, WRONG = {}, DISCARDED = {}'.format(num_valid, num_wrong, num_discarded))
    print('WRONG / (VALID + WRONG) = {:.3e}'.format(num_wrong / (num_valid + num_wrong)))
    print('(VALID + WRONG) / SHOTS = {:.3f}'.format(
        (num_valid + num_wrong) / (num_valid + num_wrong + num_discarded)))


if __name__ == '__main__':
    main()
