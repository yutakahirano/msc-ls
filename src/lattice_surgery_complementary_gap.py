from __future__ import annotations

import concurrent
import concurrent.futures
import argparse
import enum
import math
import numpy as np
import pymatching
import random
import re
import sqlite3
import stim
import sys

import steane_code

from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from enum import auto
from util import QubitMapping, Circuit, MultiplexingCircuit
from util import MeasurementIdentifier, DetectorIdentifier, ObservableIdentifier, SuppressNoise
from surface_code import SurfaceStabilizerPattern, SurfaceSyndromeMeasurement
from surface_code import SurfaceXSyndromeMeasurement, SurfaceZSyndromeMeasurement
from lookup_table import LookupTable, LookupTableKey, LookupTableWithNegativeSamplesOnly
from lookup_table import ensure_lookup_tables_table, query_lookup_table, store_lookup_table


class InitialValue(enum.Enum):
    Plus = auto(),
    Zero = auto(),
    SPlus = auto(),


class SteaneSyndromeExtractionPattern(enum.Enum):
    XZZ = auto(),
    ZXZ = auto(),
    ZZ = auto(),


# Representing a merged QEC code of the Steane code and the rotated surface code.
class SteanePlusSurfaceCode:
    def __init__(self, mapping: QubitMapping, surface_intermediate_distance: int, surface_final_distance: int,
                 initial_value: InitialValue, steane_syndrome_extraction_pattern: SteaneSyndromeExtractionPattern,
                 perfect_initialization: bool,
                 error_probability: float, with_heuristic_post_selection: bool,
                 full_post_selection: bool, num_stabilization_rounds_after_surgery: int,
                 num_epilogue_syndrome_extraction_rounds: int,
                 skip_detector_for_complementary_gap: bool) -> None:
        self.mapping = mapping
        self.surface_intermediate_distance = surface_intermediate_distance
        self.surface_distance = surface_intermediate_distance
        self.surface_final_distance = surface_final_distance
        self.initial_value = initial_value
        self.steane_syndrome_extraction_pattern = steane_syndrome_extraction_pattern
        self.perfect_initialization = perfect_initialization
        self.error_probability = error_probability
        self.with_heuristic_post_selection = with_heuristic_post_selection
        self.full_post_selection = full_post_selection
        self.num_stabilization_rounds_after_surgery = num_stabilization_rounds_after_surgery
        self.num_epilogue_syndrome_extraction_rounds = num_epilogue_syndrome_extraction_rounds
        self.primal_circuit = Circuit(mapping, error_probability)
        self.partially_noiseless_circuit = Circuit(mapping, error_probability)
        noiseless_qubits: list[tuple[int, int]] = []
        if full_post_selection:
            for y in range(0, mapping.height):
                for x in range(0, mapping.width):
                    if (x + y) % 2 == 0:
                        noiseless_qubits.append((x, y))
        else:
            for y in range(0, 16):
                for x in range(0, mapping.width):
                    if (x + y) % 2 == 0:
                        noiseless_qubits.append((x, y))
        self.partially_noiseless_circuit.mark_qubits_as_noiseless(noiseless_qubits)
        self.circuit = MultiplexingCircuit(self.primal_circuit, self.partially_noiseless_circuit)
        self.surface_syndrome_measurements: dict[tuple[int, int], SurfaceSyndromeMeasurement] = {}
        self.surface_offset_x = 1
        self.surface_offset_y = 17
        self.detector_for_complementary_gap: DetectorIdentifier | None = None
        self.num_detectors_for_lookup_table: int = -1
        self.skip_detector_for_complementary_gap = skip_detector_for_complementary_gap

        self._setup_syndrome_measurements()

    def _setup_syndrome_measurements(self) -> None:
        surface_distance = self.surface_distance
        surface_code_offset_x = self.surface_offset_x
        surface_code_offset_y = self.surface_offset_y

        FOUR_WEIGHT = SurfaceStabilizerPattern.FOUR_WEIGHT
        TWO_WEIGHT_UP = SurfaceStabilizerPattern.TWO_WEIGHT_UP
        TWO_WEIGHT_DOWN = SurfaceStabilizerPattern.TWO_WEIGHT_DOWN
        TWO_WEIGHT_LEFT = SurfaceStabilizerPattern.TWO_WEIGHT_LEFT
        TWO_WEIGHT_RIGHT = SurfaceStabilizerPattern.TWO_WEIGHT_RIGHT

        m: SurfaceSyndromeMeasurement
        for i in range(surface_distance):
            for j in range(surface_distance):
                x = surface_code_offset_x + j * 2
                y = surface_code_offset_y + i * 2

                # Weight-two syndrome measurements:
                if i == 0 and j % 2 == 0 and j < surface_distance - 1:
                    m = SurfaceXSyndromeMeasurement(self.circuit, (x + 1, y - 1), TWO_WEIGHT_DOWN, True)
                    self.surface_syndrome_measurements[(x + 1, y - 1)] = m
                if i == surface_distance - 1 and j % 2 == 1:
                    m = SurfaceXSyndromeMeasurement(self.circuit, (x + 1, y + 1), TWO_WEIGHT_UP, True)
                    self.surface_syndrome_measurements[(x + 1, y + 1)] = m
                if j == 0 and i % 2 == 1:
                    m = SurfaceZSyndromeMeasurement(self.circuit, (x - 1, y + 1), TWO_WEIGHT_RIGHT, False)
                    self.surface_syndrome_measurements[(x - 1, y + 1)] = m
                if j == surface_distance - 1 and i % 2 == 0 and i < surface_distance - 1:
                    m = SurfaceZSyndromeMeasurement(self.circuit, (x + 1, y + 1), TWO_WEIGHT_LEFT, False)
                    self.surface_syndrome_measurements[(x + 1, y + 1)] = m

                # Weight-four syndrome measurements:
                if i < surface_distance - 1 and j < surface_distance - 1:
                    if (i + j) % 2 == 0:
                        m = SurfaceZSyndromeMeasurement(self.circuit, (x + 1, y + 1), FOUR_WEIGHT, False)
                        if self.with_heuristic_post_selection and i < 4 and j < 5:
                            m.set_post_selection(True)
                    else:
                        m = SurfaceXSyndromeMeasurement(self.circuit, (x + 1, y + 1), FOUR_WEIGHT, True)
                        if self.with_heuristic_post_selection and i < 4 and j < 5:
                            m.set_post_selection(True)
                    self.surface_syndrome_measurements[(x + 1, y + 1)] = m

        if self.full_post_selection:
            for m in self.surface_syndrome_measurements.values():
                m.set_post_selection(True)

    def _prepare_qubits_for_code_expansion_upward(self) -> None:
        if self.surface_intermediate_distance == self.surface_final_distance:
            return

        surface_distance = self.surface_distance
        surface_offset_x = self.surface_offset_x
        surface_offset_y = self.surface_offset_y
        circuit = self.circuit

        intermediate_distance = self.surface_intermediate_distance
        final_distance = self.surface_final_distance
        assert final_distance == surface_distance

        for i in range(surface_distance):
            for j in range(surface_distance):
                x = surface_offset_x + j * 2
                y = surface_offset_y + i * 2

                # Initialize data qubits:
                if j < intermediate_distance and i >= final_distance - intermediate_distance:
                    pass
                elif i + j < final_distance - 1:
                    circuit.place_reset_x((x, y))
                else:
                    circuit.place_reset_z((x, y))

    def _prepare_qubits_for_code_expansion_downward(self) -> None:
        if self.surface_intermediate_distance == self.surface_final_distance:
            return

        surface_distance = self.surface_distance
        surface_offset_x = self.surface_offset_x
        surface_offset_y = self.surface_offset_y
        circuit = self.circuit

        intermediate_distance = self.surface_intermediate_distance
        final_distance = self.surface_final_distance
        assert final_distance == surface_distance

        for i in range(surface_distance):
            for j in range(surface_distance):
                x = surface_offset_x + j * 2
                y = surface_offset_y + i * 2

                # Initialize data qubits:
                if i < intermediate_distance and j < intermediate_distance:
                    pass
                elif i >= j:
                    circuit.place_reset_x((x, y))
                else:
                    circuit.place_reset_z((x, y))

    def _setup_syndrome_measurements_for_code_expansion_upward(self) -> None:
        if self.surface_intermediate_distance == self.surface_final_distance:
            return

        assert self.surface_intermediate_distance < self.surface_final_distance
        assert self.surface_distance == self.surface_final_distance
        surface_offset_x = self.surface_offset_x
        surface_offset_y = self.surface_offset_y
        surface_distance = self.surface_distance
        intermediate_distance = self.surface_intermediate_distance
        final_distance = self.surface_final_distance
        circuit = self.circuit
        syndrome_measurements = self.surface_syndrome_measurements

        TWO_WEIGHT_UP = SurfaceStabilizerPattern.TWO_WEIGHT_UP
        TWO_WEIGHT_DOWN = SurfaceStabilizerPattern.TWO_WEIGHT_DOWN
        TWO_WEIGHT_LEFT = SurfaceStabilizerPattern.TWO_WEIGHT_LEFT
        TWO_WEIGHT_RIGHT = SurfaceStabilizerPattern.TWO_WEIGHT_RIGHT
        FOUR_WEIGHT = SurfaceStabilizerPattern.FOUR_WEIGHT

        for i in range(surface_distance):
            for j in range(surface_distance):
                x = surface_offset_x + j * 2
                y = surface_offset_y + i * 2
                m: SurfaceSyndromeMeasurement

                # Weight-two syndrome measurements:
                if i == 0 and j % 2 == 0 and j < final_distance - 1:
                    assert (x + 1, y - 1) not in syndrome_measurements
                    m = SurfaceXSyndromeMeasurement(circuit, (x + 1, y - 1), TWO_WEIGHT_DOWN, True)
                    syndrome_measurements[(x + 1, y - 1)] = m
                if i == final_distance - 1 and j % 2 == 1 and intermediate_distance - 1 <= j and j < final_distance - 1:
                    assert (x + 1, y + 1) not in syndrome_measurements
                    m = SurfaceXSyndromeMeasurement(circuit, (x + 1, y + 1), TWO_WEIGHT_UP, False)
                    syndrome_measurements[(x + 1, y + 1)] = m
                if j == 0 and i % 2 == 1 and i < (final_distance - intermediate_distance):
                    assert (x - 1, y + 1) not in syndrome_measurements
                    m = SurfaceZSyndromeMeasurement(circuit, (x - 1, y + 1), TWO_WEIGHT_RIGHT, False)
                    syndrome_measurements[(x - 1, y + 1)] = m
                if j == final_distance - 1 and i % 2 == 0 and i < final_distance - 1:
                    assert (x + 1, y + 1) not in syndrome_measurements
                    m = SurfaceZSyndromeMeasurement(circuit, (x + 1, y + 1), TWO_WEIGHT_LEFT, True)
                    syndrome_measurements[(x + 1, y + 1)] = m

                # Weight-four syndrome measurements:
                if i >= final_distance - 1 or j >= final_distance - 1:
                    continue
                if i >= final_distance - intermediate_distance and j < intermediate_distance - 1:
                    continue

                last_measurement: MeasurementIdentifier | None = None
                if (i + j) % 2 == 0:
                    satisfied = i + j >= final_distance - 1
                    if (x + 1, y + 1) in syndrome_measurements:
                        assert j == intermediate_distance - 1
                        assert satisfied
                        m = syndrome_measurements[(x + 1), (y + 1)]
                        del syndrome_measurements[(x + 1), (y + 1)]
                        assert isinstance(m, SurfaceZSyndromeMeasurement)
                        assert m.pattern == TWO_WEIGHT_LEFT
                        last_measurement = m.last_measurement
                        assert last_measurement is not None
                        satisfied = False
                    m = SurfaceZSyndromeMeasurement(circuit, (x + 1, y + 1), FOUR_WEIGHT, satisfied)
                else:
                    satisfied = i + j < final_distance - 2
                    if (x + 1, y + 1) in syndrome_measurements:
                        assert i == final_distance - intermediate_distance - 1
                        assert satisfied
                        m = syndrome_measurements[(x + 1), (y + 1)]
                        del syndrome_measurements[(x + 1), (y + 1)]
                        assert isinstance(m, SurfaceXSyndromeMeasurement)
                        assert m.pattern == TWO_WEIGHT_DOWN
                        last_measurement = m.last_measurement
                        assert last_measurement is not None
                        satisfied = False
                    m = SurfaceXSyndromeMeasurement(circuit, (x + 1, y + 1), FOUR_WEIGHT, satisfied)
                m.last_measurement = last_measurement
                syndrome_measurements[(x + 1, y + 1)] = m

        assert len(syndrome_measurements) == (surface_distance * surface_distance) - 1

    def _setup_syndrome_measurements_for_code_expansion_downward(self) -> None:
        if self.surface_intermediate_distance == self.surface_final_distance:
            return

        assert self.surface_intermediate_distance < self.surface_final_distance
        assert self.surface_distance == self.surface_final_distance
        surface_offset_x = self.surface_offset_x
        surface_offset_y = self.surface_offset_y
        surface_distance = self.surface_distance
        intermediate_distance = self.surface_intermediate_distance
        final_distance = self.surface_final_distance
        circuit = self.circuit
        syndrome_measurements = self.surface_syndrome_measurements

        TWO_WEIGHT_UP = SurfaceStabilizerPattern.TWO_WEIGHT_UP
        TWO_WEIGHT_DOWN = SurfaceStabilizerPattern.TWO_WEIGHT_DOWN
        TWO_WEIGHT_LEFT = SurfaceStabilizerPattern.TWO_WEIGHT_LEFT
        TWO_WEIGHT_RIGHT = SurfaceStabilizerPattern.TWO_WEIGHT_RIGHT
        FOUR_WEIGHT = SurfaceStabilizerPattern.FOUR_WEIGHT

        for i in range(surface_distance):
            for j in range(surface_distance):
                x = surface_offset_x + j * 2
                y = surface_offset_y + i * 2
                m: SurfaceSyndromeMeasurement

                # Weight-two syndrome measurements:
                if i == 0 and j % 2 == 0 and intermediate_distance - 1 <= j and j < final_distance - 1:
                    assert (x + 1, y - 1) not in syndrome_measurements
                    m = SurfaceXSyndromeMeasurement(circuit, (x + 1, y - 1), TWO_WEIGHT_DOWN, False)
                    syndrome_measurements[(x + 1, y - 1)] = m
                if i == final_distance - 1 and j % 2 == 1 and j < final_distance - 1:
                    assert (x + 1, y + 1) not in syndrome_measurements
                    m = SurfaceXSyndromeMeasurement(circuit, (x + 1, y + 1), TWO_WEIGHT_UP, True)
                    syndrome_measurements[(x + 1, y + 1)] = m
                if j == 0 and i % 2 == 1 and intermediate_distance - 1 <= i and i < final_distance - 1:
                    assert (x - 1, y + 1) not in syndrome_measurements
                    m = SurfaceZSyndromeMeasurement(circuit, (x - 1, y + 1), TWO_WEIGHT_RIGHT, False)
                    syndrome_measurements[(x - 1, y + 1)] = m
                if j == final_distance - 1 and i % 2 == 0 and i < final_distance - 1:
                    assert (x + 1, y + 1) not in syndrome_measurements
                    m = SurfaceZSyndromeMeasurement(circuit, (x + 1, y + 1), TWO_WEIGHT_LEFT, True)
                    syndrome_measurements[(x + 1, y + 1)] = m

                # Weight-four syndrome measurements:
                if i >= final_distance - 1 or j >= final_distance - 1:
                    continue
                if i < intermediate_distance - 1 and j < intermediate_distance - 1:
                    continue

                last_measurement: MeasurementIdentifier | None = None
                if (i + j) % 2 == 0:
                    satisfied = i < j
                    if (x + 1, y + 1) in syndrome_measurements:
                        assert j == intermediate_distance - 1
                        assert satisfied
                        m = syndrome_measurements[(x + 1), (y + 1)]
                        del syndrome_measurements[(x + 1), (y + 1)]
                        assert isinstance(m, SurfaceZSyndromeMeasurement)
                        assert m.pattern == TWO_WEIGHT_LEFT
                        last_measurement = m.last_measurement
                        assert last_measurement is not None
                        satisfied = False
                    m = SurfaceZSyndromeMeasurement(circuit, (x + 1, y + 1), FOUR_WEIGHT, satisfied)
                else:
                    satisfied = j < i
                    if (x + 1, y + 1) in syndrome_measurements:
                        assert i == intermediate_distance - 1
                        assert satisfied
                        m = syndrome_measurements[(x + 1), (y + 1)]
                        del syndrome_measurements[(x + 1), (y + 1)]
                        assert isinstance(m, SurfaceXSyndromeMeasurement)
                        assert m.pattern == TWO_WEIGHT_UP
                        last_measurement = m.last_measurement
                        assert last_measurement is not None
                        satisfied = False
                    m = SurfaceXSyndromeMeasurement(circuit, (x + 1, y + 1), FOUR_WEIGHT, satisfied)
                m.last_measurement = last_measurement
                syndrome_measurements[(x + 1, y + 1)] = m

        assert len(syndrome_measurements) == (surface_distance * surface_distance) - 1

    def run(self) -> None:
        SURFACE_SYNDROME_MEASUREMENT_DEPTH = 6
        surface_distance = self.surface_distance
        circuit = self.circuit
        mapping = self.mapping

        surface_offset_x = self.surface_offset_x
        surface_offset_y = self.surface_offset_y

        if self.perfect_initialization:
            for stim_circuit in [self.primal_circuit.circuit, self.partially_noiseless_circuit.circuit]:
                match self.initial_value:
                    case InitialValue.Plus:
                        steane_code.perform_perfect_steane_plus_initialization(stim_circuit, mapping)
                    case InitialValue.Zero:
                        steane_code.perform_perfect_steane_zero_initialization(stim_circuit, mapping)
                    case InitialValue.SPlus:
                        steane_code.perform_perfect_steane_s_plus_initialization(stim_circuit, mapping)
            circuit.place_tick()
        else:
            steane_code.perform_injection(circuit)
            circuit.place_tick()
            circuit.place_layering_tick('Encode T')

            steane_code.perform_zx_syndrome_extraction_after_injection(circuit)
            circuit.place_tick()
            circuit.place_layering_tick('Stabilize')

            # We have one `place_layering_tick()` call in `perform_check()`.
            steane_code.perform_check(circuit)
            circuit.place_tick()
            circuit.place_layering_tick('Check T')

        ls_results = steane_code.LatticeSurgeryMeasurements()
        match self.steane_syndrome_extraction_pattern:
            case SteaneSyndromeExtractionPattern.XZZ:
                g = steane_code.lattice_surgery_generator_xzz(circuit, surface_distance, ls_results)
                SURFACE_SYNDROME_EXTRACTION_OFFSET = 3
            case SteaneSyndromeExtractionPattern.ZXZ:
                g = steane_code.lattice_surgery_generator_zxz(circuit, surface_distance, ls_results)
                SURFACE_SYNDROME_EXTRACTION_OFFSET = 0
            case SteaneSyndromeExtractionPattern.ZZ:
                g = steane_code.lattice_surgery_generator_zz(circuit, surface_distance, ls_results)
                SURFACE_SYNDROME_EXTRACTION_OFFSET = 0
        tick = 0

        while True:
            if tick == SURFACE_SYNDROME_EXTRACTION_OFFSET:
                for i in range(surface_distance):
                    for j in range(surface_distance):
                        x = surface_offset_x + j * 2
                        y = surface_offset_y + i * 2
                        circuit.place_reset_x((x, y))
                # Remove the stabilizers that conflict with the lattice surgery.
                for j in range(surface_distance):
                    x = surface_offset_x + j * 2
                    y = surface_offset_y
                    if j % 2 == 0 and j < surface_distance - 1:
                        del self.surface_syndrome_measurements[(x + 1, y - 1)]

            if tick >= SURFACE_SYNDROME_EXTRACTION_OFFSET:
                for m in self.surface_syndrome_measurements.values():
                    m.run()

            try:
                next(g)
            except StopIteration:
                assert ls_results.is_complete()
                circuit.place_tick()
                break

            circuit.place_tick()
            tick += 1

        circuit.place_layering_tick('Stabilize_2')

        # The qubits on the Steane code are now noisy for `self.partially_noiseless_circuit`.
        self.partially_noiseless_circuit.mark_qubits_as_noiseless([])
        self.num_detectors_for_lookup_table = self.partially_noiseless_circuit.circuit.num_detectors

        # Let's recover and reconfigure some stabilizers.
        for j in range(surface_distance):
            x = surface_offset_x + j * 2
            y = surface_offset_y
            if j % 2 == 0 and j < surface_distance - 1:
                m = SurfaceXSyndromeMeasurement(
                    self.circuit, (x + 1, y - 1), SurfaceStabilizerPattern.TWO_WEIGHT_DOWN, False)
                self.surface_syndrome_measurements[(x + 1, y - 1)] = m
                m.set_post_selection(self.full_post_selection)
        self.surface_syndrome_measurements[(surface_offset_x + 1, surface_offset_y - 1)].last_measurement = \
            ls_results.x_ab_measurement()

        if False:
            # Upward code expansion:
            # TODO: Consider removing this along with _setup_syndrome_measurements_for_code_expansion_upward() and
            # _prepare_qubits_for_code_expansion_upward().
            assert self.surface_distance == self.surface_intermediate_distance
            self.surface_distance = self.surface_final_distance
            self.surface_offset_y -= 2 * (self.surface_final_distance - self.surface_intermediate_distance)
            surface_offset_y = self.surface_offset_y
            surface_distance = self.surface_distance
            assert surface_offset_y >= 0
            self._setup_syndrome_measurements_for_code_expansion_upward()
            self._prepare_qubits_for_code_expansion_upward()
        else:
            # Downward code expansion:
            assert self.surface_distance == self.surface_intermediate_distance
            self.surface_distance = self.surface_final_distance
            surface_distance = self.surface_distance
            assert surface_offset_y + 2 * (surface_distance - 1) < mapping.height
            self._setup_syndrome_measurements_for_code_expansion_downward()
            self._prepare_qubits_for_code_expansion_downward()

        for m in self.surface_syndrome_measurements.values():
            m.set_post_selection(False)

        for _ in range(SURFACE_SYNDROME_MEASUREMENT_DEPTH):
            for m in self.surface_syndrome_measurements.values():
                m.run()
            circuit.place_tick()
        circuit.place_layering_tick('Escape!')

        for i in range(self.num_stabilization_rounds_after_surgery):
            for _ in range(SURFACE_SYNDROME_MEASUREMENT_DEPTH):
                for m in self.surface_syndrome_measurements.values():
                    m.run()
                circuit.place_tick()
            circuit.place_layering_tick('Stabilize\'_{}'.format(i))

        for i in range(self.num_epilogue_syndrome_extraction_rounds):
            for _ in range(SURFACE_SYNDROME_MEASUREMENT_DEPTH):
                for m in self.surface_syndrome_measurements.values():
                    m.run()
                circuit.place_tick()
            if i < self.num_epilogue_syndrome_extraction_rounds - 1:
                circuit.place_layering_tick('[wait for gap]')

        # Perfect verification of the resultant state.
        with SuppressNoise(circuit):
            for _ in range(SURFACE_SYNDROME_MEASUREMENT_DEPTH):
                for m in self.surface_syndrome_measurements.values():
                    m.run()
                circuit.place_tick()

            ms: list[MeasurementIdentifier] = []
            match self.initial_value:
                case InitialValue.Plus:
                    ms.append(circuit.place_mpp(self._logical_x_pauli_string()))
                    ms.extend(ls_results.logical_x_measurements())
                    if not self.skip_detector_for_complementary_gap:
                        self.detector_for_complementary_gap = circuit.place_detector(ms)
                    circuit.place_observable_include(ms)
                case InitialValue.Zero:
                    ms.append(circuit.place_mpp(self._logical_z_pauli_string()))
                    ms.extend(ls_results.lattice_surgery_zz_measurements())
                    if not self.skip_detector_for_complementary_gap:
                        self.detector_for_complementary_gap = circuit.place_detector(ms)
                    circuit.place_observable_include(ms)
                case InitialValue.SPlus:
                    ms.append(circuit.place_mpp(self._logical_y_pauli_string()))
                    ms.extend(ls_results.logical_x_measurements())
                    ms.extend(ls_results.lattice_surgery_zz_measurements())
                    if not self.skip_detector_for_complementary_gap:
                        self.detector_for_complementary_gap = circuit.place_detector(ms)
                    circuit.place_observable_include(ms)
            circuit.place_layering_tick('ready')

    def _logical_x_pauli_string(self) -> stim.PauliString:
        surface_distance = self.surface_distance
        mapping = self.mapping
        surface_code_offset_x = self.surface_offset_x
        surface_code_offset_y = self.surface_offset_y

        logical_x: stim.PauliString = stim.PauliString()
        for i in range(surface_distance):
            x = surface_code_offset_x
            y = surface_code_offset_y + i * 2
            logical_x *= stim.PauliString('X{}'.format(mapping.get_id(x, y)))
        return logical_x

    def _logical_z_pauli_string(self) -> stim.PauliString:
        surface_distance = self.surface_distance
        mapping = self.mapping
        surface_code_offset_x = self.surface_offset_x
        surface_code_offset_y = self.surface_offset_y

        logical_z: stim.PauliString = stim.PauliString()
        for j in range(surface_distance):
            x = surface_code_offset_x + j * 2
            y = surface_code_offset_y
            logical_z *= stim.PauliString('Z{}'.format(mapping.get_id(x, y)))
        return logical_z

    def _logical_y_pauli_string(self) -> stim.PauliString:
        return self._logical_x_pauli_string() * self._logical_z_pauli_string()


