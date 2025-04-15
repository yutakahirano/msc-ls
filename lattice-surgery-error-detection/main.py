from __future__ import annotations

import argparse
import enum
import numpy as np
import pymatching
import sinter
import stim

from collections.abc import Callable
from enum import auto


class QubitMapping:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.mapping: list[tuple[int, tuple[int, int]]] = []

        id = 0
        for x in range(width):
            for y in range(height):
                if x % 2 == 0 and y % 2 == 0:
                    self.mapping.append((id, (x, y)))
                    id += 1

        for x in range(width):
            for y in range(height):
                if x % 2 == 1 and y % 2 == 1:
                    self.mapping.append((id, (x, y)))
                    id += 1

    def get_id(self, x: int, y: int) -> int:
        for id, (qx, qy) in self.mapping:
            if x == qx and y == qy:
                return id
        raise ValueError(f'Qubit ({x}, {y}) not found in mapping.')


class MeasurementIdentifier:
    def __init__(self, id: int):
        self.id = id

    def __eq__(self, other: object):
        if not isinstance(other, MeasurementIdentifier):
            return False
        return self.id == other.id


class DetectorIdentifier:
    def __init__(self, id: int):
        self.id = id

    def __eq__(self, other: object):
        if not isinstance(other, DetectorIdentifier):
            return False
        return self.id == other.id


class ObservableIdentifier:
    def __init__(self, id: int):
        self.id = id

    def __eq__(self, other: object):
        if not isinstance(other, ObservableIdentifier):
            return False
        return self.id == other.id


class Circuit:
    def __init__(self, mapping: QubitMapping, error_probability: float):
        self.mapping = mapping
        self.error_probability = error_probability
        self.circuit = stim.Circuit()
        for id, (x, y) in mapping.mapping:
            self.circuit.append('QUBIT_COORDS', (x, y), id)
        self.tained_qubits: list[int] = []
        self.num_z0246_syndrome_measurements = 0
        self.num_z0235_syndrome_measurements = 0
        self.num_z0145_syndrome_measurements = 0
        self.measurements: dict[int, int] = {}
        self.detectors_for_post_selection: list[DetectorIdentifier] = []

    # Adds idling noise, and places a TICK virtual gate.
    def place_tick(self) -> None:
        if self.error_probability > 0:
            for id, (x, y) in self.mapping.mapping:
                if id in self.tained_qubits:
                    continue
                self.circuit.append('DEPOLARIZE1', id, self.error_probability)
        self.tained_qubits.clear()
        self.circuit.append('TICK')

    def is_tained_by_id(self, id: int) -> bool:
        return id in self.tained_qubits

    def is_tained_by_position(self, x: int, y: int) -> bool:
        return self.mapping.get_id(x, y) in self.tained_qubits

    def place_single_qubit_gate(self, gate: str, target_position: tuple[int, int]) -> None:
        target = self.mapping.get_id(*target_position)
        if target in self.tained_qubits:
            raise ValueError(f'Cannot place {gate} gate on tained qubit.')
        self.circuit.append(gate, target)
        if self.error_probability > 0:
            self.circuit.append('DEPOLARIZE1', target, self.error_probability)
        self.tained_qubits.append(target)

    def place_reset_z(self, target_position: tuple[int, int]) -> None:
        target = self.mapping.get_id(*target_position)
        if target in self.tained_qubits:
            raise ValueError(f'Cannot place reset Z gate on tained qubit.')
        self.circuit.append('R', target)
        if self.error_probability > 0:
            self.circuit.append('X_ERROR', target, self.error_probability)
        self.tained_qubits.append(target)

    def place_reset_x(self, target_position: tuple[int, int]) -> None:
        target = self.mapping.get_id(*target_position)
        if target in self.tained_qubits:
            raise ValueError(f'Cannot place reset X gate on tained qubit.')
        self.circuit.append('RX', target)
        if self.error_probability > 0:
            self.circuit.append('Z_ERROR', target, self.error_probability)
        self.tained_qubits.append(target)

    def place_measurement_z(self, target_position: tuple[int, int]) -> MeasurementIdentifier:
        target = self.mapping.get_id(*target_position)
        if target in self.tained_qubits:
            raise ValueError(f'Cannot place measurement Z gate on tained qubit.')
        if self.error_probability > 0:
            self.circuit.append('X_ERROR', target, self.error_probability)

        m: int | None = self.measurements[target] if target in self.measurements else None
        self.circuit.append('M', target)
        self.tained_qubits.append(target)
        return MeasurementIdentifier(self.circuit.num_measurements - 1)

    def place_measurement_x(self, target_position: tuple[int, int]) -> MeasurementIdentifier:
        target = self.mapping.get_id(*target_position)
        if target in self.tained_qubits:
            raise ValueError(f'Cannot place measurement X gate on tained qubit.')
        if self.error_probability > 0:
            self.circuit.append('Z_ERROR', target, self.error_probability)
        self.circuit.append('MX', target)
        self.tained_qubits.append(target)
        return MeasurementIdentifier(self.circuit.num_measurements - 1)

    def place_detector(self, measurements: list[MeasurementIdentifier], post_selection: bool = False) -> None:
        circuit = self.circuit
        self.circuit.append('DETECTOR', [stim.target_rec(i.id - circuit.num_measurements) for i in measurements])
        if post_selection:
            self.detectors_for_post_selection.append(DetectorIdentifier(self.circuit.num_detectors - 1))

    def place_observable_include(self, measurements: list[MeasurementIdentifier], id: ObservableIdentifier) -> None:
        targets = [stim.target_rec(m.id - self.circuit.num_measurements) for m in measurements]
        self.circuit.append('OBSERVABLE_INCLUDE', targets, id.id)

    def place_cx(self, control_position: tuple[int, int], target_position: tuple[int, int]) -> None:
        assert abs(control_position[0] - target_position[0]) == 1, 'CX {} {}'.format(control_position, target_position)
        assert abs(control_position[1] - target_position[1]) == 1, 'CX {} {}'.format(control_position, target_position)

        control = self.mapping.get_id(control_position[0], control_position[1])
        target = self.mapping.get_id(target_position[0], target_position[1])
        if control in self.tained_qubits or target in self.tained_qubits:
            raise ValueError(f'Cannot place CX gate on tained qubits.')
        self.circuit.append('CX', (control, target))
        if self.error_probability > 0:
            self.circuit.append('DEPOLARIZE2', [control, target], self.error_probability)
        self.tained_qubits.append(control)
        self.tained_qubits.append(target)


