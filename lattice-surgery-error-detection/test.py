import textwrap
import unittest

from main import *


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


class SurfaceFourWeightZSyndromeMeasurementTest(unittest.TestCase):
    def test_run_four_weight(self) -> None:
        mapping = QubitMapping(20, 20)

        ancilla_position = (6, 6)
        left_top = (5, 5)
        left_bottom = (5, 7)
        right_top = (7, 5)
        right_bottom = (7, 7)
        self.assertEqual(mapping.get_id(*ancilla_position), 33)
        self.assertEqual(mapping.get_id(*left_top), 122)
        self.assertEqual(mapping.get_id(*left_bottom), 123)
        self.assertEqual(mapping.get_id(*right_top), 132)
        self.assertEqual(mapping.get_id(*right_bottom), 133)

        circuit = Circuit(mapping, 0)
        prologue = str(circuit.circuit)
        m = SurfaceZSyndromeMeasurement(circuit, ancilla_position, SurfaceStabilizerPattern.FOUR_WEIGHT, False)
        self.assertTrue(m.is_complete())

        m.run()
        self.assertEqual(m.stage, 1)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            R 33'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 2)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            R 33
            TICK
            CX 122 33'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 3)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            R 33
            TICK
            CX 122 33
            TICK
            CX 123 33'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 4)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            R 33
            TICK
            CX 122 33
            TICK
            CX 123 33
            TICK
            CX 132 33'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 5)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            R 33
            TICK
            CX 122 33
            TICK
            CX 123 33
            TICK
            CX 132 33
            TICK
            CX 133 33'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 0)
        self.assertTrue(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            R 33
            TICK
            CX 122 33
            TICK
            CX 123 33
            TICK
            CX 132 33
            TICK
            CX 133 33
            TICK
            M 33'''))

        for i in range(6):
            circuit.place_tick()
            m.run()
        self.assertEqual(m.stage, 0)
        self.assertTrue(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            R 33
            TICK
            CX 122 33
            TICK
            CX 123 33
            TICK
            CX 132 33
            TICK
            CX 133 33
            TICK
            M 33
            TICK
            R 33
            TICK
            CX 122 33
            TICK
            CX 123 33
            TICK
            CX 132 33
            TICK
            CX 133 33
            TICK
            M 33
            DETECTOR rec[-2] rec[-1]'''))
        self.assertEqual(circuit.detectors_for_post_selection, [])
        m.set_post_selection(True)

        for i in range(6):
            circuit.place_tick()
            m.run()
        self.assertEqual(m.stage, 0)
        self.assertTrue(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            R 33
            TICK
            CX 122 33
            TICK
            CX 123 33
            TICK
            CX 132 33
            TICK
            CX 133 33
            TICK
            M 33
            TICK
            R 33
            TICK
            CX 122 33
            TICK
            CX 123 33
            TICK
            CX 132 33
            TICK
            CX 133 33
            TICK
            M 33
            DETECTOR rec[-2] rec[-1]
            TICK
            R 33
            TICK
            CX 122 33
            TICK
            CX 123 33
            TICK
            CX 132 33
            TICK
            CX 133 33
            TICK
            M 33
            DETECTOR rec[-2] rec[-1]'''))
        self.assertEqual(circuit.detectors_for_post_selection, [DetectorIdentifier(1)])

    def test_run_up(self) -> None:
        mapping = QubitMapping(20, 20)

        ancilla_position = (4, 4)
        left_top = (3, 3)
        left_bottom = (3, 5)
        right_top = (5, 3)
        right_bottom = (5, 5)
        self.assertEqual(mapping.get_id(*ancilla_position), 22)
        self.assertEqual(mapping.get_id(*left_top), 111)
        self.assertEqual(mapping.get_id(*left_bottom), 112)
        self.assertEqual(mapping.get_id(*right_top), 121)
        self.assertEqual(mapping.get_id(*right_bottom), 122)

        circuit = Circuit(mapping, 0)
        prologue = str(circuit.circuit)
        m = SurfaceZSyndromeMeasurement(circuit, ancilla_position, SurfaceStabilizerPattern.TWO_WEIGHT_UP, False)

        m.run()
        self.assertEqual(m.stage, 1)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            R 22'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 2)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            R 22
            TICK
            CX 111 22'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 3)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            R 22
            TICK
            CX 111 22
            TICK'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 4)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            R 22
            TICK
            CX 111 22
            TICK
            TICK
            CX 121 22'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 5)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            R 22
            TICK
            CX 111 22
            TICK
            TICK
            CX 121 22
            TICK
            M 22'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 0)
        self.assertTrue(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            R 22
            TICK
            CX 111 22
            TICK
            TICK
            CX 121 22
            TICK
            M 22
            TICK'''))

        # Let's see if `m` can work with a four-weight X syndrome measurement positioned above.
        mx = SurfaceXSyndromeMeasurement(circuit, (4, 2), SurfaceStabilizerPattern.FOUR_WEIGHT, False)
        for i in range(6):
            circuit.place_tick()
            m.run()
            mx.run()

    def test_run_down(self) -> None:
        mapping = QubitMapping(20, 20)

        ancilla_position = (4, 4)
        left_top = (3, 3)
        left_bottom = (3, 5)
        right_top = (5, 3)
        right_bottom = (5, 5)
        self.assertEqual(mapping.get_id(*ancilla_position), 22)
        self.assertEqual(mapping.get_id(*left_top), 111)
        self.assertEqual(mapping.get_id(*left_bottom), 112)
        self.assertEqual(mapping.get_id(*right_top), 121)
        self.assertEqual(mapping.get_id(*right_bottom), 122)

        circuit = Circuit(mapping, 0)
        prologue = str(circuit.circuit)
        m = SurfaceZSyndromeMeasurement(circuit, ancilla_position, SurfaceStabilizerPattern.TWO_WEIGHT_DOWN, False)

        m.run()
        self.assertEqual(m.stage, 1)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue)

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 2)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            TICK
            R 22'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 3)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            TICK
            R 22
            TICK
            CX 112 22'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 4)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            TICK
            R 22
            TICK
            CX 112 22
            TICK'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 5)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            TICK
            R 22
            TICK
            CX 112 22
            TICK
            TICK
            CX 122 22'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 0)
        self.assertTrue(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            TICK
            R 22
            TICK
            CX 112 22
            TICK
            TICK
            CX 122 22
            TICK
            M 22'''))

        # Let's see if `m` can work with a four-weight X syndrome measurement positioned below.
        mx = SurfaceXSyndromeMeasurement(circuit, (4, 6), SurfaceStabilizerPattern.FOUR_WEIGHT, False)
        for i in range(6):
            circuit.place_tick()
            m.run()
            mx.run()

    def test_run_left(self) -> None:
        mapping = QubitMapping(20, 20)

        ancilla_position = (4, 4)
        left_top = (3, 3)
        left_bottom = (3, 5)
        right_top = (5, 3)
        right_bottom = (5, 5)
        self.assertEqual(mapping.get_id(*ancilla_position), 22)
        self.assertEqual(mapping.get_id(*left_top), 111)
        self.assertEqual(mapping.get_id(*left_bottom), 112)
        self.assertEqual(mapping.get_id(*right_top), 121)
        self.assertEqual(mapping.get_id(*right_bottom), 122)

        circuit = Circuit(mapping, 0)
        prologue = str(circuit.circuit)
        m = SurfaceZSyndromeMeasurement(circuit, ancilla_position, SurfaceStabilizerPattern.TWO_WEIGHT_LEFT, False)

        m.run()
        self.assertEqual(m.stage, 1)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            R 22'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 2)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            R 22
            TICK
            CX 111 22'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 3)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            R 22
            TICK
            CX 111 22
            TICK
            CX 112 22'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 4)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            R 22
            TICK
            CX 111 22
            TICK
            CX 112 22
            TICK
            M 22'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 5)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            R 22
            TICK
            CX 111 22
            TICK
            CX 112 22
            TICK
            M 22
            TICK'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 0)
        self.assertTrue(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            R 22
            TICK
            CX 111 22
            TICK
            CX 112 22
            TICK
            M 22
            TICK
            TICK'''))

        # Let's see if `m` can work with a four-weight X syndrome measurement positioned to the left.
        mx = SurfaceXSyndromeMeasurement(circuit, (2, 4), SurfaceStabilizerPattern.FOUR_WEIGHT, False)
        for i in range(6):
            circuit.place_tick()
            m.run()
            mx.run()

    def test_run_right(self) -> None:
        mapping = QubitMapping(20, 20)

        ancilla_position = (4, 4)
        left_top = (3, 3)
        left_bottom = (3, 5)
        right_top = (5, 3)
        right_bottom = (5, 5)
        self.assertEqual(mapping.get_id(*ancilla_position), 22)
        self.assertEqual(mapping.get_id(*left_top), 111)
        self.assertEqual(mapping.get_id(*left_bottom), 112)
        self.assertEqual(mapping.get_id(*right_top), 121)
        self.assertEqual(mapping.get_id(*right_bottom), 122)

        circuit = Circuit(mapping, 0)
        prologue = str(circuit.circuit)
        m = SurfaceZSyndromeMeasurement(circuit, ancilla_position, SurfaceStabilizerPattern.TWO_WEIGHT_RIGHT, False)

        m.run()
        self.assertEqual(m.stage, 1)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue)

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 2)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            TICK'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 3)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            TICK
            TICK
            R 22'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 4)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            TICK
            TICK
            R 22
            TICK
            CX 121 22'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 5)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            TICK
            TICK
            R 22
            TICK
            CX 121 22
            TICK
            CX 122 22'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 0)
        self.assertTrue(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            TICK
            TICK
            R 22
            TICK
            CX 121 22
            TICK
            CX 122 22
            TICK
            M 22'''))

        # Let's see if `m` can work with a four-weight X syndrome measurement positioned to the right.
        mx = SurfaceXSyndromeMeasurement(circuit, (6, 4), SurfaceStabilizerPattern.FOUR_WEIGHT, False)
        for i in range(6):
            circuit.place_tick()
            m.run()
            mx.run()


class SurfaceFourWeightXSyndromeMeasurementTest(unittest.TestCase):
    def test_run_four_weight(self) -> None:
        mapping = QubitMapping(20, 20)

        ancilla_position = (6, 6)
        left_top = (5, 5)
        left_bottom = (5, 7)
        right_top = (7, 5)
        right_bottom = (7, 7)
        self.assertEqual(mapping.get_id(*ancilla_position), 33)
        self.assertEqual(mapping.get_id(*left_top), 122)
        self.assertEqual(mapping.get_id(*left_bottom), 123)
        self.assertEqual(mapping.get_id(*right_top), 132)
        self.assertEqual(mapping.get_id(*right_bottom), 133)

        self.maxDiff = None
        circuit = Circuit(mapping, 0)
        prologue = str(circuit.circuit)
        m = SurfaceXSyndromeMeasurement(circuit, ancilla_position, SurfaceStabilizerPattern.FOUR_WEIGHT, False)
        self.assertTrue(m.is_complete())

        m.run()
        self.assertEqual(m.stage, 1)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            RX 33'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 2)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            RX 33
            TICK
            CX 33 122'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 3)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            RX 33
            TICK
            CX 33 122
            TICK
            CX 33 132'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 4)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            RX 33
            TICK
            CX 33 122
            TICK
            CX 33 132
            TICK
            CX 33 123'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 5)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            RX 33
            TICK
            CX 33 122
            TICK
            CX 33 132
            TICK
            CX 33 123
            TICK
            CX 33 133'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 0)
        self.assertTrue(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            RX 33
            TICK
            CX 33 122
            TICK
            CX 33 132
            TICK
            CX 33 123
            TICK
            CX 33 133
            TICK
            MX 33'''))

        for i in range(6):
            circuit.place_tick()
            m.run()
        self.assertEqual(m.stage, 0)
        self.assertTrue(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            RX 33
            TICK
            CX 33 122
            TICK
            CX 33 132
            TICK
            CX 33 123
            TICK
            CX 33 133
            TICK
            MX 33
            TICK
            RX 33
            TICK
            CX 33 122
            TICK
            CX 33 132
            TICK
            CX 33 123
            TICK
            CX 33 133
            TICK
            MX 33
            DETECTOR rec[-2] rec[-1]'''))
        self.assertEqual(circuit.detectors_for_post_selection, [])
        m.set_post_selection(True)

        for i in range(6):
            circuit.place_tick()
            m.run()
        self.assertEqual(m.stage, 0)
        self.assertTrue(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            RX 33
            TICK
            CX 33 122
            TICK
            CX 33 132
            TICK
            CX 33 123
            TICK
            CX 33 133
            TICK
            MX 33
            TICK
            RX 33
            TICK
            CX 33 122
            TICK
            CX 33 132
            TICK
            CX 33 123
            TICK
            CX 33 133
            TICK
            MX 33
            DETECTOR rec[-2] rec[-1]
            TICK
            RX 33
            TICK
            CX 33 122
            TICK
            CX 33 132
            TICK
            CX 33 123
            TICK
            CX 33 133
            TICK
            MX 33
            DETECTOR rec[-2] rec[-1]'''))

        self.assertEqual(circuit.detectors_for_post_selection, [DetectorIdentifier(1)])

    def test_run_up(self) -> None:
        mapping = QubitMapping(20, 20)

        ancilla_position = (4, 4)
        left_top = (3, 3)
        left_bottom = (3, 5)
        right_top = (5, 3)
        right_bottom = (5, 5)
        self.assertEqual(mapping.get_id(*ancilla_position), 22)
        self.assertEqual(mapping.get_id(*left_top), 111)
        self.assertEqual(mapping.get_id(*left_bottom), 112)
        self.assertEqual(mapping.get_id(*right_top), 121)
        self.assertEqual(mapping.get_id(*right_bottom), 122)

        circuit = Circuit(mapping, 0)
        prologue = str(circuit.circuit)
        m = SurfaceXSyndromeMeasurement(circuit, ancilla_position, SurfaceStabilizerPattern.TWO_WEIGHT_UP, False)

        m.run()
        self.assertEqual(m.stage, 1)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            RX 22'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 2)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            RX 22
            TICK
            CX 22 111'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 3)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            RX 22
            TICK
            CX 22 111
            TICK
            CX 22 121'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 4)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            RX 22
            TICK
            CX 22 111
            TICK
            CX 22 121
            TICK
            MX 22'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 5)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            RX 22
            TICK
            CX 22 111
            TICK
            CX 22 121
            TICK
            MX 22
            TICK'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 0)
        self.assertTrue(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            RX 22
            TICK
            CX 22 111
            TICK
            CX 22 121
            TICK
            MX 22
            TICK
            TICK'''))

        # Let's see if `m` can work with a four-weight Z syndrome measurement positioned above.
        mz = SurfaceZSyndromeMeasurement(circuit, (4, 6), SurfaceStabilizerPattern.FOUR_WEIGHT, False)
        for i in range(6):
            circuit.place_tick()
            m.run()
            mz.run()

    def test_run_down(self) -> None:
        mapping = QubitMapping(20, 20)

        ancilla_position = (4, 4)
        left_top = (3, 3)
        left_bottom = (3, 5)
        right_top = (5, 3)
        right_bottom = (5, 5)
        self.assertEqual(mapping.get_id(*ancilla_position), 22)
        self.assertEqual(mapping.get_id(*left_top), 111)
        self.assertEqual(mapping.get_id(*left_bottom), 112)
        self.assertEqual(mapping.get_id(*right_top), 121)
        self.assertEqual(mapping.get_id(*right_bottom), 122)

        circuit = Circuit(mapping, 0)
        prologue = str(circuit.circuit)
        m = SurfaceXSyndromeMeasurement(circuit, ancilla_position, SurfaceStabilizerPattern.TWO_WEIGHT_DOWN, False)

        m.run()
        self.assertEqual(m.stage, 1)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue)

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 2)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            TICK'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 3)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            TICK
            TICK
            RX 22'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 4)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            TICK
            TICK
            RX 22
            TICK
            CX 22 112'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 5)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            TICK
            TICK
            RX 22
            TICK
            CX 22 112
            TICK
            CX 22 122'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 0)
        self.assertTrue(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            TICK
            TICK
            RX 22
            TICK
            CX 22 112
            TICK
            CX 22 122
            TICK
            MX 22'''))

        # Let's see if `m` can work with a four-weight Z syndrome measurement positioned below.
        mz = SurfaceZSyndromeMeasurement(circuit, (4, 6), SurfaceStabilizerPattern.FOUR_WEIGHT, False)
        for i in range(6):
            circuit.place_tick()
            m.run()
            mz.run()

    def test_run_left(self) -> None:
        mapping = QubitMapping(20, 20)

        ancilla_position = (4, 4)
        left_top = (3, 3)
        left_bottom = (3, 5)
        right_top = (5, 3)
        right_bottom = (5, 5)
        self.assertEqual(mapping.get_id(*ancilla_position), 22)
        self.assertEqual(mapping.get_id(*left_top), 111)
        self.assertEqual(mapping.get_id(*left_bottom), 112)
        self.assertEqual(mapping.get_id(*right_top), 121)
        self.assertEqual(mapping.get_id(*right_bottom), 122)

        circuit = Circuit(mapping, 0)
        prologue = str(circuit.circuit)
        m = SurfaceXSyndromeMeasurement(circuit, ancilla_position, SurfaceStabilizerPattern.TWO_WEIGHT_LEFT, False)

        m.run()
        self.assertEqual(m.stage, 1)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            RX 22'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 2)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            RX 22
            TICK
            CX 22 111'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 3)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            RX 22
            TICK
            CX 22 111
            TICK'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 4)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            RX 22
            TICK
            CX 22 111
            TICK
            TICK
            CX 22 112'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 5)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            RX 22
            TICK
            CX 22 111
            TICK
            TICK
            CX 22 112
            TICK
            MX 22'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 0)
        self.assertTrue(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            RX 22
            TICK
            CX 22 111
            TICK
            TICK
            CX 22 112
            TICK
            MX 22
            TICK'''))

        # Let's see if `m` can work with a four-weight Z syndrome measurement positioned to the left.
        mz = SurfaceZSyndromeMeasurement(circuit, (2, 4), SurfaceStabilizerPattern.FOUR_WEIGHT, False)
        for i in range(6):
            circuit.place_tick()
            m.run()
            mz.run()

    def test_run_right(self) -> None:
        mapping = QubitMapping(20, 20)

        ancilla_position = (4, 4)
        left_top = (3, 3)
        left_bottom = (3, 5)
        right_top = (5, 3)
        right_bottom = (5, 5)
        self.assertEqual(mapping.get_id(*ancilla_position), 22)
        self.assertEqual(mapping.get_id(*left_top), 111)
        self.assertEqual(mapping.get_id(*left_bottom), 112)
        self.assertEqual(mapping.get_id(*right_top), 121)
        self.assertEqual(mapping.get_id(*right_bottom), 122)

        circuit = Circuit(mapping, 0)
        prologue = str(circuit.circuit)
        m = SurfaceXSyndromeMeasurement(circuit, ancilla_position, SurfaceStabilizerPattern.TWO_WEIGHT_RIGHT, False)

        m.run()
        self.assertEqual(m.stage, 1)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue)

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 2)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            TICK
            RX 22'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 3)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            TICK
            RX 22
            TICK
            CX 22 121'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 4)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            TICK
            RX 22
            TICK
            CX 22 121
            TICK'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 5)
        self.assertFalse(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            TICK
            RX 22
            TICK
            CX 22 121
            TICK
            TICK
            CX 22 122'''))

        circuit.place_tick()
        m.run()
        self.assertEqual(m.stage, 0)
        self.assertTrue(m.is_complete())
        self.assertEqual(str(circuit.circuit), prologue + textwrap.dedent(f'''
            TICK
            RX 22
            TICK
            CX 22 121
            TICK
            TICK
            CX 22 122
            TICK
            MX 22'''))

        # Let's see if `m` can work with a four-weight Z syndrome measurement positioned to the right.
        mz = SurfaceZSyndromeMeasurement(circuit, (6, 4), SurfaceStabilizerPattern.FOUR_WEIGHT, False)
        for i in range(6):
            circuit.place_tick()
            m.run()
            mz.run()


