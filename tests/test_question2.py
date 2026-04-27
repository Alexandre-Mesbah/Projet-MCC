"""Strict tests for part 1, question 2."""

from __future__ import annotations

from pathlib import Path

from tm_project.parseur_tm import initial_configuration, parse_machine_file

MACHINES_DIR = Path(__file__).resolve().parents[1] / "machines"


def test_question2_parses_a_machine_file_and_builds_the_initial_configuration() -> None:
    machine = parse_machine_file(MACHINES_DIR / "strict_flip_bits.tm")
    configuration = initial_configuration(machine, "0101")

    assert machine.initial_state == "I"
    assert machine.final_state == "F"
    assert configuration.current_state == machine.initial_state
    assert configuration.tapes[0].normalized_content() == "0101"
    assert configuration.head_positions == [0]