class SteaneZ0145SyndromeMeasurement:
    def __init__(self, circuit: Circuit) -> None:
        self.circuit: Circuit = circuit
        self.has_initialized_ancillae = False
        self.has_entangled_ancillae = False
        self.has_performed_cx_0 = False
        self.has_performed_cx_1 = False
        self.has_performed_cx_4 = False
        self.has_performed_cx_5 = False
        self.has_disentangled_ancillae = False
        self.has_measured_ancillae = False
        self._num_rounds = 0

    def advance(self) -> None:
        assert self.is_complete()
        self._num_rounds += 1
        self.has_initialized_ancillae = False
        self.has_entangled_ancillae = False
        self.has_performed_cx_0 = False
        self.has_performed_cx_1 = False
        self.has_performed_cx_4 = False
        self.has_performed_cx_5 = False
        self.has_disentangled_ancillae = False
        self.has_measured_ancillae = False

    def num_rounds(self) -> int:
        return self._num_rounds

    def is_complete(self) -> bool:
        return self.has_measured_ancillae

    # Returns true if the syndrome measurement is complete.
    # This method must not be called when `is_complete()` returns true.
    def run(self) -> bool:
        assert not self.has_measured_ancillae
        circuit = self.circuit
        steane_0 = (3, 3)
        steane_1 = (1, 5)
        steane_4 = (0, 2)
        steane_5 = (3, 5)
        ancilla_a = (1, 3)
        ancilla_b = (2, 4)

        if not self.has_initialized_ancillae:
            if circuit.is_tained_by_position(*ancilla_a) or circuit.is_tained_by_position(*ancilla_b):
                return False
            circuit.place_reset_x(ancilla_a)
            circuit.place_reset_z(ancilla_b)
            self.has_initialized_ancillae = True
        if not self.has_entangled_ancillae:
            if circuit.is_tained_by_position(*ancilla_a) or circuit.is_tained_by_position(*ancilla_b):
                return False
            circuit.place_cx(ancilla_a, ancilla_b)
            self.has_entangled_ancillae = True
        while not (self.has_performed_cx_0 and self.has_performed_cx_1 and
                   self.has_performed_cx_4 and self.has_performed_cx_5):
            has_progress = False
            if not self.has_performed_cx_1:
                if self._perform_cx(steane_1, ancilla_b):
                    self.has_performed_cx_1 = True
                    has_progress = True
            if not self.has_performed_cx_4:
                if self._perform_cx(steane_4, ancilla_a):
                    self.has_performed_cx_4 = True
                    has_progress = True
            if not self.has_performed_cx_5:
                if self._perform_cx(steane_5, ancilla_b):
                    self.has_performed_cx_5 = True
                    has_progress = True
            if not self.has_performed_cx_0:
                if self._perform_cx(steane_0, ancilla_b):
                    self.has_performed_cx_0 = True
                    has_progress = True
            if not has_progress:
                return False
        if not self.has_disentangled_ancillae:
            if circuit.is_tained_by_position(*ancilla_a) or circuit.is_tained_by_position(*ancilla_b):
                return False
            circuit.place_cx(ancilla_a, ancilla_b)
            self.has_disentangled_ancillae = True
        if not self.has_measured_ancillae:
            if circuit.is_tained_by_position(*ancilla_a) or circuit.is_tained_by_position(*ancilla_b):
                return False
            i = circuit.place_measurement_x(ancilla_a)
            circuit.place_detector([i], post_selection=True)
            i = circuit.place_measurement_z(ancilla_b)
            circuit.place_detector([i], post_selection=True)
            self.has_measured_ancillae = True
        return True

    def _perform_cx(self, control_position: tuple[int, int], target_position: tuple[int, int]) -> bool:
        circuit = self.circuit
        if circuit.is_tained_by_position(*control_position) or circuit.is_tained_by_position(*target_position):
            return False
        circuit.place_cx(control_position, target_position)
        return True


