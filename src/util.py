from __future__ import annotations


import stim

from typing import Any


class QubitMapping:
    '''A mapping between qubit IDs and coordinates.'''
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
        '''Returns the qubit ID for the given coordinate.'''
        for id, (qx, qy) in self.mapping:
            if x == qx and y == qy:
                return id
        raise ValueError(f'Qubit ({x}, {y}) not found in mapping.')


class MeasurementIdentifier:
    '''Representing a Stim measurement ID.'''
    def __init__(self, id: int):
        self.id = id

    def __eq__(self, other: object):
        if not isinstance(other, MeasurementIdentifier):
            return False
        return self.id == other.id

    def target_rec(self, circuit: Circuit) -> Any:
        return stim.target_rec(self.id - circuit.circuit.num_measurements)


class DetectorIdentifier:
    '''Representing a Stim detector event ID.'''
    def __init__(self, id: int):
        self.id = id

    def __eq__(self, other: object):
        if not isinstance(other, DetectorIdentifier):
            return False
        return self.id == other.id


class ObservableIdentifier:
    '''Representing a Stim observable ID.'''
    def __init__(self, id: int):
        self.id = id

    def __eq__(self, other: object):
        if not isinstance(other, ObservableIdentifier):
            return False
        return self.id == other.id


class Circuit:
    '''\
    A wrapper for stim.Circuit.

    This class provides additional functionality and enforces the
    following restrictions:
      - Each qubit may participate in at most one gate per tick.
      - Two-qubit gates must respect nearest-neighbor connectivity.
      - Noise is automatically inserted when gates are placed.
      - Measurement, detector, and observable IDs are strongly typed.
    '''
    def __init__(self, mapping: QubitMapping, error_probability: float):
        self.mapping = mapping
        self.error_probability = error_probability
        self.circuit = stim.Circuit()
        for id, (x, y) in mapping.mapping:
            self.circuit.append('QUBIT_COORDS', id, (x, y))
        self.noiseless_qubits: list[int] = []
        self.tainted_qubits: list[int] = []
        self.detectors_for_post_selection: list[DetectorIdentifier] = []

    def place_tick(self) -> None:
        '''Adds idling noise, and places a TICK virtual gate.'''
        if self.error_probability > 0:
            for id, (x, y) in self.mapping.mapping:
                if id in self.tainted_qubits:
                    continue
                if id in self.noiseless_qubits:
                    continue
                self.circuit.append('DEPOLARIZE1', id, self.error_probability)
        self.tainted_qubits.clear()
        self.circuit.append('TICK')

    def is_tainted_by_id(self, id: int) -> bool:
        '''\
        Returns True if the qubit with the given ID has been involved in a gate
        during the current tick.
        '''
        return id in self.tainted_qubits

    def is_tainted_by_position(self, x: int, y: int) -> bool:
        '''\
        Returns True if the qubit with the given coordinate has been involved in
        a gate during the current tick.
        '''
        return self.mapping.get_id(x, y) in self.tainted_qubits

    def mark_qubits_as_noiseless(self, qubit_positions: list[tuple[int, int]]) -> None:
        '''\
        Marks the specified qubits as noiseless.
        '''
        self.noiseless_qubits = [self.mapping.get_id(*pos) for pos in qubit_positions]

    def place_single_qubit_gate(self, gate: str, target_position: tuple[int, int]) -> None:
        '''Places a single-qubit unitary gate `gate`.'''
        target = self.mapping.get_id(*target_position)
        if target in self.tainted_qubits:
            raise ValueError(f'Cannot place {gate} gate on tainted qubit.')
        self.circuit.append(gate, target)
        if target not in self.noiseless_qubits and self.error_probability > 0:
            self.circuit.append('DEPOLARIZE1', target, self.error_probability)
        self.tainted_qubits.append(target)

    def place_cx(self, control_position: tuple[int, int], target_position: tuple[int, int]) -> None:
        '''Places a CX gate.'''
        assert abs(control_position[0] - target_position[0]) == 1, 'CX {} {}'.format(control_position, target_position)
        assert abs(control_position[1] - target_position[1]) == 1, 'CX {} {}'.format(control_position, target_position)

        control = self.mapping.get_id(control_position[0], control_position[1])
        target = self.mapping.get_id(target_position[0], target_position[1])
        if control in self.tainted_qubits or target in self.tainted_qubits:
            raise ValueError(f'Cannot place CX gate on tainted qubits.')
        self.circuit.append('CX', (control, target))
        if self.error_probability > 0:
            if control in self.noiseless_qubits and target in self.noiseless_qubits:
                pass
            elif control in self.noiseless_qubits:
                self.circuit.append('DEPOLARIZE1', [target], self.error_probability)
            elif target in self.noiseless_qubits:
                self.circuit.append('DEPOLARIZE1', [control], self.error_probability)
            else:
                self.circuit.append('DEPOLARIZE2', [control, target], self.error_probability)
        self.tainted_qubits.append(control)
        self.tainted_qubits.append(target)

    def place_reset_z(self, target_position: tuple[int, int]) -> None:
        '''Places a reset_z gate.'''
        target = self.mapping.get_id(*target_position)
        if target in self.tainted_qubits:
            raise ValueError(f'Cannot place reset Z gate on tainted qubit.')
        self.circuit.append('R', target)
        if target not in self.noiseless_qubits and self.error_probability > 0:
            self.circuit.append('X_ERROR', target, self.error_probability)
        self.tainted_qubits.append(target)

    def place_reset_x(self, target_position: tuple[int, int]) -> None:
        '''Places a reset_x gate.'''
        target = self.mapping.get_id(*target_position)
        if target in self.tainted_qubits:
            raise ValueError(f'Cannot place reset X gate on tainted qubit.')
        self.circuit.append('RX', target)
        if target not in self.noiseless_qubits and self.error_probability > 0:
            self.circuit.append('Z_ERROR', target, self.error_probability)
        self.tainted_qubits.append(target)

    def place_measurement_z(self, target_position: tuple[int, int]) -> MeasurementIdentifier:
        '''Places a measurement_z gate, and returns the measurement ID.'''
        target = self.mapping.get_id(*target_position)
        if target in self.tainted_qubits:
            raise ValueError(f'Cannot place measurement Z gate on tainted qubit.')
        if target not in self.noiseless_qubits and self.error_probability > 0:
            self.circuit.append('X_ERROR', target, self.error_probability)

        self.circuit.append('M', target)
        self.tainted_qubits.append(target)
        return MeasurementIdentifier(self.circuit.num_measurements - 1)

    def place_measurement_x(self, target_position: tuple[int, int]) -> MeasurementIdentifier:
        '''Places a measurement_x gate, and returns the measurement ID.'''
        target = self.mapping.get_id(*target_position)
        if target in self.tainted_qubits:
            raise ValueError(f'Cannot place measurement X gate on tainted qubit.')
        if target not in self.noiseless_qubits and self.error_probability > 0:
            self.circuit.append('Z_ERROR', target, self.error_probability)
        self.circuit.append('MX', target)
        self.tainted_qubits.append(target)
        return MeasurementIdentifier(self.circuit.num_measurements - 1)

    def place_mpp(self, target: stim.PauliString) -> MeasurementIdentifier:
        '''Places a multi-qubit Pauli product measurement, and returns the measurement ID.'''
        for (i, p) in enumerate(target):
            if p == 0:
                continue
            if i in self.tainted_qubits:
                raise ValueError(f'Cannot place MPP gate on tainted qubit {i}.')
        for (i, p) in enumerate(target):
            if p == 0:
                continue
            self.tainted_qubits.append(i)
            if i in self.noiseless_qubits or self.error_probability == 0:
                continue
            match p:
                case 1:  # X
                    self.circuit.append('Z_ERROR', i, self.error_probability)
                case 2:  # Y
                    self.circuit.append('Z_ERROR', i, self.error_probability)
                case 3:  # Z
                    self.circuit.append('X_ERROR', i, self.error_probability)
                case _:
                    raise ValueError(f'Invalid Pauli value {p} for qubit {i}.')
        self.circuit.append('MPP', [target])
        return MeasurementIdentifier(self.circuit.num_measurements - 1)

    def place_detector(
            self, measurements: list[MeasurementIdentifier], post_selection: bool = False) -> DetectorIdentifier:
        '''Places a detector with the given measurements.'''
        circuit = self.circuit
        self.circuit.append('DETECTOR', [i.target_rec(self) for i in measurements])
        id = DetectorIdentifier(self.circuit.num_detectors - 1)
        if post_selection:
            self.detectors_for_post_selection.append(id)
        return id

    def place_observable_include(
            self,
            measurements: list[MeasurementIdentifier],
            id: ObservableIdentifier | None = None) -> ObservableIdentifier:
        '''Adds measurement records to a specified logical observable.'''
        id = id or ObservableIdentifier(self.circuit.num_observables)
        targets = [m.target_rec(self) for m in measurements]
        self.circuit.append('OBSERVABLE_INCLUDE', targets, id.id)
        return id


