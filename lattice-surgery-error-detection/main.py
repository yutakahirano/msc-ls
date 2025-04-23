from __future__ import annotations

import argparse
import enum
import numpy as np
import pymatching
import sinter

from enum import auto
from util import QubitMapping, Circuit, MeasurementIdentifier, ObservableIdentifier
from steane_code import SteaneZ0145SyndromeMeasurement, SteaneZ0235SyndromeMeasurement, SteaneZ0246SyndromeMeasurement
from surface_code import SurfaceStabilizerPattern, SurfaceSyndromeMeasurement
from surface_code import SurfaceXSyndromeMeasurement, SurfaceZSyndromeMeasurement


class InitialValue(enum.Enum):
    Plus = auto(),
    Zero = auto(),


# Representing a merged QEC code of the Steane code and the rotated surface code.
class SteanePlusSurfaceCode:
    def __init__(self, mapping: QubitMapping, surface_distance: int, initial_value: InitialValue,
                 error_probability: float, full_post_selection: bool) -> None:
        self.mapping = mapping
        self.surface_distance = surface_distance
        self.initial_value = initial_value
        self.error_probability = error_probability
        self.full_post_selection = full_post_selection
        self.circuit = Circuit(mapping, error_probability)
        self.steane_z0145 = SteaneZ0145SyndromeMeasurement(self.circuit)
        self.steane_z0235 = SteaneZ0235SyndromeMeasurement(self.circuit)
        self.steane_z0246 = SteaneZ0246SyndromeMeasurement(self.circuit)
        self.surface_syndrome_measurements: dict[tuple[int, int], SurfaceSyndromeMeasurement] = {}
        self.lattice_surgery_syndrome_measurements: list[SurfaceSyndromeMeasurement] = []
        self.steane_x_measurements: list[MeasurementIdentifier] = []
        self.surface_x_measurements: dict[tuple[int, int], MeasurementIdentifier] = {}
        self.surface_z_measurements: dict[tuple[int, int], MeasurementIdentifier] = {}
        self.surface_code_offset_x = 1
        self.surface_code_offset_y = 7

        self._setup_syndrome_measurements()

    def _setup_syndrome_measurements(self) -> None:
        surface_distance = self.surface_distance
        surface_code_offset_x = self.surface_code_offset_x
        surface_code_offset_y = self.surface_code_offset_y

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
                    if i + j <= surface_distance // 2 and (i + j) % 2 == 1:
                        m.set_post_selection(True)

                # Lattice surgery syndrome measurements:
                if i == 0 and j == 0:
                    m = SurfaceZSyndromeMeasurement(self.circuit, (x - 1, y - 1), TWO_WEIGHT_RIGHT, False)
                    m.set_post_selection(True)
                    self.lattice_surgery_syndrome_measurements.append(m)
                elif i == 0 and j == 1:
                    m = SurfaceZSyndromeMeasurement(self.circuit, (x + 1, y - 1), FOUR_WEIGHT, False)
                    m.set_post_selection(True)
                    self.lattice_surgery_syndrome_measurements.append(m)
                elif i == 0 and j % 2 == 1:
                    m = SurfaceZSyndromeMeasurement(self.circuit, (x + 1, y - 1), TWO_WEIGHT_DOWN, False)
                    m.set_post_selection(True)
                    self.lattice_surgery_syndrome_measurements.append(m)

        if self.full_post_selection:
            for m in self.surface_syndrome_measurements.values():
                m.set_post_selection(True)

    def run(self) -> None:
        depth_for_surface_code_syndrome_measurement = 6
        surface_distance = self.surface_distance
        circuit = self.circuit

        surface_code_offset_x = self.surface_code_offset_x
        surface_code_offset_y = self.surface_code_offset_y

        for i in range(surface_distance):
            for j in range(surface_distance):
                x = surface_code_offset_x + j * 2
                y = surface_code_offset_y + i * 2
                circuit.place_reset_x((x, y))

        for i in range(depth_for_surface_code_syndrome_measurement - 1):
            for m in self.surface_syndrome_measurements.values():
                m.run()
            circuit.place_tick()
        match self.initial_value:
            case InitialValue.Plus:
                self._perform_perfect_steane_plus_initialization()
            case InitialValue.Zero:
                self._perform_perfect_steane_zero_initialization()
        for m in self.surface_syndrome_measurements.values():
            m.run()
        circuit.place_tick()

        self._perform_lattice_surgery()

        if not self.full_post_selection:
            # We perform one-round syndrome measurement at the last of `_perform_lattice_surgery()`, and that's why
            # we perform `(surface_distance - 1)` rounds syndrome measurment here.
            for i in range(depth_for_surface_code_syndrome_measurement * (surface_distance - 1)):
                for m in self.surface_syndrome_measurements.values():
                    m.run()
                circuit.place_tick()

        match self.initial_value:
            case InitialValue.Plus:
                self._perform_destructive_x_measurement()
                measurements = self.surface_x_measurements
                assert len(measurements) == surface_distance * surface_distance
                xs = [
                    measurements[
                        (surface_code_offset_x, surface_code_offset_y + i * 2)
                    ] for i in range(surface_distance)
                ] + [
                    self.steane_x_measurements[1], self.steane_x_measurements[4], self.steane_x_measurements[6]
                ]
                circuit.place_observable_include(xs, ObservableIdentifier(0))
            case InitialValue.Zero:
                self._perform_destructive_z_measurement()
                measurements = self.surface_z_measurements
                assert len(measurements) == surface_distance * surface_distance
                zs = [
                    measurements[
                        (surface_code_offset_x + j * 2, surface_code_offset_y + 2 * 0)
                    ] for j in range(surface_distance)
                ]
                for m in self.lattice_surgery_syndrome_measurements:
                    last = m.last_measurement
                    assert last is not None
                    zs.append(last)
                circuit.place_observable_include(zs, ObservableIdentifier(0))

    def run_surface_only(self) -> None:
        depth_for_surface_code_syndrome_measurement = 6
        surface_distance = self.surface_distance
        circuit = self.circuit

        surface_code_offset_x = self.surface_code_offset_x
        surface_code_offset_y = self.surface_code_offset_y

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

    def _perform_lattice_surgery(self) -> None:
        depth_for_surface_code_syndrome_measurement = 6
        lattice_surgery_distance = 3
        num_steane_syndrome_measurement_rounds = 2
        circuit = self.circuit
        surface_distance = self.surface_distance
        surface_code_offset_x = self.surface_code_offset_x
        surface_code_offset_y = self.surface_code_offset_y
        z0145 = self.steane_z0145
        z0235 = self.steane_z0235
        z0246 = self.steane_z0246

        for i in range(surface_distance):
            for j in range(surface_distance):
                x = surface_code_offset_x + j * 2
                y = surface_code_offset_y + i * 2
                if i == 0 and j % 2 == 0 and j < surface_distance - 1:
                    # This stabilizer conflicts with the lattice surgery, let's remove it.
                    del self.surface_syndrome_measurements[(x + 1, y - 1)]

                if j < surface_distance - 1 and i < surface_distance - 1:
                    if (j, i) == (1, 0) or (j, i) == (0, 1):
                        m = self.surface_syndrome_measurements[(x + 1, y + 1)]
                        m.set_post_selection(True)

        STEANE_6 = (2, 0)
        STEANE_2 = (4, 2)
        STEANE_4 = (0, 2)
        STEANE_0 = (3, 3)
        STEANE_1 = (1, 5)
        STEANE_5 = (3, 5)
        STEANE_3 = (5, 5)

        m0: MeasurementIdentifier | None = None
        m1: MeasurementIdentifier | None = None
        m2: MeasurementIdentifier | None = None
        m3: MeasurementIdentifier | None = None
        m4: MeasurementIdentifier | None = None
        m5: MeasurementIdentifier | None = None
        m6: MeasurementIdentifier | None = None

        # We want Steane Z syndrome measurements to touch qubits 1, 3, and 5 after the lattice surgery Z syndrome
        # measurements touch them.
        z0145.lock_qubit_1()
        z0145.lock_qubit_5()
        z0235.lock_qubit_3()
        z0235.lock_qubit_5()

        for i in range(depth_for_surface_code_syndrome_measurement * lattice_surgery_distance):
            # TODO: Remove these magic numbers.
            if i == 3:
                z0145.unlock_qubit_1()
                z0145.unlock_qubit_5()
                z0235.unlock_qubit_5()
            if i == 5:
                z0235.unlock_qubit_3()

            for m in self.surface_syndrome_measurements.values():
                m.run()
            for m in self.lattice_surgery_syndrome_measurements:
                m.run()

            if z0145.num_rounds() >= num_steane_syndrome_measurement_rounds - 1 and \
               z0235.num_rounds() >= num_steane_syndrome_measurement_rounds - 1 and \
               z0246.num_rounds() >= num_steane_syndrome_measurement_rounds - 1:
                num_steane_rounds = num_steane_syndrome_measurement_rounds

                if m0 is None and z0145.has_done_with_qubit_0() and \
                        z0235.has_done_with_qubit_0() and z0246.has_done_with_qubit_0():
                    m0 = self.circuit.place_measurement_x(STEANE_0)
                if m2 is None and z0145.has_done_with_qubit_2() and \
                        z0235.has_done_with_qubit_2() and z0246.has_done_with_qubit_2():
                    m2 = self.circuit.place_measurement_x(STEANE_2)
                if m4 is None and z0145.has_done_with_qubit_4() and \
                        z0235.has_done_with_qubit_4() and z0246.has_done_with_qubit_4():
                    m4 = self.circuit.place_measurement_x(STEANE_4)
                if m6 is None and z0145.has_done_with_qubit_6() and \
                        z0235.has_done_with_qubit_6() and z0246.has_done_with_qubit_6():
                    m6 = self.circuit.place_measurement_x(STEANE_6)

            # TODO: Remove these magic numbers.
            if i == 16:
                m1 = self.circuit.place_measurement_x(STEANE_1)
            if i == 16:
                m3 = self.circuit.place_measurement_x(STEANE_3)
            if i == 14:
                m5 = self.circuit.place_measurement_x(STEANE_5)

            if z0145.num_rounds() < num_steane_syndrome_measurement_rounds and z0145.run():
                z0145.advance()
            if z0235.num_rounds() < num_steane_syndrome_measurement_rounds and z0235.run():
                z0235.advance()
            if z0246.num_rounds() < num_steane_syndrome_measurement_rounds and z0246.run():
                z0246.advance()
            self.circuit.place_tick()

        # Here we implicitly assume that performing lattice surgery syndrome measurements three times takes longer than
        # performing Steane syndrome measurements twice.
        assert z0145.num_rounds() == num_steane_syndrome_measurement_rounds
        assert z0235.num_rounds() == num_steane_syndrome_measurement_rounds
        assert z0246.num_rounds() == num_steane_syndrome_measurement_rounds

        if m0 is None:
            m0 = self.circuit.place_measurement_x(STEANE_0)
        if m1 is None:
            m1 = self.circuit.place_measurement_x(STEANE_1)
        if m2 is None:
            m2 = self.circuit.place_measurement_x(STEANE_2)
        if m3 is None:
            m3 = self.circuit.place_measurement_x(STEANE_3)
        if m4 is None:
            m4 = self.circuit.place_measurement_x(STEANE_4)
        if m5 is None:
            m5 = self.circuit.place_measurement_x(STEANE_5)
        if m6 is None:
            m6 = self.circuit.place_measurement_x(STEANE_6)
        self.steane_x_measurements = [m0, m1, m2, m3, m4, m5, m6]

        circuit.place_detector([m0, m2, m4, m6], post_selection=True)
        circuit.place_detector([m0, m2, m3, m5], post_selection=True)

        # Let's recover and reconfigure some stabilizers.
        for i in range(surface_distance):
            for j in range(surface_distance):
                x = surface_code_offset_x + j * 2
                y = surface_code_offset_y + i * 2
                if i == 0 and j % 2 == 0 and j < surface_distance - 1:
                    m = SurfaceXSyndromeMeasurement(
                        self.circuit, (x + 1, y - 1), SurfaceStabilizerPattern.TWO_WEIGHT_DOWN, False)
                    self.surface_syndrome_measurements[(x + 1, y - 1)] = m
                    m.set_post_selection(True)

                if j < surface_distance - 1 and i < surface_distance - 1:
                    if (j, i) == (1, 0) or (j, i) == (0, 1):
                        m = self.surface_syndrome_measurements[(x + 1, y + 1)]
                        m.set_post_selection(True)

        for i in range(depth_for_surface_code_syndrome_measurement):
            for m in self.surface_syndrome_measurements.values():
                m.run()
            circuit.place_tick()

        # We perform six-weight X stabilizer measurements virtually.
        m = self.surface_syndrome_measurements[(surface_code_offset_x + 1, surface_code_offset_y - 1)]
        assert isinstance(m, SurfaceXSyndromeMeasurement)
        assert m.pattern == SurfaceStabilizerPattern.TWO_WEIGHT_DOWN
        last = m.last_measurement
        assert last is not None
        circuit.place_detector([m0, m1, m4, m5, last], post_selection=True)

    def _perform_destructive_x_measurement(self) -> None:
        surface_distance = self.surface_distance
        circuit = self.circuit
        surface_code_offset_x = self.surface_code_offset_x
        surface_code_offset_y = self.surface_code_offset_y
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
        surface_code_offset_x = self.surface_code_offset_x
        surface_code_offset_y = self.surface_code_offset_y
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

    # Places a circuit encoding a perfect logical |+⟩ to the Steane code.
    # The placed gates ignore the connectivity restrictions.
    def _perform_perfect_steane_plus_initialization(self) -> None:
        circuit = self.circuit
        mapping = circuit.mapping
        STEANE_6 = mapping.get_id(2, 0)
        STEANE_2 = mapping.get_id(4, 2)
        STEANE_4 = mapping.get_id(0, 2)
        STEANE_0 = mapping.get_id(3, 3)
        STEANE_1 = mapping.get_id(1, 5)
        STEANE_5 = mapping.get_id(3, 5)
        STEANE_3 = mapping.get_id(5, 5)

        circuit.circuit.append('RX', STEANE_0)
        circuit.circuit.append('RX', STEANE_1)
        circuit.circuit.append('RX', STEANE_2)
        circuit.circuit.append('RX', STEANE_3)
        circuit.circuit.append('R', STEANE_4)
        circuit.circuit.append('R', STEANE_5)
        circuit.circuit.append('R', STEANE_6)

        circuit.circuit.append('CX', [STEANE_0, STEANE_5])
        circuit.circuit.append('CX', [STEANE_0, STEANE_6])
        circuit.circuit.append('CX', [STEANE_1, STEANE_0])
        circuit.circuit.append('CX', [STEANE_3, STEANE_4])
        circuit.circuit.append('CX', [STEANE_2, STEANE_6])
        circuit.circuit.append('CX', [STEANE_1, STEANE_5])
        circuit.circuit.append('CX', [STEANE_2, STEANE_4])
        circuit.circuit.append('CX', [STEANE_3, STEANE_6])
        circuit.circuit.append('CX', [STEANE_1, STEANE_4])
        circuit.circuit.append('CX', [STEANE_2, STEANE_0])
        circuit.circuit.append('CX', [STEANE_3, STEANE_5])

    def _perform_perfect_steane_zero_initialization(self) -> None:
        circuit = self.circuit
        mapping = circuit.mapping
        STEANE_6 = mapping.get_id(2, 0)
        STEANE_2 = mapping.get_id(4, 2)
        STEANE_4 = mapping.get_id(0, 2)
        STEANE_0 = mapping.get_id(3, 3)
        STEANE_1 = mapping.get_id(1, 5)
        STEANE_5 = mapping.get_id(3, 5)
        STEANE_3 = mapping.get_id(5, 5)

        circuit.circuit.append('R', STEANE_0)
        circuit.circuit.append('RX', STEANE_1)
        circuit.circuit.append('RX', STEANE_2)
        circuit.circuit.append('RX', STEANE_3)
        circuit.circuit.append('R', STEANE_4)
        circuit.circuit.append('R', STEANE_5)
        circuit.circuit.append('R', STEANE_6)

        circuit.circuit.append('CX', [STEANE_0, STEANE_5])
        circuit.circuit.append('CX', [STEANE_0, STEANE_6])
        circuit.circuit.append('CX', [STEANE_1, STEANE_0])
        circuit.circuit.append('CX', [STEANE_3, STEANE_4])
        circuit.circuit.append('CX', [STEANE_2, STEANE_6])
        circuit.circuit.append('CX', [STEANE_1, STEANE_5])
        circuit.circuit.append('CX', [STEANE_2, STEANE_4])
        circuit.circuit.append('CX', [STEANE_3, STEANE_6])
        circuit.circuit.append('CX', [STEANE_1, STEANE_4])
        circuit.circuit.append('CX', [STEANE_2, STEANE_0])
        circuit.circuit.append('CX', [STEANE_3, STEANE_5])