class SteaneZ0235SyndromeMeasurement:
    def __init__(self, circuit: Circuit) -> None:
        self.circuit: Circuit = circuit
        self.has_initialized_ancillae = False
        self.has_entangled_ancillae = False
        self.has_performed_cx_0 = False
        self.has_performed_cx_2 = False
        self.has_performed_cx_3 = False
        self.has_performed_cx_5 = False
        self.has_disentangled_ancillae = False
        self.has_measured_ancillae = False
        self._num_rounds = 0

    def advance(self) -> None:
        assert self.is_complete()
        self._num_rounds += 1
        self.has_initialized_ancillae = False
        self.has_entangled_ancillae = False
        self.has_performed_cx_0 = False
        self.has_performed_cx_2 = False
        self.has_performed_cx_3 = False
        self.has_performed_cx_5 = False
        self.has_disentangled_ancillae = False
        self.has_measured_ancillae = False

    def num_rounds(self) -> int:
        return self._num_rounds

    def is_complete(self) -> bool:
        return self.has_measured_ancillae

    # Returns true if the syndrome measurement is complete.
    # This method must not be called when `is_complete()` returns true.
    def run(self) -> bool:
        assert not self.has_measured_ancillae
        circuit = self.circuit
        steane_0 = (3, 3)
        steane_2 = (4, 2)
        steane_3 = (5, 5)
        steane_5 = (3, 5)
        ancilla_a = (5, 3)
        ancilla_b = (4, 4)

        if not self.has_initialized_ancillae:
            if circuit.is_tained_by_position(*ancilla_a) or circuit.is_tained_by_position(*ancilla_b):
                return False
            circuit.place_reset_x(ancilla_a)
            circuit.place_reset_z(ancilla_b)
            self.has_initialized_ancillae = True
        if not self.has_entangled_ancillae:
            if circuit.is_tained_by_position(*ancilla_a) or circuit.is_tained_by_position(*ancilla_b):
                return False
            circuit.place_cx(ancilla_a, ancilla_b)
            self.has_entangled_ancillae = True
        while not (self.has_performed_cx_0 and self.has_performed_cx_2 and
                   self.has_performed_cx_3 and self.has_performed_cx_5):
            has_progress = False
            if not self.has_performed_cx_5:
                if self._perform_cx(steane_5, ancilla_b):
                    self.has_performed_cx_5 = True
                    has_progress = True
            if not self.has_performed_cx_3:
                if self._perform_cx(steane_3, ancilla_b):
                    self.has_performed_cx_3 = True
                    has_progress = True
            if not self.has_performed_cx_0:
                if self._perform_cx(steane_0, ancilla_b):
                    self.has_performed_cx_0 = True
                    has_progress = True
            if not self.has_performed_cx_2:
                if self._perform_cx(steane_2, ancilla_a):
                    self.has_performed_cx_2 = True
                    has_progress = True
            if not has_progress:
                return False
        if not self.has_disentangled_ancillae:
            if circuit.is_tained_by_position(*ancilla_a) or circuit.is_tained_by_position(*ancilla_b):
                return False
            circuit.place_cx(ancilla_a, ancilla_b)
            self.has_disentangled_ancillae = True
        if not self.has_measured_ancillae:
            if circuit.is_tained_by_position(*ancilla_a) or circuit.is_tained_by_position(*ancilla_b):
                return False
            i = circuit.place_measurement_x(ancilla_a)
            circuit.place_detector([i], post_selection=True)
            i = circuit.place_measurement_z(ancilla_b)
            circuit.place_detector([i], post_selection=True)
            self.has_measured_ancillae = True
        return True

    def _perform_cx(self, control_position: tuple[int, int], target_position: tuple[int, int]) -> bool:
        circuit = self.circuit
        if circuit.is_tained_by_position(*control_position) or circuit.is_tained_by_position(*target_position):
            return False
        circuit.place_cx(control_position, target_position)
        return True


