"""Strict tests for part 1, question 6."""

from __future__ import annotations

from pathlib import Path

from tm_project.modele import ExecutionStatus
from tm_project.parseur_tm import parse_machine_file
from tm_project.machines_q6 import materialize_part1_question6_machines
from tm_project.simulateur import run


def test_question6_compare_binary_is_general_on_multi_symbol_inputs(tmp_path: Path) -> None:
    output_dir = tmp_path / "machines"
    materialize_part1_question6_machines(output_dir)
    machine = parse_machine_file(output_dir / "compare_binary.tm")

    assert run(machine, "10#11").status == ExecutionStatus.ACCEPTED
    assert run(machine, "11#10", max_steps=200).status == ExecutionStatus.TIMEOUT
    assert run(machine, "000#1").status == ExecutionStatus.ACCEPTED
    assert run(machine, "001#1", max_steps=200).status == ExecutionStatus.TIMEOUT


def test_question6_search_list_handles_general_words_and_empty_word(tmp_path: Path) -> None:
    output_dir = tmp_path / "machines"
    materialize_part1_question6_machines(output_dir)
    machine = parse_machine_file(output_dir / "search_list.tm")

    assert run(machine, "10#0#10#11").status == ExecutionStatus.ACCEPTED
    assert run(machine, "11#0#1#11").status == ExecutionStatus.ACCEPTED
    assert run(machine, "10#0#1#11", max_steps=300).status == ExecutionStatus.TIMEOUT
    assert run(machine, "##0#1").status == ExecutionStatus.ACCEPTED


def test_question6_unary_multiply_is_general(tmp_path: Path) -> None:
    output_dir = tmp_path / "machines"
    materialize_part1_question6_machines(output_dir)
    machine = parse_machine_file(output_dir / "unary_multiply.tm")

    assert run(machine, "1#111").tapes[0].normalized_content() == "111"
    assert run(machine, "11#111").tapes[0].normalized_content() == "111111"
    assert run(machine, "111#11").tapes[0].normalized_content() == "111111"
    assert run(machine, "#111").tapes[0].normalized_content() == "_"
    assert run(machine, "111#").tapes[0].normalized_content() == "_"