def construct_lookup_table(
        primal_stim_circuit: stim.Circuit,
        partially_noiseless_stim_circuit: stim.Circuit,
        num_shots: int,
        detector_for_complementary_gap: DetectorIdentifier,
        num_detectors_for_lookup_table: int,
        seed: int | None,
        detectors_for_post_selection: list[DetectorIdentifier],
        gap_threshold: float,
        with_heuristic_gap_calculation) -> tuple[LookupTable, bool]:
    # We construct a decoder for `partially_noiseless_stim_circuit`, not to confuse the matching decoder with
    # non-matchable detectors. We perform post-selection for all detectors in the Steane code, so the difference
    # between the two DEMs should be small...
    dem = partially_noiseless_stim_circuit.detector_error_model(decompose_errors=True)
    matcher = pymatching.Matching.from_detector_error_model(dem)

    # However, we construct a sampler from `primal_stim_circuit` because it is *the real* circuit.
    sampler = primal_stim_circuit.compile_detector_sampler(seed=seed)
    detection_events, observable_flips = sampler.sample(num_shots, separate_observables=True)

    results = SimulationResultsForDiscardRates()
    postselection_ids = np.array([id.id for id in detectors_for_post_selection], dtype='uint')

    table = LookupTable(gap_threshold=gap_threshold)

    all_nontrivial_syndromes_have_gap_below_threshold = True
    for shot in range(num_shots):
        syndrome = detection_events[shot]
        if np.any(syndrome[postselection_ids] != 0):
            results.add_discarded()
            continue

        prediction, weight = matcher.decode(syndrome, return_weight=True)
        min_weight = weight
        max_weight = weight

        syndrome[detector_for_complementary_gap.id] = not syndrome[detector_for_complementary_gap.id]
        try:
            c_prediction, c_weight = matcher.decode(syndrome, return_weight=True)
        except ValueError:
            c_prediction = None
            c_weight = math.inf
        if c_weight < min_weight:
            prediction = c_prediction
        min_weight = min(min_weight, c_weight)
        max_weight = max(max_weight, c_weight)

        syndrome[detector_for_complementary_gap.id] = not syndrome[detector_for_complementary_gap.id]

        actual = observable_flips[shot]
        assert isinstance(prediction, np.ndarray)
        expected = np.array_equal(actual, prediction)
        gap = max_weight - min_weight

        syndrome_for_table_is_trivial: bool = all(syndrome[:num_detectors_for_lookup_table] == 0)
        if with_heuristic_gap_calculation and syndrome_for_table_is_trivial:
            gap += 0.01

        gap *= 100

        table.add(syndrome[:num_detectors_for_lookup_table], gap, expected)
        if not syndrome_for_table_is_trivial and gap >= gap_threshold:
            all_nontrivial_syndromes_have_gap_below_threshold = False

    return (table, all_nontrivial_syndromes_have_gap_below_threshold)


