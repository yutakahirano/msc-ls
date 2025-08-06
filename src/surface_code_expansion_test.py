import unittest

from surface_code_expansion import *

from typing import Type

TWO_WEIGHT_DOWN = SurfaceStabilizerPattern.TWO_WEIGHT_DOWN
TWO_WEIGHT_LEFT = SurfaceStabilizerPattern.TWO_WEIGHT_LEFT
TWO_WEIGHT_RIGHT = SurfaceStabilizerPattern.TWO_WEIGHT_RIGHT
TWO_WEIGHT_UP = SurfaceStabilizerPattern.TWO_WEIGHT_UP
FOUR_WEIGHT = SurfaceStabilizerPattern.FOUR_WEIGHT


# This test suite contains tests for surface code related logic in SteanePlusSurfaceCode.
class SurfaceCodePatchTest(unittest.TestCase):
    def _new_instance(self,
                      intermediate_distance: int, final_distance: int,
                      pattern: ExpansionPattern) -> SurfaceCodePatch:
        mapping = QubitMapping(20, 30)
        circuit = Circuit(mapping, 1e-3)
        patch = SurfaceCodePatch(circuit, intermediate_distance, final_distance, 2, pattern)
        return patch

    def _perform_syndrome_measurements(self, patch: SurfaceCodePatch) -> None:
        SURFACE_SYNDROME_MEASUREMENT_DEPTH = 6
        for _ in range(SURFACE_SYNDROME_MEASUREMENT_DEPTH):
            for m in patch.syndrome_measurements.values():
                m.run()
            patch.circuit.place_tick()

    def assert_syndrome_measurement(
            self, patch: SurfaceCodePatch, position: tuple[int, int],
            cls: Type[SurfaceSyndromeMeasurement],
            pattern: SurfaceStabilizerPattern,
            already_satisfied: bool) -> None:
        self.assertIsInstance(patch.syndrome_measurements[position], cls)
        self.assertEqual(patch.syndrome_measurements[position].pattern, pattern)
        self.assertEqual(patch.syndrome_measurements[position].already_satisfied, already_satisfied)

    def test_initialization_zero(self) -> None:
        mapping = QubitMapping(20, 30)
        patch = self._new_instance(3, 3, ExpansionPattern.DOWNWARD)
        circuit = patch.circuit
        stim_circuit: stim.Circuit = circuit.circuit

        patch.build()
        self.assertEqual(patch.offset, (1, 1))
        self.assertEqual(len(patch.syndrome_measurements), 8)
        self.assert_syndrome_measurement(patch, (2, 0), SurfaceXSyndromeMeasurement, TWO_WEIGHT_DOWN, False)

        self.assert_syndrome_measurement(patch, (2, 2), SurfaceZSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(patch, (4, 2), SurfaceXSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(patch, (6, 2), SurfaceZSyndromeMeasurement, TWO_WEIGHT_LEFT, False)

        self.assert_syndrome_measurement(patch, (0, 4), SurfaceZSyndromeMeasurement, TWO_WEIGHT_RIGHT, False)
        self.assert_syndrome_measurement(patch, (2, 4), SurfaceXSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(patch, (4, 4), SurfaceZSyndromeMeasurement, FOUR_WEIGHT, False)

        self.assert_syndrome_measurement(patch, (4, 6), SurfaceXSyndromeMeasurement, TWO_WEIGHT_UP, False)

        # Assert that the circuit has deterministic observables.
        _ = stim_circuit.detector_error_model()
        # Assert that the circuit has a graph-like dem.
        _ = stim_circuit.detector_error_model(decompose_errors=True)

    def test_code_expansion_zero_upward(self) -> None:
        mapping = QubitMapping(20, 30)
        patch = self._new_instance(3, 5, ExpansionPattern.UPWARD)
        circuit = patch.circuit
        stim_circuit: stim.Circuit = circuit.circuit

        patch.build()
        self.assertEqual(patch.offset, (1, 1))

        self.assertEqual(len(patch.syndrome_measurements), 24)
        self.assert_syndrome_measurement(patch, (2, 0), SurfaceXSyndromeMeasurement, TWO_WEIGHT_DOWN, True)
        self.assert_syndrome_measurement(patch, (6, 0), SurfaceXSyndromeMeasurement, TWO_WEIGHT_DOWN, True)

        self.assert_syndrome_measurement(patch, (2, 2), SurfaceZSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(patch, (4, 2), SurfaceXSyndromeMeasurement, FOUR_WEIGHT, True)
        self.assert_syndrome_measurement(patch, (6, 2), SurfaceZSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(patch, (8, 2), SurfaceXSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(patch, (10, 2), SurfaceZSyndromeMeasurement, TWO_WEIGHT_LEFT, True)

        self.assert_syndrome_measurement(patch, (0, 4), SurfaceZSyndromeMeasurement, TWO_WEIGHT_RIGHT, False)
        self.assert_syndrome_measurement(patch, (2, 4), SurfaceXSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(patch, (4, 4), SurfaceZSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(patch, (6, 4), SurfaceXSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(patch, (8, 4), SurfaceZSyndromeMeasurement, FOUR_WEIGHT, True)

        self.assert_syndrome_measurement(patch, (2, 6), SurfaceZSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(patch, (4, 6), SurfaceXSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(patch, (6, 6), SurfaceZSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(patch, (8, 6), SurfaceXSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(patch, (10, 6), SurfaceZSyndromeMeasurement, TWO_WEIGHT_LEFT, True)

        self.assert_syndrome_measurement(patch, (0, 8), SurfaceZSyndromeMeasurement, TWO_WEIGHT_RIGHT, False)
        self.assert_syndrome_measurement(patch, (2, 8), SurfaceXSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(patch, (4, 8), SurfaceZSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(patch, (6, 8), SurfaceXSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(patch, (8, 8), SurfaceZSyndromeMeasurement, FOUR_WEIGHT, True)

        self.assert_syndrome_measurement(patch, (4, 10), SurfaceXSyndromeMeasurement, TWO_WEIGHT_UP, False)
        self.assert_syndrome_measurement(patch, (8, 10), SurfaceXSyndromeMeasurement, TWO_WEIGHT_UP, False)

        # Assert that the circuit has deterministic observables.
        _ = stim_circuit.detector_error_model()
        # Assert that the circuit has a graph-like dem.
        _ = stim_circuit.detector_error_model(decompose_errors=True)

    def test_code_expansion_zero_downward(self) -> None:
        mapping = QubitMapping(20, 30)
        patch = self._new_instance(3, 5, ExpansionPattern.DOWNWARD)
        circuit = patch.circuit
        stim_circuit: stim.Circuit = circuit.circuit

        patch.build()
        self.assertEqual(patch.offset, (1, 1))

        self.assertEqual(len(patch.syndrome_measurements), 24)
        self.assert_syndrome_measurement(patch, (2, 0), SurfaceXSyndromeMeasurement, TWO_WEIGHT_DOWN, False)
        self.assert_syndrome_measurement(patch, (6, 0), SurfaceXSyndromeMeasurement, TWO_WEIGHT_DOWN, False)

        self.assert_syndrome_measurement(patch, (2, 2), SurfaceZSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(patch, (4, 2), SurfaceXSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(patch, (6, 2), SurfaceZSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(patch, (8, 2), SurfaceXSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(patch, (10, 2), SurfaceZSyndromeMeasurement, TWO_WEIGHT_LEFT, True)

        self.assert_syndrome_measurement(patch, (0, 4), SurfaceZSyndromeMeasurement, TWO_WEIGHT_RIGHT, False)
        self.assert_syndrome_measurement(patch, (2, 4), SurfaceXSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(patch, (4, 4), SurfaceZSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(patch, (6, 4), SurfaceXSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(patch, (8, 4), SurfaceZSyndromeMeasurement, FOUR_WEIGHT, True)

        self.assert_syndrome_measurement(patch, (2, 6), SurfaceZSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(patch, (4, 6), SurfaceXSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(patch, (6, 6), SurfaceZSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(patch, (8, 6), SurfaceXSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(patch, (10, 6), SurfaceZSyndromeMeasurement, TWO_WEIGHT_LEFT, True)

        self.assert_syndrome_measurement(patch, (0, 8), SurfaceZSyndromeMeasurement, TWO_WEIGHT_RIGHT, False)
        self.assert_syndrome_measurement(patch, (2, 8), SurfaceXSyndromeMeasurement, FOUR_WEIGHT, True)
        self.assert_syndrome_measurement(patch, (4, 8), SurfaceZSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(patch, (6, 8), SurfaceXSyndromeMeasurement, FOUR_WEIGHT, True)
        self.assert_syndrome_measurement(patch, (8, 8), SurfaceZSyndromeMeasurement, FOUR_WEIGHT, False)

        self.assert_syndrome_measurement(patch, (4, 10), SurfaceXSyndromeMeasurement, TWO_WEIGHT_UP, True)
        self.assert_syndrome_measurement(patch, (8, 10), SurfaceXSyndromeMeasurement, TWO_WEIGHT_UP, True)

        # Assert that the circuit has deterministic observables.
        _ = stim_circuit.detector_error_model()
        # Assert that the circuit has a graph-like dem.
        _ = stim_circuit.detector_error_model(decompose_errors=True)
