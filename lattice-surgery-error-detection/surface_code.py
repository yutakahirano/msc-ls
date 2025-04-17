from __future__ import annotations

import enum

from enum import auto
from collections.abc import Callable
from util import Circuit, MeasurementIdentifier


class SurfaceStabilizerPattern(enum.Enum):
    '''Represents a stabilizer pattern for the surface code.'''
    FOUR_WEIGHT = auto(),
    TWO_WEIGHT_UP = auto(),
    TWO_WEIGHT_DOWN = auto(),
    TWO_WEIGHT_LEFT = auto(),
    TWO_WEIGHT_RIGHT = auto(),


class SurfaceZSyndromeMeasurement:
    '''\
    A Z syndrome measurement for the surface code.
    '''

    def __init__(
            self, circuit: Circuit, ancilla_position: tuple[int, int],
            pattern: SurfaceStabilizerPattern, already_satisfied: bool) -> None:
        '''\
        When `already_satisfied` is true, the initial syndrome is added as a
        detector event.
        '''
        self.circuit = circuit
        self.stage = 0
        self._ancilla_position = ancilla_position
        self.pattern = pattern
        self.last_measurement: MeasurementIdentifier | None = None
        self.post_selection = False
        self.already_satisfied = already_satisfied

        (x, y) = ancilla_position
        left_top = (x - 1, y - 1)
        left_bottom = (x - 1, y + 1)
        right_top = (x + 1, y - 1)
        right_bottom = (x + 1, y + 1)

        self.actions: list[Callable[[], None]]
        match pattern:
            case SurfaceStabilizerPattern.FOUR_WEIGHT:
                self.actions = [
                    self._reset,
                    lambda: self._cx(left_top),
                    lambda: self._cx(left_bottom),
                    lambda: self._cx(right_top),
                    lambda: self._cx(right_bottom),
                    self._measure,
                ]
            case SurfaceStabilizerPattern.TWO_WEIGHT_UP:
                self.actions = [
                    self._reset,
                    lambda: self._cx(left_top),
                    lambda: None,
                    lambda: self._cx(right_top),
                    self._measure,
                    lambda: None,
                ]
            case SurfaceStabilizerPattern.TWO_WEIGHT_DOWN:
                self.actions = [
                    lambda: None,
                    self._reset,
                    lambda: self._cx(left_bottom),
                    lambda: None,
                    lambda: self._cx(right_bottom),
                    self._measure,
                ]
            case SurfaceStabilizerPattern.TWO_WEIGHT_LEFT:
                self.actions = [
                    self._reset,
                    lambda: self._cx(left_top),
                    lambda: self._cx(left_bottom),
                    self._measure,
                    lambda: None,
                    lambda: None,
                ]
            case SurfaceStabilizerPattern.TWO_WEIGHT_RIGHT:
                self.actions = [
                    lambda: None,
                    lambda: None,
                    self._reset,
                    lambda: self._cx(right_top),
                    lambda: self._cx(right_bottom),
                    self._measure,
                ]
        assert len(self.actions) == 6

    @property
    def ancilla_position(self) -> tuple[int, int]:
        return self._ancilla_position

    def set_post_selection(self, post_selection: bool) -> None:
        self.post_selection = post_selection

    def is_complete(self) -> bool:
        '''\
        Returns True if the current syndrome measurement process has completed
        and the next has not yet started.'''
        return self.stage == 0

    def run(self) -> None:
        '''Reus the syndrome measurement.'''
        self.actions[self.stage]()
        self.stage = (self.stage + 1) % 6

    def _reset(self) -> None:
        self.circuit.place_reset_z(self._ancilla_position)

    def _cx(self, position: tuple[int, int]) -> None:
        self.circuit.place_cx(position, self._ancilla_position)

    def _measure(self) -> None:
        last = self.last_measurement
        i = self.circuit.place_measurement_z(self._ancilla_position)
        if last is None:
            if self.already_satisfied:
                self.circuit.place_detector([i], post_selection=self.post_selection)
        else:
            self.circuit.place_detector([last, i], post_selection=self.post_selection)
        self.last_measurement = i


