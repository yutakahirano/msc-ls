import textwrap
import unittest

from steane_code import *
from util import QubitMapping, Circuit, DetectorIdentifier


class SteaneZ0145SyndromeMeasurementTest(unittest.TestCase):
    def test_run(self) -> None:
        mapping = QubitMapping(20, 20)

        self.assertEqual(mapping.get_id(*STEANE_0), 111)
        self.assertEqual(mapping.get_id(*STEANE_1), 102)
        self.assertEqual(mapping.get_id(*STEANE_4), 11)
        self.assertEqual(mapping.get_id(*STEANE_5), 112)

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
        self.assertFalse(m.is_done_with_qubit_0())
        self.assertFalse(m.is_done_with_qubit_1())
        self.assertTrue(m.is_done_with_qubit_2())
        self.assertTrue(m.is_done_with_qubit_3())
        self.assertFalse(m.is_done_with_qubit_4())
        self.assertFalse(m.is_done_with_qubit_5())
        self.assertTrue(m.is_done_with_qubit_6())
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
        self.assertFalse(m.is_done_with_qubit_0())
        self.assertTrue(m.is_done_with_qubit_1())
        self.assertTrue(m.is_done_with_qubit_2())
        self.assertTrue(m.is_done_with_qubit_3())
        self.assertTrue(m.is_done_with_qubit_4())
        self.assertFalse(m.is_done_with_qubit_5())
        self.assertTrue(m.is_done_with_qubit_6())
        expectation = prologue + textwrap.dedent(f'''
        RX 101
        R 12
        TICK
        CX 101 12
        TICK
        CX 102 12 11 101''')
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
        self.assertFalse(m.is_done_with_qubit_0())
        self.assertTrue(m.is_done_with_qubit_1())
        self.assertTrue(m.is_done_with_qubit_2())
        self.assertTrue(m.is_done_with_qubit_3())
        self.assertTrue(m.is_done_with_qubit_4())
        self.assertTrue(m.is_done_with_qubit_5())
        self.assertTrue(m.is_done_with_qubit_6())
        expectation = prologue + textwrap.dedent(f'''
        RX 101
        R 12
        TICK
        CX 101 12
        TICK
        CX 102 12 11 101
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
        self.assertTrue(m.is_done_with_qubit_0())
        self.assertTrue(m.is_done_with_qubit_1())
        self.assertTrue(m.is_done_with_qubit_2())
        self.assertTrue(m.is_done_with_qubit_3())
        self.assertTrue(m.is_done_with_qubit_4())
        self.assertTrue(m.is_done_with_qubit_5())
        self.assertTrue(m.is_done_with_qubit_6())
        expectation = prologue + textwrap.dedent(f'''
        RX 101
        R 12
        TICK
        CX 101 12
        TICK
        CX 102 12 11 101
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
        self.assertTrue(m.is_done_with_qubit_0())
        self.assertTrue(m.is_done_with_qubit_1())
        self.assertTrue(m.is_done_with_qubit_2())
        self.assertTrue(m.is_done_with_qubit_3())
        self.assertTrue(m.is_done_with_qubit_4())
        self.assertTrue(m.is_done_with_qubit_5())
        self.assertTrue(m.is_done_with_qubit_6())
        expectation = prologue + textwrap.dedent(f'''
        RX 101
        R 12
        TICK
        CX 101 12
        TICK
        CX 102 12 11 101
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
        self.assertTrue(m.is_done_with_qubit_0())
        self.assertTrue(m.is_done_with_qubit_1())
        self.assertTrue(m.is_done_with_qubit_2())
        self.assertTrue(m.is_done_with_qubit_3())
        self.assertTrue(m.is_done_with_qubit_4())
        self.assertTrue(m.is_done_with_qubit_5())
        self.assertTrue(m.is_done_with_qubit_6())
        expectation = prologue + textwrap.dedent(f'''
        RX 101
        R 12
        TICK
        CX 101 12
        TICK
        CX 102 12 11 101
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

    def test_lock_1(self) -> None:
        mapping = QubitMapping(20, 20)

        self.assertEqual(mapping.get_id(*STEANE_0), 111)
        self.assertEqual(mapping.get_id(*STEANE_1), 102)
        self.assertEqual(mapping.get_id(*STEANE_4), 11)
        self.assertEqual(mapping.get_id(*STEANE_5), 112)

        circuit = Circuit(mapping, 0)
        prologue = str(circuit.circuit)
        m = SteaneZ0145SyndromeMeasurement(circuit)
        m.lock_qubit_1()

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

        b = m.run()
        self.assertFalse(b)

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
        self.assertFalse(m.is_done_with_qubit_0())
        self.assertFalse(m.is_done_with_qubit_1())
        self.assertTrue(m.is_done_with_qubit_2())
        self.assertTrue(m.is_done_with_qubit_3())
        self.assertFalse(m.is_done_with_qubit_4())
        self.assertFalse(m.is_done_with_qubit_5())
        self.assertTrue(m.is_done_with_qubit_6())

        circuit.place_tick()
        b = m.run()
        self.assertFalse(b)
        self.assertTrue(m.has_initialized_ancillae)
        self.assertTrue(m.has_entangled_ancillae)
        self.assertFalse(m.has_performed_cx_0)
        self.assertFalse(m.has_performed_cx_1)
        self.assertTrue(m.has_performed_cx_4)
        self.assertTrue(m.has_performed_cx_5)
        self.assertFalse(m.has_disentangled_ancillae)
        self.assertFalse(m.has_measured_ancillae)
        self.assertFalse(m.is_done_with_qubit_0())
        self.assertFalse(m.is_done_with_qubit_1())
        self.assertTrue(m.is_done_with_qubit_2())
        self.assertTrue(m.is_done_with_qubit_3())
        self.assertTrue(m.is_done_with_qubit_4())
        self.assertTrue(m.is_done_with_qubit_5())
        self.assertTrue(m.is_done_with_qubit_6())

        circuit.place_tick()
        b = m.run()
        self.assertFalse(b)
        self.assertTrue(m.has_initialized_ancillae)
        self.assertTrue(m.has_entangled_ancillae)
        self.assertTrue(m.has_performed_cx_0)
        self.assertFalse(m.has_performed_cx_1)
        self.assertTrue(m.has_performed_cx_4)
        self.assertTrue(m.has_performed_cx_5)
        self.assertFalse(m.has_disentangled_ancillae)
        self.assertFalse(m.has_measured_ancillae)
        self.assertTrue(m.is_done_with_qubit_0())
        self.assertFalse(m.is_done_with_qubit_1())
        self.assertTrue(m.is_done_with_qubit_2())
        self.assertTrue(m.is_done_with_qubit_3())
        self.assertTrue(m.is_done_with_qubit_4())
        self.assertTrue(m.is_done_with_qubit_5())
        self.assertTrue(m.is_done_with_qubit_6())

        circuit.place_tick()
        b = m.run()
        self.assertFalse(b)
        self.assertTrue(m.has_initialized_ancillae)
        self.assertTrue(m.has_entangled_ancillae)
        self.assertTrue(m.has_performed_cx_0)
        self.assertFalse(m.has_performed_cx_1)
        self.assertTrue(m.has_performed_cx_4)
        self.assertTrue(m.has_performed_cx_5)
        self.assertFalse(m.has_disentangled_ancillae)
        self.assertFalse(m.has_measured_ancillae)
        self.assertTrue(m.is_done_with_qubit_0())
        self.assertFalse(m.is_done_with_qubit_1())
        self.assertTrue(m.is_done_with_qubit_2())
        self.assertTrue(m.is_done_with_qubit_3())
        self.assertTrue(m.is_done_with_qubit_4())
        self.assertTrue(m.is_done_with_qubit_5())
        self.assertTrue(m.is_done_with_qubit_6())

        m.unlock_qubit_1()

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
        self.assertTrue(m.is_done_with_qubit_0())
        self.assertTrue(m.is_done_with_qubit_1())
        self.assertTrue(m.is_done_with_qubit_2())
        self.assertTrue(m.is_done_with_qubit_3())
        self.assertTrue(m.is_done_with_qubit_4())
        self.assertTrue(m.is_done_with_qubit_5())
        self.assertTrue(m.is_done_with_qubit_6())
        expectation = prologue + textwrap.dedent(f'''
        RX 101
        R 12
        TICK
        CX 101 12
        TICK
        CX 11 101 112 12
        TICK
        CX 111 12
        TICK
        TICK
        CX 102 12''')
        self.assertEqual(str(circuit.circuit), expectation)

    def test_lock_5(self) -> None:
        mapping = QubitMapping(20, 20)

        self.assertEqual(mapping.get_id(*STEANE_0), 111)
        self.assertEqual(mapping.get_id(*STEANE_1), 102)
        self.assertEqual(mapping.get_id(*STEANE_4), 11)
        self.assertEqual(mapping.get_id(*STEANE_5), 112)

        circuit = Circuit(mapping, 0)
        prologue = str(circuit.circuit)
        m = SteaneZ0145SyndromeMeasurement(circuit)
        m.lock_qubit_5()

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

        b = m.run()
        self.assertFalse(b)

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
        self.assertFalse(m.is_done_with_qubit_0())
        self.assertFalse(m.is_done_with_qubit_1())
        self.assertTrue(m.is_done_with_qubit_2())
        self.assertTrue(m.is_done_with_qubit_3())
        self.assertFalse(m.is_done_with_qubit_4())
        self.assertFalse(m.is_done_with_qubit_5())
        self.assertTrue(m.is_done_with_qubit_6())

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
        self.assertFalse(m.is_done_with_qubit_0())
        self.assertTrue(m.is_done_with_qubit_1())
        self.assertTrue(m.is_done_with_qubit_2())
        self.assertTrue(m.is_done_with_qubit_3())
        self.assertTrue(m.is_done_with_qubit_4())
        self.assertFalse(m.is_done_with_qubit_5())
        self.assertTrue(m.is_done_with_qubit_6())

        circuit.place_tick()
        b = m.run()
        self.assertFalse(b)
        self.assertTrue(m.has_initialized_ancillae)
        self.assertTrue(m.has_entangled_ancillae)
        self.assertTrue(m.has_performed_cx_0)
        self.assertTrue(m.has_performed_cx_1)
        self.assertTrue(m.has_performed_cx_4)
        self.assertFalse(m.has_performed_cx_5)
        self.assertFalse(m.has_disentangled_ancillae)
        self.assertFalse(m.has_measured_ancillae)
        self.assertTrue(m.is_done_with_qubit_0())
        self.assertTrue(m.is_done_with_qubit_1())
        self.assertTrue(m.is_done_with_qubit_2())
        self.assertTrue(m.is_done_with_qubit_3())
        self.assertTrue(m.is_done_with_qubit_4())
        self.assertFalse(m.is_done_with_qubit_5())
        self.assertTrue(m.is_done_with_qubit_6())

        circuit.place_tick()
        b = m.run()
        self.assertFalse(b)
        self.assertTrue(m.has_initialized_ancillae)
        self.assertTrue(m.has_entangled_ancillae)
        self.assertTrue(m.has_performed_cx_0)
        self.assertTrue(m.has_performed_cx_1)
        self.assertTrue(m.has_performed_cx_4)
        self.assertFalse(m.has_performed_cx_5)
        self.assertFalse(m.has_disentangled_ancillae)
        self.assertFalse(m.has_measured_ancillae)
        self.assertTrue(m.is_done_with_qubit_0())
        self.assertTrue(m.is_done_with_qubit_1())
        self.assertTrue(m.is_done_with_qubit_2())
        self.assertTrue(m.is_done_with_qubit_3())
        self.assertTrue(m.is_done_with_qubit_4())
        self.assertFalse(m.is_done_with_qubit_5())
        self.assertTrue(m.is_done_with_qubit_6())

        m.unlock_qubit_5()

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
        self.assertTrue(m.is_done_with_qubit_0())
        self.assertTrue(m.is_done_with_qubit_1())
        self.assertTrue(m.is_done_with_qubit_2())
        self.assertTrue(m.is_done_with_qubit_3())
        self.assertTrue(m.is_done_with_qubit_4())
        self.assertTrue(m.is_done_with_qubit_5())
        self.assertTrue(m.is_done_with_qubit_6())
        expectation = prologue + textwrap.dedent(f'''
        RX 101
        R 12
        TICK
        CX 101 12
        TICK
        CX 102 12 11 101
        TICK
        CX 111 12
        TICK
        TICK
        CX 112 12''')
        self.assertEqual(str(circuit.circuit), expectation)


class SteaneZ0235SyndromeMeasurementTest(unittest.TestCase):
    def test_run(self) -> None:
        mapping = QubitMapping(20, 20)

        self.assertEqual(mapping.get_id(*STEANE_0), 111)
        self.assertEqual(mapping.get_id(*STEANE_2), 31)
        self.assertEqual(mapping.get_id(*STEANE_3), 122)
        self.assertEqual(mapping.get_id(*STEANE_5), 112)

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
        self.assertFalse(m.is_done_with_qubit_0())
        self.assertTrue(m.is_done_with_qubit_1())
        self.assertFalse(m.is_done_with_qubit_2())
        self.assertFalse(m.is_done_with_qubit_3())
        self.assertTrue(m.is_done_with_qubit_4())
        self.assertFalse(m.is_done_with_qubit_5())
        self.assertTrue(m.is_done_with_qubit_6())
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
        self.assertFalse(m.is_done_with_qubit_0())
        self.assertTrue(m.is_done_with_qubit_1())
        self.assertFalse(m.is_done_with_qubit_2())
        self.assertFalse(m.is_done_with_qubit_3())
        self.assertTrue(m.is_done_with_qubit_4())
        self.assertFalse(m.is_done_with_qubit_5())
        self.assertTrue(m.is_done_with_qubit_6())
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
        self.assertFalse(m.is_done_with_qubit_0())
        self.assertTrue(m.is_done_with_qubit_1())
        self.assertTrue(m.is_done_with_qubit_2())
        self.assertFalse(m.is_done_with_qubit_3())
        self.assertTrue(m.is_done_with_qubit_4())
        self.assertTrue(m.is_done_with_qubit_5())
        self.assertTrue(m.is_done_with_qubit_6())
        expectation = prologue + textwrap.dedent(f'''
        RX 121
        R 22
        TICK
        CX 121 22
        TICK
        CX 112 22 31 121''')
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
        self.assertFalse(m.is_done_with_qubit_0())
        self.assertTrue(m.is_done_with_qubit_1())
        self.assertTrue(m.is_done_with_qubit_2())
        self.assertTrue(m.is_done_with_qubit_3())
        self.assertTrue(m.is_done_with_qubit_4())
        self.assertTrue(m.is_done_with_qubit_5())
        self.assertTrue(m.is_done_with_qubit_6())
        expectation = prologue + textwrap.dedent(f'''
        RX 121
        R 22
        TICK
        CX 121 22
        TICK
        CX 112 22 31 121
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
        self.assertTrue(m.is_done_with_qubit_0())
        self.assertTrue(m.is_done_with_qubit_1())
        self.assertTrue(m.is_done_with_qubit_2())
        self.assertTrue(m.is_done_with_qubit_3())
        self.assertTrue(m.is_done_with_qubit_4())
        self.assertTrue(m.is_done_with_qubit_5())
        self.assertTrue(m.is_done_with_qubit_6())
        expectation = prologue + textwrap.dedent(f'''
        RX 121
        R 22
        TICK
        CX 121 22
        TICK
        CX 112 22 31 121
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
        self.assertTrue(m.is_done_with_qubit_0())
        self.assertTrue(m.is_done_with_qubit_1())
        self.assertTrue(m.is_done_with_qubit_2())
        self.assertTrue(m.is_done_with_qubit_3())
        self.assertTrue(m.is_done_with_qubit_4())
        self.assertTrue(m.is_done_with_qubit_5())
        self.assertTrue(m.is_done_with_qubit_6())
        expectation = prologue + textwrap.dedent(f'''
        RX 121
        R 22
        TICK
        CX 121 22
        TICK
        CX 112 22 31 121
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
        self.assertTrue(m.is_done_with_qubit_0())
        self.assertTrue(m.is_done_with_qubit_1())
        self.assertTrue(m.is_done_with_qubit_2())
        self.assertTrue(m.is_done_with_qubit_3())
        self.assertTrue(m.is_done_with_qubit_4())
        self.assertTrue(m.is_done_with_qubit_5())
        self.assertTrue(m.is_done_with_qubit_6())
        expectation = prologue + textwrap.dedent(f'''
        RX 121
        R 22
        TICK
        CX 121 22
        TICK
        CX 112 22 31 121
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

    def test_lock_qubit_3(self) -> None:
        mapping = QubitMapping(20, 20)

        self.assertEqual(mapping.get_id(*STEANE_0), 111)
        self.assertEqual(mapping.get_id(*STEANE_2), 31)
        self.assertEqual(mapping.get_id(*STEANE_3), 122)
        self.assertEqual(mapping.get_id(*STEANE_5), 112)

        circuit = Circuit(mapping, 0)
        prologue = str(circuit.circuit)
        m = SteaneZ0235SyndromeMeasurement(circuit)

        m.lock_qubit_3()

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
        self.assertFalse(m.is_done_with_qubit_0())
        self.assertTrue(m.is_done_with_qubit_1())
        self.assertFalse(m.is_done_with_qubit_2())
        self.assertFalse(m.is_done_with_qubit_3())
        self.assertTrue(m.is_done_with_qubit_4())
        self.assertFalse(m.is_done_with_qubit_5())
        self.assertTrue(m.is_done_with_qubit_6())

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
        self.assertFalse(m.is_done_with_qubit_0())
        self.assertTrue(m.is_done_with_qubit_1())
        self.assertFalse(m.is_done_with_qubit_2())
        self.assertFalse(m.is_done_with_qubit_3())
        self.assertTrue(m.is_done_with_qubit_4())
        self.assertFalse(m.is_done_with_qubit_5())
        self.assertTrue(m.is_done_with_qubit_6())

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
        self.assertFalse(m.is_done_with_qubit_0())
        self.assertTrue(m.is_done_with_qubit_1())
        self.assertTrue(m.is_done_with_qubit_2())
        self.assertFalse(m.is_done_with_qubit_3())
        self.assertTrue(m.is_done_with_qubit_4())
        self.assertTrue(m.is_done_with_qubit_5())
        self.assertTrue(m.is_done_with_qubit_6())

        circuit.place_tick()
        b = m.run()
        self.assertFalse(b)
        self.assertTrue(m.has_initialized_ancillae)
        self.assertTrue(m.has_entangled_ancillae)
        self.assertTrue(m.has_performed_cx_0)
        self.assertTrue(m.has_performed_cx_2)
        self.assertFalse(m.has_performed_cx_3)
        self.assertTrue(m.has_performed_cx_5)
        self.assertFalse(m.has_disentangled_ancillae)
        self.assertFalse(m.has_measured_ancillae)
        self.assertTrue(m.is_done_with_qubit_0())
        self.assertTrue(m.is_done_with_qubit_1())
        self.assertTrue(m.is_done_with_qubit_2())
        self.assertFalse(m.is_done_with_qubit_3())
        self.assertTrue(m.is_done_with_qubit_4())
        self.assertTrue(m.is_done_with_qubit_5())
        self.assertTrue(m.is_done_with_qubit_6())

        circuit.place_tick()
        b = m.run()
        self.assertFalse(b)
        self.assertTrue(m.has_initialized_ancillae)
        self.assertTrue(m.has_entangled_ancillae)
        self.assertTrue(m.has_performed_cx_0)
        self.assertTrue(m.has_performed_cx_2)
        self.assertFalse(m.has_performed_cx_3)
        self.assertTrue(m.has_performed_cx_5)
        self.assertFalse(m.has_disentangled_ancillae)
        self.assertFalse(m.has_measured_ancillae)
        self.assertTrue(m.is_done_with_qubit_0())
        self.assertTrue(m.is_done_with_qubit_1())
        self.assertTrue(m.is_done_with_qubit_2())
        self.assertFalse(m.is_done_with_qubit_3())
        self.assertTrue(m.is_done_with_qubit_4())
        self.assertTrue(m.is_done_with_qubit_5())
        self.assertTrue(m.is_done_with_qubit_6())

        m.unlock_qubit_3()

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
        self.assertTrue(m.is_done_with_qubit_0())
        self.assertTrue(m.is_done_with_qubit_1())
        self.assertTrue(m.is_done_with_qubit_2())
        self.assertTrue(m.is_done_with_qubit_3())
        self.assertTrue(m.is_done_with_qubit_4())
        self.assertTrue(m.is_done_with_qubit_5())
        self.assertTrue(m.is_done_with_qubit_6())
        expectation = prologue + textwrap.dedent(f'''
        RX 121
        R 22
        TICK
        CX 121 22
        TICK
        CX 112 22 31 121
        TICK
        CX 111 22
        TICK
        TICK
        CX 122 22''')
        self.assertEqual(str(circuit.circuit), expectation)

    def test_lock_qubit_5(self) -> None:
        mapping = QubitMapping(20, 20)

        self.assertEqual(mapping.get_id(*STEANE_0), 111)
        self.assertEqual(mapping.get_id(*STEANE_2), 31)
        self.assertEqual(mapping.get_id(*STEANE_3), 122)
        self.assertEqual(mapping.get_id(*STEANE_5), 112)

        circuit = Circuit(mapping, 0)
        prologue = str(circuit.circuit)
        m = SteaneZ0235SyndromeMeasurement(circuit)

        m.lock_qubit_5()

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
        self.assertFalse(m.is_done_with_qubit_0())
        self.assertTrue(m.is_done_with_qubit_1())
        self.assertFalse(m.is_done_with_qubit_2())
        self.assertFalse(m.is_done_with_qubit_3())
        self.assertTrue(m.is_done_with_qubit_4())
        self.assertFalse(m.is_done_with_qubit_5())
        self.assertTrue(m.is_done_with_qubit_6())

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
        self.assertFalse(m.is_done_with_qubit_0())
        self.assertTrue(m.is_done_with_qubit_1())
        self.assertFalse(m.is_done_with_qubit_2())
        self.assertFalse(m.is_done_with_qubit_3())
        self.assertTrue(m.is_done_with_qubit_4())
        self.assertFalse(m.is_done_with_qubit_5())
        self.assertTrue(m.is_done_with_qubit_6())

        circuit.place_tick()
        b = m.run()
        self.assertFalse(b)
        self.assertTrue(m.has_initialized_ancillae)
        self.assertTrue(m.has_entangled_ancillae)
        self.assertFalse(m.has_performed_cx_0)
        self.assertTrue(m.has_performed_cx_2)
        self.assertTrue(m.has_performed_cx_3)
        self.assertFalse(m.has_performed_cx_5)
        self.assertFalse(m.has_disentangled_ancillae)
        self.assertFalse(m.has_measured_ancillae)
        self.assertFalse(m.is_done_with_qubit_0())
        self.assertTrue(m.is_done_with_qubit_1())
        self.assertTrue(m.is_done_with_qubit_2())
        self.assertTrue(m.is_done_with_qubit_3())
        self.assertTrue(m.is_done_with_qubit_4())
        self.assertFalse(m.is_done_with_qubit_5())
        self.assertTrue(m.is_done_with_qubit_6())

        circuit.place_tick()
        b = m.run()
        self.assertFalse(b)
        self.assertTrue(m.has_initialized_ancillae)
        self.assertTrue(m.has_entangled_ancillae)
        self.assertTrue(m.has_performed_cx_0)
        self.assertTrue(m.has_performed_cx_2)
        self.assertTrue(m.has_performed_cx_3)
        self.assertFalse(m.has_performed_cx_5)
        self.assertFalse(m.has_disentangled_ancillae)
        self.assertFalse(m.has_measured_ancillae)
        self.assertTrue(m.is_done_with_qubit_0())
        self.assertTrue(m.is_done_with_qubit_1())
        self.assertTrue(m.is_done_with_qubit_2())
        self.assertTrue(m.is_done_with_qubit_3())
        self.assertTrue(m.is_done_with_qubit_4())
        self.assertFalse(m.is_done_with_qubit_5())
        self.assertTrue(m.is_done_with_qubit_6())

        circuit.place_tick()
        b = m.run()
        self.assertFalse(b)
        self.assertTrue(m.has_initialized_ancillae)
        self.assertTrue(m.has_entangled_ancillae)
        self.assertTrue(m.has_performed_cx_0)
        self.assertTrue(m.has_performed_cx_2)
        self.assertTrue(m.has_performed_cx_3)
        self.assertFalse(m.has_performed_cx_5)
        self.assertFalse(m.has_disentangled_ancillae)
        self.assertFalse(m.has_measured_ancillae)
        self.assertTrue(m.is_done_with_qubit_0())
        self.assertTrue(m.is_done_with_qubit_1())
        self.assertTrue(m.is_done_with_qubit_2())
        self.assertTrue(m.is_done_with_qubit_3())
        self.assertTrue(m.is_done_with_qubit_4())
        self.assertFalse(m.is_done_with_qubit_5())
        self.assertTrue(m.is_done_with_qubit_6())

        m.unlock_qubit_5()

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
        self.assertTrue(m.is_done_with_qubit_0())
        self.assertTrue(m.is_done_with_qubit_1())
        self.assertTrue(m.is_done_with_qubit_2())
        self.assertTrue(m.is_done_with_qubit_3())
        self.assertTrue(m.is_done_with_qubit_4())
        self.assertTrue(m.is_done_with_qubit_5())
        self.assertTrue(m.is_done_with_qubit_6())
        expectation = prologue + textwrap.dedent(f'''
        RX 121
        R 22
        TICK
        CX 121 22
        TICK
        CX 122 22 31 121
        TICK
        CX 111 22
        TICK
        TICK
        CX 112 22''')
        self.assertEqual(str(circuit.circuit), expectation)


class SteaneZ0246SyndromeMeasurementTest(unittest.TestCase):
    def test_run(self) -> None:
        mapping = QubitMapping(20, 20)

        self.assertEqual(mapping.get_id(*STEANE_0), 111)
        self.assertEqual(mapping.get_id(*STEANE_2), 31)
        self.assertEqual(mapping.get_id(*STEANE_4), 11)
        self.assertEqual(mapping.get_id(*STEANE_6), 10)

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
        self.assertFalse(m.is_done_with_qubit_0())
        self.assertTrue(m.is_done_with_qubit_1())
        self.assertFalse(m.is_done_with_qubit_2())
        self.assertTrue(m.is_done_with_qubit_3())
        self.assertFalse(m.is_done_with_qubit_4())
        self.assertTrue(m.is_done_with_qubit_5())
        self.assertFalse(m.is_done_with_qubit_6())
        expectation = prologue + textwrap.dedent(f'''
        R 21
        RX 110 120''')
        self.assertEqual(str(circuit.circuit), expectation)

        b = m.run()
        self.assertFalse(b)
        expectation = prologue + textwrap.dedent(f'''
        R 21
        RX 110 120''')
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
        self.assertFalse(m.is_done_with_qubit_0())
        self.assertTrue(m.is_done_with_qubit_1())
        self.assertFalse(m.is_done_with_qubit_2())
        self.assertTrue(m.is_done_with_qubit_3())
        self.assertFalse(m.is_done_with_qubit_4())
        self.assertTrue(m.is_done_with_qubit_5())
        self.assertFalse(m.is_done_with_qubit_6())
        expectation = prologue + textwrap.dedent(f'''
        R 21
        RX 110 120
        TICK
        CX 110 21''')
        self.assertEqual(str(circuit.circuit), expectation)

        circuit.place_tick()
        b = m.run()
        self.assertFalse(b)
        self.assertTrue(m.has_initialized_ancillae)
        self.assertTrue(m.has_entangled_ancillae_ab)
        self.assertTrue(m.has_entangled_ancillae_ac)
        self.assertFalse(m.has_performed_cx_0)
        self.assertFalse(m.has_performed_cx_2)
        self.assertTrue(m.has_performed_cx_4)
        self.assertFalse(m.has_performed_cx_6)
        self.assertFalse(m.has_disentangled_ancillae_ab)
        self.assertFalse(m.has_disentangled_ancillae_ac)
        self.assertFalse(m.has_measured_ancillae)
        self.assertFalse(m.is_done_with_qubit_0())
        self.assertTrue(m.is_done_with_qubit_1())
        self.assertFalse(m.is_done_with_qubit_2())
        self.assertTrue(m.is_done_with_qubit_3())
        self.assertTrue(m.is_done_with_qubit_4())
        self.assertTrue(m.is_done_with_qubit_5())
        self.assertFalse(m.is_done_with_qubit_6())
        expectation = prologue + textwrap.dedent(f'''
        R 21
        RX 110 120
        TICK
        CX 110 21
        TICK
        CX 120 21 11 110''')
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
        self.assertTrue(m.is_done_with_qubit_0())
        self.assertTrue(m.is_done_with_qubit_1())
        self.assertTrue(m.is_done_with_qubit_2())
        self.assertTrue(m.is_done_with_qubit_3())
        self.assertTrue(m.is_done_with_qubit_4())
        self.assertTrue(m.is_done_with_qubit_5())
        self.assertTrue(m.is_done_with_qubit_6())
        expectation = prologue + textwrap.dedent(f'''
        R 21
        RX 110 120
        TICK
        CX 110 21
        TICK
        CX 120 21 11 110
        TICK
        CX 111 21 31 120 10 110''')
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
        self.assertTrue(m.is_done_with_qubit_0())
        self.assertTrue(m.is_done_with_qubit_1())
        self.assertTrue(m.is_done_with_qubit_2())
        self.assertTrue(m.is_done_with_qubit_3())
        self.assertTrue(m.is_done_with_qubit_4())
        self.assertTrue(m.is_done_with_qubit_5())
        self.assertTrue(m.is_done_with_qubit_6())
        expectation = prologue + textwrap.dedent(f'''
        R 21
        RX 110 120
        TICK
        CX 110 21
        TICK
        CX 120 21 11 110
        TICK
        CX 111 21 31 120 10 110
        TICK
        CX 110 21''')
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
        self.assertTrue(m.is_done_with_qubit_0())
        self.assertTrue(m.is_done_with_qubit_1())
        self.assertTrue(m.is_done_with_qubit_2())
        self.assertTrue(m.is_done_with_qubit_3())
        self.assertTrue(m.is_done_with_qubit_4())
        self.assertTrue(m.is_done_with_qubit_5())
        self.assertTrue(m.is_done_with_qubit_6())
        expectation = prologue + textwrap.dedent(f'''
        R 21
        RX 110 120
        TICK
        CX 110 21
        TICK
        CX 120 21 11 110
        TICK
        CX 111 21 31 120 10 110
        TICK
        CX 110 21
        TICK
        CX 120 21''')
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
        self.assertTrue(m.is_done_with_qubit_0())
        self.assertTrue(m.is_done_with_qubit_1())
        self.assertTrue(m.is_done_with_qubit_2())
        self.assertTrue(m.is_done_with_qubit_3())
        self.assertTrue(m.is_done_with_qubit_4())
        self.assertTrue(m.is_done_with_qubit_5())
        self.assertTrue(m.is_done_with_qubit_6())
        expectation = prologue + textwrap.dedent(f'''
        R 21
        RX 110 120
        TICK
        CX 110 21
        TICK
        CX 120 21 11 110
        TICK
        CX 111 21 31 120 10 110
        TICK
        CX 110 21
        TICK
        CX 120 21
        TICK
        M 21
        DETECTOR rec[-1]
        MX 110
        DETECTOR rec[-1]
        MX 120
        DETECTOR rec[-1]''')
        self.assertEqual(str(circuit.circuit), expectation)
        self.assertEqual(circuit.detectors_for_post_selection, [
            DetectorIdentifier(0), DetectorIdentifier(1), DetectorIdentifier(2)
        ])


class SteaneInitializationTest(unittest.TestCase):
    def test_plus(self) -> None:
        mapping = QubitMapping(20, 20)
        stim_circuit = stim.Circuit()

        perform_perfect_steane_plus_initialization(stim_circuit, mapping)
        stim_circuit.append('MX', [mapping.get_id(*STEANE_0)])
        stim_circuit.append('MX', [mapping.get_id(*STEANE_1)])
        stim_circuit.append('MX', [mapping.get_id(*STEANE_2)])
        stim_circuit.append('MX', [mapping.get_id(*STEANE_3)])
        stim_circuit.append('MX', [mapping.get_id(*STEANE_4)])
        stim_circuit.append('MX', [mapping.get_id(*STEANE_5)])
        stim_circuit.append('MX', [mapping.get_id(*STEANE_6)])
        stim_circuit.append('DETECTOR', [stim.target_rec(i) for i in range(-7, 0)])

        # Asserting that the detector event is deterministic.
        stim_circuit.detector_error_model()

    def test_zero(self) -> None:
        mapping = QubitMapping(20, 20)
        stim_circuit = stim.Circuit()

        perform_perfect_steane_zero_initialization(stim_circuit, mapping)
        stim_circuit.append('M', [mapping.get_id(*STEANE_0)])
        stim_circuit.append('M', [mapping.get_id(*STEANE_1)])
        stim_circuit.append('M', [mapping.get_id(*STEANE_2)])
        stim_circuit.append('M', [mapping.get_id(*STEANE_3)])
        stim_circuit.append('M', [mapping.get_id(*STEANE_4)])
        stim_circuit.append('M', [mapping.get_id(*STEANE_5)])
        stim_circuit.append('M', [mapping.get_id(*STEANE_6)])
        stim_circuit.append('DETECTOR', [stim.target_rec(i) for i in range(-7, 0)])

        # Asserting that the detector event is deterministic.
        stim_circuit.detector_error_model()

    def test_s_plus(self) -> None:
        mapping = QubitMapping(20, 20)
        stim_circuit = stim.Circuit()

        perform_perfect_steane_s_plus_initialization(stim_circuit, mapping)
        stim_circuit.append('MY', [mapping.get_id(*STEANE_0)])
        stim_circuit.append('MY', [mapping.get_id(*STEANE_1)])
        stim_circuit.append('MY', [mapping.get_id(*STEANE_2)])
        stim_circuit.append('MY', [mapping.get_id(*STEANE_3)])
        stim_circuit.append('MY', [mapping.get_id(*STEANE_4)])
        stim_circuit.append('MY', [mapping.get_id(*STEANE_5)])
        stim_circuit.append('MY', [mapping.get_id(*STEANE_6)])
        stim_circuit.append('DETECTOR', [stim.target_rec(i) for i in range(-7, 0)])

        # Asserting that the detector event is deterministic.
        stim_circuit.detector_error_model()

    def test_injection(self) -> None:
        mapping = QubitMapping(20, 20)
        circuit = Circuit(mapping, 0)
        stim_circuit = circuit.circuit

        perform_injection(circuit)
        stim_circuit.append('MY', [mapping.get_id(*STEANE_0_INJECTION)])
        stim_circuit.append('MY', [mapping.get_id(*STEANE_1_INJECTION)])
        stim_circuit.append('MY', [mapping.get_id(*STEANE_2_INJECTION)])
        stim_circuit.append('MY', [mapping.get_id(*STEANE_3_INJECTION)])
        stim_circuit.append('MY', [mapping.get_id(*STEANE_4_INJECTION)])
        stim_circuit.append('MY', [mapping.get_id(*STEANE_5_INJECTION)])
        stim_circuit.append('MY', [mapping.get_id(*STEANE_6_INJECTION)])
        stim_circuit.append('DETECTOR', [stim.target_rec(i) for i in range(-7, 0)])

        # Asserting that the detector event is deterministic.
        stim_circuit.detector_error_model()

    def test_syndrome_extraction_after_injection(self) -> None:
        mapping = QubitMapping(20, 20)
        circuit = Circuit(mapping, 0)
        stim_circuit = circuit.circuit

        perform_injection(circuit)
        circuit.place_tick()
        perform_syndrome_extraction_after_injection(circuit)
        circuit.place_tick()

        stim_circuit.append('MY', [mapping.get_id(*STEANE_0)])
        stim_circuit.append('MY', [mapping.get_id(*STEANE_1)])
        stim_circuit.append('MY', [mapping.get_id(*STEANE_2)])
        stim_circuit.append('MY', [mapping.get_id(*STEANE_3)])
        stim_circuit.append('MY', [mapping.get_id(*STEANE_4)])
        stim_circuit.append('MY', [mapping.get_id(*STEANE_5)])
        stim_circuit.append('MY', [mapping.get_id(*STEANE_6)])
        stim_circuit.append('DETECTOR', [stim.target_rec(i) for i in range(-7, 0)])

        # Asserting that the detector event is deterministic.
        stim_circuit.detector_error_model()

    def test_check(self) -> None:
        mapping = QubitMapping(20, 20)
        circuit = Circuit(mapping, 0)
        stim_circuit = circuit.circuit

        perform_injection(circuit)
        circuit.place_tick()
        perform_syndrome_extraction_after_injection(circuit)

        circuit.place_tick()
        perform_check(circuit)

        stim_circuit.append('MY', [mapping.get_id(*STEANE_0)])
        stim_circuit.append('MY', [mapping.get_id(*STEANE_1)])
        stim_circuit.append('MY', [mapping.get_id(*STEANE_2)])
        stim_circuit.append('MY', [mapping.get_id(*STEANE_3)])
        stim_circuit.append('MY', [mapping.get_id(*STEANE_4)])
        stim_circuit.append('MY', [mapping.get_id(*STEANE_5)])
        stim_circuit.append('MY', [mapping.get_id(*STEANE_6)])
        stim_circuit.append('DETECTOR', [stim.target_rec(i) for i in range(-7, 0)])

        # Asserting that the detector event is deterministic.
        stim_circuit.detector_error_model()
