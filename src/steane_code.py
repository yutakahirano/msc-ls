import stim

import surface_code

from collections.abc import Generator
from surface_code import SurfaceZSyndromeMeasurement
from typing import Literal
from util import Circuit, MultiplexingCircuit, QubitMapping, MeasurementIdentifier

# These coordinates are hardcoded.
STEANE_0 = (3, 3)
STEANE_1 = (1, 5)
STEANE_2 = (6, 2)
STEANE_3 = (5, 5)
STEANE_4 = (2, 2)
STEANE_5 = (3, 5)
STEANE_6 = (2, 0)

# Qubit coordinates after the injection stage.
STEANE_0_INJECTION = (3, 3)
STEANE_1_INJECTION = (0, 4)
STEANE_2_INJECTION = (6, 2)
STEANE_3_INJECTION = (5, 5)
STEANE_4_INJECTION = (2, 2)
STEANE_5_INJECTION = (3, 5)
STEANE_6_INJECTION = (2, 0)


class SteaneZ0145SyndromeMeasurement:
    def __init__(self, circuit: Circuit | MultiplexingCircuit) -> None:
        self.circuit: Circuit | MultiplexingCircuit = circuit
        self.has_initialized_ancillae = False
        self.has_entangled_ancillae = False
        self.has_performed_cx_0 = False
        self.has_performed_cx_1 = False
        self.has_performed_cx_4 = False
        self.has_performed_cx_5 = False
        self.has_disentangled_ancillae = False
        self.has_measured_ancillae = False
        self.is_qubit1_locked = False
        self.is_qubit5_locked = False
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

    def is_done_with_qubit_0(self) -> bool:
        return self.has_performed_cx_0

    def is_done_with_qubit_1(self) -> bool:
        return self.has_performed_cx_1

    def is_done_with_qubit_2(self) -> bool:
        return True

    def is_done_with_qubit_3(self) -> bool:
        return True

    def is_done_with_qubit_4(self) -> bool:
        return self.has_performed_cx_4

    def is_done_with_qubit_5(self) -> bool:
        return self.has_performed_cx_5

    def is_done_with_qubit_6(self) -> bool:
        return True

    def num_rounds(self) -> int:
        return self._num_rounds

    def is_complete(self) -> bool:
        return self.has_measured_ancillae

    def lock_qubit_1(self) -> None:
        self.is_qubit1_locked = True

    def unlock_qubit_1(self) -> None:
        self.is_qubit1_locked = False

    def lock_qubit_5(self) -> None:
        self.is_qubit5_locked = True

    def unlock_qubit_5(self) -> None:
        self.is_qubit5_locked = False

    # Returns true if the syndrome measurement is complete.
    # This method must not be called when `is_complete()` returns true.
    def run(self) -> bool:
        assert not self.has_measured_ancillae
        circuit = self.circuit
        ancilla_a = (1, 3)
        ancilla_b = (2, 4)

        if not self.has_initialized_ancillae:
            if circuit.is_tainted_by_position(*ancilla_a) or circuit.is_tainted_by_position(*ancilla_b):
                return False
            circuit.place_reset_x(ancilla_a)
            circuit.place_reset_z(ancilla_b)
            self.has_initialized_ancillae = True
        if not self.has_entangled_ancillae:
            if circuit.is_tainted_by_position(*ancilla_a) or circuit.is_tainted_by_position(*ancilla_b):
                return False
            circuit.place_cx(ancilla_a, ancilla_b)
            self.has_entangled_ancillae = True
        while not (self.has_performed_cx_0 and self.has_performed_cx_1 and
                   self.has_performed_cx_4 and self.has_performed_cx_5):
            has_progress = False
            if not self.has_performed_cx_1 and not self.is_qubit1_locked:
                if self._perform_cx(STEANE_1, ancilla_b):
                    self.has_performed_cx_1 = True
                    has_progress = True
            if not self.has_performed_cx_4:
                if self._perform_cx(STEANE_4, ancilla_a):
                    self.has_performed_cx_4 = True
                    has_progress = True
            if not self.has_performed_cx_5 and not self.is_qubit5_locked:
                if self._perform_cx(STEANE_5, ancilla_b):
                    self.has_performed_cx_5 = True
                    has_progress = True
            if not self.has_performed_cx_0:
                if self._perform_cx(STEANE_0, ancilla_b):
                    self.has_performed_cx_0 = True
                    has_progress = True
            if not has_progress:
                return False
        if not self.has_disentangled_ancillae:
            if circuit.is_tainted_by_position(*ancilla_a) or circuit.is_tainted_by_position(*ancilla_b):
                return False
            circuit.place_cx(ancilla_a, ancilla_b)
            self.has_disentangled_ancillae = True
        if not self.has_measured_ancillae:
            if circuit.is_tainted_by_position(*ancilla_a) or circuit.is_tainted_by_position(*ancilla_b):
                return False
            i = circuit.place_measurement_x(ancilla_a)
            circuit.place_detector([i], post_selection=True)
            i = circuit.place_measurement_z(ancilla_b)
            circuit.place_detector([i], post_selection=True)
            self.has_measured_ancillae = True
        return True

    def _perform_cx(self, control_position: tuple[int, int], target_position: tuple[int, int]) -> bool:
        circuit = self.circuit
        if circuit.is_tainted_by_position(*control_position) or circuit.is_tainted_by_position(*target_position):
            return False
        circuit.place_cx(control_position, target_position)
        return True