class SteaneZ0246SyndromeMeasurement:
    def __init__(self, circuit: Circuit) -> None:
        self.circuit: Circuit = circuit
        self.has_initialized_ancillae = False
        self.has_entangled_ancillae_ab = False
        self.has_entangled_ancillae_ac = False
        self.has_performed_cx_0 = False
        self.has_performed_cx_2 = False
        self.has_performed_cx_4 = False
        self.has_performed_cx_6 = False
        self.has_disentangled_ancillae_ab = False
        self.has_disentangled_ancillae_ac = False
        self.has_measured_ancillae = False
        self._num_rounds = 0

    def is_complete(self) -> bool:
        return self.has_measured_ancillae

    def advance(self) -> None:
        assert self.is_complete()
        self._num_rounds += 1
        self.has_initialized_ancillae = False
        self.has_entangled_ancillae_ab = False
        self.has_entangled_ancillae_ac = False
        self.has_performed_cx_0 = False
        self.has_performed_cx_2 = False
        self.has_performed_cx_4 = False
        self.has_performed_cx_6 = False
        self.has_disentangled_ancillae_ab = False
        self.has_disentangled_ancillae_ac = False
        self.has_measured_ancillae = False

    def num_rounds(self) -> int:
        return self._num_rounds

    # Returns true if the syndrome measurement is complete.
    # This method must not be called when `is_complete()` returns true.
    def run(self) -> bool:
        assert not self.has_measured_ancillae
        circuit = self.circuit
        steane_0 = (3, 3)
        steane_2 = (4, 2)
        steane_4 = (0, 2)
        steane_6 = (2, 0)
        ancilla_a = (2, 2)
        ancilla_b = (3, 1)
        ancilla_c = (1, 1)

        if not self.has_initialized_ancillae:
            if circuit.is_tained_by_position(*ancilla_a) or circuit.is_tained_by_position(*ancilla_b) or\
               circuit.is_tained_by_position(*ancilla_c):
                return False
            circuit.place_reset_z(ancilla_a)
            circuit.place_reset_x(ancilla_b)
            circuit.place_reset_x(ancilla_c)
            self.has_initialized_ancillae = True
        if not self.has_entangled_ancillae_ab:
            if not circuit.is_tained_by_position(*ancilla_a) and not circuit.is_tained_by_position(*ancilla_b):
                circuit.place_cx(ancilla_b, ancilla_a)
                self.has_entangled_ancillae_ab = True
        if not self.has_entangled_ancillae_ac:
            if not circuit.is_tained_by_position(*ancilla_a) and not circuit.is_tained_by_position(*ancilla_c):
                circuit.place_cx(ancilla_c, ancilla_a)
                self.has_entangled_ancillae_ac = True
        while not (self.has_performed_cx_0 and self.has_performed_cx_2 and
                   self.has_performed_cx_4 and self.has_performed_cx_6):
            has_progress = False
            if not self.has_performed_cx_0 and self.has_entangled_ancillae_ab and self.has_entangled_ancillae_ac:
                if self._perform_cx(steane_0, ancilla_a):
                    self.has_performed_cx_0 = True
                    has_progress = True
            if not self.has_performed_cx_4 and self.has_entangled_ancillae_ac:
                if self._perform_cx(steane_4, ancilla_c):
                    self.has_performed_cx_4 = True
                    has_progress = True
            if not self.has_performed_cx_2 and self.has_entangled_ancillae_ab:
                if self._perform_cx(steane_2, ancilla_b):
                    self.has_performed_cx_2 = True
                    has_progress = True
            if not self.has_performed_cx_6 and self.has_entangled_ancillae_ab:
                if self._perform_cx(steane_6, ancilla_b):
                    self.has_performed_cx_6 = True
                    has_progress = True
            if not self.has_performed_cx_6 and self.has_entangled_ancillae_ac:
                if self._perform_cx(steane_6, ancilla_c):
                    self.has_performed_cx_6 = True
                    has_progress = True
            if not has_progress:
                return False
        if not self.has_disentangled_ancillae_ab and not circuit.is_tained_by_position(*ancilla_a) and \
           not circuit.is_tained_by_position(*ancilla_b):
            circuit.place_cx(ancilla_b, ancilla_a)
            self.has_disentangled_ancillae_ab = True
        if not self.has_disentangled_ancillae_ac and not circuit.is_tained_by_position(*ancilla_a) and \
           not circuit.is_tained_by_position(*ancilla_c):
            circuit.place_cx(ancilla_c, ancilla_a)
            self.has_disentangled_ancillae_ac = True
        if not self.has_disentangled_ancillae_ab or not self.has_disentangled_ancillae_ac:
            return False

        if not self.has_measured_ancillae:
            if circuit.is_tained_by_position(*ancilla_a) or circuit.is_tained_by_position(*ancilla_b) or\
               circuit.is_tained_by_position(*ancilla_c):
                return False
            i = circuit.place_measurement_z(ancilla_a)
            circuit.place_detector([i], post_selection=True)
            i = circuit.place_measurement_x(ancilla_b)
            circuit.place_detector([i], post_selection=True)
            i = circuit.place_measurement_x(ancilla_c)
            circuit.place_detector([i], post_selection=True)

            self.has_measured_ancillae = True
        return True

    def _perform_cx(self, control_position: tuple[int, int], target_position: tuple[int, int]) -> bool:
        circuit = self.circuit
        if circuit.is_tained_by_position(*control_position) or circuit.is_tained_by_position(*target_position):
            return False
        circuit.place_cx(control_position, target_position)
        return True