def parallel_construct_lookup_table(
        primal_circuit: Circuit,
        partially_noiseless_circuit: Circuit,
        num_shots: int,
        detector_for_complementary_gap: DetectorIdentifier,
        num_detectors_for_lookup_table: int,
        seed: int,
        gap_threshold: float,
        with_heuristic_gap_calculation: bool,
        parallelism: int,
        num_shots_per_task: int,
        show_progress: bool) -> tuple[LookupTable, bool]:
    if num_shots / parallelism < 1000 or parallelism == 1:
        return construct_lookup_table(
            primal_circuit.circuit,
            partially_noiseless_circuit.circuit,
            num_shots,
            detector_for_complementary_gap,
            num_detectors_for_lookup_table,
            seed,
            primal_circuit.detectors_for_post_selection,
            gap_threshold,
            with_heuristic_gap_calculation)

    table = LookupTable(gap_threshold=gap_threshold)
    progress = 0

    all_nontrivial_syndromes_have_gap_below_threshold = True

    with ProcessPoolExecutor(max_workers=parallelism) as executor:
        futures: list[concurrent.futures.Future] = []
        remaining_shots = num_shots

        num_shots_per_task = min(num_shots_per_task, (num_shots + parallelism - 1) // parallelism)
        num_shots_for_future: dict[concurrent.futures.Future, int] = {}
        while remaining_shots > 0:
            seed_to_pass = (seed + remaining_shots) % (2 ** 64)
            num_shots_for_this_task = min(num_shots_per_task, remaining_shots)
            remaining_shots -= num_shots_for_this_task
            future = executor.submit(construct_lookup_table,
                                     primal_circuit.circuit,
                                     partially_noiseless_circuit.circuit,
                                     num_shots_for_this_task,
                                     detector_for_complementary_gap,
                                     num_detectors_for_lookup_table,
                                     seed_to_pass,
                                     primal_circuit.detectors_for_post_selection,
                                     gap_threshold,
                                     with_heuristic_gap_calculation)
            futures.append(future)
            num_shots_for_future[future] = num_shots_for_this_task
        try:
            while len(futures) > 0:
                import sys
                if show_progress:
                    print('Progress: {}% ({}/{})\r'.format(
                        round((progress / num_shots) * 100), progress, num_shots), end='')
                concurrent.futures.wait(futures, timeout=None, return_when=concurrent.futures.FIRST_COMPLETED)
                new_futures = []
                for future in futures:
                    if future.done():
                        table_per_task, all_nontrivial_syndromes_have_gap_below_threshold_per_task = future.result()
                        table.extend(table_per_task)
                        all_nontrivial_syndromes_have_gap_below_threshold = \
                            all_nontrivial_syndromes_have_gap_below_threshold and \
                            all_nontrivial_syndromes_have_gap_below_threshold_per_task
                        progress += num_shots_for_future[future]
                        del num_shots_for_future[future]
                    else:
                        new_futures.append(future)
                futures = new_futures
            if show_progress:
                print()
        finally:
            for future in futures:
                future.cancel()
    return (table, all_nontrivial_syndromes_have_gap_below_threshold)


@dataclass(unsafe_hash=True, frozen=True)
class SyndromeExtractionRound:
    label: str
    index: int


class SyndromeExtractionRounds:
    def __init__(self, circuit: Circuit, qubits_refreshing_label: str) -> None:
        self._rounds: list[SyndromeExtractionRound] = []
        self._num_qubits_used_for: dict[SyndromeExtractionRound, int] = {}
        self._aborting_rounds_for: list[SyndromeExtractionRound] = []
        qubits_in_use: set[int] = set()
        num_detectors_in_this_round = 0

        annotation_gates = {
            'DETECTOR',
            'MPAD',
            'OBSERVABLE_INCLUDE',
            'QUBIT_COORDS',
            'SHIFT_COORDS',
            'TICK'
        }
        error_gates = {
            'CORRELATED_ERROR',
            'DEPOLARIZE1',
            'DEPOLARIZE2',
            'E',
            'ELSE_CORRELATED_ERROR',
            'HERALDED_ERASE',
            'HERALDED_PAULI_CHANNEL_1',
            'II_ERROR',
            'I_ERROR',
            'PAULI_CHANNEL_1',
            'PAULI_CHANNEL_2',
            'X_ERROR',
            'Y_ERROR',
            'Z_ERROR'
        }

        for inst in circuit.circuit:
            # We don't support CircuitRepeatBlock.
            assert isinstance(inst, stim.CircuitInstruction)
            if inst.name == 'TICK' and inst.tag != '':
                r = SyndromeExtractionRound(inst.tag, len(self._rounds))
                self._rounds.append(r)
                self._num_qubits_used_for[r] = len(qubits_in_use)
                if inst.tag == qubits_refreshing_label:
                    qubits_in_use = set()
                for _ in range(num_detectors_in_this_round):
                    self._aborting_rounds_for.append(r)
                num_detectors_in_this_round = 0
            if inst.name == 'DETECTOR':
                num_detectors_in_this_round += 1
            if inst.name not in annotation_gates and inst.name not in error_gates:
                for target in inst.targets_copy():
                    if target.is_combiner:
                        continue
                    if target.is_qubit_target:
                        qubits_in_use.add(target.value)
                    elif target.is_x_target or target.is_y_target or target.is_z_target:
                        qubits_in_use.add(target.value)
                    else:
                        raise ValueError('Unsupported gate target')

        assert num_detectors_in_this_round == 0

    def num_qubits_used(self, round: SyndromeExtractionRound) -> int:
        return self._num_qubits_used_for[round]

    def aborting_round_for_syndrome(self, syndrome: np.ndarray) -> SyndromeExtractionRound:
        assert any(syndrome)
        return self._aborting_rounds_for[np.argmax(syndrome)]

    def aborting_round_for_detector_index(self, detector_index: int) -> SyndromeExtractionRound:
        return self._aborting_rounds_for[detector_index]

    def rounds(self) -> list[SyndromeExtractionRound]:
        return self._rounds


class SimulationResultsForDiscardRates:
    class Bucket:
        def __init__(self) -> None:
            self.num_valid_samples: int = 0
            self.num_wrong_samples: int = 0

    def __init__(self) -> None:
        self.buckets: list[SimulationResultsForDiscardRates.Bucket] = []
        self.num_discarded_samples: int = 0

    def ensure_bucket(self, gap: float) -> SimulationResultsForDiscardRates.Bucket:
        int_gap = int(gap)
        if len(self.buckets) > int_gap:
            return self.buckets[int_gap]
        Bucket = SimulationResultsForDiscardRates.Bucket
        self.buckets.extend([Bucket() for _ in range(int_gap - len(self.buckets) + 1)])
        assert len(self.buckets) == int_gap + 1
        return self.buckets[int_gap]

    def add(self, gap: float, expected: bool) -> None:
        bucket = self.ensure_bucket(gap)

        if expected:
            bucket.num_valid_samples += 1
        else:
            bucket.num_wrong_samples += 1

    def add_discarded(self) -> None:
        self.num_discarded_samples += 1

    def extend(self, other: SimulationResultsForDiscardRates) -> None:
        Bucket = SimulationResultsForDiscardRates.Bucket
        self.buckets.extend([Bucket() for _ in range(len(other.buckets) - len(self.buckets))])
        assert len(self.buckets) >= len(other.buckets)

        self.num_discarded_samples += other.num_discarded_samples
        for (i, bucket) in enumerate(other.buckets):
            self.buckets[i].num_valid_samples += bucket.num_valid_samples
            self.buckets[i].num_wrong_samples += bucket.num_wrong_samples

    def __len__(self) -> int:
        return sum([b.num_valid_samples + b.num_wrong_samples for b in self.buckets]) + self.num_discarded_samples


class SimulationResultsForGapThreshold:
    class Entry:
        def __init__(self) -> None:
            self._num_valid_samples: int = 0
            self._num_wrong_samples: int = 0
            self._num_discarded_samples: dict[SyndromeExtractionRound, int] = {}

        def extend(self, other: SimulationResultsForGapThreshold.Entry):
            self._num_valid_samples += other._num_valid_samples
            self._num_wrong_samples += other._num_wrong_samples
            for round, count in other._num_discarded_samples.items():
                if round not in self._num_discarded_samples:
                    self._num_discarded_samples[round] = 0
                self._num_discarded_samples[round] += count

        def num_valid_samples(self) -> int:
            return self._num_valid_samples

        def num_wrong_samples(self) -> int:
            return self._num_wrong_samples

        def num_discarded_samples(self) -> int:
            return sum(self._num_discarded_samples.values())

        def num_discarded_samples_for(self, round: SyndromeExtractionRound) -> int:
            return self._num_discarded_samples.get(round, 0)

        def add_valid(self) -> None:
            self._num_valid_samples += 1

        def add_wrong(self) -> None:
            self._num_wrong_samples += 1

        def add_discarded(self, round: SyndromeExtractionRound) -> None:
            if round not in self._num_discarded_samples:
                self._num_discarded_samples[round] = 0
            self._num_discarded_samples[round] += 1

        def __len__(self):
            return self._num_valid_samples + self._num_wrong_samples + self.num_discarded_samples()

    def __init__(self, gap_threshold: float) -> None:
        self._entry_with_lookup_table = SimulationResultsForGapThreshold.Entry()
        self._entry_without_lookup_table = SimulationResultsForGapThreshold.Entry()

        self.gap_threshold = gap_threshold

    def add_discarded(self, round: SyndromeExtractionRound) -> None:
        self._entry_with_lookup_table.add_discarded(round)
        self._entry_without_lookup_table.add_discarded(round)

    def add(self, gap: float, expected: bool, discarded_due_to_lookup_table: bool,
            lookup_table_round: SyndromeExtractionRound, gap_round: SyndromeExtractionRound) -> None:
        if discarded_due_to_lookup_table:
            self._entry_with_lookup_table.add_discarded(lookup_table_round)
        if gap < self.gap_threshold:
            if not discarded_due_to_lookup_table:
                self._entry_with_lookup_table.add_discarded(gap_round)
            self._entry_without_lookup_table.add_discarded(gap_round)
        elif expected:
            if not discarded_due_to_lookup_table:
                self._entry_with_lookup_table.add_valid()
            self._entry_without_lookup_table.add_valid()
        else:
            if not discarded_due_to_lookup_table:
                self._entry_with_lookup_table.add_wrong()
            self._entry_without_lookup_table.add_wrong()

    def entry_with_lookup_table(self) -> SimulationResultsForGapThreshold.Entry:
        return self._entry_with_lookup_table

    def entry_without_lookup_table(self) -> SimulationResultsForGapThreshold.Entry:
        return self._entry_without_lookup_table

    def extend(self, other: SimulationResultsForGapThreshold) -> None:
        assert self.gap_threshold == other.gap_threshold
        self._entry_with_lookup_table.extend(other._entry_with_lookup_table)
        self._entry_without_lookup_table.extend(other._entry_without_lookup_table)

    def __len__(self) -> int:
        a = len(self._entry_with_lookup_table)
        b = len(self._entry_without_lookup_table)
        assert a == b
        return a


SimulationResults = SimulationResultsForDiscardRates | SimulationResultsForGapThreshold


def perform_simulation(
        primal_circuit: Circuit,
        partially_noiseless_circuit: Circuit,
        num_shots: int,
        gap_threshold: float | None,
        with_heuristic_gap_calculation: bool,
        lookup_table: LookupTableWithNegativeSamplesOnly | None,
        num_detectors_for_lookup_table: int,
        detector_for_complementary_gap: DetectorIdentifier,
        seed: int | None) -> SimulationResults:
    primal_stim_circuit: stim.Circuit = primal_circuit.circuit
    partially_noiseless_stim_circuit: stim.Circuit = partially_noiseless_circuit.circuit
    detectors_for_post_selection: list[DetectorIdentifier] = primal_circuit.detectors_for_post_selection

    # We construct a decoder for `partially_noiseless_stim_circuit`, not to confuse the matching decoder with
    # non-matchable detectors. We perform post-selection for all detectors in the Steane code, so the difference
    # between the two DEMs should be small...
    dem = partially_noiseless_stim_circuit.detector_error_model(decompose_errors=True)
    matcher = pymatching.Matching.from_detector_error_model(dem)

    # However, we construct a sampler from `primal_stim_circuit` because it is *the real* circuit.
    sampler = primal_stim_circuit.compile_detector_sampler(seed=seed)
    detection_events, observable_flips = sampler.sample(num_shots, separate_observables=True)
    rounds = SyndromeExtractionRounds(primal_circuit, '')
    lookup_table_round: SyndromeExtractionRound = \
        rounds.aborting_round_for_detector_index(num_detectors_for_lookup_table - 1)
    last_round = rounds.rounds()[-1]

    results: SimulationResults
    if gap_threshold is None:
        results = SimulationResultsForDiscardRates()
    else:
        results = SimulationResultsForGapThreshold(gap_threshold)
    postselection_ids = np.array([id.id for id in detectors_for_post_selection], dtype='uint')

    for shot in range(num_shots):
        syndrome = detection_events[shot]
        if np.any(syndrome[postselection_ids] != 0):
            if isinstance(results, SimulationResultsForGapThreshold):
                results.add_discarded(rounds.aborting_round_for_syndrome(syndrome))
            else:
                assert isinstance(results, SimulationResultsForDiscardRates)
                results.add_discarded()
            continue

        prediction, weight = matcher.decode(syndrome, return_weight=True)
        min_weight = weight
        max_weight = weight

        syndrome[detector_for_complementary_gap.id] = not syndrome[detector_for_complementary_gap.id]
        try:
            c_prediction, c_weight = matcher.decode(syndrome, return_weight=True)
        except ValueError:
            c_prediction = None
            c_weight = math.inf
        if c_weight < min_weight:
            prediction = c_prediction
        min_weight = min(min_weight, c_weight)
        max_weight = max(max_weight, c_weight)

        syndrome[detector_for_complementary_gap.id] = not syndrome[detector_for_complementary_gap.id]

        actual = observable_flips[shot]
        assert isinstance(prediction, np.ndarray)
        expected = np.array_equal(actual, prediction)
        gap = max_weight - min_weight

        if with_heuristic_gap_calculation and all(syndrome[:num_detectors_for_lookup_table] == 0):
            gap += 0.01

        gap *= 100

        if gap_threshold is None:
            assert isinstance(results, SimulationResultsForDiscardRates)
            results.add(gap, expected)
        else:
            assert isinstance(results, SimulationResultsForGapThreshold)
            discarded_due_to_lookup_table = False
            if lookup_table is not None:
                bytes = syndrome[:num_detectors_for_lookup_table].tobytes()
                discarded_due_to_lookup_table = bytes in lookup_table
            results.add(gap, expected, discarded_due_to_lookup_table, lookup_table_round, last_round)

    return results


def perform_parallel_simulation(
        primal_circuit: Circuit,
        partially_noiseless_circuit: Circuit,
        detector_for_complementary_gap: DetectorIdentifier,
        num_shots: int,
        gap_threshold: float | None,
        with_heuristic_gap_calculation: bool,
        lookup_table: LookupTableWithNegativeSamplesOnly | None,
        num_detectors_for_lookup_table: int,
        seed: int,
        parallelism: int,
        num_shots_per_task: int,
        show_progress: bool) -> SimulationResults:
    if num_shots / parallelism < 1000 or parallelism == 1:
        return perform_simulation(
                primal_circuit,
                partially_noiseless_circuit,
                num_shots,
                gap_threshold,
                with_heuristic_gap_calculation,
                lookup_table,
                num_detectors_for_lookup_table,
                detector_for_complementary_gap,
                seed)

    results: SimulationResults
    if gap_threshold is None:
        results = SimulationResultsForDiscardRates()
    else:
        results = SimulationResultsForGapThreshold(gap_threshold)
    progress = 0
    with ProcessPoolExecutor(max_workers=parallelism) as executor:
        futures: list[concurrent.futures.Future] = []
        remaining_shots = num_shots

        num_shots_per_task = min(num_shots_per_task, (num_shots + parallelism - 1) // parallelism)
        while remaining_shots > 0:
            seed_to_pass = (seed + remaining_shots) % (2 ** 64)
            num_shots_for_this_task = min(num_shots_per_task, remaining_shots)
            remaining_shots -= num_shots_for_this_task
            future = executor.submit(perform_simulation,
                                     primal_circuit,
                                     partially_noiseless_circuit,
                                     num_shots_for_this_task,
                                     gap_threshold,
                                     with_heuristic_gap_calculation,
                                     lookup_table,
                                     num_detectors_for_lookup_table,
                                     detector_for_complementary_gap,
                                     seed_to_pass)
            futures.append(future)
        try:
            while len(futures) > 0:
                import sys
                if show_progress:
                    print('Progress: {}% ({}/{})\r'.format(
                        round((progress / num_shots) * 100), progress, num_shots), end='')
                concurrent.futures.wait(futures, timeout=None, return_when=concurrent.futures.FIRST_COMPLETED)
                new_futures = []
                for future in futures:
                    if future.done():
                        future_results = future.result()
                        if gap_threshold is None:
                            assert isinstance(results, SimulationResultsForDiscardRates)
                            assert isinstance(future_results, SimulationResultsForDiscardRates)
                            results.extend(future_results)
                        else:
                            assert isinstance(results, SimulationResultsForGapThreshold)
                            assert isinstance(future_results, SimulationResultsForGapThreshold)
                            results.extend(future_results)
                        progress += len(future.result())
                    else:
                        new_futures.append(future)
                futures = new_futures
            if show_progress:
                print()
        finally:
            for future in futures:
                future.cancel()
    return results


def print_results_for_gap_threshold_entry(
        result_entry: SimulationResultsForGapThreshold.Entry, label: str, rounds: SyndromeExtractionRounds) -> None:
    num_valid = result_entry.num_valid_samples()
    num_wrong = result_entry.num_wrong_samples()
    num_discarded = result_entry.num_discarded_samples()
    num_samples = num_valid + num_wrong + num_discarded

    print(label)
    print('  VALID = {}, WRONG = {}, DISCARDED = {}'.format(num_valid, num_wrong, num_discarded))
    if num_valid + num_wrong == 0:
        print('  WRONG / (VALID + WRONG) = nan')
    else:
        print('  WRONG / (VALID + WRONG) = {:.3e}'.format(num_wrong / (num_valid + num_wrong)))
    print('  (VALID + WRONG) / SHOTS = {:.3f}'.format((num_valid + num_wrong) / num_samples))

    if num_valid + num_wrong == 0:
        print('  QUBITROUNDS = inf')
        return

    num_samples_at_this_round = num_samples
    qubitround_so_far: float = 0
    for round in rounds.rounds():
        num_qubits = rounds.num_qubits_used(round)

        num_discarded_at_this_round = result_entry.num_discarded_samples_for(round)
        round_success_rate = 1 - num_discarded_at_this_round / num_samples_at_this_round
        qubitround_so_far = (qubitround_so_far + num_qubits) / round_success_rate

        num_samples_at_this_round -= num_discarded_at_this_round
        print('  {}: num_qubits = {}, round success rate = {:.3f}, cost = {:.3f} '.format(
            round.label, num_qubits, round_success_rate, qubitround_so_far))
    assert num_samples_at_this_round == num_valid + num_wrong
    print('  QUBITROUNDS = {:.3f}'.format(qubitround_so_far))


def main() -> None:
    parser = argparse.ArgumentParser(description='description')
    parser.add_argument('--num-shots', type=int, default=1000)
    parser.add_argument('--error-probability', type=float, default=0)
    parser.add_argument('--parallelism', type=int, default=1)
    parser.add_argument('--max-shots-per-task', type=int, default=2 ** 20)
    parser.add_argument('--surface-intermediate-distance', type=int, default=None)
    parser.add_argument('--surface-final-distance', type=int, default=3)
    parser.add_argument('--initial-value', choices=['+', '0', 'S+'], default='+')
    parser.add_argument('--steane-syndrome-extraction-pattern', choices=['XZZ', 'ZXZ', 'ZZ'], default='ZXZ',)
    parser.add_argument('--perfect-initialization', action='store_true')
    parser.add_argument('--imperfect-initialization', action='store_true')
    parser.add_argument('--with-heuristic-post-selection', action='store_true')
    parser.add_argument('--with-heuristic-gap-calculation', action='store_true')
    parser.add_argument('--full-post-selection', action='store_true')
    parser.add_argument('--num-stabilization-rounds-after-surgery', type=int, default=3)
    parser.add_argument('--num-epilogue-syndrome-extraction-rounds', type=int, default=10)
    parser.add_argument('--discard-rates', type=str)
    parser.add_argument('--gap-threshold', type=float)
    parser.add_argument('--print-circuit', action='store_true')
    parser.add_argument('--construct-lookup-table', action='store_true')
    parser.add_argument('--lookup-table-min-samples', type=int, default=100)
    parser.add_argument('--skip-detector-for-complementary-gap', action='store_true')
    parser.add_argument('--seed', type=int, default=None)
    parser.add_argument('--show-progress', action='store_true')

    args = parser.parse_args()

    if args.perfect_initialization and args.imperfect_initialization:
        print('Error: Cannot specify both --perfect-initialization and --imperfect-initialization.', file=sys.stderr)
        return

    perfect_initialization: bool = False
    if args.perfect_initialization:
        perfect_initialization = True
    elif args.imperfect_initialization:
        perfect_initialization = False

    if args.discard_rates is None and args.gap_threshold is None:
        print('Error: at least one of --discard-rates or --gap-threshold must be specified.', file=sys.stderr)
        return
    if args.discard_rates is not None and args.gap_threshold is not None:
        print('Error: Cannot specify both --discard-rates and --gap-threshold.', file=sys.stderr)
        return

    seed: int
    if args.seed is None:
        seed = random.randrange(0, 2 ** 32)
    else:
        seed = args.seed

    print('  num-shots = {}'.format(args.num_shots))
    print('  error-probability = {}'.format(args.error_probability))
    print('  parallelism = {}'.format(args.parallelism))
    print('  max-shots-per-task = {}'.format(args.max_shots_per_task))
    print('  surface-intermediate-distance = {}'.format(args.surface_intermediate_distance))
    print('  surface-final-distance = {}'.format(args.surface_final_distance))
    print('  initial-value = {}'.format(args.initial_value))
    print('  steane-syndrome-extraction-pattern = {}'.format(args.steane_syndrome_extraction_pattern))
    print('  perfect-initialization = {}'.format(perfect_initialization))
    print('  with-heuristic-post-selection = {}'.format(args.with_heuristic_post_selection))
    print('  with-heuristic-gap-calculation = {}'.format(args.with_heuristic_gap_calculation))
    print('  full-post-selection = {}'.format(args.full_post_selection))
    print('  num-stabilization-rounds-after-surgery = {}'.format(args.num_stabilization_rounds_after_surgery))
    print('  num-epilogue-syndrome-extraction-rounds = {}'.format(args.num_epilogue_syndrome_extraction_rounds))
    print('  discard-rates = {}'.format(args.discard_rates))
    print('  gap-threshold = {}'.format(args.gap_threshold))
    print('  print-circuit = {}'.format(args.print_circuit))
    print('  construct-lookup-table = {}'.format(args.construct_lookup_table))
    print('  lookup-table-min-samples = {}'.format(args.lookup_table_min_samples))
    print('  skip-detector-for-complementary-gap = {}'.format(args.skip_detector_for_complementary_gap))
    if args.seed is None:
        print('  seed = None ({})'.format(seed))
    else:
        print('  seed = {}'.format(seed))
    print('  show-progress = {}'.format(args.show_progress))

    num_shots: int = args.num_shots
    error_probability: float = args.error_probability
    parallelism: int = args.parallelism
    max_shots_per_task: int = args.max_shots_per_task
    surface_final_distance: int = args.surface_final_distance
    surface_intermediate_distance: int = args.surface_intermediate_distance or surface_final_distance
    match args.initial_value:
        case '+':
            initial_value = InitialValue.Plus
        case '0':
            initial_value = InitialValue.Zero
        case 'S+':
            initial_value = InitialValue.SPlus
        case _:
            assert False
    match args.steane_syndrome_extraction_pattern:
        case 'XZZ':
            steane_syndrome_extraction_pattern = SteaneSyndromeExtractionPattern.XZZ
        case 'ZXZ':
            steane_syndrome_extraction_pattern = SteaneSyndromeExtractionPattern.ZXZ
        case 'ZZ':
            steane_syndrome_extraction_pattern = SteaneSyndromeExtractionPattern.ZZ
        case _:
            assert False
    gap_threshold: float | None
    discard_rates: list[float]
    if args.gap_threshold is None:
        gap_threshold = None
        assert isinstance(args.discard_rates, str)
        if not re.compile(r'^\d+(\.\d+)?(,\d+(\.\d+)?)*$').match(args.discard_rates):
            print('Error: --discard-rates must be a comma-separated list of numbers.', file=sys.stderr)
            return
        discard_rates = [float(x) for x in args.discard_rates.split(',')]
        discard_rates.sort()
    else:
        assert isinstance(args.gap_threshold, float)
        assert args.discard_rates is None
        gap_threshold = args.gap_threshold
        discard_rates = []

    with_heuristic_post_selection: bool = args.with_heuristic_post_selection
    with_heuristic_gap_calculation: bool = args.with_heuristic_gap_calculation
    full_post_selection: bool = args.full_post_selection
    num_stabilization_rounds_after_surgery: int = args.num_stabilization_rounds_after_surgery
    num_epilogue_syndrome_extraction_rounds: int = args.num_epilogue_syndrome_extraction_rounds
    print_circuit: bool = args.print_circuit
    construct_lookup_table: bool = args.construct_lookup_table
    lookup_table_min_samples: int = args.lookup_table_min_samples
    skip_detector_for_complementary_gap: bool = args.skip_detector_for_complementary_gap
    show_progress: bool = args.show_progress

    if not perfect_initialization and initial_value != InitialValue.SPlus:
        print('perfect-initialization=False is supported only for S+ initial value.', file=sys.stderr)
        return

    if construct_lookup_table and gap_threshold is None:
        print('Error: --construct-lookup-table must be used with --gap-threshold.', file=sys.stderr)
        return

    mapping = QubitMapping(30, 40)
    r = SteanePlusSurfaceCode(
        mapping, surface_intermediate_distance, surface_final_distance, initial_value,
        steane_syndrome_extraction_pattern,
        perfect_initialization, error_probability, with_heuristic_post_selection, full_post_selection,
        num_stabilization_rounds_after_surgery,
        num_epilogue_syndrome_extraction_rounds, skip_detector_for_complementary_gap)
    primal_circuit = r.primal_circuit
    partially_noiseless_circuit = r.partially_noiseless_circuit
    stim_circuit = primal_circuit.circuit
    r.run()
    if print_circuit:
        print(primal_circuit.circuit)

    # Assert that the circuit have deterministic detectors.
    # The primal circuit has a non-graph-like DEM.
    _ = stim_circuit.detector_error_model()
    # The partially noiseless circuit has a graph-like DEM.
    _ = partially_noiseless_circuit.circuit.detector_error_model(decompose_errors=True)

    if num_shots == 0:
        return

    detector_for_complementary_gap = r.detector_for_complementary_gap
    assert detector_for_complementary_gap is not None

    lookup_table_key = LookupTableKey(
        error_probability=error_probability,
        surface_intermediate_distance=surface_intermediate_distance,
        surface_final_distance=surface_final_distance,
        initial_value=initial_value.name,
        steane_syndrome_extraction_pattern=steane_syndrome_extraction_pattern.name,
        perfect_initialization=perfect_initialization,
        with_heuristic_post_selection=with_heuristic_post_selection,
        with_heuristic_gap_calculation=with_heuristic_gap_calculation,
        full_post_selection=full_post_selection,
        num_stabilization_rounds_after_surgery=num_stabilization_rounds_after_surgery,
        num_epilogue_syndrome_extraction_rounds=num_epilogue_syndrome_extraction_rounds,
        gap_threshold=gap_threshold or 0)

    lookup_table: LookupTableWithNegativeSamplesOnly | None = None
    with sqlite3.connect('lookup_table.db') as lookup_table_con:
        ensure_lookup_tables_table(lookup_table_con)

        if construct_lookup_table:
            assert gap_threshold is not None
            print('Constructing the lookup table...')
            (table, all_nontrivial_syndromes_have_gap_below_threshold) = parallel_construct_lookup_table(
                primal_circuit,
                partially_noiseless_circuit,
                num_shots,
                detector_for_complementary_gap,
                r.num_detectors_for_lookup_table,
                seed,
                gap_threshold,
                with_heuristic_gap_calculation,
                parallelism,
                max_shots_per_task,
                show_progress
            )
            if all_nontrivial_syndromes_have_gap_below_threshold:
                print('All non-trivial syndromes have gap below threshold.')
                table.set_reject_nontrivial()
            print('len(table) = {}, num_samples = {}'.format(len(table), table.num_samples()))
            lookup_table_to_store = table.negative_samples_only(lookup_table_min_samples)
            print('Storing the lookup table of size {}...'.format(len(lookup_table_to_store)))
            store_lookup_table(lookup_table_con, lookup_table_key, lookup_table_to_store)
            return

        if gap_threshold is not None:
            lookup_table = query_lookup_table(lookup_table_con, lookup_table_key)
            if lookup_table is None:
                print('No lookup table is found.')
            else:
                print('A lookup table of size {} is found.'.format(len(lookup_table)))

    results = perform_parallel_simulation(
        primal_circuit,
        partially_noiseless_circuit,
        detector_for_complementary_gap,
        num_shots,
        gap_threshold,
        with_heuristic_gap_calculation,
        lookup_table,
        r.num_detectors_for_lookup_table,
        seed,
        parallelism,
        max_shots_per_task,
        show_progress)

    if gap_threshold is None:
        assert isinstance(results, SimulationResultsForDiscardRates)
        num_discarded = results.num_discarded_samples
        num_samples = len(results)
        num_valid = sum([b.num_valid_samples for b in results.buckets])
        num_wrong = sum([b.num_wrong_samples for b in results.buckets])
        bucket_index = 0
        for rate in discard_rates:
            while True:
                bucket = results.buckets[bucket_index]
                if num_discarded + bucket.num_valid_samples + bucket.num_wrong_samples >= num_samples * rate:
                    break

                num_valid -= bucket.num_valid_samples
                num_wrong -= bucket.num_wrong_samples
                num_discarded += bucket.num_valid_samples + bucket.num_wrong_samples
                bucket_index += 1

            v = num_valid
            w = num_wrong
            d = num_discarded
            num_to_be_discarded_additionally = num_samples * rate - num_discarded
            if num_to_be_discarded_additionally > 0:
                assert num_to_be_discarded_additionally <= bucket.num_valid_samples + bucket.num_wrong_samples
                bucket_valid_rate = bucket.num_valid_samples / (bucket.num_valid_samples + bucket.num_wrong_samples)
                bucket_wrong_rate = 1 - bucket_valid_rate
                v -= round(num_to_be_discarded_additionally * bucket_valid_rate)
                w -= round(num_to_be_discarded_additionally * bucket_wrong_rate)
                assert abs(v + w + d + num_to_be_discarded_additionally - num_samples) < 3
                d = num_samples - v - w

            print('Discard {:.1f}% samples, VALID = {}, WRONG = {}, DISCARDED = {}, bucket_index = {}'.format(
                rate * 100, v, w, d, bucket_index))
            if num_valid + num_wrong == 0:
                print('WRONG / (VALID + WRONG) = nan')
            else:
                print('WRONG / (VALID + WRONG) = {:.3e}'.format(w / (v + w)))
            print('(VALID + WRONG) / SHOTS = {:.3f}'.format((v + w) / num_samples))
    else:
        assert isinstance(results, SimulationResultsForGapThreshold)
        rounds = SyndromeExtractionRounds(partially_noiseless_circuit, 'Stabilize_2')

        print_results_for_gap_threshold_entry(results.entry_without_lookup_table(), 'Without lookup table:', rounds)
        print_results_for_gap_threshold_entry(results.entry_with_lookup_table(), 'With lookup table:', rounds)
    print()


if __name__ == '__main__':
    main()
