import unittest

from lattice_surgery_error_detection import *


class SteanePlusSurfaceCodeTest(unittest.TestCase):
    def test_init_distance_3(self) -> None:
        pattern = SteaneSyndromeExtractionPattern.ZXZ
        mapping = QubitMapping(20, 20)
        m = SteanePlusSurfaceCode(mapping, 3, InitialValue.Zero, pattern, 0, False)

        ms = m.surface_syndrome_measurements
        self.assertEqual(len(ms), 8)
        assert isinstance(ms[(2, 16)], SurfaceXSyndromeMeasurement)
        self.assertEqual(ms[(2, 16)].ancilla_position, (2, 16))
        self.assertEqual(ms[(2, 16)].pattern, SurfaceStabilizerPattern.TWO_WEIGHT_DOWN)
        self.assertTrue(ms[(2, 16)].already_satisfied)
        self.assertFalse(ms[(2, 16)].post_selection)

        assert isinstance(ms[(2, 18)], SurfaceZSyndromeMeasurement)
        self.assertEqual(ms[(2, 18)].ancilla_position, (2, 18))
        self.assertEqual(ms[(2, 18)].pattern, SurfaceStabilizerPattern.FOUR_WEIGHT)
        self.assertFalse(ms[(2, 18)].already_satisfied)
        self.assertFalse(ms[(2, 18)].post_selection)

        assert isinstance(ms[(4, 18)], SurfaceXSyndromeMeasurement)
        self.assertEqual(ms[(4, 18)].ancilla_position, (4, 18))
        self.assertEqual(ms[(4, 18)].pattern, SurfaceStabilizerPattern.FOUR_WEIGHT)
        self.assertTrue(ms[(4, 18)].already_satisfied)
        self.assertTrue(ms[(4, 18)].post_selection)

        assert isinstance(ms[(6, 18)], SurfaceZSyndromeMeasurement)
        self.assertEqual(ms[(6, 18)].ancilla_position, (6, 18))
        self.assertEqual(ms[(6, 18)].pattern, SurfaceStabilizerPattern.TWO_WEIGHT_LEFT)
        self.assertFalse(ms[(6, 18)].already_satisfied)
        self.assertFalse(ms[(6, 18)].post_selection)

        assert isinstance(ms[(0, 20)], SurfaceZSyndromeMeasurement)
        self.assertEqual(ms[(0, 20)].ancilla_position, (0, 20))
        self.assertEqual(ms[(0, 20)].pattern, SurfaceStabilizerPattern.TWO_WEIGHT_RIGHT)
        self.assertFalse(ms[(0, 20)].already_satisfied)
        self.assertFalse(ms[(0, 20)].post_selection)

        assert isinstance(ms[(2, 20)], SurfaceXSyndromeMeasurement)
        self.assertEqual(ms[(2, 20)].ancilla_position, (2, 20))
        self.assertEqual(ms[(2, 20)].pattern, SurfaceStabilizerPattern.FOUR_WEIGHT)
        self.assertTrue(ms[(2, 20)].already_satisfied)
        self.assertTrue(ms[(2, 20)].post_selection)

        assert isinstance(ms[(4, 20)], SurfaceZSyndromeMeasurement)
        self.assertEqual(ms[(4, 20)].ancilla_position, (4, 20))
        self.assertEqual(ms[(4, 20)].pattern, SurfaceStabilizerPattern.FOUR_WEIGHT)
        self.assertFalse(ms[(4, 20)].already_satisfied)
        self.assertFalse(ms[(4, 20)].post_selection)

        assert isinstance(ms[(4, 22)], SurfaceXSyndromeMeasurement)
        self.assertEqual(ms[(4, 22)].ancilla_position, (4, 22))
        self.assertEqual(ms[(4, 22)].pattern, SurfaceStabilizerPattern.TWO_WEIGHT_UP)
        self.assertTrue(ms[(4, 22)].already_satisfied)
        self.assertFalse(ms[(4, 22)].post_selection)

    def test_init_post_selection(self) -> None:
        pattern = SteaneSyndromeExtractionPattern.ZXZ
        mapping = QubitMapping(20, 20)
        m = SteanePlusSurfaceCode(mapping, 3, InitialValue.Plus, pattern, 0, True)

        for m0 in m.surface_syndrome_measurements.values():
            self.assertTrue(m0.post_selection)