class SurfaceStabilizerPattern(enum.Enum):
    FOUR_WEIGHT = auto(),
    TWO_WEIGHT_UP = auto(),
    TWO_WEIGHT_DOWN = auto(),
    TWO_WEIGHT_LEFT = auto(),
    TWO_WEIGHT_RIGHT = auto(),


class SurfaceZSyndromeMeasurement:
    '''
    A Z syndrome measurement for the surface code. Unlike syndrome measurements for the Steane code,
    this class expects the consumer to call `run()` in coordination with other syndrome measurements.
    '''

    def __init__(
            self, circuit: Circuit, ancilla_position: tuple[int, int],
            pattern: SurfaceStabilizerPattern, already_satisfied: bool) -> None:
        '''`direction` represents the direction of data qubit positions relative to the ancilla qubit position.'''
        self.circuit = circuit
        self.stage = 0
        self._ancilla_position = ancilla_position
        self.pattern = pattern
        self.last_measurement: MeasurementIdentifier | None = None
        self.post_selection = False
        self.already_satisfied = already_satisfied

        (x, y) = ancilla_position
        left_top = (x - 1, y - 1)
        left_bottom = (x - 1, y + 1)
        right_top = (x + 1, y - 1)
        right_bottom = (x + 1, y + 1)

        self.actions: list[Callable[[], None]]
        match pattern:
            case SurfaceStabilizerPattern.FOUR_WEIGHT:
                self.actions = [
                    self._reset,
                    lambda: self._cx(left_top),
                    lambda: self._cx(left_bottom),
                    lambda: self._cx(right_top),
                    lambda: self._cx(right_bottom),
                    self._measure,
                ]
            case SurfaceStabilizerPattern.TWO_WEIGHT_UP:
                self.actions = [
                    self._reset,
                    lambda: self._cx(left_top),
                    lambda: None,
                    lambda: self._cx(right_top),
                    self._measure,
                    lambda: None,
                ]
            case SurfaceStabilizerPattern.TWO_WEIGHT_DOWN:
                self.actions = [
                    lambda: None,
                    self._reset,
                    lambda: self._cx(left_bottom),
                    lambda: None,
                    lambda: self._cx(right_bottom),
                    self._measure,
                ]
            case SurfaceStabilizerPattern.TWO_WEIGHT_LEFT:
                self.actions = [
                    self._reset,
                    lambda: self._cx(left_top),
                    lambda: self._cx(left_bottom),
                    self._measure,
                    lambda: None,
                    lambda: None,
                ]
            case SurfaceStabilizerPattern.TWO_WEIGHT_RIGHT:
                self.actions = [
                    lambda: None,
                    lambda: None,
                    self._reset,
                    lambda: self._cx(right_top),
                    lambda: self._cx(right_bottom),
                    self._measure,
                ]
        assert len(self.actions) == 6

    @property
    def ancilla_position(self) -> tuple[int, int]:
        return self._ancilla_position

    def set_post_selection(self, post_selection: bool) -> None:
        self.post_selection = post_selection

    def set_already_satisfied(self, already_satisfied: bool) -> None:
        self.already_satisfied = already_satisfied

    def is_complete(self) -> bool:
        return self.stage == 0

    def run(self) -> None:
        self.actions[self.stage]()
        self.stage = (self.stage + 1) % 6

    def _reset(self) -> None:
        self.circuit.place_reset_z(self._ancilla_position)

    def _cx(self, position: tuple[int, int]) -> None:
        self.circuit.place_cx(position, self._ancilla_position)

    def _measure(self) -> None:
        last = self.last_measurement
        i = self.circuit.place_measurement_z(self._ancilla_position)
        if last is None:
            if self.already_satisfied:
                self.circuit.place_detector([i], post_selection=self.post_selection)
        else:
            self.circuit.place_detector([last, i], post_selection=self.post_selection)
        self.last_measurement = i