class SteaneZ0235SyndromeMeasurement:
    def __init__(self, circuit: Circuit | MultiplexingCircuit) -> None:
        self.circuit: Circuit | MultiplexingCircuit = circuit
        self.has_initialized_ancillae = False
        self.has_entangled_ancillae = False
        self.has_performed_cx_0 = False
        self.has_performed_cx_2 = False
        self.has_performed_cx_3 = False
        self.has_performed_cx_5 = False
        self.has_disentangled_ancillae = False
        self.has_measured_ancillae = False
        self._num_rounds = 0
        self.is_qubit3_locked = False
        self.is_qubit5_locked = False

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

    def is_done_with_qubit_0(self) -> bool:
        return self.has_performed_cx_0

    def is_done_with_qubit_1(self) -> bool:
        return True

    def is_done_with_qubit_2(self) -> bool:
        return self.has_performed_cx_2

    def is_done_with_qubit_3(self) -> bool:
        return self.has_performed_cx_3

    def is_done_with_qubit_4(self) -> bool:
        return True

    def is_done_with_qubit_5(self) -> bool:
        return self.has_performed_cx_5

    def is_done_with_qubit_6(self) -> bool:
        return True

    def num_rounds(self) -> int:
        return self._num_rounds

    def is_complete(self) -> bool:
        return self.has_measured_ancillae

    def lock_qubit_3(self) -> None:
        self.is_qubit3_locked = True

    def unlock_qubit_3(self) -> None:
        self.is_qubit3_locked = False

    def lock_qubit_5(self) -> None:
        self.is_qubit5_locked = True

    def unlock_qubit_5(self) -> None:
        self.is_qubit5_locked = False

    # Returns true if the syndrome measurement is complete.
    # This method must not be called when `is_complete()` returns true.
    def run(self) -> bool:
        assert not self.has_measured_ancillae
        circuit = self.circuit
        ancilla_a = (5, 3)
        ancilla_b = (4, 4)

        if not self.has_initialized_ancillae:
            if circuit.is_tainted_by_position(*ancilla_a) or circuit.is_tainted_by_position(*ancilla_b):
                return False
            circuit.place_reset_x(ancilla_a)
            circuit.place_reset_z(ancilla_b)
            self.has_initialized_ancillae = True
        if not self.has_entangled_ancillae:
            if circuit.is_tainted_by_position(*ancilla_a) or circuit.is_tainted_by_position(*ancilla_b):
                return False
            circuit.place_cx(ancilla_a, ancilla_b)
            self.has_entangled_ancillae = True
        while not (self.has_performed_cx_0 and self.has_performed_cx_2 and
                   self.has_performed_cx_3 and self.has_performed_cx_5):
            has_progress = False
            if not self.has_performed_cx_5 and not self.is_qubit5_locked:
                if self._perform_cx(STEANE_5, ancilla_b):
                    self.has_performed_cx_5 = True
                    has_progress = True
            if not self.has_performed_cx_3 and not self.is_qubit3_locked:
                if self._perform_cx(STEANE_3, ancilla_b):
                    self.has_performed_cx_3 = True
                    has_progress = True
            if not self.has_performed_cx_0:
                if self._perform_cx(STEANE_0, ancilla_b):
                    self.has_performed_cx_0 = True
                    has_progress = True
            if not self.has_performed_cx_2:
                if self._perform_cx(STEANE_2, ancilla_a):
                    self.has_performed_cx_2 = True
                    has_progress = True
            if not has_progress:
                return False
        if not self.has_disentangled_ancillae:
            if circuit.is_tainted_by_position(*ancilla_a) or circuit.is_tainted_by_position(*ancilla_b):
                return False
            circuit.place_cx(ancilla_a, ancilla_b)
            self.has_disentangled_ancillae = True
        if not self.has_measured_ancillae:
            if circuit.is_tainted_by_position(*ancilla_a) or circuit.is_tainted_by_position(*ancilla_b):
                return False
            i = circuit.place_measurement_x(ancilla_a)
            circuit.place_detector([i], post_selection=True)
            i = circuit.place_measurement_z(ancilla_b)
            circuit.place_detector([i], post_selection=True)
            self.has_measured_ancillae = True
        return True

    def _perform_cx(self, control_position: tuple[int, int], target_position: tuple[int, int]) -> bool:
        circuit = self.circuit
        if circuit.is_tainted_by_position(*control_position) or circuit.is_tainted_by_position(*target_position):
            return False
        circuit.place_cx(control_position, target_position)
        return True


