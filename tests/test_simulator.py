"""Integration tests for the simulation engine."""

from __future__ import annotations

from pathlib import Path

import pytest

from tm_project.modele import Configuration, ExecutionStatus, TuringMachine
from tm_project.parseur_tm import initial_configuration, parse_machine_file, parse_machine_text
from tm_project.simulateur import MachineRuntimeError, run, run_verbose, step
from tm_project.ruban import Tape

MACHINES_DIR = Path(__file__).resolve().parents[1] / "machines"


def _flip_machine() -> TuringMachine:
    return parse_machine_file(MACHINES_DIR / "demo_flip_bits.tm")


def _copy_machine() -> TuringMachine:
    return parse_machine_file(MACHINES_DIR / "demo_copy_2tapes.tm")


def _loop_machine() -> TuringMachine:
    return parse_machine_file(MACHINES_DIR / "demo_loop.tm")


def test_step_single_tape_is_functional_and_non_mutating() -> None:
    machine = _flip_machine()
    initial = initial_configuration(machine, "0")

    next_config = step(machine, initial)

    assert initial.tapes[0].normalized_content() == "0"
    assert initial.head_positions == [0]
    assert next_config.tapes[0].normalized_content() == "1"
    assert next_config.head_positions == [1]
    assert next_config.step_count == 1
    assert next_config.status == ExecutionStatus.RUNNING


def test_step_multi_tape_updates_each_tape_head() -> None:
    machine = _copy_machine()
    initial = initial_configuration(machine, "10")

    next_config = step(machine, initial)

    assert next_config.tapes[0].normalized_content() == "10"
    assert next_config.tapes[1].normalized_content() == "1"
    assert next_config.head_positions == [1, 1]
    assert next_config.step_count == 1


def test_step_blocks_when_no_transition_matches() -> None:
    machine = parse_machine_text(
        """
        name: blocked
        init: q0
        final: qf
        q0 0 -> qf 1 S
        """
    )
    config = initial_configuration(machine, "1")

    blocked = step(machine, config)

    assert blocked.status == ExecutionStatus.BLOCKED
    assert blocked.halted is True
    assert blocked.step_count == 0


def test_step_accepts_when_reaching_final_state() -> None:
    machine = _flip_machine()

    accepted = run(machine, "01")

    assert accepted.status == ExecutionStatus.ACCEPTED
    assert accepted.halted is True
    assert accepted.tapes[0].normalized_content() == "10"


def test_run_timeout_is_explicit() -> None:
    machine = _loop_machine()

    final = run(machine, "", max_steps=3)

    assert final.status == ExecutionStatus.TIMEOUT
    assert final.halted is False
    assert final.step_count == 3


def test_run_verbose_returns_consistent_history() -> None:
    machine = _flip_machine()

    history = run_verbose(machine, "01")

    assert history[0].step_count == 0
    assert history[-1].status == ExecutionStatus.ACCEPTED
    assert [config.step_count for config in history] == [0, 1, 2, 3]


def test_step_rejects_configuration_with_wrong_tape_count() -> None:
    machine = _copy_machine()
    invalid_config = Configuration(
        current_state=machine.initial_state,
        tapes=[Tape(blank_symbol="_")],
        head_positions=[0],
    )

    with pytest.raises(MachineRuntimeError, match="expected 2"):
        step(machine, invalid_config)


def test_step_rejects_configuration_with_wrong_blank_symbol() -> None:
    machine = _flip_machine()
    invalid_config = Configuration(
        current_state=machine.initial_state,
        tapes=[Tape(blank_symbol=".")],
        head_positions=[0],
    )

    with pytest.raises(MachineRuntimeError, match="blank symbol"):
        step(machine, invalid_config)
