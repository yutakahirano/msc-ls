import textwrap
import unittest

from steane_code import *
from surface_code import SurfaceSyndromeMeasurement, SurfaceXSyndromeMeasurement, SurfaceZSyndromeMeasurement
from surface_code import SurfaceStabilizerPattern
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

    def test_xz_syndrome_extraction_after_injection(self) -> None:
        mapping = QubitMapping(20, 20)
        circuit = Circuit(mapping, 0)
        stim_circuit = circuit.circuit

        perform_injection(circuit)
        circuit.place_tick()
        perform_xz_syndrome_extraction_after_injection(circuit)
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

    def test_zx_syndrome_extraction_after_injection(self) -> None:
        mapping = QubitMapping(20, 20)
        circuit = Circuit(mapping, 0)
        stim_circuit = circuit.circuit

        perform_injection(circuit)
        circuit.place_tick()
        perform_zx_syndrome_extraction_after_injection(circuit)
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
        perform_xz_syndrome_extraction_after_injection(circuit)

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

    def _setup_surface_code_patch_to_plus(
            self, circuit: Circuit, surface_offset: tuple[int, int], surface_distance: int,
            surface_syndrome_measurements: dict[tuple[int, int], SurfaceSyndromeMeasurement]) -> None:
        FOUR_WEIGHT = SurfaceStabilizerPattern.FOUR_WEIGHT
        TWO_WEIGHT_UP = SurfaceStabilizerPattern.TWO_WEIGHT_UP
        TWO_WEIGHT_DOWN = SurfaceStabilizerPattern.TWO_WEIGHT_DOWN
        TWO_WEIGHT_LEFT = SurfaceStabilizerPattern.TWO_WEIGHT_LEFT
        TWO_WEIGHT_RIGHT = SurfaceStabilizerPattern.TWO_WEIGHT_RIGHT
        SURFACE_SYNDROME_MEASUREMENT_DEPTH = 6

        (surface_offset_x, surface_offset_y) = surface_offset

        m: SurfaceSyndromeMeasurement
        # Initializing the surface code patch. The logical state is \ket{+}.
        for i in range(surface_distance):
            for j in range(surface_distance):
                x = surface_offset_x + j * 2
                y = surface_offset_y + i * 2
                circuit.place_reset_x((x, y))

                # Weight-two syndrome measurements:
                if i == 0 and j % 2 == 0 and j < surface_distance - 1:
                    m = SurfaceXSyndromeMeasurement(circuit, (x + 1, y - 1), TWO_WEIGHT_DOWN, True)
                    surface_syndrome_measurements[(x + 1, y - 1)] = m
                if i == surface_distance - 1 and j % 2 == 1 and j < surface_distance - 1:
                    m = SurfaceXSyndromeMeasurement(circuit, (x + 1, y + 1), TWO_WEIGHT_UP, True)
                    surface_syndrome_measurements[(x + 1, y + 1)] = m
                if j == 0 and i % 2 == 1 and i < surface_distance - 1:
                    m = SurfaceZSyndromeMeasurement(circuit, (x - 1, y + 1), TWO_WEIGHT_RIGHT, False)
                    surface_syndrome_measurements[(x - 1, y + 1)] = m
                if j == surface_distance - 1 and i % 2 == 0 and i < surface_distance - 1:
                    m = SurfaceZSyndromeMeasurement(circuit, (x + 1, y + 1), TWO_WEIGHT_LEFT, False)
                    surface_syndrome_measurements[(x + 1, y + 1)] = m

                # Weight-four syndrome measurements:
                if i < surface_distance - 1 and j < surface_distance - 1:
                    if (i + j) % 2 == 0:
                        m = SurfaceZSyndromeMeasurement(circuit, (x + 1, y + 1), FOUR_WEIGHT, False)
                    else:
                        m = SurfaceXSyndromeMeasurement(circuit, (x + 1, y + 1), FOUR_WEIGHT, True)
                    surface_syndrome_measurements[(x + 1, y + 1)] = m
        for _ in range(SURFACE_SYNDROME_MEASUREMENT_DEPTH):
            for m in surface_syndrome_measurements.values():
                m.run()
            circuit.place_tick()

        # Remove some syndrome measurements before the lattice surgery.
        for j in range(surface_distance):
            x = surface_offset_x + j * 2
            y = surface_offset_y
            if j % 2 == 0 and j < surface_distance - 1:
                del surface_syndrome_measurements[(x + 1, y - 1)]

    def test_lattice_surgery_xzz_plus(self) -> None:
        mapping = QubitMapping(20, 20)
        circuit = Circuit(mapping, 0)
        stim_circuit = circuit.circuit
        surface_distance = 5
        results = LatticeSurgeryMeasurements()
        surface_offset_x = 1
        surface_offset_y = 7
        SURFACE_SYNDROME_MEASUREMENT_DEPTH = 6

        TWO_WEIGHT_DOWN = SurfaceStabilizerPattern.TWO_WEIGHT_DOWN

        surface_syndrome_measurements: dict[tuple[int, int], SurfaceSyndromeMeasurement] = {}
        # Initializing the surface code patch. The logical state is \ket{+}.
        self._setup_surface_code_patch_to_plus(
            circuit, (surface_offset_x, surface_offset_y), surface_distance,
            surface_syndrome_measurements)

        perform_perfect_steane_plus_initialization(stim_circuit, mapping)
        circuit.place_tick()

        g = lattice_surgery_generator_xzz(circuit, surface_distance, results)

        tick = 0
        while not results.is_complete():
            if tick >= 3:
                for m in surface_syndrome_measurements.values():
                    m.run()

            try:
                next(g)
            except StopIteration:
                assert results.is_complete()

            circuit.place_tick()
            tick += 1

        for m in surface_syndrome_measurements.values():
            assert m.is_complete()

        # Reconfigure some syndrome measurements after the lattice surgery.
        for j in range(surface_distance):
            x = surface_offset_x + j * 2
            y = surface_offset_y
            if j % 2 == 0 and j < surface_distance - 1:
                m = SurfaceXSyndromeMeasurement(circuit, (x + 1, y - 1), TWO_WEIGHT_DOWN, False)
                surface_syndrome_measurements[(x + 1, y - 1)] = m

        for _ in range(SURFACE_SYNDROME_MEASUREMENT_DEPTH * 2):
            for m in surface_syndrome_measurements.values():
                m.run()
            circuit.place_tick()

        last = surface_syndrome_measurements[(surface_offset_x + 1, surface_offset_y - 1)].last_measurement
        assert last is not None
        # Place a detector for the six-weight syndrome.
        circuit.place_detector(results.x_0145_measurements() + [last], post_selection=True)

        # Place an observable for the logical value.
        logical_x_pauli_string = stim.PauliString()
        for i in range(surface_distance):
            x = surface_offset_x
            y = surface_offset_y + i * 2
            logical_x_pauli_string *= stim.PauliString('X{}'.format(mapping.get_id(x, y)))
        circuit.place_observable_include(
            [circuit.place_mpp(logical_x_pauli_string)] + results.logical_x_measurements())

        # Asserting that the detector event model is deterministic.
        stim_circuit.detector_error_model()

    def test_lattice_surgery_xzz_zero(self) -> None:
        mapping = QubitMapping(20, 20)
        circuit = Circuit(mapping, 0)
        stim_circuit = circuit.circuit
        surface_distance = 5
        results = LatticeSurgeryMeasurements()
        surface_offset_x = 1
        surface_offset_y = 7
        SURFACE_SYNDROME_MEASUREMENT_DEPTH = 6

        TWO_WEIGHT_DOWN = SurfaceStabilizerPattern.TWO_WEIGHT_DOWN

        surface_syndrome_measurements: dict[tuple[int, int], SurfaceSyndromeMeasurement] = {}
        # Initializing the surface code patch. The logical state is \ket{+}.
        self._setup_surface_code_patch_to_plus(
            circuit, (surface_offset_x, surface_offset_y), surface_distance,
            surface_syndrome_measurements)

        perform_perfect_steane_zero_initialization(stim_circuit, mapping)
        circuit.place_tick()

        g = lattice_surgery_generator_xzz(circuit, surface_distance, results)

        tick = 0
        while not results.is_complete():
            if tick >= 3:
                for m in surface_syndrome_measurements.values():
                    m.run()

            try:
                next(g)
            except StopIteration:
                assert results.is_complete()

            circuit.place_tick()
            tick += 1

        for m in surface_syndrome_measurements.values():
            assert m.is_complete()

        # Reconfigure some syndrome measurements after the lattice surgery.
        for j in range(surface_distance):
            x = surface_offset_x + j * 2
            y = surface_offset_y
            if j % 2 == 0 and j < surface_distance - 1:
                m = SurfaceXSyndromeMeasurement(circuit, (x + 1, y - 1), TWO_WEIGHT_DOWN, False)
                surface_syndrome_measurements[(x + 1, y - 1)] = m

        for _ in range(SURFACE_SYNDROME_MEASUREMENT_DEPTH * 2):
            for m in surface_syndrome_measurements.values():
                m.run()
            circuit.place_tick()

        last = surface_syndrome_measurements[(surface_offset_x + 1, surface_offset_y - 1)].last_measurement
        assert last is not None
        # Place a detector for the six-weight syndrome.
        circuit.place_detector(results.x_0145_measurements() + [last], post_selection=True)

        # Place an observable for the logical value.
        logical_z_pauli_string = stim.PauliString()
        for j in range(surface_distance):
            x = surface_offset_x + j * 2
            y = surface_offset_y
            logical_z_pauli_string *= stim.PauliString('Z{}'.format(mapping.get_id(x, y)))
        circuit.place_observable_include(
            [circuit.place_mpp(logical_z_pauli_string)] + results.lattice_surgery_zz_measurements())

        # Asserting that the detector event model is deterministic.
        stim_circuit.detector_error_model()

    def test_lattice_surgery_zz_plus(self) -> None:
        mapping = QubitMapping(20, 20)
        circuit = Circuit(mapping, 0)
        stim_circuit = circuit.circuit
        surface_distance = 5
        results = LatticeSurgeryMeasurements()
        surface_offset_x = 1
        surface_offset_y = 7
        SURFACE_SYNDROME_MEASUREMENT_DEPTH = 6

        TWO_WEIGHT_DOWN = SurfaceStabilizerPattern.TWO_WEIGHT_DOWN

        surface_syndrome_measurements: dict[tuple[int, int], SurfaceSyndromeMeasurement] = {}
        # Initializing the surface code patch. The logical state is \ket{+}.
        self._setup_surface_code_patch_to_plus(
            circuit, (surface_offset_x, surface_offset_y), surface_distance,
            surface_syndrome_measurements)

        perform_perfect_steane_plus_initialization(stim_circuit, mapping)
        circuit.place_tick()

        g = lattice_surgery_generator_zz(circuit, surface_distance, results)

        tick = 0
        while not results.is_complete():
            for m in surface_syndrome_measurements.values():
                m.run()

            try:
                next(g)
            except StopIteration:
                assert results.is_complete()

            circuit.place_tick()

        for m in surface_syndrome_measurements.values():
            assert m.is_complete()

        # Reconfigure some syndrome measurements after the lattice surgery.
        for j in range(surface_distance):
            x = surface_offset_x + j * 2
            y = surface_offset_y
            if j % 2 == 0 and j < surface_distance - 1:
                m = SurfaceXSyndromeMeasurement(circuit, (x + 1, y - 1), TWO_WEIGHT_DOWN, False)
                surface_syndrome_measurements[(x + 1, y - 1)] = m

        for _ in range(SURFACE_SYNDROME_MEASUREMENT_DEPTH * 2):
            for m in surface_syndrome_measurements.values():
                m.run()
            circuit.place_tick()

        last = surface_syndrome_measurements[(surface_offset_x + 1, surface_offset_y - 1)].last_measurement
        assert last is not None
        # Place a detector for the six-weight syndrome.
        circuit.place_detector(results.x_0145_measurements() + [last], post_selection=True)

        # Place an observable for the logical value.
        logical_x_pauli_string = stim.PauliString()
        for i in range(surface_distance):
            x = surface_offset_x
            y = surface_offset_y + i * 2
            logical_x_pauli_string *= stim.PauliString('X{}'.format(mapping.get_id(x, y)))
        circuit.place_observable_include(
            [circuit.place_mpp(logical_x_pauli_string)] + results.logical_x_measurements())

        # Asserting that the detector event model is deterministic.
        stim_circuit.detector_error_model()

    def test_lattice_surgery_zz_zero(self) -> None:
        mapping = QubitMapping(20, 20)
        circuit = Circuit(mapping, 0)
        stim_circuit = circuit.circuit
        surface_distance = 5
        results = LatticeSurgeryMeasurements()
        surface_offset_x = 1
        surface_offset_y = 7
        SURFACE_SYNDROME_MEASUREMENT_DEPTH = 6

        TWO_WEIGHT_DOWN = SurfaceStabilizerPattern.TWO_WEIGHT_DOWN

        surface_syndrome_measurements: dict[tuple[int, int], SurfaceSyndromeMeasurement] = {}
        # Initializing the surface code patch. The logical state is \ket{+}.
        self._setup_surface_code_patch_to_plus(
            circuit, (surface_offset_x, surface_offset_y), surface_distance,
            surface_syndrome_measurements)

        perform_perfect_steane_zero_initialization(stim_circuit, mapping)
        circuit.place_tick()

        g = lattice_surgery_generator_zz(circuit, surface_distance, results)

        tick = 0
        while not results.is_complete():
            for m in surface_syndrome_measurements.values():
                m.run()

            try:
                next(g)
            except StopIteration:
                assert results.is_complete()

            circuit.place_tick()

        for m in surface_syndrome_measurements.values():
            assert m.is_complete()

        # Reconfigure some syndrome measurements after the lattice surgery.
        for j in range(surface_distance):
            x = surface_offset_x + j * 2
            y = surface_offset_y
            if j % 2 == 0 and j < surface_distance - 1:
                m = SurfaceXSyndromeMeasurement(circuit, (x + 1, y - 1), TWO_WEIGHT_DOWN, False)
                surface_syndrome_measurements[(x + 1, y - 1)] = m

        for _ in range(SURFACE_SYNDROME_MEASUREMENT_DEPTH * 2):
            for m in surface_syndrome_measurements.values():
                m.run()
            circuit.place_tick()

        last = surface_syndrome_measurements[(surface_offset_x + 1, surface_offset_y - 1)].last_measurement
        assert last is not None
        # Place a detector for the six-weight syndrome.
        circuit.place_detector(results.x_0145_measurements() + [last], post_selection=True)

        # Place an observable for the logical value.
        logical_z_pauli_string = stim.PauliString()
        for j in range(surface_distance):
            x = surface_offset_x + j * 2
            y = surface_offset_y
            logical_z_pauli_string *= stim.PauliString('Z{}'.format(mapping.get_id(x, y)))
        circuit.place_observable_include(
            [circuit.place_mpp(logical_z_pauli_string)] + results.lattice_surgery_zz_measurements())

        # Asserting that the detector event model is deterministic.
        stim_circuit.detector_error_model()

    def test_lattice_surgery_zxz_plus(self) -> None:
        mapping = QubitMapping(20, 20)
        circuit = Circuit(mapping, 0)
        stim_circuit = circuit.circuit
        surface_distance = 5
        results = LatticeSurgeryMeasurements()
        surface_offset_x = 1
        surface_offset_y = 7
        SURFACE_SYNDROME_MEASUREMENT_DEPTH = 6

        TWO_WEIGHT_DOWN = SurfaceStabilizerPattern.TWO_WEIGHT_DOWN

        surface_syndrome_measurements: dict[tuple[int, int], SurfaceSyndromeMeasurement] = {}
        # Initializing the surface code patch. The logical state is \ket{+}.
        self._setup_surface_code_patch_to_plus(
            circuit, (surface_offset_x, surface_offset_y), surface_distance,
            surface_syndrome_measurements)

        perform_perfect_steane_plus_initialization(stim_circuit, mapping)
        circuit.place_tick()

        g = lattice_surgery_generator_zxz(circuit, surface_distance, results)

        tick = 0
        while not results.is_complete():
            for m in surface_syndrome_measurements.values():
                m.run()

            try:
                next(g)
            except StopIteration:
                assert results.is_complete()

            circuit.place_tick()

        for m in surface_syndrome_measurements.values():
            assert m.is_complete()

        # Reconfigure some syndrome measurements after the lattice surgery.
        for j in range(surface_distance):
            x = surface_offset_x + j * 2
            y = surface_offset_y
            if j % 2 == 0 and j < surface_distance - 1:
                m = SurfaceXSyndromeMeasurement(circuit, (x + 1, y - 1), TWO_WEIGHT_DOWN, False)
                surface_syndrome_measurements[(x + 1, y - 1)] = m

        for _ in range(SURFACE_SYNDROME_MEASUREMENT_DEPTH * 2):
            for m in surface_syndrome_measurements.values():
                m.run()
            circuit.place_tick()

        last = surface_syndrome_measurements[(surface_offset_x + 1, surface_offset_y - 1)].last_measurement
        assert last is not None
        # Place a detector for the six-weight syndrome.
        circuit.place_detector(results.x_0145_measurements() + [last], post_selection=True)

        # Place an observable for the logical value.
        logical_x_pauli_string = stim.PauliString()
        for i in range(surface_distance):
            x = surface_offset_x
            y = surface_offset_y + i * 2
            logical_x_pauli_string *= stim.PauliString('X{}'.format(mapping.get_id(x, y)))
        circuit.place_observable_include(
            [circuit.place_mpp(logical_x_pauli_string)] + results.logical_x_measurements())

        # Asserting that the detector event model is deterministic.
        stim_circuit.detector_error_model()

    def test_lattice_surgery_zxz_zero(self) -> None:
        mapping = QubitMapping(20, 20)
        circuit = Circuit(mapping, 0)
        stim_circuit = circuit.circuit
        surface_distance = 5
        results = LatticeSurgeryMeasurements()
        surface_offset_x = 1
        surface_offset_y = 7
        SURFACE_SYNDROME_MEASUREMENT_DEPTH = 6

        TWO_WEIGHT_DOWN = SurfaceStabilizerPattern.TWO_WEIGHT_DOWN

        surface_syndrome_measurements: dict[tuple[int, int], SurfaceSyndromeMeasurement] = {}
        # Initializing the surface code patch. The logical state is \ket{+}.
        self._setup_surface_code_patch_to_plus(
            circuit, (surface_offset_x, surface_offset_y), surface_distance,
            surface_syndrome_measurements)

        perform_perfect_steane_zero_initialization(stim_circuit, mapping)
        circuit.place_tick()

        g = lattice_surgery_generator_zxz(circuit, surface_distance, results)

        tick = 0
        while not results.is_complete():
            for m in surface_syndrome_measurements.values():
                m.run()

            try:
                next(g)
            except StopIteration:
                assert results.is_complete()

            circuit.place_tick()

        for m in surface_syndrome_measurements.values():
            assert m.is_complete()

        # Reconfigure some syndrome measurements after the lattice surgery.
        for j in range(surface_distance):
            x = surface_offset_x + j * 2
            y = surface_offset_y
            if j % 2 == 0 and j < surface_distance - 1:
                m = SurfaceXSyndromeMeasurement(circuit, (x + 1, y - 1), TWO_WEIGHT_DOWN, False)
                surface_syndrome_measurements[(x + 1, y - 1)] = m

        for _ in range(SURFACE_SYNDROME_MEASUREMENT_DEPTH * 2):
            for m in surface_syndrome_measurements.values():
                m.run()
            circuit.place_tick()

        last = surface_syndrome_measurements[(surface_offset_x + 1, surface_offset_y - 1)].last_measurement
        assert last is not None
        # Place a detector for the six-weight syndrome.
        circuit.place_detector(results.x_0145_measurements() + [last], post_selection=True)

        # Place an observable for the logical value.
        logical_z_pauli_string = stim.PauliString()
        for j in range(surface_distance):
            x = surface_offset_x + j * 2
            y = surface_offset_y
            logical_z_pauli_string *= stim.PauliString('Z{}'.format(mapping.get_id(x, y)))
        circuit.place_observable_include(
            [circuit.place_mpp(logical_z_pauli_string)] + results.lattice_surgery_zz_measurements())

        # Asserting that the detector event model is deterministic.
        stim_circuit.detector_error_model()
