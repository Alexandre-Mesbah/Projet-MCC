"""Tests for the Turing machine core model."""

from __future__ import annotations

import pytest

from tm_project.modele import (
    Configuration,
    ExecutionStatus,
    MachineValidationError,
    Transition,
    TuringMachine,
)
from tm_project.ruban import Tape


def make_transition(**overrides: object) -> Transition:
    """Build a valid mono-tape transition with optional overrides."""
    values: dict[str, object] = {
        "current_state": "q0",
        "symbols_read": ("0",),
        "next_state": "qf",
        "symbols_write": ("1",),
        "moves": ("R",),
    }
    values.update(overrides)
    return Transition(**values)


def make_machine(**overrides: object) -> TuringMachine:
    """Build a minimal valid mono-tape machine."""
    transition = make_transition()
    values: dict[str, object] = {
        "name": "demo",
        "num_tapes": 1,
        "states": {"q0", "qf"},
        "initial_state": "q0",
        "final_state": "qf",
        "transitions": {transition.key: transition},
        "blank_symbol": "_",
    }
    values.update(overrides)
    return TuringMachine(**values)


def test_valid_single_tape_transition() -> None:
    transition = make_transition(next_state="q1")

    assert transition.key == ("q0", ("0",))
    assert transition.tape_count == 1


def test_transition_rejects_invalid_move() -> None:
    with pytest.raises(MachineValidationError, match="Invalid move"):
        make_transition(moves=("X",))  # type: ignore[arg-type]


def test_transition_rejects_inconsistent_tuple_sizes() -> None:
    with pytest.raises(MachineValidationError, match="must match"):
        make_transition(
            symbols_read=("0", "1"),
            symbols_write=("1",),
            moves=("R", "S"),
        )


def test_transition_rejects_non_string_symbol() -> None:
    with pytest.raises(MachineValidationError, match="Tape symbols must be a string"):
        make_transition(symbols_read=(0,))  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("field_name", "kwargs"),
    [
        ("current", {"current_state": "   "}),
        ("next", {"next_state": "   "}),
    ],
)
def test_transition_rejects_blank_or_whitespace_state_names(
    field_name: str,
    kwargs: dict[str, object],
) -> None:
    with pytest.raises(MachineValidationError, match="must be a non-empty string"):
        make_transition(**kwargs)


def test_machine_rejects_missing_initial_state() -> None:
    with pytest.raises(MachineValidationError, match="Initial state"):
        make_machine(states={"qf"})


def test_machine_rejects_missing_final_state() -> None:
    with pytest.raises(MachineValidationError, match="Final state"):
        make_machine(states={"q0"})


def test_machine_rejects_transition_with_unknown_state() -> None:
    with pytest.raises(MachineValidationError, match="Unknown next state"):
        make_machine(transitions={make_transition(next_state="q1").key: make_transition(next_state="q1")})


def test_machine_rejects_whitespace_only_declared_state() -> None:
    with pytest.raises(MachineValidationError, match="Declared state"):
        make_machine(states={"q0", "qf", "   "})


def test_machine_rejects_whitespace_only_name() -> None:
    with pytest.raises(MachineValidationError, match="machine name must be a non-empty"):
        make_machine(name="   ")


def test_machine_rejects_non_integer_num_tapes() -> None:
    with pytest.raises(MachineValidationError, match="num_tapes must be an integer"):
        make_machine(num_tapes="1")  # type: ignore[arg-type]


def test_configuration_rejects_mismatched_tapes_and_heads() -> None:
    with pytest.raises(MachineValidationError, match="must match"):
        Configuration(
            current_state="q0",
            tapes=[Tape(blank_symbol="_")],
            head_positions=[0, 1],
        )


def test_configuration_rejects_invalid_tape_instances() -> None:
    with pytest.raises(MachineValidationError, match="Tape instances"):
        Configuration(
            current_state="q0",
            tapes=["not-a-tape"],  # type: ignore[list-item]
            head_positions=[0],
        )


@pytest.mark.parametrize("head_position", ["0", 1.2, True])
def test_configuration_rejects_invalid_head_positions(head_position: object) -> None:
    with pytest.raises(MachineValidationError, match="Head positions must be integers"):
        Configuration(
            current_state="q0",
            tapes=[Tape(blank_symbol="_")],
            head_positions=[head_position],  # type: ignore[list-item]
        )


def test_configuration_rejects_negative_step_count() -> None:
    with pytest.raises(MachineValidationError, match="step_count must be non-negative"):
        Configuration(
            current_state="q0",
            tapes=[Tape(blank_symbol="_")],
            head_positions=[0],
            step_count=-1,
        )


def test_configuration_clone_is_independent() -> None:
    machine = make_machine()
    configuration = Configuration(
        current_state=machine.initial_state,
        tapes=[Tape.from_string("0", blank_symbol=machine.blank_symbol)],
        head_positions=[0],
        halted=False,
        step_count=3,
        status=ExecutionStatus.RUNNING,
    )

    configuration_clone = configuration.clone()
    configuration_clone.current_state = "qf"
    configuration_clone.head_positions[0] = 1
    configuration_clone.tapes[0].write(0, "1")

    assert configuration.current_state == "q0"
    assert configuration.head_positions == [0]
    assert configuration.tapes[0].read(0) == "0"
    assert configuration_clone.current_state == "qf"
    assert configuration_clone.head_positions == [1]
    assert configuration_clone.tapes[0].read(0) == "1"
