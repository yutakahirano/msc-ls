import textwrap
import unittest


from surface_code import *
from util import QubitMapping, DetectorIdentifier


class SurfaceZSyndromeMeasurementTest(unittest.TestCase):
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
            DETECTOR[SURFACE-Z] rec[-2] rec[-1]'''))
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
            DETECTOR[SURFACE-Z] rec[-2] rec[-1]
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
            DETECTOR[SURFACE-Z] rec[-2] rec[-1]'''))
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


class SurfaceXSyndromeMeasurementTest(unittest.TestCase):
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
            DETECTOR[SURFACE-X] rec[-2] rec[-1]'''))
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
            DETECTOR[SURFACE-X] rec[-2] rec[-1]
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
            DETECTOR[SURFACE-X] rec[-2] rec[-1]'''))

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
