import textwrap
import unittest

from steane_code import *
from util import QubitMapping, Circuit, DetectorIdentifier


class SteaneZ0145SyndromeMeasurementTest(unittest.TestCase):
    def test_run(self) -> None:
        mapping = QubitMapping(20, 20)

        # STEANE_0
        self.assertEqual(mapping.get_id(3, 3), 111)
        # STEANE_1
        self.assertEqual(mapping.get_id(1, 5), 102)
        # STEANE_4
        self.assertEqual(mapping.get_id(0, 2), 1)
        # STEANE_5
        self.assertEqual(mapping.get_id(3, 5), 112)

        circuit = Circuit(mapping, 0)
        prologue = str(circuit.circuit)
        m = SteaneZ0145SyndromeMeasurement(circuit)

        b = m.run()
        self.assertFalse(b)
        self.assertTrue(m.has_initialized_ancillae)
        self.assertFalse(m.has_entangled_ancillae)
        self.assertFalse(m.has_performed_cx_0)
        self.assertFalse(m.has_performed_cx_1)
        self.assertFalse(m.has_performed_cx_4)
        self.assertFalse(m.has_performed_cx_5)
        self.assertFalse(m.has_disentangled_ancillae)
        self.assertFalse(m.has_measured_ancillae)
        self.maxDiff = None

        expectation = prologue + textwrap.dedent(f'''
        RX 101
        R 12''')
        self.assertEqual(str(circuit.circuit), expectation)

        b = m.run()
        self.assertFalse(b)
        self.assertEqual(str(circuit.circuit), expectation)

        circuit.place_tick()
        b = m.run()
        self.assertFalse(b)
        self.assertTrue(m.has_initialized_ancillae)
        self.assertTrue(m.has_entangled_ancillae)
        self.assertFalse(m.has_performed_cx_0)
        self.assertFalse(m.has_performed_cx_1)
        self.assertFalse(m.has_performed_cx_4)
        self.assertFalse(m.has_performed_cx_5)
        self.assertFalse(m.has_disentangled_ancillae)
        self.assertFalse(m.has_measured_ancillae)
        self.assertFalse(m.has_done_with_qubit_0())
        self.assertFalse(m.has_done_with_qubit_1())
        self.assertTrue(m.has_done_with_qubit_2())
        self.assertTrue(m.has_done_with_qubit_3())
        self.assertFalse(m.has_done_with_qubit_4())
        self.assertFalse(m.has_done_with_qubit_5())
        self.assertTrue(m.has_done_with_qubit_6())
        expectation = prologue + textwrap.dedent(f'''
        RX 101
        R 12
        TICK
        CX 101 12''')
        self.assertEqual(str(circuit.circuit), expectation)

        circuit.place_tick()
        b = m.run()
        self.assertFalse(b)
        self.assertTrue(m.has_initialized_ancillae)
        self.assertTrue(m.has_entangled_ancillae)
        self.assertFalse(m.has_performed_cx_0)
        self.assertTrue(m.has_performed_cx_1)
        self.assertTrue(m.has_performed_cx_4)
        self.assertFalse(m.has_performed_cx_5)
        self.assertFalse(m.has_disentangled_ancillae)
        self.assertFalse(m.has_measured_ancillae)
        self.assertFalse(m.has_done_with_qubit_0())
        self.assertTrue(m.has_done_with_qubit_1())
        self.assertTrue(m.has_done_with_qubit_2())
        self.assertTrue(m.has_done_with_qubit_3())
        self.assertTrue(m.has_done_with_qubit_4())
        self.assertFalse(m.has_done_with_qubit_5())
        self.assertTrue(m.has_done_with_qubit_6())
        expectation = prologue + textwrap.dedent(f'''
        RX 101
        R 12
        TICK
        CX 101 12
        TICK
        CX 102 12 1 101''')
        self.assertEqual(str(circuit.circuit), expectation)

        circuit.place_tick()
        b = m.run()
        self.assertFalse(b)
        self.assertTrue(m.has_initialized_ancillae)
        self.assertTrue(m.has_entangled_ancillae)
        self.assertFalse(m.has_performed_cx_0)
        self.assertTrue(m.has_performed_cx_1)
        self.assertTrue(m.has_performed_cx_4)
        self.assertTrue(m.has_performed_cx_5)
        self.assertFalse(m.has_disentangled_ancillae)
        self.assertFalse(m.has_measured_ancillae)
        self.assertFalse(m.has_done_with_qubit_0())
        self.assertTrue(m.has_done_with_qubit_1())
        self.assertTrue(m.has_done_with_qubit_2())
        self.assertTrue(m.has_done_with_qubit_3())
        self.assertTrue(m.has_done_with_qubit_4())
        self.assertTrue(m.has_done_with_qubit_5())
        self.assertTrue(m.has_done_with_qubit_6())
        expectation = prologue + textwrap.dedent(f'''
        RX 101
        R 12
        TICK
        CX 101 12
        TICK
        CX 102 12 1 101
        TICK
        CX 112 12''')
        self.assertEqual(str(circuit.circuit), expectation)

        circuit.place_tick()
        b = m.run()
        self.assertFalse(b)
        self.assertTrue(m.has_initialized_ancillae)
        self.assertTrue(m.has_entangled_ancillae)
        self.assertTrue(m.has_performed_cx_0)
        self.assertTrue(m.has_performed_cx_1)
        self.assertTrue(m.has_performed_cx_4)
        self.assertTrue(m.has_performed_cx_5)
        self.assertFalse(m.has_disentangled_ancillae)
        self.assertFalse(m.has_measured_ancillae)
        self.assertTrue(m.has_done_with_qubit_0())
        self.assertTrue(m.has_done_with_qubit_1())
        self.assertTrue(m.has_done_with_qubit_2())
        self.assertTrue(m.has_done_with_qubit_3())
        self.assertTrue(m.has_done_with_qubit_4())
        self.assertTrue(m.has_done_with_qubit_5())
        self.assertTrue(m.has_done_with_qubit_6())
        expectation = prologue + textwrap.dedent(f'''
        RX 101
        R 12
        TICK
        CX 101 12
        TICK
        CX 102 12 1 101
        TICK
        CX 112 12
        TICK
        CX 111 12''')
        self.assertEqual(str(circuit.circuit), expectation)

        circuit.place_tick()
        b = m.run()
        self.assertFalse(b)
        self.assertTrue(m.has_initialized_ancillae)
        self.assertTrue(m.has_entangled_ancillae)
        self.assertTrue(m.has_performed_cx_0)
        self.assertTrue(m.has_performed_cx_1)
        self.assertTrue(m.has_performed_cx_4)
        self.assertTrue(m.has_performed_cx_5)
        self.assertTrue(m.has_disentangled_ancillae)
        self.assertFalse(m.has_measured_ancillae)
        self.assertTrue(m.has_done_with_qubit_0())
        self.assertTrue(m.has_done_with_qubit_1())
        self.assertTrue(m.has_done_with_qubit_2())
        self.assertTrue(m.has_done_with_qubit_3())
        self.assertTrue(m.has_done_with_qubit_4())
        self.assertTrue(m.has_done_with_qubit_5())
        self.assertTrue(m.has_done_with_qubit_6())
        expectation = prologue + textwrap.dedent(f'''
        RX 101
        R 12
        TICK
        CX 101 12
        TICK
        CX 102 12 1 101
        TICK
        CX 112 12
        TICK
        CX 111 12
        TICK
        CX 101 12''')
        self.assertEqual(str(circuit.circuit), expectation)

        circuit.place_tick()
        b = m.run()
        self.assertTrue(b)
        self.assertTrue(m.has_initialized_ancillae)
        self.assertTrue(m.has_entangled_ancillae)
        self.assertTrue(m.has_performed_cx_0)
        self.assertTrue(m.has_performed_cx_1)
        self.assertTrue(m.has_performed_cx_4)
        self.assertTrue(m.has_performed_cx_5)
        self.assertTrue(m.has_disentangled_ancillae)
        self.assertTrue(m.has_measured_ancillae)
        self.assertTrue(m.has_done_with_qubit_0())
        self.assertTrue(m.has_done_with_qubit_1())
        self.assertTrue(m.has_done_with_qubit_2())
        self.assertTrue(m.has_done_with_qubit_3())
        self.assertTrue(m.has_done_with_qubit_4())
        self.assertTrue(m.has_done_with_qubit_5())
        self.assertTrue(m.has_done_with_qubit_6())
        expectation = prologue + textwrap.dedent(f'''
        RX 101
        R 12
        TICK
        CX 101 12
        TICK
        CX 102 12 1 101
        TICK
        CX 112 12
        TICK
        CX 111 12
        TICK
        CX 101 12
        TICK
        MX 101
        DETECTOR rec[-1]
        M 12
        DETECTOR rec[-1]''')
        self.assertEqual(str(circuit.circuit), expectation)
        self.assertEqual(circuit.detectors_for_post_selection, [DetectorIdentifier(0), DetectorIdentifier(1)])


