"""Strict tests for part 1, question 3."""

from __future__ import annotations

from pathlib import Path

from tm_project.parseur_tm import initial_configuration, parse_machine_file
from tm_project.simulateur import step

MACHINES_DIR = Path(__file__).resolve().parents[1] / "machines"


def test_question3_executes_exactly_one_step() -> None:
    machine = parse_machine_file(MACHINES_DIR / "strict_flip_bits.tm")
    configuration = initial_configuration(machine, "0")
    next_configuration = step(machine, configuration)

    assert configuration.tapes[0].normalized_content() == "0"
    assert next_configuration.tapes[0].normalized_content() == "1"
    assert next_configuration.head_positions == [1]
    assert next_configuration.step_count == 1