# An X syndrome measurement for the surface code. Unlike syndrome measurements for the Steane code,
# this class expects the consumer to call `run()` in coordination with other syndrome measurements.
class SurfaceXSyndromeMeasurement:
    # `direction` represents the direction of data qubit positions relative to the ancilla qubit position.
    def __init__(
            self, circuit: Circuit, ancilla_position: tuple[int, int],
            pattern: SurfaceStabilizerPattern, already_satisfied: bool) -> None:
        self.circuit = circuit
        self.stage = 0
        self._ancilla_position = ancilla_position
        self.pattern = pattern
        self.last_measurement: MeasurementIdentifier | None = None
        self.post_selection = False
        self.already_satisfied = already_satisfied

        (x, y) = ancilla_position
        left_top = (x - 1, y - 1)
        left_bottom = (x - 1, y + 1)
        right_top = (x + 1, y - 1)
        right_bottom = (x + 1, y + 1)

        self.actions: list[Callable[[], None]]
        match pattern:
            case SurfaceStabilizerPattern.FOUR_WEIGHT:
                self.actions = [
                    self._reset,
                    lambda: self._cx(left_top),
                    lambda: self._cx(right_top),
                    lambda: self._cx(left_bottom),
                    lambda: self._cx(right_bottom),
                    self._measure,
                ]
            case SurfaceStabilizerPattern.TWO_WEIGHT_UP:
                self.actions = [
                    self._reset,
                    lambda: self._cx(left_top),
                    lambda: self._cx(right_top),
                    self._measure,
                    lambda: None,
                    lambda: None,
                ]
            case SurfaceStabilizerPattern.TWO_WEIGHT_DOWN:
                self.actions = [
                    lambda: None,
                    lambda: None,
                    self._reset,
                    lambda: self._cx(left_bottom),
                    lambda: self._cx(right_bottom),
                    self._measure,
                ]
            case SurfaceStabilizerPattern.TWO_WEIGHT_LEFT:
                self.actions = [
                    self._reset,
                    lambda: self._cx(left_top),
                    lambda: None,
                    lambda: self._cx(left_bottom),
                    self._measure,
                    lambda: None,
                ]
            case SurfaceStabilizerPattern.TWO_WEIGHT_RIGHT:
                self.actions = [
                    lambda: None,
                    self._reset,
                    lambda: self._cx(right_top),
                    lambda: None,
                    lambda: self._cx(right_bottom),
                    self._measure,
                ]
        assert len(self.actions) == 6

    @property
    def ancilla_position(self) -> tuple[int, int]:
        return self._ancilla_position

    def set_post_selection(self, post_selection: bool) -> None:
        self.post_selection = post_selection

    def set_already_satisfied(self, already_satisfied: bool) -> None:
        self.already_satisfied = already_satisfied

    def is_complete(self) -> bool:
        return self.stage == 0

    def run(self) -> None:
        self.actions[self.stage]()
        self.stage = (self.stage + 1) % 6

    def _reset(self) -> None:
        self.circuit.place_reset_x(self._ancilla_position)

    def _cx(self, position: tuple[int, int]) -> None:
        self.circuit.place_cx(self._ancilla_position, position)

    def _measure(self) -> None:
        last = self.last_measurement
        i = self.circuit.place_measurement_x(self._ancilla_position)
        if last is None:
            if self.already_satisfied:
                self.circuit.place_detector([i], post_selection=self.post_selection)
        else:
            self.circuit.place_detector([last, i], post_selection=self.post_selection)
        self.last_measurement = i