class MultiplexingCircuit:
    '''\
    A wrapper for util.Circuit.

    A MultiplexingCircuit has two Circuit instances and dispatches the same operation for them.
    This class assumes that the two circuits share the same Measurement/Detector/Observable identifiers.
    '''
    def __init__(self, circuit1: Circuit, circuit2: Circuit):
        self.circuit1 = circuit1
        self.circuit2 = circuit2
        assert circuit1.mapping is circuit2.mapping
        self.mapping = circuit1.mapping

    def is_tainted_by_id(self, id: int) -> bool:
        return self.circuit1.is_tainted_by_id(id)

    def is_tainted_by_position(self, x: int, y: int) -> bool:
        return self.circuit1.is_tainted_by_position(x, y)

    def place_tick(self) -> None:
        self.circuit1.place_tick()
        self.circuit2.place_tick()

    def place_single_qubit_gate(self, gate: str, target_position: tuple[int, int]) -> None:
        self.circuit1.place_single_qubit_gate(gate, target_position)
        self.circuit2.place_single_qubit_gate(gate, target_position)

    def place_cx(self, control_position: tuple[int, int], target_position: tuple[int, int]) -> None:
        self.circuit1.place_cx(control_position, target_position)
        self.circuit2.place_cx(control_position, target_position)

    def place_reset_z(self, target_position: tuple[int, int]) -> None:
        self.circuit1.place_reset_z(target_position)
        self.circuit2.place_reset_z(target_position)

    def place_reset_x(self, target_position: tuple[int, int]) -> None:
        self.circuit1.place_reset_x(target_position)
        self.circuit2.place_reset_x(target_position)

    def place_measurement_z(self, target_position: tuple[int, int]) -> MeasurementIdentifier:
        m1 = self.circuit1.place_measurement_z(target_position)
        m2 = self.circuit2.place_measurement_z(target_position)
        assert m1 == m2
        return m1

    def place_measurement_x(self, target_position: tuple[int, int]) -> MeasurementIdentifier:
        m1 = self.circuit1.place_measurement_x(target_position)
        m2 = self.circuit2.place_measurement_x(target_position)
        assert m1 == m2
        return m1

    def place_mpp(self, target: stim.PauliString) -> MeasurementIdentifier:
        m1 = self.circuit1.place_mpp(target)
        m2 = self.circuit2.place_mpp(target)
        assert m1 == m2
        return m1

    def place_detector(
            self, measurements: list[MeasurementIdentifier], post_selection: bool = False) -> DetectorIdentifier:
        d1 = self.circuit1.place_detector(measurements, post_selection)
        d2 = self.circuit2.place_detector(measurements, post_selection)
        assert d1 == d2
        return d1

    def place_observable_include(
            self,
            measurements: list[MeasurementIdentifier],
            id: ObservableIdentifier | None = None) -> ObservableIdentifier:
        i = self.circuit1.place_observable_include(measurements, id)
        j = self.circuit2.place_observable_include(measurements, id)
        assert i == j
        return i