# An X syndrome measurement for the surface code. Unlike syndrome measurements for the Steane code,
# this class expects the consumer to call `run()` in coordination with other syndrome measurements.
class SurfaceXSyndromeMeasurement:
    '''\
    An X syndrome measurement for the surface code.
    '''
    def __init__(
            self, circuit: Circuit, ancilla_position: tuple[int, int],
            pattern: SurfaceStabilizerPattern, already_satisfied: bool) -> None:
        '''\
        When `already_satisfied` is true, the initial syndrome is added as a
        detector event.
        '''
        self.circuit = circuit
        self.stage = 0
        self._ancilla_position = ancilla_position
        self.pattern = pattern
        self.last_measurement: MeasurementIdentifier | None = None
        self.post_selection = False
        self.already_satisfied = already_satisfied

        (x, y) = ancilla_position
        left_top = (x - 1, y - 1)
        left_bottom = (x - 1, y + 1)
        right_top = (x + 1, y - 1)
        right_bottom = (x + 1, y + 1)

        self.actions: list[Callable[[], None]]
        match pattern:
            case SurfaceStabilizerPattern.FOUR_WEIGHT:
                self.actions = [
                    self._reset,
                    lambda: self._cx(left_top),
                    lambda: self._cx(right_top),
                    lambda: self._cx(left_bottom),
                    lambda: self._cx(right_bottom),
                    self._measure,
                ]
            case SurfaceStabilizerPattern.TWO_WEIGHT_UP:
                self.actions = [
                    self._reset,
                    lambda: self._cx(left_top),
                    lambda: self._cx(right_top),
                    self._measure,
                    lambda: None,
                    lambda: None,
                ]
            case SurfaceStabilizerPattern.TWO_WEIGHT_DOWN:
                self.actions = [
                    lambda: None,
                    lambda: None,
                    self._reset,
                    lambda: self._cx(left_bottom),
                    lambda: self._cx(right_bottom),
                    self._measure,
                ]
            case SurfaceStabilizerPattern.TWO_WEIGHT_LEFT:
                self.actions = [
                    self._reset,
                    lambda: self._cx(left_top),
                    lambda: None,
                    lambda: self._cx(left_bottom),
                    self._measure,
                    lambda: None,
                ]
            case SurfaceStabilizerPattern.TWO_WEIGHT_RIGHT:
                self.actions = [
                    lambda: None,
                    self._reset,
                    lambda: self._cx(right_top),
                    lambda: None,
                    lambda: self._cx(right_bottom),
                    self._measure,
                ]
        assert len(self.actions) == 6

    @property
    def ancilla_position(self) -> tuple[int, int]:
        return self._ancilla_position

    def set_post_selection(self, post_selection: bool) -> None:
        self.post_selection = post_selection

    def is_complete(self) -> bool:
        '''\
        Returns True if the current syndrome measurement process has completed
        and the next has not yet started.'''
        return self.stage == 0

    def run(self) -> None:
        '''Reus the syndrome measurement.'''
        self.actions[self.stage]()
        self.stage = (self.stage + 1) % 6

    def _reset(self) -> None:
        self.circuit.place_reset_x(self._ancilla_position)

    def _cx(self, position: tuple[int, int]) -> None:
        self.circuit.place_cx(self._ancilla_position, position)

    def _measure(self) -> None:
        last = self.last_measurement
        i = self.circuit.place_measurement_x(self._ancilla_position)
        if last is None:
            if self.already_satisfied:
                self.circuit.place_detector([i], post_selection=self.post_selection)
        else:
            self.circuit.place_detector([last, i], post_selection=self.post_selection)
        self.last_measurement = i


SurfaceSyndromeMeasurement = SurfaceXSyndromeMeasurement | SurfaceZSyndromeMeasurement
