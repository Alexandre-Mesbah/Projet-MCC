"""Strict tests for part 1, question 4."""

from __future__ import annotations

from pathlib import Path

from tm_project.modele import ExecutionStatus
from tm_project.parseur_tm import parse_machine_file
from tm_project.simulateur import run

MACHINES_DIR = Path(__file__).resolve().parents[1] / "machines"


def test_question4_runs_until_the_machine_halts() -> None:
    machine = parse_machine_file(MACHINES_DIR / "strict_flip_bits.tm")
    result = run(machine, "0101")

    assert result.status == ExecutionStatus.ACCEPTED
    assert result.tapes[0].normalized_content() == "1010"
