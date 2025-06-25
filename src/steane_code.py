import stim

from util import Circuit, MultiplexingCircuit, QubitMapping


# These coordinates are hardcoded.
STEANE_6 = (2, 0)
STEANE_2 = (4, 2)
STEANE_4 = (0, 2)
STEANE_0 = (3, 3)
STEANE_1 = (1, 5)
STEANE_5 = (3, 5)
STEANE_3 = (5, 5)

# Qubit coordinates after the injection stage.
STEANE_0_INJECTION = (3, 3)
STEANE_1_INJECTION = (0, 4)
STEANE_2_INJECTION = (5, 3)
STEANE_3_INJECTION = (6, 4)
STEANE_4_INJECTION = (2, 2)
STEANE_5_INJECTION = (3, 5)
STEANE_6_INJECTION = (2, 0)

# Qubit coordinates before and after the check stage.
STEANE_0_CHECK = (3, 3)
STEANE_1_CHECK = (1, 5)
STEANE_2_CHECK = (5, 3)
STEANE_3_CHECK = (6, 4)
STEANE_4_CHECK = (2, 2)
STEANE_5_CHECK = (3, 5)
STEANE_6_CHECK = (2, 0)


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
        ancilla_a = (2, 2)
        ancilla_b = (3, 1)
        ancilla_c = (1, 1)

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
            if not self.has_performed_cx_4 and self.has_entangled_ancillae_ac:
                if self._perform_cx(STEANE_4, ancilla_c):
                    self.has_performed_cx_4 = True
                    has_progress = True
            if not self.has_performed_cx_2 and self.has_entangled_ancillae_ab:
                if self._perform_cx(STEANE_2, ancilla_b):
                    self.has_performed_cx_2 = True
                    has_progress = True
            if not self.has_performed_cx_6 and self.has_entangled_ancillae_ab:
                if self._perform_cx(STEANE_6, ancilla_b):
                    self.has_performed_cx_6 = True
                    has_progress = True
            if not self.has_performed_cx_6 and self.has_entangled_ancillae_ac:
                if self._perform_cx(STEANE_6, ancilla_c):
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


def perform_injection(circuit: Circuit | MultiplexingCircuit) -> None:
    # Reset qubits 0, 2, 5 and their peers.
    # TICK 0
    circuit.place_reset_x((5, 3))
    circuit.place_reset_x((3, 3))
    circuit.place_reset_x((3, 5))
    circuit.place_reset_z((4, 2))
    circuit.place_reset_z((4, 4))
    circuit.place_reset_z((2, 4))
    circuit.place_tick()

    # TICK 1
    circuit.place_cx((5, 3), (4, 2))
    circuit.place_cx((3, 3), (4, 4))
    circuit.place_cx((3, 5), (2, 4))
    circuit.place_tick()

    # TICK 2
    circuit.place_cx((5, 3), (4, 4))
    circuit.place_cx((3, 3), (2, 4))
    circuit.place_tick()

    # TICK 3
    circuit.place_cx((3, 3), (4, 2))
    circuit.place_cx((3, 5), (4, 4))

    circuit.place_reset_x((3, 1))
    circuit.place_reset_x((5, 5))
    circuit.place_reset_x((1, 3))
    circuit.place_tick()

    # TICK 4
    circuit.place_cx((3, 1), (4, 2))
    circuit.place_cx((5, 5), (4, 4))
    circuit.place_cx((1, 3), (2, 4))
    circuit.place_tick()

    # TICK 5
    circuit.place_cx((4, 2), (3, 1))
    circuit.place_cx((4, 4), (5, 5))
    circuit.place_cx((2, 4), (1, 3))

    circuit.place_reset_x((2, 2))
    circuit.place_reset_x((6, 4))
    circuit.place_tick()

    # TICK 6
    circuit.place_cx((2, 2), (1, 3))
    circuit.place_cx((6, 4), (5, 5))
    circuit.place_tick()

    # TICK 7
    circuit.place_cx((2, 2), (3, 1))
    circuit.place_cx((5, 5), (6, 4))
    circuit.place_tick()

    # TICK 8
    circuit.place_cx((1, 3), (2, 2))
    circuit.place_tick()

    # TICK 9
    circuit.place_cx((3, 1), (2, 2))
    circuit.place_tick()

    # TICK 10
    circuit.place_single_qubit_gate('S_DAG', (2, 2))
    circuit.place_tick()

    # TICK 11
    circuit.place_cx((3, 1), (2, 2))
    circuit.place_tick()

    # TICK 12
    circuit.place_cx((1, 3), (2, 2))

    circuit.place_reset_x((2, 0))
    circuit.place_reset_x((0, 4))
    circuit.place_tick()

    # TICK 13
    circuit.place_cx((2, 0), (3, 1))
    circuit.place_cx((0, 4), (1, 3))
    circuit.place_tick()

    # TICK 14
    circuit.place_cx((3, 1), (2, 0))
    circuit.place_cx((1, 3), (0, 4))