SurfaceSyndromeMeasurement = SurfaceXSyndromeMeasurement | SurfaceZSyndromeMeasurement


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

        for i in range(depth_for_surface_code_syndrome_measurement * lattice_surgery_distance):
            for m in self.surface_syndrome_measurements.values():
                m.run()
            for m in self.lattice_surgery_syndrome_measurements:
                m.run()

            if self.steane_z0145.num_rounds() < num_steane_syndrome_measurement_rounds and self.steane_z0145.run():
                self.steane_z0145.advance()
            if self.steane_z0235.num_rounds() < num_steane_syndrome_measurement_rounds and self.steane_z0235.run():
                self.steane_z0235.advance()
            if self.steane_z0246.num_rounds() < num_steane_syndrome_measurement_rounds and self.steane_z0246.run():
                self.steane_z0246.advance()

            self.circuit.place_tick()

        # Here we implicitly assume that performing lattice surgery syndrome measurements three times takes longer than
        # performing Steane syndrome measurements twice.
        assert self.steane_z0145.num_rounds() == num_steane_syndrome_measurement_rounds
        assert self.steane_z0235.num_rounds() == num_steane_syndrome_measurement_rounds
        assert self.steane_z0246.num_rounds() == num_steane_syndrome_measurement_rounds

        # TODO: We should perform part of these measurements earlier to reduce the effect of idling noise.
        m0 = self.circuit.place_measurement_x(STEANE_0)
        m1 = self.circuit.place_measurement_x(STEANE_1)
        m2 = self.circuit.place_measurement_x(STEANE_2)
        m3 = self.circuit.place_measurement_x(STEANE_3)
        m4 = self.circuit.place_measurement_x(STEANE_4)
        m5 = self.circuit.place_measurement_x(STEANE_5)
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
