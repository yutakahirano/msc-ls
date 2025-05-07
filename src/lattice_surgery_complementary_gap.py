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
from util import QubitMapping, Circuit, MultiplexingCircuit
from util import MeasurementIdentifier, DetectorIdentifier, ObservableIdentifier, SuppressNoise
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
        self.primal_circuit = Circuit(mapping, error_probability)
        self.partially_noiseless_circuit = Circuit(mapping, error_probability)
        noiseless_qubits: list[tuple[int, int]] = []
        for y in range(0, 6):
            for x in range(0, mapping.width):
                if (x + y) % 2 == 0:
                    noiseless_qubits.append((x, y))
        self.partially_noiseless_circuit.mark_qubits_as_noiseless(noiseless_qubits)
        self.circuit = MultiplexingCircuit(self.primal_circuit, self.partially_noiseless_circuit)
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
        self.x_detector_for_complementary_gap: DetectorIdentifier | None = None
        self.z_detector_for_complementary_gap: DetectorIdentifier | None = None
        # Note that `self.circuit` does not recognize this qubit, and hence we use raw Stim APIs to access these qubits.
        # This also means that we do not need to worry about idling noise on these qubits.
        self.x_boundary_ancilla_id: int = 10000
        self.z_boundary_ancilla_id: int = 20000

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
        mapping = self.mapping

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

        STEANE_6 = (2, 0)
        STEANE_4 = (0, 2)
        STEANE_1 = (1, 5)
        for stim_circuit in [self.primal_circuit.circuit, self.partially_noiseless_circuit.circuit]:
            stim_circuit.append('RX', self.x_boundary_ancilla_id)
            stim_circuit.append('CX', [self.x_boundary_ancilla_id, mapping.get_id(*STEANE_1)])
            stim_circuit.append('CX', [self.x_boundary_ancilla_id, mapping.get_id(*STEANE_4)])
            stim_circuit.append('CX', [self.x_boundary_ancilla_id, mapping.get_id(*STEANE_6)])
            stim_circuit.append('R', self.z_boundary_ancilla_id)
            stim_circuit.append('CX', [mapping.get_id(*STEANE_1), self.z_boundary_ancilla_id])
            stim_circuit.append('CX', [mapping.get_id(*STEANE_4), self.z_boundary_ancilla_id])
            stim_circuit.append('CX', [mapping.get_id(*STEANE_6), self.z_boundary_ancilla_id])

        for m in self.surface_syndrome_measurements.values():
            m.run()
        circuit.place_tick()

        self._perform_lattice_surgery()

        if not self.full_post_selection:
            for m in self.surface_syndrome_measurements.values():
                m.set_post_selection(False)
            # We perform one-round of syndrome measurements at the end of `_perform_lattice_surgery()`, and
            # we perform two-rounds of syndrome measurements above. Hence, here we perform
            # `(surface_distance - 3)` rounds of syndrome measurments.
            for i in range(depth_for_surface_code_syndrome_measurement * (surface_distance - 1)):
                for m in self.surface_syndrome_measurements.values():
                    m.run()
                circuit.place_tick()

        steane_logical_x_measurements: list[MeasurementIdentifier] = [
            self.steane_x_measurements[1], self.steane_x_measurements[4], self.steane_x_measurements[6]
        ]

        for c in [self.primal_circuit, self.partially_noiseless_circuit]:
            stim_circuit = c.circuit
            mapping = self.mapping

            for j in range(surface_distance):
                x = surface_code_offset_x + j * 2
                y = surface_code_offset_y
                control_id = mapping.get_id(x, y)
                stim_circuit.append('CX', [control_id, self.z_boundary_ancilla_id])
            stim_circuit.append('M', self.z_boundary_ancilla_id)
            for i in range(surface_distance):
                x = surface_code_offset_x
                y = surface_code_offset_y + i * 2
                target_id = mapping.get_id(x, y)
                stim_circuit.append('CX', [self.x_boundary_ancilla_id, target_id])

            ls = [stim.target_rec(-1)]
            for m in self.lattice_surgery_syndrome_measurements:
                last = m.last_measurement
                assert last is not None
                ls.append(last.target_rec(c))
            stim_circuit.append('DETECTOR', ls)
            stim_circuit.append('MX', self.x_boundary_ancilla_id)
            stim_circuit.append('DETECTOR', [stim.target_rec(-1)] + [
                m.target_rec(c) for m in steane_logical_x_measurements
            ])
        assert self.primal_circuit.circuit.num_detectors == self.partially_noiseless_circuit.circuit.num_detectors
        self.x_detector_for_complementary_gap = DetectorIdentifier(self.primal_circuit.circuit.num_detectors - 2)
        self.z_detector_for_complementary_gap = DetectorIdentifier(self.primal_circuit.circuit.num_detectors - 1)

        match self.initial_value:
            case InitialValue.Plus:
                self._perform_perfect_destructive_x_measurement()
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
                self._perform_perfect_destructive_z_measurement()
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

        self._perform_perfect_destructive_x_measurement()
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

                if m0 is None and z0145.is_done_with_qubit_0() and \
                        z0235.is_done_with_qubit_0() and z0246.is_done_with_qubit_0():
                    m0 = self.circuit.place_measurement_x(STEANE_0)
                if m2 is None and z0145.is_done_with_qubit_2() and \
                        z0235.is_done_with_qubit_2() and z0246.is_done_with_qubit_2():
                    m2 = self.circuit.place_measurement_x(STEANE_2)
                if m4 is None and z0145.is_done_with_qubit_4() and \
                        z0235.is_done_with_qubit_4() and z0246.is_done_with_qubit_4():
                    m4 = self.circuit.place_measurement_x(STEANE_4)
                if m6 is None and z0145.is_done_with_qubit_6() and \
                        z0235.is_done_with_qubit_6() and z0246.is_done_with_qubit_6():
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

        self.partially_noiseless_circuit.mark_qubits_as_noiseless([])

        # Let's recover and reconfigure some stabilizers.
        for i in range(surface_distance):
            for j in range(surface_distance):
                x = surface_code_offset_x + j * 2
                y = surface_code_offset_y + i * 2
                if i == 0 and j % 2 == 0 and j < surface_distance - 1:
                    m = SurfaceXSyndromeMeasurement(
                        self.circuit, (x + 1, y - 1), SurfaceStabilizerPattern.TWO_WEIGHT_DOWN, False)
                    self.surface_syndrome_measurements[(x + 1, y - 1)] = m

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

    def _perform_perfect_destructive_x_measurement(self) -> None:
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

        with SuppressNoise(circuit):
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

    def _perform_perfect_destructive_z_measurement(self) -> None:
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

        with SuppressNoise(circuit):
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
        mapping = self.mapping
        STEANE_6 = mapping.get_id(2, 0)
        STEANE_2 = mapping.get_id(4, 2)
        STEANE_4 = mapping.get_id(0, 2)
        STEANE_0 = mapping.get_id(3, 3)
        STEANE_1 = mapping.get_id(1, 5)
        STEANE_5 = mapping.get_id(3, 5)
        STEANE_3 = mapping.get_id(5, 5)

        for stim_circuit in [self.primal_circuit.circuit, self.partially_noiseless_circuit.circuit]:
            stim_circuit.append('RX', STEANE_0)
            stim_circuit.append('RX', STEANE_1)
            stim_circuit.append('RX', STEANE_2)
            stim_circuit.append('RX', STEANE_3)
            stim_circuit.append('R', STEANE_4)
            stim_circuit.append('R', STEANE_5)
            stim_circuit.append('R', STEANE_6)

            stim_circuit.append('CX', [STEANE_0, STEANE_5])
            stim_circuit.append('CX', [STEANE_0, STEANE_6])
            stim_circuit.append('CX', [STEANE_1, STEANE_0])
            stim_circuit.append('CX', [STEANE_3, STEANE_4])
            stim_circuit.append('CX', [STEANE_2, STEANE_6])
            stim_circuit.append('CX', [STEANE_1, STEANE_5])
            stim_circuit.append('CX', [STEANE_2, STEANE_4])
            stim_circuit.append('CX', [STEANE_3, STEANE_6])
            stim_circuit.append('CX', [STEANE_1, STEANE_4])
            stim_circuit.append('CX', [STEANE_2, STEANE_0])
            stim_circuit.append('CX', [STEANE_3, STEANE_5])

    def _perform_perfect_steane_zero_initialization(self) -> None:
        mapping = self.mapping
        STEANE_6 = mapping.get_id(2, 0)
        STEANE_2 = mapping.get_id(4, 2)
        STEANE_4 = mapping.get_id(0, 2)
        STEANE_0 = mapping.get_id(3, 3)
        STEANE_1 = mapping.get_id(1, 5)
        STEANE_5 = mapping.get_id(3, 5)
        STEANE_3 = mapping.get_id(5, 5)

        for stim_circuit in [self.primal_circuit.circuit, self.partially_noiseless_circuit.circuit]:
            stim_circuit.append('R', STEANE_0)
            stim_circuit.append('RX', STEANE_1)
            stim_circuit.append('RX', STEANE_2)
            stim_circuit.append('RX', STEANE_3)
            stim_circuit.append('R', STEANE_4)
            stim_circuit.append('R', STEANE_5)
            stim_circuit.append('R', STEANE_6)

            stim_circuit.append('CX', [STEANE_0, STEANE_5])
            stim_circuit.append('CX', [STEANE_0, STEANE_6])
            stim_circuit.append('CX', [STEANE_1, STEANE_0])
            stim_circuit.append('CX', [STEANE_3, STEANE_4])
            stim_circuit.append('CX', [STEANE_2, STEANE_6])
            stim_circuit.append('CX', [STEANE_1, STEANE_5])
            stim_circuit.append('CX', [STEANE_2, STEANE_4])
            stim_circuit.append('CX', [STEANE_3, STEANE_6])
            stim_circuit.append('CX', [STEANE_1, STEANE_4])
            stim_circuit.append('CX', [STEANE_2, STEANE_0])
            stim_circuit.append('CX', [STEANE_3, STEANE_5])


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
        detectors_for_post_selection: list[DetectorIdentifier]) -> list[SimulationResults]:

    # We construct a decoder for `partially_noiseless_stim_circuit`, not to confuse the matching decoder with
    # non-matchable detectors. We perform post-selection for all detectors in the Steane code, so the difference
    # between the two DEMs should be small...
    dem = partially_noiseless_stim_circuit.detector_error_model(decompose_errors=True)
    matcher = pymatching.Matching.from_detector_error_model(dem)

    # However, we construct a sampler from `primal_stim_circuit` because it is *the real* circuit.
    sampler = primal_stim_circuit.compile_detector_sampler()
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
                primal_circuit.detectors_for_post_selection)

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
                                     primal_circuit.circuit,
                                     partially_noiseless_circuit.circuit,
                                     num_shots_for_this_task,
                                     x_detector_for_complementary_gap,
                                     z_detector_for_complementary_gap,
                                     gap_filters,
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
    r = SteanePlusSurfaceCode(mapping, surface_distance, initial_value, error_probability, full_post_selection)
    primal_circuit = r.primal_circuit
    partially_noiseless_circuit = r.partially_noiseless_circuit
    stim_circuit = primal_circuit.circuit
    r.run()
    if print_circuit:
        print(partially_noiseless_circuit.circuit)

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

    discard_rates = [0, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60]
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