class SteaneZ0246SyndromeMeasurement:
    def __init__(self, circuit: Circuit | MultiplexingCircuit) -> None:
        self.circuit: Circuit | MultiplexingCircuit = circuit
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

    def is_done_with_qubit_0(self) -> bool:
        return self.has_performed_cx_0

    def is_done_with_qubit_1(self) -> bool:
        return True

    def is_done_with_qubit_2(self) -> bool:
        return self.has_performed_cx_2

    def is_done_with_qubit_3(self) -> bool:
        return True

    def is_done_with_qubit_4(self) -> bool:
        return self.has_performed_cx_4

    def is_done_with_qubit_5(self) -> bool:
        return True

    def is_done_with_qubit_6(self) -> bool:
        return self.has_performed_cx_6

    def num_rounds(self) -> int:
        return self._num_rounds

    # Returns true if the syndrome measurement is complete.
    # This method must not be called when `is_complete()` returns true.
    def run(self) -> bool:
        assert not self.has_measured_ancillae
        circuit = self.circuit
        ancilla_a = (4, 2)
        ancilla_b = (3, 1)
        ancilla_c = (5, 1)

        if not self.has_initialized_ancillae:
            if circuit.is_tainted_by_position(*ancilla_a) or circuit.is_tainted_by_position(*ancilla_b) or\
               circuit.is_tainted_by_position(*ancilla_c):
                return False
            circuit.place_reset_z(ancilla_a)
            circuit.place_reset_x(ancilla_b)
            circuit.place_reset_x(ancilla_c)
            self.has_initialized_ancillae = True
        if not self.has_entangled_ancillae_ab:
            if not circuit.is_tainted_by_position(*ancilla_a) and not circuit.is_tainted_by_position(*ancilla_b):
                circuit.place_cx(ancilla_b, ancilla_a)
                self.has_entangled_ancillae_ab = True
        if not self.has_entangled_ancillae_ac:
            if not circuit.is_tainted_by_position(*ancilla_a) and not circuit.is_tainted_by_position(*ancilla_c):
                circuit.place_cx(ancilla_c, ancilla_a)
                self.has_entangled_ancillae_ac = True
        while not (self.has_performed_cx_0 and self.has_performed_cx_2 and
                   self.has_performed_cx_4 and self.has_performed_cx_6):
            has_progress = False
            if not self.has_performed_cx_0 and self.has_entangled_ancillae_ab and self.has_entangled_ancillae_ac:
                if self._perform_cx(STEANE_0, ancilla_a):
                    self.has_performed_cx_0 = True
                    has_progress = True
            if not self.has_performed_cx_4 and self.has_entangled_ancillae_ab:
                if self._perform_cx(STEANE_4, ancilla_b):
                    self.has_performed_cx_4 = True
                    has_progress = True
            if not self.has_performed_cx_2 and self.has_entangled_ancillae_ac:
                if self._perform_cx(STEANE_2, ancilla_c):
                    self.has_performed_cx_2 = True
                    has_progress = True
            if not self.has_performed_cx_6 and self.has_entangled_ancillae_ab:
                if self._perform_cx(STEANE_6, ancilla_b):
                    self.has_performed_cx_6 = True
                    has_progress = True
            if not has_progress:
                return False
        if not self.has_disentangled_ancillae_ab and not circuit.is_tainted_by_position(*ancilla_a) and \
           not circuit.is_tainted_by_position(*ancilla_b):
            circuit.place_cx(ancilla_b, ancilla_a)
            self.has_disentangled_ancillae_ab = True
        if not self.has_disentangled_ancillae_ac and not circuit.is_tainted_by_position(*ancilla_a) and \
           not circuit.is_tainted_by_position(*ancilla_c):
            circuit.place_cx(ancilla_c, ancilla_a)
            self.has_disentangled_ancillae_ac = True
        if not self.has_disentangled_ancillae_ab or not self.has_disentangled_ancillae_ac:
            return False

        if not self.has_measured_ancillae:
            if circuit.is_tainted_by_position(*ancilla_a) or circuit.is_tainted_by_position(*ancilla_b) or\
               circuit.is_tainted_by_position(*ancilla_c):
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
        if circuit.is_tainted_by_position(*control_position) or circuit.is_tainted_by_position(*target_position):
            return False
        circuit.place_cx(control_position, target_position)
        return True


def perform_perfect_steane_plus_initialization(stim_circuit: stim.Circuit, mapping: QubitMapping) -> None:
    STEANE_0_ID = mapping.get_id(*STEANE_0)
    STEANE_1_ID = mapping.get_id(*STEANE_1)
    STEANE_2_ID = mapping.get_id(*STEANE_2)
    STEANE_3_ID = mapping.get_id(*STEANE_3)
    STEANE_4_ID = mapping.get_id(*STEANE_4)
    STEANE_5_ID = mapping.get_id(*STEANE_5)
    STEANE_6_ID = mapping.get_id(*STEANE_6)

    stim_circuit.append('RX', STEANE_0_ID)
    stim_circuit.append('RX', STEANE_1_ID)
    stim_circuit.append('RX', STEANE_2_ID)
    stim_circuit.append('RX', STEANE_3_ID)
    stim_circuit.append('R', STEANE_4_ID)
    stim_circuit.append('R', STEANE_5_ID)
    stim_circuit.append('R', STEANE_6_ID)

    stim_circuit.append('CX', [STEANE_0_ID, STEANE_5_ID])
    stim_circuit.append('CX', [STEANE_0_ID, STEANE_6_ID])
    stim_circuit.append('CX', [STEANE_1_ID, STEANE_0_ID])
    stim_circuit.append('CX', [STEANE_3_ID, STEANE_4_ID])
    stim_circuit.append('CX', [STEANE_2_ID, STEANE_6_ID])
    stim_circuit.append('CX', [STEANE_1_ID, STEANE_5_ID])
    stim_circuit.append('CX', [STEANE_2_ID, STEANE_4_ID])
    stim_circuit.append('CX', [STEANE_3_ID, STEANE_6_ID])
    stim_circuit.append('CX', [STEANE_1_ID, STEANE_4_ID])
    stim_circuit.append('CX', [STEANE_2_ID, STEANE_0_ID])
    stim_circuit.append('CX', [STEANE_3_ID, STEANE_5_ID])


