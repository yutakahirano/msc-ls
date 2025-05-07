from util import Circuit, MultiplexingCircuit


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
        steane_0 = (3, 3)
        steane_1 = (1, 5)
        steane_4 = (0, 2)
        steane_5 = (3, 5)
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
                if self._perform_cx(steane_1, ancilla_b):
                    self.has_performed_cx_1 = True
                    has_progress = True
            if not self.has_performed_cx_4:
                if self._perform_cx(steane_4, ancilla_a):
                    self.has_performed_cx_4 = True
                    has_progress = True
            if not self.has_performed_cx_5 and not self.is_qubit5_locked:
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
        steane_0 = (3, 3)
        steane_2 = (4, 2)
        steane_3 = (5, 5)
        steane_5 = (3, 5)
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
                if self._perform_cx(steane_5, ancilla_b):
                    self.has_performed_cx_5 = True
                    has_progress = True
            if not self.has_performed_cx_3 and not self.is_qubit3_locked:
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
        steane_0 = (3, 3)
        steane_2 = (4, 2)
        steane_4 = (0, 2)
        steane_6 = (2, 0)
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