class SteaneZ0235SyndromeMeasurementTest(unittest.TestCase):
    def test_run(self) -> None:
        mapping = QubitMapping(20, 20)

        # STEANE_0
        self.assertEqual(mapping.get_id(3, 3), 111)
        # STEANE_2
        self.assertEqual(mapping.get_id(4, 2), 21)
        # STEANE_3
        self.assertEqual(mapping.get_id(5, 5), 122)
        # STEANE_5
        self.assertEqual(mapping.get_id(3, 5), 112)

        circuit = Circuit(mapping, 0)
        prologue = str(circuit.circuit)
        m = SteaneZ0235SyndromeMeasurement(circuit)

        b = m.run()
        self.assertFalse(b)
        self.assertTrue(m.has_initialized_ancillae)
        self.assertFalse(m.has_entangled_ancillae)
        self.assertFalse(m.has_performed_cx_0)
        self.assertFalse(m.has_performed_cx_2)
        self.assertFalse(m.has_performed_cx_3)
        self.assertFalse(m.has_performed_cx_5)
        self.assertFalse(m.has_disentangled_ancillae)
        self.assertFalse(m.has_measured_ancillae)
        self.assertFalse(m.has_done_with_qubit_0())
        self.assertTrue(m.has_done_with_qubit_1())
        self.assertFalse(m.has_done_with_qubit_2())
        self.assertFalse(m.has_done_with_qubit_3())
        self.assertTrue(m.has_done_with_qubit_4())
        self.assertFalse(m.has_done_with_qubit_5())
        self.assertTrue(m.has_done_with_qubit_6())
        expectation = prologue + textwrap.dedent(f'''
        RX 121
        R 22''')
        self.assertEqual(str(circuit.circuit), expectation)

        b = m.run()
        self.assertFalse(b)
        self.assertEqual(str(circuit.circuit), expectation)

        circuit.place_tick()
        b = m.run()
        self.assertFalse(b)
        self.assertTrue(m.has_initialized_ancillae)
        self.assertTrue(m.has_entangled_ancillae)
        self.assertFalse(m.has_performed_cx_0)
        self.assertFalse(m.has_performed_cx_2)
        self.assertFalse(m.has_performed_cx_3)
        self.assertFalse(m.has_performed_cx_5)
        self.assertFalse(m.has_disentangled_ancillae)
        self.assertFalse(m.has_measured_ancillae)
        self.assertFalse(m.has_done_with_qubit_0())
        self.assertTrue(m.has_done_with_qubit_1())
        self.assertFalse(m.has_done_with_qubit_2())
        self.assertFalse(m.has_done_with_qubit_3())
        self.assertTrue(m.has_done_with_qubit_4())
        self.assertFalse(m.has_done_with_qubit_5())
        self.assertTrue(m.has_done_with_qubit_6())
        expectation = prologue + textwrap.dedent(f'''
        RX 121
        R 22
        TICK
        CX 121 22''')
        self.assertEqual(str(circuit.circuit), expectation)

        circuit.place_tick()
        b = m.run()
        self.assertFalse(b)
        self.assertTrue(m.has_initialized_ancillae)
        self.assertTrue(m.has_entangled_ancillae)
        self.assertFalse(m.has_performed_cx_0)
        self.assertTrue(m.has_performed_cx_2)
        self.assertFalse(m.has_performed_cx_3)
        self.assertTrue(m.has_performed_cx_5)
        self.assertFalse(m.has_disentangled_ancillae)
        self.assertFalse(m.has_measured_ancillae)
        self.assertFalse(m.has_done_with_qubit_0())
        self.assertTrue(m.has_done_with_qubit_1())
        self.assertTrue(m.has_done_with_qubit_2())
        self.assertFalse(m.has_done_with_qubit_3())
        self.assertTrue(m.has_done_with_qubit_4())
        self.assertTrue(m.has_done_with_qubit_5())
        self.assertTrue(m.has_done_with_qubit_6())
        expectation = prologue + textwrap.dedent(f'''
        RX 121
        R 22
        TICK
        CX 121 22
        TICK
        CX 112 22 21 121''')
        self.assertEqual(str(circuit.circuit), expectation)

        circuit.place_tick()
        b = m.run()
        self.assertFalse(b)
        self.assertTrue(m.has_initialized_ancillae)
        self.assertTrue(m.has_entangled_ancillae)
        self.assertFalse(m.has_performed_cx_0)
        self.assertTrue(m.has_performed_cx_2)
        self.assertTrue(m.has_performed_cx_3)
        self.assertTrue(m.has_performed_cx_5)
        self.assertFalse(m.has_disentangled_ancillae)
        self.assertFalse(m.has_measured_ancillae)
        self.assertFalse(m.has_done_with_qubit_0())
        self.assertTrue(m.has_done_with_qubit_1())
        self.assertTrue(m.has_done_with_qubit_2())
        self.assertTrue(m.has_done_with_qubit_3())
        self.assertTrue(m.has_done_with_qubit_4())
        self.assertTrue(m.has_done_with_qubit_5())
        self.assertTrue(m.has_done_with_qubit_6())
        expectation = prologue + textwrap.dedent(f'''
        RX 121
        R 22
        TICK
        CX 121 22
        TICK
        CX 112 22 21 121
        TICK
        CX 122 22''')
        self.assertEqual(str(circuit.circuit), expectation)

        circuit.place_tick()
        b = m.run()
        self.assertFalse(b)
        self.assertTrue(m.has_initialized_ancillae)
        self.assertTrue(m.has_entangled_ancillae)
        self.assertTrue(m.has_performed_cx_0)
        self.assertTrue(m.has_performed_cx_2)
        self.assertTrue(m.has_performed_cx_3)
        self.assertTrue(m.has_performed_cx_5)
        self.assertFalse(m.has_disentangled_ancillae)
        self.assertFalse(m.has_measured_ancillae)
        self.assertTrue(m.has_done_with_qubit_0())
        self.assertTrue(m.has_done_with_qubit_1())
        self.assertTrue(m.has_done_with_qubit_2())
        self.assertTrue(m.has_done_with_qubit_3())
        self.assertTrue(m.has_done_with_qubit_4())
        self.assertTrue(m.has_done_with_qubit_5())
        self.assertTrue(m.has_done_with_qubit_6())
        expectation = prologue + textwrap.dedent(f'''
        RX 121
        R 22
        TICK
        CX 121 22
        TICK
        CX 112 22 21 121
        TICK
        CX 122 22
        TICK
        CX 111 22''')
        self.assertEqual(str(circuit.circuit), expectation)

        circuit.place_tick()
        b = m.run()
        self.assertFalse(b)
        self.assertTrue(m.has_initialized_ancillae)
        self.assertTrue(m.has_entangled_ancillae)
        self.assertTrue(m.has_performed_cx_0)
        self.assertTrue(m.has_performed_cx_2)
        self.assertTrue(m.has_performed_cx_3)
        self.assertTrue(m.has_performed_cx_5)
        self.assertTrue(m.has_disentangled_ancillae)
        self.assertFalse(m.has_measured_ancillae)
        self.assertTrue(m.has_done_with_qubit_0())
        self.assertTrue(m.has_done_with_qubit_1())
        self.assertTrue(m.has_done_with_qubit_2())
        self.assertTrue(m.has_done_with_qubit_3())
        self.assertTrue(m.has_done_with_qubit_4())
        self.assertTrue(m.has_done_with_qubit_5())
        self.assertTrue(m.has_done_with_qubit_6())
        expectation = prologue + textwrap.dedent(f'''
        RX 121
        R 22
        TICK
        CX 121 22
        TICK
        CX 112 22 21 121
        TICK
        CX 122 22
        TICK
        CX 111 22
        TICK
        CX 121 22''')
        self.assertEqual(str(circuit.circuit), expectation)

        circuit.place_tick()
        b = m.run()
        self.assertTrue(b)
        self.assertTrue(m.has_initialized_ancillae)
        self.assertTrue(m.has_entangled_ancillae)
        self.assertTrue(m.has_performed_cx_0)
        self.assertTrue(m.has_performed_cx_2)
        self.assertTrue(m.has_performed_cx_3)
        self.assertTrue(m.has_performed_cx_5)
        self.assertTrue(m.has_disentangled_ancillae)
        self.assertTrue(m.has_measured_ancillae)
        self.assertTrue(m.has_done_with_qubit_0())
        self.assertTrue(m.has_done_with_qubit_1())
        self.assertTrue(m.has_done_with_qubit_2())
        self.assertTrue(m.has_done_with_qubit_3())
        self.assertTrue(m.has_done_with_qubit_4())
        self.assertTrue(m.has_done_with_qubit_5())
        self.assertTrue(m.has_done_with_qubit_6())
        expectation = prologue + textwrap.dedent(f'''
        RX 121
        R 22
        TICK
        CX 121 22
        TICK
        CX 112 22 21 121
        TICK
        CX 122 22
        TICK
        CX 111 22
        TICK
        CX 121 22
        TICK
        MX 121
        DETECTOR rec[-1]
        M 22
        DETECTOR rec[-1]''')
        self.assertEqual(str(circuit.circuit), expectation)
        self.assertEqual(circuit.detectors_for_post_selection, [DetectorIdentifier(0), DetectorIdentifier(1)])