def perform_perfect_steane_zero_initialization(stim_circuit: stim.Circuit, mapping: QubitMapping) -> None:
    STEANE_0_ID = mapping.get_id(*STEANE_0)
    STEANE_1_ID = mapping.get_id(*STEANE_1)
    STEANE_2_ID = mapping.get_id(*STEANE_2)
    STEANE_3_ID = mapping.get_id(*STEANE_3)
    STEANE_4_ID = mapping.get_id(*STEANE_4)
    STEANE_5_ID = mapping.get_id(*STEANE_5)
    STEANE_6_ID = mapping.get_id(*STEANE_6)

    stim_circuit.append('R', STEANE_0_ID)
    stim_circuit.append('RX', STEANE_1_ID)
    stim_circuit.append('RX', STEANE_2_ID)
    stim_circuit.append('RX', STEANE_3_ID)
    stim_circuit.append('R', STEANE_4_ID)
    stim_circuit.append('R', STEANE_5_ID)
    stim_circuit.append('R', STEANE_6_ID)

    stim_circuit.append('CX', [STEANE_0_ID, STEANE_5_ID])
    stim_circuit.append('CX', [STEANE_0_ID, STEANE_6_ID])
    stim_circuit.append('CX', [STEANE_1_ID, STEANE_0_ID])
    stim_circuit.append('CX', [STEANE_3_ID, STEANE_4_ID])
    stim_circuit.append('CX', [STEANE_2_ID, STEANE_6_ID])
    stim_circuit.append('CX', [STEANE_1_ID, STEANE_5_ID])
    stim_circuit.append('CX', [STEANE_2_ID, STEANE_4_ID])
    stim_circuit.append('CX', [STEANE_3_ID, STEANE_6_ID])
    stim_circuit.append('CX', [STEANE_1_ID, STEANE_4_ID])
    stim_circuit.append('CX', [STEANE_2_ID, STEANE_0_ID])
    stim_circuit.append('CX', [STEANE_3_ID, STEANE_5_ID])


def perform_perfect_steane_s_plus_initialization(stim_circuit: stim.Circuit, mapping: QubitMapping) -> None:
    perform_perfect_steane_plus_initialization(stim_circuit, mapping)

    stim_circuit.append('S', mapping.get_id(*STEANE_0))
    stim_circuit.append('S', mapping.get_id(*STEANE_1))
    stim_circuit.append('S', mapping.get_id(*STEANE_2))
    stim_circuit.append('S', mapping.get_id(*STEANE_3))
    stim_circuit.append('S', mapping.get_id(*STEANE_4))
    stim_circuit.append('S', mapping.get_id(*STEANE_5))
    stim_circuit.append('S', mapping.get_id(*STEANE_6))


def injection_generator(circuit: Circuit | MultiplexingCircuit) -> Generator[None, None, None]:
    # TICK 0
    # Reset qubits 0, 2, 5 and their peers.
    circuit.place_reset_x((5, 3))
    circuit.place_reset_x((3, 3))
    circuit.place_reset_x((3, 5))
    circuit.place_reset_z((4, 2))
    circuit.place_reset_z((4, 4))
    circuit.place_reset_z((2, 4))
    yield

    # TICK 1
    circuit.place_cx((5, 3), (4, 2))
    circuit.place_cx((3, 3), (4, 4))
    circuit.place_cx((3, 5), (2, 4))
    yield

    # TICK 2
    circuit.place_cx((5, 3), (4, 4))
    circuit.place_cx((3, 3), (2, 4))
    circuit.place_reset_x((1, 3))
    circuit.place_reset_x((6, 2))
    yield

    # TICK 3
    circuit.place_cx((3, 3), (4, 2))
    circuit.place_cx((3, 5), (4, 4))
    circuit.place_cx((1, 3), (2, 4))
    circuit.place_cx((6, 2), (5, 3))

    circuit.place_reset_x((3, 1))
    circuit.place_reset_x((5, 5))
    circuit.place_reset_x((2, 2))
    yield

    # TICK 4
    circuit.place_cx((3, 1), (4, 2))
    circuit.place_cx((5, 5), (4, 4))
    circuit.place_cx((2, 2), (1, 3))
    circuit.place_cx((5, 3), (6, 2))
    yield

    # TICK 5
    circuit.place_cx((2, 2), (3, 1))
    circuit.place_cx((4, 4), (5, 5))
    circuit.place_cx((2, 4), (1, 3))

    circuit.place_reset_x((6, 4))
    yield

    # TICK 6
    circuit.place_cx((4, 2), (3, 1))
    circuit.place_cx((1, 3), (2, 2))
    yield

    # TICK 7
    circuit.place_cx((3, 1), (2, 2))
    yield

    # TICK 8
    circuit.place_single_qubit_gate('S_DAG', (2, 2))
    yield

    # TICK 9
    circuit.place_cx((3, 1), (2, 2))
    yield

    # TICK 10
    circuit.place_cx((1, 3), (2, 2))

    circuit.place_reset_x((2, 0))
    circuit.place_reset_x((0, 4))
    yield

    # TICK 11
    circuit.place_cx((2, 0), (3, 1))
    circuit.place_cx((0, 4), (1, 3))
    yield

    # TICK 12
    circuit.place_cx((3, 1), (2, 0))
    circuit.place_cx((1, 3), (0, 4))


def perform_injection(circuit: Circuit | MultiplexingCircuit) -> None:
    g = injection_generator(circuit)
    while True:
        try:
            next(g)
            circuit.place_tick()
        except StopIteration:
            break