class SteanePlusSurfaceCodeTest(unittest.TestCase):
    def test_init_distance_3(self) -> None:
        mapping = QubitMapping(20, 20)
        m = SteanePlusSurfaceCode(mapping, 3, InitialValue.Zero, 0, False)

        ms = m.surface_syndrome_measurements
        self.assertEqual(len(ms), 8)
        assert isinstance(ms[(2, 6)], SurfaceXSyndromeMeasurement)
        self.assertEqual(ms[(2, 6)].ancilla_position, (2, 6))
        self.assertEqual(ms[(2, 6)].pattern, SurfaceStabilizerPattern.TWO_WEIGHT_DOWN)
        self.assertTrue(ms[(2, 6)].already_satisfied)
        self.assertFalse(ms[(2, 6)].post_selection)

        assert isinstance(ms[(2, 8)], SurfaceZSyndromeMeasurement)
        self.assertEqual(ms[(2, 8)].ancilla_position, (2, 8))
        self.assertEqual(ms[(2, 8)].pattern, SurfaceStabilizerPattern.FOUR_WEIGHT)
        self.assertFalse(ms[(2, 8)].already_satisfied)
        self.assertFalse(ms[(2, 8)].post_selection)

        assert isinstance(ms[(4, 8)], SurfaceXSyndromeMeasurement)
        self.assertEqual(ms[(4, 8)].ancilla_position, (4, 8))
        self.assertEqual(ms[(4, 8)].pattern, SurfaceStabilizerPattern.FOUR_WEIGHT)
        self.assertTrue(ms[(4, 8)].already_satisfied)
        self.assertFalse(ms[(4, 8)].post_selection)

        assert isinstance(ms[(6, 8)], SurfaceZSyndromeMeasurement)
        self.assertEqual(ms[(6, 8)].ancilla_position, (6, 8))
        self.assertEqual(ms[(6, 8)].pattern, SurfaceStabilizerPattern.TWO_WEIGHT_LEFT)
        self.assertFalse(ms[(6, 8)].already_satisfied)
        self.assertFalse(ms[(6, 8)].post_selection)

        assert isinstance(ms[(0, 10)], SurfaceZSyndromeMeasurement)
        self.assertEqual(ms[(0, 10)].ancilla_position, (0, 10))
        self.assertEqual(ms[(0, 10)].pattern, SurfaceStabilizerPattern.TWO_WEIGHT_RIGHT)
        self.assertFalse(ms[(0, 10)].already_satisfied)
        self.assertFalse(ms[(0, 10)].post_selection)

        assert isinstance(ms[(2, 10)], SurfaceXSyndromeMeasurement)
        self.assertEqual(ms[(2, 10)].ancilla_position, (2, 10))
        self.assertEqual(ms[(2, 10)].pattern, SurfaceStabilizerPattern.FOUR_WEIGHT)
        self.assertTrue(ms[(2, 10)].already_satisfied)
        self.assertFalse(ms[(2, 10)].post_selection)

        assert isinstance(ms[(4, 10)], SurfaceZSyndromeMeasurement)
        self.assertEqual(ms[(4, 10)].ancilla_position, (4, 10))
        self.assertEqual(ms[(4, 10)].pattern, SurfaceStabilizerPattern.FOUR_WEIGHT)
        self.assertFalse(ms[(4, 10)].already_satisfied)
        self.assertFalse(ms[(4, 10)].post_selection)

        assert isinstance(ms[(4, 12)], SurfaceXSyndromeMeasurement)
        self.assertEqual(ms[(4, 12)].ancilla_position, (4, 12))
        self.assertEqual(ms[(4, 12)].pattern, SurfaceStabilizerPattern.TWO_WEIGHT_UP)
        self.assertTrue(ms[(4, 12)].already_satisfied)
        self.assertFalse(ms[(4, 12)].post_selection)

        lsms = m.lattice_surgery_syndrome_measurements
        self.assertEqual(len(lsms), 2)
        assert isinstance(lsms[0], SurfaceZSyndromeMeasurement)
        self.assertEqual(lsms[0].ancilla_position, (0, 6))
        self.assertEqual(lsms[0].pattern, SurfaceStabilizerPattern.TWO_WEIGHT_RIGHT)
        self.assertTrue(lsms[0].post_selection)

        assert isinstance(lsms[1], SurfaceZSyndromeMeasurement)
        self.assertEqual(lsms[1].ancilla_position, (4, 6))
        self.assertEqual(lsms[1].pattern, SurfaceStabilizerPattern.FOUR_WEIGHT)
        self.assertTrue(lsms[1].post_selection)

    def test_init_post_selection(self) -> None:
        mapping = QubitMapping(20, 20)
        m = SteanePlusSurfaceCode(mapping, 3, InitialValue.Plus, 0, True)

        for m0 in m.surface_syndrome_measurements.values():
            self.assertTrue(m0.post_selection)

        for m1 in m.lattice_surgery_syndrome_measurements:
            self.assertTrue(m1.post_selection)
