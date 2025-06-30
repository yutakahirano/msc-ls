import unittest

from lattice_surgery_error_detection import *


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
        self.assertTrue(ms[(4, 8)].post_selection)

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
        self.assertTrue(ms[(2, 10)].post_selection)

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

    def test_init_post_selection(self) -> None:
        mapping = QubitMapping(20, 20)
        m = SteanePlusSurfaceCode(mapping, 3, InitialValue.Plus, 0, True)

        for m0 in m.surface_syndrome_measurements.values():
            self.assertTrue(m0.post_selection)