def syndrome_extraction_after_injection_generator(
        circuit: Circuit | MultiplexingCircuit) -> Generator[None, None, None]:
    # For 0145
    circuit.place_reset_x((1, 3))
    circuit.place_reset_z((2, 4))
    circuit.place_reset_z((1, 5))
    # For 0235
    circuit.place_reset_x((4, 4))
    circuit.place_reset_z((5, 3))
    # For 0246
    circuit.place_reset_x((3, 1))
    circuit.place_reset_z((4, 2))
    circuit.place_reset_x((5, 1))
    yield

    # Entangling ancillae.
    # For 0145
    circuit.place_cx((0, 4), (1, 5))
    circuit.place_cx((1, 3), (2, 4))
    # For 0235
    circuit.place_cx((4, 4), (5, 3))
    # For 0246
    circuit.place_cx((3, 1), (4, 2))
    circuit.place_cx((5, 1), (6, 2))  # Moving the qubit 2 to (5, 1).
    yield

    # CX(1)
    # For 0145
    circuit.place_cx((2, 4), (3, 5))
    circuit.place_cx((1, 5), (0, 4))
    # For 0235
    circuit.place_cx((4, 4), (5, 5))
    circuit.place_cx((5, 3), (6, 2))
    # For 0246
    circuit.place_cx((3, 1), (2, 0))
    circuit.place_cx((4, 2), (3, 3))
    yield

    # CX(2)
    # For 0145
    circuit.place_cx((2, 4), (1, 5))
    # For 0235
    circuit.place_cx((4, 4), (3, 3))
    # For 0246
    circuit.place_cx((3, 1), (2, 2))
    circuit.place_cx((6, 2), (5, 1))  # Now the qubit 2 is moved to (5, 1).
    yield

    # CX(3)
    # For 0145
    circuit.place_cx((1, 3), (2, 2))
    circuit.place_cx((2, 4), (3, 3))
    # For 0235
    circuit.place_cx((4, 4), (3, 5))
    # For 0246
    circuit.place_cx((4, 2), (5, 1))
    circuit.place_reset_z((6, 2))
    yield

    # CX(4)
    # For 0145
    circuit.place_cx((2, 2), (1, 3))
    circuit.place_cx((3, 3), (2, 4))
    # For 0235
    circuit.place_cx((3, 5), (4, 4))
    # For 0246
    circuit.place_cx((5, 1), (4, 2))
    yield

    # CX(5)
    # For 0145
    circuit.place_cx((3, 5), (2, 4))
    # For 0235
    circuit.place_cx((3, 3), (4, 4))
    # For 0246
    circuit.place_cx((2, 0), (3, 1))
    circuit.place_cx((5, 1), (6, 2))  # Moving the qubit 2 back to (6, 2).
    yield

    # CX(6)
    # For 0145
    circuit.place_cx((1, 5), (2, 4))
    # For 0235
    circuit.place_cx((5, 5), (4, 4))
    circuit.place_cx((6, 2), (5, 3))
    # For 0246
    circuit.place_cx((2, 2), (3, 1))
    circuit.place_cx((3, 3), (4, 2))
    yield

    # Disentangling ancillae.
    circuit.place_cx((1, 3), (2, 4))
    circuit.place_cx((4, 4), (5, 3))
    circuit.place_cx((3, 1), (4, 2))
    circuit.place_cx((6, 2), (5, 1))  # Now the qubit 2 is moved back to (6, 2).
    yield

    # For 0145
    circuit.place_detector([circuit.place_measurement_x((1, 3))], post_selection=True)
    circuit.place_detector([circuit.place_measurement_z((2, 4))], post_selection=True)
    circuit.place_detector([circuit.place_measurement_z((0, 4))], post_selection=True)
    # For 0235
    circuit.place_detector([circuit.place_measurement_x((4, 4))], post_selection=True)
    circuit.place_detector([circuit.place_measurement_z((5, 3))], post_selection=True)
    # For 0246
    circuit.place_detector([circuit.place_measurement_x((3, 1))], post_selection=True)
    circuit.place_detector([circuit.place_measurement_z((4, 2))], post_selection=True)


def perform_syndrome_extraction_after_injection(circuit: Circuit | MultiplexingCircuit) -> None:
    g = syndrome_extraction_after_injection_generator(circuit)
    while True:
        try:
            next(g)
            circuit.place_tick()
        except StopIteration:
            break


def check_generator(circuit: Circuit | MultiplexingCircuit) -> Generator[None, None, None]:
    circuit.place_reset_x((3, 1))
    circuit.place_reset_x((4, 2))
    circuit.place_reset_x((5, 3))
    circuit.place_reset_x((4, 4))
    circuit.place_reset_x((1, 3))
    circuit.place_reset_x((2, 4))
    circuit.place_single_qubit_gate('S_DAG', STEANE_0)
    circuit.place_single_qubit_gate('S_DAG', STEANE_1)
    circuit.place_single_qubit_gate('S_DAG', STEANE_2)
    circuit.place_single_qubit_gate('S_DAG', STEANE_3)
    circuit.place_single_qubit_gate('S_DAG', STEANE_4)
    circuit.place_single_qubit_gate('S_DAG', STEANE_5)
    circuit.place_single_qubit_gate('S_DAG', STEANE_6)
    yield

    circuit.place_cx((3, 1), (2, 0))
    circuit.place_cx((4, 2), (3, 3))
    circuit.place_cx((5, 3), (6, 2))
    circuit.place_cx((4, 4), (5, 5))
    circuit.place_cx((1, 3), (2, 2))
    circuit.place_cx((2, 4), (1, 5))
    yield

    circuit.place_cx((2, 2), (3, 1))
    circuit.place_cx((4, 4), (5, 3))
    circuit.place_cx((3, 3), (2, 4))
    yield

    circuit.place_cx((3, 3), (2, 2))
    circuit.place_cx((4, 4), (3, 5))
    yield

    circuit.place_cx((3, 3), (4, 4))
    yield

    m = circuit.place_measurement_x((3, 3))
    circuit.place_detector([m], post_selection=True)
    yield

    circuit.place_reset_x((3, 3))
    yield

    circuit.place_cx((3, 3), (4, 4))
    yield

    circuit.place_cx((3, 3), (2, 2))
    circuit.place_cx((4, 4), (3, 5))
    yield

    circuit.place_cx((2, 2), (3, 1))
    circuit.place_cx((4, 4), (5, 3))
    circuit.place_cx((3, 3), (2, 4))
    yield

    circuit.place_cx((3, 1), (2, 0))
    circuit.place_cx((4, 2), (3, 3))
    circuit.place_cx((5, 3), (6, 2))
    circuit.place_cx((4, 4), (5, 5))
    circuit.place_cx((1, 3), (2, 2))
    circuit.place_cx((2, 4), (1, 5))
    yield

    circuit.place_single_qubit_gate('S', STEANE_0)
    circuit.place_single_qubit_gate('S', STEANE_1)
    circuit.place_single_qubit_gate('S', STEANE_2)
    circuit.place_single_qubit_gate('S', STEANE_3)
    circuit.place_single_qubit_gate('S', STEANE_4)
    circuit.place_single_qubit_gate('S', STEANE_5)
    circuit.place_single_qubit_gate('S', STEANE_6)

    for pos in [(3, 1), (4, 2), (5, 3), (4, 4), (1, 3), (2, 4)]:
        m = circuit.place_measurement_x(pos)
        circuit.place_detector([m], post_selection=True)
    circuit.place_detector([circuit.place_measurement_z((4, 6))], post_selection=True)