class SuppressNoise:
    '''\
    Context manager to temporarily suppress noise for a Circuit.

    When used with a `with` statement, this class sets the circuit's error
    probability to zero for the duration of the block, and restores it
    afterward.

    Example:
        with SuppressNoise(circuit):
            circuit.place_reset_x(q)
            ...
    '''
    def __init__(self, circuit: Circuit | MultiplexingCircuit):
        self.circuit = circuit
        self.error_probability: float | None = None

    def __enter__(self):
        assert self.error_probability is None
        if isinstance(self.circuit, Circuit):
            self.error_probability = self.circuit.error_probability
            self.circuit.error_probability = 0
        else:
            assert isinstance(self.circuit, MultiplexingCircuit)
            assert self.circuit.circuit1.error_probability == self.circuit.circuit2.error_probability
            self.error_probability = self.circuit.circuit1.error_probability
            self.circuit.circuit1.error_probability = 0
            self.circuit.circuit2.error_probability = 0

    def __exit__(self, ex_type, ex_value, trace):
        assert self.error_probability is not None
        if isinstance(self.circuit, Circuit):
            self.circuit.error_probability = self.error_probability
        else:
            assert isinstance(self.circuit, MultiplexingCircuit)
            self.circuit.circuit1.error_probability = self.error_probability
            self.circuit.circuit2.error_probability = self.error_probability
        self.error_probability = None
