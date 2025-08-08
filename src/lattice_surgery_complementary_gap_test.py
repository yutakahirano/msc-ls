import unittest

from lattice_surgery_complementary_gap import *

from typing import Type


TWO_WEIGHT_DOWN = SurfaceStabilizerPattern.TWO_WEIGHT_DOWN
TWO_WEIGHT_LEFT = SurfaceStabilizerPattern.TWO_WEIGHT_LEFT
TWO_WEIGHT_RIGHT = SurfaceStabilizerPattern.TWO_WEIGHT_RIGHT
TWO_WEIGHT_UP = SurfaceStabilizerPattern.TWO_WEIGHT_UP
FOUR_WEIGHT = SurfaceStabilizerPattern.FOUR_WEIGHT


class SteanePlusSurfaceCodeTest(unittest.TestCase):
    def _new_instance(self, intermediate_distance: int, final_distance: int,
                      initial_value: InitialValue) -> SteanePlusSurfaceCode:
        mapping = QubitMapping(20, 30)
        return SteanePlusSurfaceCode(mapping, intermediate_distance, final_distance, initial_value,
                                     SteaneSyndromeExtractionPattern.ZXZ, True, 0.001, False, False, 2)

    def _perform_surface_initialization(self, c: SteanePlusSurfaceCode, initial_value: InitialValue) -> None:
        if initial_value == InitialValue.Zero:
            for m in c.surface_syndrome_measurements.values():
                m.already_satisfied = False

        for i in range(c.surface_distance):
            for j in range(c.surface_distance):
                x = c.surface_offset_x + j * 2
                y = c.surface_offset_y + i * 2
                match initial_value:
                    case InitialValue.Plus:
                        c.circuit.place_reset_x((x, y))
                    case InitialValue.Zero:
                        c.circuit.place_reset_z((x, y))
                    case _:
                        raise ValueError(f'Unsupported initial value: {initial_value}')

        self._perform_syndrome_measurements(c)
        self._perform_syndrome_measurements(c)

    def _perform_syndrome_measurements(self, c: SteanePlusSurfaceCode) -> None:
        SURFACE_SYNDROME_MEASUREMENT_DEPTH = 6
        for _ in range(SURFACE_SYNDROME_MEASUREMENT_DEPTH):
            for m in c.surface_syndrome_measurements.values():
                m.run()
            c.circuit.place_tick()

    def assert_syndrome_measurement(self, c: SteanePlusSurfaceCode, position: tuple[int, int],
                                    cls: Type[SurfaceSyndromeMeasurement],
                                    pattern: SurfaceStabilizerPattern,
                                    already_satisfied: bool) -> None:
        self.assertIsInstance(c.surface_syndrome_measurements[position], cls)
        self.assertEqual(c.surface_syndrome_measurements[position].pattern, pattern)
        self.assertEqual(c.surface_syndrome_measurements[position].already_satisfied, already_satisfied)

    def test_setup_surface_code_patch(self) -> None:
        mapping = QubitMapping(20, 30)
        c = self._new_instance(3, 3, InitialValue.Plus)

        self.assertEqual(c.surface_offset_x, 1)
        self.assertEqual(c.surface_offset_y, 17)
        self.assertEqual(len(c.surface_syndrome_measurements), 8)
        self.assert_syndrome_measurement(c, (2, 16), SurfaceXSyndromeMeasurement, TWO_WEIGHT_DOWN, True)

        self.assert_syndrome_measurement(c, (2, 18), SurfaceZSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(c, (4, 18), SurfaceXSyndromeMeasurement, FOUR_WEIGHT, True)
        self.assert_syndrome_measurement(c, (6, 18), SurfaceZSyndromeMeasurement, TWO_WEIGHT_LEFT, False)

        self.assert_syndrome_measurement(c, (0, 20), SurfaceZSyndromeMeasurement, TWO_WEIGHT_RIGHT, False)
        self.assert_syndrome_measurement(c, (2, 20), SurfaceXSyndromeMeasurement, FOUR_WEIGHT, True)
        self.assert_syndrome_measurement(c, (4, 20), SurfaceZSyndromeMeasurement, FOUR_WEIGHT, False)

        self.assert_syndrome_measurement(c, (4, 22), SurfaceXSyndromeMeasurement, TWO_WEIGHT_UP, True)

    def test_initialization_plus(self) -> None:
        mapping = QubitMapping(20, 30)
        c = self._new_instance(3, 3, InitialValue.Plus)
        circuit = c.circuit

        self._perform_surface_initialization(c, InitialValue.Plus)
        circuit.place_observable_include([circuit.place_mpp(c._logical_x_pauli_string())])

        stim_circuit: stim.Circuit = circuit.circuit1.circuit
        # Assert that the circuit has deterministic observables.
        _ = stim_circuit.detector_error_model()

    def test_initialization_zero(self) -> None:
        # Note that in practice the surface code patch in SteanePlusSurfaceCode is always initialized to \ket{+}.
        # This test tests initialization to \ket{0}, mainly for code expansion test cases.

        mapping = QubitMapping(20, 30)
        c = self._new_instance(3, 3, InitialValue.Plus)
        circuit = c.circuit

        # Because `SteanePlustSurfaceCode` expects the surface code region to be initialized to \ket{+},
        # we manually manipulate syndrome measurements to enable \ket{0} initialization.
        for m in c.surface_syndrome_measurements.values():
            m.already_satisfied = False

        self._perform_surface_initialization(c, InitialValue.Zero)
        circuit.place_observable_include([circuit.place_mpp(c._logical_z_pauli_string())])

        stim_circuit: stim.Circuit = circuit.circuit1.circuit
        # Assert that the circuit has deterministic observables.
        _ = stim_circuit.detector_error_model()

    def test_code_expansion_plus(self) -> None:
        mapping = QubitMapping(20, 30)
        c = self._new_instance(3, 5, InitialValue.Plus)
        circuit = c.partially_noiseless_circuit
        stim_circuit: stim.Circuit = circuit.circuit

        self._perform_surface_initialization(c, InitialValue.Plus)

        for m in c.surface_syndrome_measurements.values():
            # `already_satisfied` is used only for the first syndrome measurement, and this does not
            # affect the actual behavior. We reset it here just to make the following test expectations
            # easier to read.
            m.already_satisfied = False

        c.surface_distance = 5
        c._prepare_qubits_for_code_expansion_downward()
        c._setup_syndrome_measurements_for_code_expansion_downward()

        self.assertEqual(len(c.surface_syndrome_measurements), 24)
        self.assert_syndrome_measurement(c, (2, 16), SurfaceXSyndromeMeasurement, TWO_WEIGHT_DOWN, False)
        self.assert_syndrome_measurement(c, (6, 16), SurfaceXSyndromeMeasurement, TWO_WEIGHT_DOWN, False)

        self.assert_syndrome_measurement(c, (2, 18), SurfaceZSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(c, (4, 18), SurfaceXSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(c, (6, 18), SurfaceZSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assertIsNotNone(c.surface_syndrome_measurements[(6, 18)].last_measurement)
        self.assert_syndrome_measurement(c, (8, 18), SurfaceXSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(c, (10, 18), SurfaceZSyndromeMeasurement, TWO_WEIGHT_LEFT, True)

        self.assert_syndrome_measurement(c, (0, 20), SurfaceZSyndromeMeasurement, TWO_WEIGHT_RIGHT, False)
        self.assert_syndrome_measurement(c, (2, 20), SurfaceXSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assertIsNotNone(c.surface_syndrome_measurements[(2, 20)].last_measurement)
        self.assert_syndrome_measurement(c, (4, 20), SurfaceZSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(c, (6, 20), SurfaceXSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(c, (8, 20), SurfaceZSyndromeMeasurement, FOUR_WEIGHT, True)

        self.assert_syndrome_measurement(c, (2, 22), SurfaceZSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(c, (4, 22), SurfaceXSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(c, (6, 22), SurfaceZSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(c, (8, 22), SurfaceXSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(c, (10, 22), SurfaceZSyndromeMeasurement, TWO_WEIGHT_LEFT, True)

        self.assert_syndrome_measurement(c, (0, 24), SurfaceZSyndromeMeasurement, TWO_WEIGHT_RIGHT, False)
        self.assert_syndrome_measurement(c, (2, 24), SurfaceXSyndromeMeasurement, FOUR_WEIGHT, True)
        self.assert_syndrome_measurement(c, (4, 24), SurfaceZSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(c, (6, 24), SurfaceXSyndromeMeasurement, FOUR_WEIGHT, True)
        self.assert_syndrome_measurement(c, (8, 24), SurfaceZSyndromeMeasurement, FOUR_WEIGHT, False)

        self.assert_syndrome_measurement(c, (4, 26), SurfaceXSyndromeMeasurement, TWO_WEIGHT_UP, True)
        self.assert_syndrome_measurement(c, (8, 26), SurfaceXSyndromeMeasurement, TWO_WEIGHT_UP, True)

        self.assertEqual(c.surface_offset_x, 1)
        self.assertEqual(c.surface_offset_y, 17)

        self._perform_syndrome_measurements(c)
        self._perform_syndrome_measurements(c)
        self._perform_syndrome_measurements(c)

        ms = [circuit.place_mpp(c._logical_x_pauli_string())]
        circuit.place_observable_include(ms)
        circuit.place_detector(ms)
        # Assert that the circuit has deterministic observables.
        _ = stim_circuit.detector_error_model()
        # Assert that the circuit has a graph-like dem.
        _ = stim_circuit.detector_error_model(decompose_errors=True)

    def test_code_expansion_zero(self) -> None:
        mapping = QubitMapping(20, 30)
        c = self._new_instance(3, 5, InitialValue.Plus)
        circuit = c.partially_noiseless_circuit
        stim_circuit: stim.Circuit = circuit.circuit

        self._perform_surface_initialization(c, InitialValue.Zero)

        for m in c.surface_syndrome_measurements.values():
            # `already_satisfied` is used only for the first syndrome measurement, and this does not
            # affect the actual behavior. We reset it here just to make the following test expectations
            # easier to read.
            m.already_satisfied = False

        c.surface_distance = 5
        c._prepare_qubits_for_code_expansion_downward()
        c._setup_syndrome_measurements_for_code_expansion_downward()

        self.assertEqual(len(c.surface_syndrome_measurements), 24)
        self.assert_syndrome_measurement(c, (2, 16), SurfaceXSyndromeMeasurement, TWO_WEIGHT_DOWN, False)
        self.assert_syndrome_measurement(c, (6, 16), SurfaceXSyndromeMeasurement, TWO_WEIGHT_DOWN, False)

        self.assert_syndrome_measurement(c, (2, 18), SurfaceZSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(c, (4, 18), SurfaceXSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(c, (6, 18), SurfaceZSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assertIsNotNone(c.surface_syndrome_measurements[(6, 18)].last_measurement)
        self.assert_syndrome_measurement(c, (8, 18), SurfaceXSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(c, (10, 18), SurfaceZSyndromeMeasurement, TWO_WEIGHT_LEFT, True)

        self.assert_syndrome_measurement(c, (0, 20), SurfaceZSyndromeMeasurement, TWO_WEIGHT_RIGHT, False)
        self.assert_syndrome_measurement(c, (2, 20), SurfaceXSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assertIsNotNone(c.surface_syndrome_measurements[(2, 20)].last_measurement)
        self.assert_syndrome_measurement(c, (4, 20), SurfaceZSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(c, (6, 20), SurfaceXSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(c, (8, 20), SurfaceZSyndromeMeasurement, FOUR_WEIGHT, True)

        self.assert_syndrome_measurement(c, (2, 22), SurfaceZSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(c, (4, 22), SurfaceXSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(c, (6, 22), SurfaceZSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(c, (8, 22), SurfaceXSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(c, (10, 22), SurfaceZSyndromeMeasurement, TWO_WEIGHT_LEFT, True)

        self.assert_syndrome_measurement(c, (0, 24), SurfaceZSyndromeMeasurement, TWO_WEIGHT_RIGHT, False)
        self.assert_syndrome_measurement(c, (2, 24), SurfaceXSyndromeMeasurement, FOUR_WEIGHT, True)
        self.assert_syndrome_measurement(c, (4, 24), SurfaceZSyndromeMeasurement, FOUR_WEIGHT, False)
        self.assert_syndrome_measurement(c, (6, 24), SurfaceXSyndromeMeasurement, FOUR_WEIGHT, True)
        self.assert_syndrome_measurement(c, (8, 24), SurfaceZSyndromeMeasurement, FOUR_WEIGHT, False)

        self.assert_syndrome_measurement(c, (4, 26), SurfaceXSyndromeMeasurement, TWO_WEIGHT_UP, True)
        self.assert_syndrome_measurement(c, (8, 26), SurfaceXSyndromeMeasurement, TWO_WEIGHT_UP, True)

        self.assertEqual(c.surface_offset_x, 1)
        self.assertEqual(c.surface_offset_y, 17)

        self._perform_syndrome_measurements(c)
        self._perform_syndrome_measurements(c)

        logical_pauli_string = c._logical_z_pauli_string()
        ms = [circuit.place_mpp(logical_pauli_string)]
        circuit.place_observable_include(ms)
        circuit.place_detector(ms)

        # Assert that the circuit has deterministic observables.
        _ = stim_circuit.detector_error_model()
        # Assert that the circuit has a graph-like dem.
        _ = stim_circuit.detector_error_model(decompose_errors=True)

    def test_distillation_plus_without_expansion(self) -> None:
        mapping = QubitMapping(20, 30)
        c = self._new_instance(3, 3, InitialValue.Plus)
        circuit = c.partially_noiseless_circuit
        stim_circuit: stim.Circuit = circuit.circuit

        c.run()
        # Assert that the circuit has deterministic observables.
        _ = stim_circuit.detector_error_model()
        # Assert that the circuit has a graph-like dem.
        _ = stim_circuit.detector_error_model(decompose_errors=True)

    def test_distillation_zero_without_expansion(self) -> None:
        mapping = QubitMapping(20, 30)
        c = self._new_instance(3, 3, InitialValue.Zero)
        circuit = c.partially_noiseless_circuit
        stim_circuit: stim.Circuit = circuit.circuit

        c.run()

        # Assert that the circuit has deterministic observables.
        _ = stim_circuit.detector_error_model()
        # Assert that the circuit has a graph-like dem.
        _ = stim_circuit.detector_error_model(decompose_errors=True)

    def test_distillation_s_plus_without_expansion(self) -> None:
        mapping = QubitMapping(20, 30)
        c = self._new_instance(3, 5, InitialValue.SPlus)
        circuit = c.partially_noiseless_circuit
        stim_circuit: stim.Circuit = circuit.circuit

        c.run()
        # Assert that the circuit has deterministic observables.
        _ = stim_circuit.detector_error_model()
        # Assert that the circuit has a graph-like dem.
        _ = stim_circuit.detector_error_model(decompose_errors=True)

    def test_distillation_plus_with_expansion(self) -> None:
        mapping = QubitMapping(20, 30)
        c = self._new_instance(3, 3, InitialValue.Plus)
        circuit = c.partially_noiseless_circuit
        stim_circuit: stim.Circuit = circuit.circuit

        c.run()
        # Assert that the circuit has deterministic observables.
        _ = stim_circuit.detector_error_model()
        # Assert that the circuit has a graph-like dem.
        _ = stim_circuit.detector_error_model(decompose_errors=True)

    def test_distillation_zero_with_expansion(self) -> None:
        mapping = QubitMapping(20, 30)
        c = self._new_instance(3, 3, InitialValue.Zero)
        circuit = c.partially_noiseless_circuit
        stim_circuit: stim.Circuit = circuit.circuit

        c.run()

        # Assert that the circuit has deterministic observables.
        _ = stim_circuit.detector_error_model()
        # Assert that the circuit has a graph-like dem.
        _ = stim_circuit.detector_error_model(decompose_errors=True)

    def test_distillation_s_plus_with_expansion(self) -> None:
        mapping = QubitMapping(20, 30)
        c = self._new_instance(3, 5, InitialValue.SPlus)
        circuit = c.partially_noiseless_circuit
        stim_circuit: stim.Circuit = circuit.circuit

        c.run()
        # Assert that the circuit has deterministic observables.
        _ = stim_circuit.detector_error_model()
        # Assert that the circuit has a graph-like dem.
        _ = stim_circuit.detector_error_model(decompose_errors=True)