class SteaneZ0246SyndromeMeasurementTest(unittest.TestCase):
    def test_run(self) -> None:
        mapping = QubitMapping(20, 20)

        # STEANE_0
        self.assertEqual(mapping.get_id(3, 3), 111)
        # STEANE_2
        self.assertEqual(mapping.get_id(4, 2), 21)
        # STEANE_4
        self.assertEqual(mapping.get_id(0, 2), 1)
        # STEANE_6
        self.assertEqual(mapping.get_id(2, 0), 10)

        circuit = Circuit(mapping, 0)
        prologue = str(circuit.circuit)
        m = SteaneZ0246SyndromeMeasurement(circuit)

        b = m.run()
        self.assertFalse(b)
        self.assertTrue(m.has_initialized_ancillae)
        self.assertFalse(m.has_entangled_ancillae_ab)
        self.assertFalse(m.has_entangled_ancillae_ac)
        self.assertFalse(m.has_performed_cx_0)
        self.assertFalse(m.has_performed_cx_2)
        self.assertFalse(m.has_performed_cx_4)
        self.assertFalse(m.has_performed_cx_6)
        self.assertFalse(m.has_disentangled_ancillae_ab)
        self.assertFalse(m.has_disentangled_ancillae_ac)
        self.assertFalse(m.has_measured_ancillae)
        self.assertFalse(m.has_done_with_qubit_0())
        self.assertTrue(m.has_done_with_qubit_1())
        self.assertFalse(m.has_done_with_qubit_2())
        self.assertTrue(m.has_done_with_qubit_3())
        self.assertFalse(m.has_done_with_qubit_4())
        self.assertTrue(m.has_done_with_qubit_5())
        self.assertFalse(m.has_done_with_qubit_6())
        expectation = prologue + textwrap.dedent(f'''
        R 11
        RX 110 100''')
        self.assertEqual(str(circuit.circuit), expectation)

        b = m.run()
        self.assertFalse(b)
        expectation = prologue + textwrap.dedent(f'''
        R 11
        RX 110 100''')
        self.assertEqual(str(circuit.circuit), expectation)

        circuit.place_tick()
        b = m.run()
        self.assertFalse(b)
        self.assertTrue(m.has_initialized_ancillae)
        self.assertTrue(m.has_entangled_ancillae_ab)
        self.assertFalse(m.has_entangled_ancillae_ac)
        self.assertFalse(m.has_performed_cx_0)
        self.assertFalse(m.has_performed_cx_2)
        self.assertFalse(m.has_performed_cx_4)
        self.assertFalse(m.has_performed_cx_6)
        self.assertFalse(m.has_disentangled_ancillae_ab)
        self.assertFalse(m.has_disentangled_ancillae_ac)
        self.assertFalse(m.has_measured_ancillae)
        self.assertFalse(m.has_done_with_qubit_0())
        self.assertTrue(m.has_done_with_qubit_1())
        self.assertFalse(m.has_done_with_qubit_2())
        self.assertTrue(m.has_done_with_qubit_3())
        self.assertFalse(m.has_done_with_qubit_4())
        self.assertTrue(m.has_done_with_qubit_5())
        self.assertFalse(m.has_done_with_qubit_6())
        expectation = prologue + textwrap.dedent(f'''
        R 11
        RX 110 100
        TICK
        CX 110 11''')
        self.assertEqual(str(circuit.circuit), expectation)

        circuit.place_tick()
        b = m.run()
        self.assertFalse(b)
        self.assertTrue(m.has_initialized_ancillae)
        self.assertTrue(m.has_entangled_ancillae_ab)
        self.assertTrue(m.has_entangled_ancillae_ac)
        self.assertFalse(m.has_performed_cx_0)
        self.assertTrue(m.has_performed_cx_2)
        self.assertFalse(m.has_performed_cx_4)
        self.assertFalse(m.has_performed_cx_6)
        self.assertFalse(m.has_disentangled_ancillae_ab)
        self.assertFalse(m.has_disentangled_ancillae_ac)
        self.assertFalse(m.has_measured_ancillae)
        self.assertFalse(m.has_done_with_qubit_0())
        self.assertTrue(m.has_done_with_qubit_1())
        self.assertTrue(m.has_done_with_qubit_2())
        self.assertTrue(m.has_done_with_qubit_3())
        self.assertFalse(m.has_done_with_qubit_4())
        self.assertTrue(m.has_done_with_qubit_5())
        self.assertFalse(m.has_done_with_qubit_6())
        expectation = prologue + textwrap.dedent(f'''
        R 11
        RX 110 100
        TICK
        CX 110 11
        TICK
        CX 100 11 21 110''')
        self.assertEqual(str(circuit.circuit), expectation)

        circuit.place_tick()
        b = m.run()
        self.assertFalse(b)
        self.assertTrue(m.has_initialized_ancillae)
        self.assertTrue(m.has_entangled_ancillae_ab)
        self.assertTrue(m.has_entangled_ancillae_ac)
        self.assertTrue(m.has_performed_cx_0)
        self.assertTrue(m.has_performed_cx_2)
        self.assertTrue(m.has_performed_cx_4)
        self.assertTrue(m.has_performed_cx_6)
        self.assertFalse(m.has_disentangled_ancillae_ab)
        self.assertFalse(m.has_disentangled_ancillae_ac)
        self.assertFalse(m.has_measured_ancillae)
        self.assertTrue(m.has_done_with_qubit_0())
        self.assertTrue(m.has_done_with_qubit_1())
        self.assertTrue(m.has_done_with_qubit_2())
        self.assertTrue(m.has_done_with_qubit_3())
        self.assertTrue(m.has_done_with_qubit_4())
        self.assertTrue(m.has_done_with_qubit_5())
        self.assertTrue(m.has_done_with_qubit_6())
        expectation = prologue + textwrap.dedent(f'''
        R 11
        RX 110 100
        TICK
        CX 110 11
        TICK
        CX 100 11 21 110
        TICK
        CX 111 11 1 100 10 110''')
        self.assertEqual(str(circuit.circuit), expectation)

        circuit.place_tick()
        b = m.run()
        self.assertFalse(b)
        self.assertTrue(m.has_initialized_ancillae)
        self.assertTrue(m.has_entangled_ancillae_ab)
        self.assertTrue(m.has_entangled_ancillae_ac)
        self.assertTrue(m.has_performed_cx_0)
        self.assertTrue(m.has_performed_cx_2)
        self.assertTrue(m.has_performed_cx_4)
        self.assertTrue(m.has_performed_cx_6)
        self.assertTrue(m.has_disentangled_ancillae_ab)
        self.assertFalse(m.has_disentangled_ancillae_ac)
        self.assertFalse(m.has_measured_ancillae)
        self.assertTrue(m.has_done_with_qubit_0())
        self.assertTrue(m.has_done_with_qubit_1())
        self.assertTrue(m.has_done_with_qubit_2())
        self.assertTrue(m.has_done_with_qubit_3())
        self.assertTrue(m.has_done_with_qubit_4())
        self.assertTrue(m.has_done_with_qubit_5())
        self.assertTrue(m.has_done_with_qubit_6())
        expectation = prologue + textwrap.dedent(f'''
        R 11
        RX 110 100
        TICK
        CX 110 11
        TICK
        CX 100 11 21 110
        TICK
        CX 111 11 1 100 10 110
        TICK
        CX 110 11''')
        self.assertEqual(str(circuit.circuit), expectation)

        circuit.place_tick()
        b = m.run()
        self.assertFalse(b)
        self.assertTrue(m.has_initialized_ancillae)
        self.assertTrue(m.has_entangled_ancillae_ab)
        self.assertTrue(m.has_entangled_ancillae_ac)
        self.assertTrue(m.has_performed_cx_0)
        self.assertTrue(m.has_performed_cx_2)
        self.assertTrue(m.has_performed_cx_4)
        self.assertTrue(m.has_performed_cx_6)
        self.assertTrue(m.has_disentangled_ancillae_ab)
        self.assertTrue(m.has_disentangled_ancillae_ac)
        self.assertFalse(m.has_measured_ancillae)
        self.assertTrue(m.has_done_with_qubit_0())
        self.assertTrue(m.has_done_with_qubit_1())
        self.assertTrue(m.has_done_with_qubit_2())
        self.assertTrue(m.has_done_with_qubit_3())
        self.assertTrue(m.has_done_with_qubit_4())
        self.assertTrue(m.has_done_with_qubit_5())
        self.assertTrue(m.has_done_with_qubit_6())
        expectation = prologue + textwrap.dedent(f'''
        R 11
        RX 110 100
        TICK
        CX 110 11
        TICK
        CX 100 11 21 110
        TICK
        CX 111 11 1 100 10 110
        TICK
        CX 110 11
        TICK
        CX 100 11''')
        self.assertEqual(str(circuit.circuit), expectation)

        circuit.place_tick()
        b = m.run()
        self.assertTrue(b)
        self.assertTrue(m.has_initialized_ancillae)
        self.assertTrue(m.has_entangled_ancillae_ab)
        self.assertTrue(m.has_entangled_ancillae_ac)
        self.assertTrue(m.has_performed_cx_0)
        self.assertTrue(m.has_performed_cx_2)
        self.assertTrue(m.has_performed_cx_4)
        self.assertTrue(m.has_performed_cx_6)
        self.assertTrue(m.has_disentangled_ancillae_ab)
        self.assertTrue(m.has_disentangled_ancillae_ac)
        self.assertTrue(m.has_measured_ancillae)
        self.assertTrue(m.has_done_with_qubit_0())
        self.assertTrue(m.has_done_with_qubit_1())
        self.assertTrue(m.has_done_with_qubit_2())
        self.assertTrue(m.has_done_with_qubit_3())
        self.assertTrue(m.has_done_with_qubit_4())
        self.assertTrue(m.has_done_with_qubit_5())
        self.assertTrue(m.has_done_with_qubit_6())
        expectation = prologue + textwrap.dedent(f'''
        R 11
        RX 110 100
        TICK
        CX 110 11
        TICK
        CX 100 11 21 110
        TICK
        CX 111 11 1 100 10 110
        TICK
        CX 110 11
        TICK
        CX 100 11
        TICK
        M 11
        DETECTOR rec[-1]
        MX 110
        DETECTOR rec[-1]
        MX 100
        DETECTOR rec[-1]''')
        self.assertEqual(str(circuit.circuit), expectation)
        self.assertEqual(circuit.detectors_for_post_selection, [
            DetectorIdentifier(0), DetectorIdentifier(1), DetectorIdentifier(2)
        ])