def perform_check(circuit: Circuit | MultiplexingCircuit) -> None:
    g = check_generator(circuit)
    while True:
        try:
            next(g)
            circuit.place_tick()
        except StopIteration:
            break


def perform_tomography_after_check_stage(circuit: Circuit | MultiplexingCircuit) -> None:
    mapping = circuit.mapping

    def pauli_string(
            axis: Literal['X'] | Literal['Y'] | Literal['Z'], positions: list[tuple[int, int]]) -> stim.PauliString:
        return stim.PauliString('*'.join('{}{}'.format(axis, mapping.get_id(*pos)) for pos in positions))

    stabilizer_positions = [
        [STEANE_0, STEANE_1, STEANE_4, STEANE_5],
        [STEANE_0, STEANE_2, STEANE_3, STEANE_5],
        [STEANE_0, STEANE_2, STEANE_4, STEANE_6]
    ]

    for positions in stabilizer_positions:
        m = circuit.place_mpp(pauli_string('X', positions))
        circuit.place_detector([m], post_selection=True)
        circuit.place_tick()

        m = circuit.place_mpp(pauli_string('Z', positions))
        circuit.place_detector([m], post_selection=True)
        circuit.place_tick()

    m = circuit.place_mpp(pauli_string('Y', [STEANE_1, STEANE_3, STEANE_5]))
    circuit.place_observable_include([m])


class LatticeSurgeryMeasurements:
    '''\
    A set of (lists of) measurements produced by a ZZ lattice surgery operation between the rotated surface code
    and the Steane code, followed by a destructive X measurement performed on the Steane code.
    '''
    def __init__(self) -> None:
        self._complete = False
        self._logical_x_measurements: list[MeasurementIdentifier] = []
        self._lattice_surgery_zz_measurements: list[MeasurementIdentifier] = []
        self._x_0145_measurements: list[MeasurementIdentifier] = []

    def is_complete(self) -> bool:
        return self._complete

    def logical_x_measurements(self) -> list[MeasurementIdentifier]:
        assert self.is_complete()
        return self._logical_x_measurements

    def lattice_surgery_zz_measurements(self) -> list[MeasurementIdentifier]:
        assert self.is_complete()
        return self._lattice_surgery_zz_measurements

    def x_0145_measurements(self) -> list[MeasurementIdentifier]:
        assert self.is_complete()
        return self._x_0145_measurements