def main() -> None:
    parser = argparse.ArgumentParser(description='description')
    parser.add_argument('--max-shots', type=int, default=1000)
    parser.add_argument('--max-errors', type=int, default=100)
    parser.add_argument('--error-probability', type=float, default=0)
    parser.add_argument('--parallelism', type=int, default=1)
    parser.add_argument('--surface-distance', type=int, default=3)
    parser.add_argument('--initial-value', choices=['+', '0'], default='+')
    parser.add_argument('--full-post-selection', action='store_true')

    args = parser.parse_args()

    print('  max-shots = {}'.format(args.max_shots))
    print('  max-errors = {}'.format(args.max_errors))
    print('  error-probability = {}'.format(args.error_probability))
    print('  parallelism = {}'.format(args.parallelism))
    print('  surface-distance = {}'.format(args.surface_distance))
    print('  initial-value = {}'.format(args.initial_value))
    print('  full-post-selection = {}'.format(args.full_post_selection))

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
    full_post_selection: bool = args.full_post_selection

    mapping = QubitMapping(30, 30)
    r = SteanePlusSurfaceCode(mapping, surface_distance, initial_value, error_probability, full_post_selection)
    circuit = r.circuit
    stim_circuit = circuit.circuit
    r.run()
    # r.run_surface_only()
    # print(stim_circuit)

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
    print('WRONG / VALID = {:.3e}'.format(num_wrong / num_valid))
    print('(VALID + WRONG) / SHOTS = {:.3f}'.format(
        (num_valid + num_wrong) / (num_valid + num_wrong + num_discarded)))


if __name__ == '__main__':
    main()