def perform_check(circuit: Circuit | MultiplexingCircuit) -> None:
    circuit.place_reset_x((3, 1))
    circuit.place_reset_x((4, 2))
    circuit.place_reset_x((1, 1))
    circuit.place_reset_x((4, 4))
    circuit.place_reset_x((5, 5))
    circuit.place_reset_x((2, 4))
    circuit.place_single_qubit_gate('S_DAG', STEANE_0_CHECK)
    circuit.place_single_qubit_gate('S_DAG', STEANE_1_CHECK)
    circuit.place_single_qubit_gate('S_DAG', STEANE_2_CHECK)
    circuit.place_single_qubit_gate('S_DAG', STEANE_3_CHECK)
    circuit.place_single_qubit_gate('S_DAG', STEANE_4_CHECK)
    circuit.place_single_qubit_gate('S_DAG', STEANE_5_CHECK)
    circuit.place_single_qubit_gate('S_DAG', STEANE_6_CHECK)
    circuit.place_tick()

    circuit.place_cx((1, 1), (2, 0))
    circuit.place_cx((3, 1), (2, 2))
    circuit.place_cx((4, 2), (3, 3))
    circuit.place_cx((4, 4), (5, 3))
    circuit.place_cx((5, 5), (6, 4))
    circuit.place_cx((2, 4), (1, 5))
    circuit.place_tick()

    circuit.place_cx((2, 2), (1, 1))
    circuit.place_cx((3, 3), (2, 4))
    circuit.place_cx((4, 4), (5, 5))
    circuit.place_tick()

    circuit.place_cx((3, 3), (2, 2))
    circuit.place_cx((4, 4), (3, 5))
    circuit.place_tick()

    circuit.place_cx((3, 3), (4, 4))
    circuit.place_tick()

    m = circuit.place_measurement_x((3, 3))
    circuit.place_detector([m], post_selection=True)
    circuit.place_tick()

    circuit.place_reset_x((3, 3))
    circuit.place_tick()

    circuit.place_cx((3, 3), (4, 4))
    circuit.place_tick()

    circuit.place_cx((3, 3), (2, 2))
    circuit.place_cx((4, 4), (3, 5))
    circuit.place_tick()

    circuit.place_cx((2, 2), (1, 1))
    circuit.place_cx((3, 3), (2, 4))
    circuit.place_cx((4, 4), (5, 5))
    circuit.place_tick()

    circuit.place_cx((1, 1), (2, 0))
    circuit.place_cx((3, 1), (2, 2))
    circuit.place_cx((4, 2), (3, 3))
    circuit.place_cx((4, 4), (5, 3))
    circuit.place_cx((5, 5), (6, 4))
    circuit.place_cx((2, 4), (1, 5))
    circuit.place_tick()

    circuit.place_single_qubit_gate('S_DAG', STEANE_0_CHECK)
    circuit.place_single_qubit_gate('S_DAG', STEANE_1_CHECK)
    circuit.place_single_qubit_gate('S_DAG', STEANE_2_CHECK)
    circuit.place_single_qubit_gate('S_DAG', STEANE_3_CHECK)
    circuit.place_single_qubit_gate('S_DAG', STEANE_4_CHECK)
    circuit.place_single_qubit_gate('S_DAG', STEANE_5_CHECK)
    circuit.place_single_qubit_gate('S_DAG', STEANE_6_CHECK)

    for pos in [(3, 1), (4, 2), (1, 1), (4, 4), (5, 5), (2, 4)]:
        m = circuit.place_measurement_x(pos)
        circuit.place_detector([m], post_selection=True)
