import stim
import unittest
import textwrap


from util import *


class MappingTest(unittest.TestCase):
    def test_get_id(self):
        mapping = QubitMapping(20, 20)

        self.assertEqual(mapping.get_id(0, 0), 0)
        self.assertEqual(mapping.get_id(0, 2), 1)

        self.assertEqual(mapping.get_id(1, 1), 100)
        self.assertEqual(mapping.get_id(3, 1), 110)


class CircuitTest(unittest.TestCase):
    def test_place_single_qubit_gate(self):
        mapping = QubitMapping(20, 20)
        circuit = Circuit(mapping, 0.01)
        prologue = str(circuit.circuit)

        circuit.place_single_qubit_gate('H', (0, 2))
        expectation = prologue + textwrap.dedent('''
        H 1
        DEPOLARIZE1(0.01) 1''')
        self.assertEqual(str(circuit.circuit), expectation)

    def test_place_cx(self):
        mapping = QubitMapping(20, 20)
        circuit = Circuit(mapping, 0.01)
        prologue = str(circuit.circuit)

        circuit.place_cx((0, 2), (1, 1))
        expectation = prologue + textwrap.dedent('''
        CX 1 100
        DEPOLARIZE2(0.01) 1 100''')
        self.assertEqual(str(circuit.circuit), expectation)

    def test_place_cx_violating_nn_connectivity(self):
        mapping = QubitMapping(20, 20)
        circuit = Circuit(mapping, 0.01)

        self.assertRaises(
            AssertionError,
            lambda: circuit.place_cx((0, 2), (1, 2)))
        self.assertRaises(
            AssertionError,
            lambda: circuit.place_cx((0, 2), (0, 1)))
        self.assertRaises(
            AssertionError,
            lambda: circuit.place_cx((0, 2), (0, 4)))
        self.assertRaises(
            AssertionError,
            lambda: circuit.place_cx((0, 2), (1, 4)))

    def test_reset_z(self):
        mapping = QubitMapping(20, 20)
        circuit = Circuit(mapping, 0.01)
        prologue = str(circuit.circuit)

        circuit.place_reset_z((1, 1))
        expectation = prologue + textwrap.dedent('''
        R 100
        X_ERROR(0.01) 100''')
        self.assertEqual(str(circuit.circuit), expectation)

    def test_reset_x(self):
        mapping = QubitMapping(20, 20)
        circuit = Circuit(mapping, 0.01)
        prologue = str(circuit.circuit)

        circuit.place_reset_x((1, 1))
        expectation = prologue + textwrap.dedent('''
        RX 100
        Z_ERROR(0.01) 100''')
        self.assertEqual(str(circuit.circuit), expectation)

    def test_place_measurement_z(self):
        mapping = QubitMapping(20, 20)
        circuit = Circuit(mapping, 0.01)
        prologue = str(circuit.circuit)

        i = circuit.place_measurement_z((1, 1))
        expectation = prologue + textwrap.dedent('''
        X_ERROR(0.01) 100
        M 100''')
        self.assertEqual(str(circuit.circuit), expectation)
        self.assertEqual(i.id, 0)

    def test_place_measurement_x(self):
        mapping = QubitMapping(20, 20)
        circuit = Circuit(mapping, 0.01)
        prologue = str(circuit.circuit)

        i = circuit.place_measurement_x((1, 1))
        expectation = prologue + textwrap.dedent('''
        Z_ERROR(0.01) 100
        MX 100''')
        self.assertEqual(str(circuit.circuit), expectation)
        self.assertEqual(i.id, 0)

    def test_place_tick_and_tained(self):
        mapping = QubitMapping(4, 4)
        circuit = Circuit(mapping, 0.01)
        prologue = str(circuit.circuit)

        self.assertEqual(mapping.mapping, [
            (0, (0, 0)), (1, (0, 2)), (2, (2, 0)), (3, (2, 2)),
            (4, (1, 1)), (5, (1, 3)), (6, (3, 1)), (7, (3, 3))
        ])

        circuit.place_reset_z((0, 0))
        circuit.place_reset_x((0, 2))

        self.assertTrue(circuit.is_tainted_by_position(0, 0))
        self.assertTrue(circuit.is_tainted_by_position(0, 2))
        self.assertFalse(circuit.is_tainted_by_position(2, 0))
        self.assertFalse(circuit.is_tainted_by_position(2, 2))
        self.assertFalse(circuit.is_tainted_by_position(1, 1))
        self.assertFalse(circuit.is_tainted_by_position(1, 3))
        self.assertFalse(circuit.is_tainted_by_position(3, 1))
        self.assertFalse(circuit.is_tainted_by_position(3, 3))

        self.assertTrue(circuit.is_tainted_by_id(0))
        self.assertTrue(circuit.is_tainted_by_id(1))
        self.assertFalse(circuit.is_tainted_by_id(2))
        self.assertFalse(circuit.is_tainted_by_id(3))
        self.assertFalse(circuit.is_tainted_by_id(4))
        self.assertFalse(circuit.is_tainted_by_id(5))
        self.assertFalse(circuit.is_tainted_by_id(6))
        self.assertFalse(circuit.is_tainted_by_id(7))

        circuit.place_tick()
        expectation = prologue + textwrap.dedent('''
        R 0
        X_ERROR(0.01) 0
        RX 1
        Z_ERROR(0.01) 1
        DEPOLARIZE1(0.01) 2 3 4 5 6 7
        TICK''')
        self.assertEqual(str(circuit.circuit), expectation)

        self.assertFalse(circuit.is_tainted_by_id(0))
        self.assertFalse(circuit.is_tainted_by_id(1))
        self.assertFalse(circuit.is_tainted_by_id(2))
        self.assertFalse(circuit.is_tainted_by_id(3))
        self.assertFalse(circuit.is_tainted_by_id(4))
        self.assertFalse(circuit.is_tainted_by_id(5))
        self.assertFalse(circuit.is_tainted_by_id(6))
        self.assertFalse(circuit.is_tainted_by_id(7))

    def test_place_detector(self):
        mapping = QubitMapping(20, 20)
        circuit = Circuit(mapping, 0.01)
        prologue = str(circuit.circuit)

        i0 = circuit.place_measurement_z((0, 0))
        i1 = circuit.place_measurement_z((0, 2))
        i2 = circuit.place_measurement_z((0, 4))

        circuit.place_detector([i0, i1])
        circuit.place_detector([i1, i2], post_selection=True)
        expectation = prologue + textwrap.dedent('''
        X_ERROR(0.01) 0
        M 0
        X_ERROR(0.01) 1
        M 1
        X_ERROR(0.01) 2
        M 2
        DETECTOR rec[-3] rec[-2]
        DETECTOR rec[-2] rec[-1]''')
        self.assertEqual(str(circuit.circuit), expectation)
        self.assertEqual(circuit.detectors_for_post_selection, [DetectorIdentifier(1)])

    def test_place_observable_inlclude(self):
        mapping = QubitMapping(20, 20)
        circuit = Circuit(mapping, 0.01)
        prologue = str(circuit.circuit)

        i0 = circuit.place_measurement_z((0, 0))
        i1 = circuit.place_measurement_z((0, 2))
        i2 = circuit.place_measurement_z((0, 4))

        circuit.place_observable_include([i0, i1], ObservableIdentifier(4))
        circuit.place_observable_include([i1, i2], ObservableIdentifier(1))
        expectation = prologue + textwrap.dedent('''
        X_ERROR(0.01) 0
        M 0
        X_ERROR(0.01) 1
        M 1
        X_ERROR(0.01) 2
        M 2
        OBSERVABLE_INCLUDE(4) rec[-3] rec[-2]
        OBSERVABLE_INCLUDE(1) rec[-2] rec[-1]''')
        self.assertEqual(str(circuit.circuit), expectation)