def lattice_surgery_generator(
        circuit: Circuit | MultiplexingCircuit,
        surface_distance: int,
        results: LatticeSurgeryMeasurements) -> Generator[None, None, None]:
    # We temporarily move the qubit 2 to (5, 1).
    STEANE_2_ = (5, 1)

    # The top-left data qubit for the surface code.
    SURFACE_A = (1, 7)
    # Ancillae for the two-weight syndrome measurements between the Steane and surface codes.
    A_1A_L = (0, 6)
    A_1A_R = (2, 6)

    FOUR_WEIGHT = surface_code.SurfaceStabilizerPattern.FOUR_WEIGHT
    TWO_WEIGHT_DOWN = surface_code.SurfaceStabilizerPattern.TWO_WEIGHT_DOWN

    ls_surface_syndrome_measurements: list[SurfaceZSyndromeMeasurement] = [
        SurfaceZSyndromeMeasurement(circuit, (4, 6), FOUR_WEIGHT, False)
    ] + [
        SurfaceZSyndromeMeasurement(circuit, (8 + 4 * i, 6), TWO_WEIGHT_DOWN, False)
        for i in range((surface_distance - 1) // 2 - 1)
    ]
    for m in ls_surface_syndrome_measurements:
        m.set_post_selection(True)

    # Ancillae for 0145 syndrome measurements.
    A_0145_4 = (1, 3)  # adjacent to STEANE_4.
    A_0145_015 = (2, 4)  # adjacent to STEANE_0, STEANE_1, STEANE_5.
    # Ancillae for 0235 syndrome measurements.
    A_0235_035 = (4, 4)  # adjacent to STEANE_0, STEANE_3, STEANE_5.
    A_0235_2 = (5, 3)  # adjacent to STEANE_2.
    # Ancillae for 0246 syndrome measurements.
    A_0246_46 = (3, 1)  # adjacent to STEANE_4, STEANE_6.
    A_0246_02 = (4, 2)  # adjacent to STEANE_0, STEANE_2_.

    # First, we perform X => Z superdence syndrome measurements on the Steane code.
    # For 0145
    circuit.place_reset_x(A_0145_4)
    circuit.place_reset_z(A_0145_015)
    # For 0235
    circuit.place_reset_x(A_0235_035)
    circuit.place_reset_z(A_0235_2)
    # For 0246
    circuit.place_reset_x(A_0246_46)
    circuit.place_reset_z(A_0246_02)
    circuit.place_reset_x(STEANE_2_)
    yield

    # Entangling ancillae.
    # For 0145
    circuit.place_cx(A_0145_4, A_0145_015)
    # For 0235
    circuit.place_cx(A_0235_035, A_0235_2)
    # For 0246
    circuit.place_cx(A_0246_46, A_0246_02)
    circuit.place_cx(STEANE_2_, STEANE_2)  # Moving the qubit 2 to (5, 1).
    yield

    # CX(1)
    # For 0145
    circuit.place_cx(A_0145_015, STEANE_5)
    # For 0235
    circuit.place_cx(A_0235_035, STEANE_3)
    circuit.place_cx(A_0235_2, STEANE_2)
    # For 0246
    circuit.place_cx(A_0246_46, STEANE_6)
    circuit.place_cx(A_0246_02, STEANE_0)
    yield

    # CX(2)
    # For 0145
    circuit.place_cx(A_0145_015, STEANE_1)
    # For 0235
    circuit.place_cx(A_0235_035, STEANE_0)
    # For 0246
    circuit.place_cx(A_0246_46, STEANE_4)
    circuit.place_cx(STEANE_2, STEANE_2_)  # Now the qubit 2 is moved to (5, 1).
    yield

    # CX(3)
    # For 0145
    circuit.place_cx(A_0145_4, STEANE_4)
    circuit.place_cx(A_0145_015, STEANE_0)
    # For 0235
    circuit.place_cx(A_0235_035, STEANE_5)
    # For 0246
    circuit.place_cx(A_0246_02, STEANE_2_)
    circuit.place_reset_z(STEANE_2)

    # We are about to end the X syndrome measurements for the Steane code. Let's start lattice surgery Z syndrome
    # measurements.
    circuit.place_reset_z(A_1A_R)
    # Surface(0)
    for m in ls_surface_syndrome_measurements:
        m.run()
    yield

    # CX(4)
    # For 0145
    circuit.place_cx(STEANE_4, A_0145_4)
    circuit.place_cx(STEANE_0, A_0145_015)
    # For 0235
    circuit.place_cx(STEANE_3, A_0235_035)
    # For 0246
    circuit.place_cx(STEANE_2_, A_0246_02)

    circuit.place_cx(STEANE_1, A_1A_R)
    # Surface(1); STEANE_5 and the SURFACE_A are accessed by the corresponding surface syndrome measurement.
    for m in ls_surface_syndrome_measurements:
        m.run()
    yield

    # CX(5)
    # For 0145
    circuit.place_cx(STEANE_5, A_0145_015)
    # For 0235
    circuit.place_cx(STEANE_0, A_0235_035)
    # For 0246
    circuit.place_cx(STEANE_6, A_0246_46)
    circuit.place_cx(STEANE_2_, STEANE_2)  # Moving the qubit 2 back to (6, 2).

    circuit.place_cx(SURFACE_A, A_1A_R)
    # Surface(2)
    for m in ls_surface_syndrome_measurements:
        m.run()
    yield

    # CX(6)
    # For 0145
    circuit.place_cx(STEANE_1, A_0145_015)
    # For 0235
    circuit.place_cx(STEANE_5, A_0235_035)
    circuit.place_cx(STEANE_2, A_0235_2)
    # For 0246
    circuit.place_cx(STEANE_4, A_0246_46)
    circuit.place_cx(STEANE_0, A_0246_02)

    left_boundary_measurement: MeasurementIdentifier = circuit.place_measurement_z(A_1A_R)
    # Surface(3); STEANE_3 is accessed by the corresponding surface syndrome measurement.
    for m in ls_surface_syndrome_measurements:
        m.run()
    yield

    # Disentangling ancillae.
    circuit.place_cx(A_0145_4, A_0145_015)
    circuit.place_cx(A_0235_035, A_0235_2)
    circuit.place_cx(A_0246_46, A_0246_02)
    circuit.place_cx(STEANE_2, STEANE_2_)  # Now the qubit 2 is moved back to (6, 2).

    circuit.place_reset_z(A_1A_L)
    circuit.place_reset_z(A_1A_R)

    # Surface(4)
    for m in ls_surface_syndrome_measurements:
        m.run()
    yield

    # For 0145
    circuit.place_detector([circuit.place_measurement_x(A_0145_4)], post_selection=True)
    circuit.place_detector([circuit.place_measurement_z(A_0145_015)], post_selection=True)
    # For 0235
    circuit.place_detector([circuit.place_measurement_x(A_0235_035)], post_selection=True)
    circuit.place_detector([circuit.place_measurement_z(A_0235_2)], post_selection=True)
    # For 0246
    circuit.place_detector([circuit.place_measurement_x(A_0246_46)], post_selection=True)
    circuit.place_detector([circuit.place_measurement_z(A_0246_02)], post_selection=True)
    # Now we have completed the Z-X syndrome measurements on the Steane code.

    circuit.place_cx(SURFACE_A, A_1A_L)
    circuit.place_cx(STEANE_1, A_1A_R)

    # Surface (5); The last cycle of the first round.
    for m in ls_surface_syndrome_measurements:
        assert not m.is_complete()
        m.run()
        assert m.is_complete()
    yield

    # Let's start another Z syndrome measurement round on the Steane code.
    # For 0145
    circuit.place_reset_x(A_0145_4)
    circuit.place_reset_z(A_0145_015)
    # For 0235
    circuit.place_reset_x(A_0235_035)
    circuit.place_reset_z(A_0235_2)
    # For 0246
    circuit.place_reset_x(A_0246_46)
    circuit.place_reset_z(A_0246_02)
    circuit.place_reset_x(STEANE_2_)

    circuit.place_cx(STEANE_1, A_1A_L)
    circuit.place_cx(SURFACE_A, A_1A_R)

    # We are starting the second round of the lattice surgery Z syndrome measurements.
    # Surface(0)
    for m in ls_surface_syndrome_measurements:
        m.run()
    yield

    # Entangling ancillae.
    # For 0145
    circuit.place_cx(A_0145_4, A_0145_015)
    # For 0235
    circuit.place_cx(A_0235_035, A_0235_2)
    # For 0246
    circuit.place_cx(A_0246_46, A_0246_02)
    circuit.place_cx(STEANE_2_, STEANE_2)  # An X error on STEANE_2 is copied to STEANE_2_.

    # These are the second and third rounds of the left-most lattice surgery Z syndrome measurement.
    circuit.place_detector([circuit.place_measurement_z(A_1A_L), left_boundary_measurement], post_selection=True)
    circuit.place_detector([circuit.place_measurement_z(A_1A_R), left_boundary_measurement], post_selection=True)

    # Surface(1); STEANE_5 and SURFACE_A are accessed by the corresponding surface syndrome measurement.
    for m in ls_surface_syndrome_measurements:
        m.run()
    yield

    # CX(1)
    # For 0145
    circuit.place_cx(STEANE_4, A_0145_4)
    circuit.place_cx(STEANE_1, A_0145_015)
    # For 0235
    circuit.place_cx(STEANE_5, A_0235_035)
    # For 0246
    circuit.place_cx(STEANE_6, A_0246_46)
    circuit.place_cx(STEANE_0, A_0246_02)

    # Surface(2)
    for m in ls_surface_syndrome_measurements:
        m.run()
    yield

    # CX(2)
    # For 0145
    circuit.place_cx(STEANE_5, A_0145_015)
    # For 0235
    circuit.place_cx(STEANE_2, A_0235_2)
    circuit.place_cx(STEANE_0, A_0235_035)
    # For 0246
    circuit.place_cx(STEANE_4, A_0246_46)
    circuit.place_cx(STEANE_2_, A_0246_02)

    m_steane_1 = circuit.place_measurement_x(STEANE_1)
    m_steane_6 = circuit.place_measurement_x(STEANE_6)

    # Surface(3); STEANE_3 is accessed by the corresponding surface syndrome measurement.
    for m in ls_surface_syndrome_measurements:
        m.run()
    yield

    # CX(3)
    # For 0145
    circuit.place_cx(STEANE_0, A_0145_015)
    # For 0235
    circuit.place_cx(STEANE_3, A_0235_035)
    # For 0246

    m_steane_2 = circuit.place_measurement_x(STEANE_2)
    m_steane_4 = circuit.place_measurement_x(STEANE_4)

    # Surface(4)
    for m in ls_surface_syndrome_measurements:
        m.run()
    yield

    # Disentangling ancillae.
    circuit.place_cx(A_0145_4, A_0145_015)
    circuit.place_cx(A_0235_035, A_0235_2)
    circuit.place_cx(A_0246_46, A_0246_02)
    circuit.place_cx(STEANE_2, STEANE_2_)  # Now the qubit 2 is moved back to (6, 2).

    m_steane_0 = circuit.place_measurement_x(STEANE_0)

    # Surface(5); The last cycle of the second round.
    for m in ls_surface_syndrome_measurements:
        assert not m.is_complete()
        m.run()
        assert m.is_complete()

    # Now we have second syndrome measurements.
    yield

    # We are starting the third round of the lattice surgery Z syndrome measurements.
    # Surface(0)
    for m in ls_surface_syndrome_measurements:
        m.run()
    yield

    # Surface(1); STEANE_5 and the SURFACE_A are accessed by the corresponding surface syndrome measurement.
    for m in ls_surface_syndrome_measurements:
        m.run()
    yield

    m_steane_5 = circuit.place_measurement_x(STEANE_5)
    # Surface(2)
    for m in ls_surface_syndrome_measurements:
        m.run()
    yield

    # Surface(3); STEANE_3 is accessed by the corresponding surface syndrome measurement.
    for m in ls_surface_syndrome_measurements:
        m.run()
    yield

    m_steane_3 = circuit.place_measurement_x(STEANE_3)
    # Surface(4)
    for m in ls_surface_syndrome_measurements:
        m.run()
    yield

    boundary_measurements: list[MeasurementIdentifier] = [left_boundary_measurement]

    # Surface(5); The last cycle of the third round.
    for m in ls_surface_syndrome_measurements:
        assert not m.is_complete()
        m.run()
        assert m.is_complete()
        assert m.last_measurement is not None
        boundary_measurements.append(m.last_measurement)

    results._lattice_surgery_zz_measurements = boundary_measurements
    results._logical_x_measurements = [m_steane_1, m_steane_4, m_steane_6]
    results._x_0145_measurements = [m_steane_0, m_steane_1, m_steane_4, m_steane_5]
    results._complete = True
