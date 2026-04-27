"""Tests for the machine parser and initial configuration builder."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from tm_project.modele import ExecutionStatus
from tm_project.parseur_tm import (
    MachineParseError,
    initial_configuration,
    parse_machine_file,
    parse_machine_text,
)


def machine_source(source: str) -> str:
    """Normalize multi-line machine snippets for stable tests."""
    return dedent(source).strip() + "\n"


def test_parse_valid_single_tape_machine() -> None:
    machine = parse_machine_text(
        machine_source(
            """
            name: flip
            init: q0
            final: qf
            blank: _
            q0 0 -> q0 1 R
            q0 1 -> q0 0 R
            q0 _ -> qf _ S
            """
        )
    )

    assert machine.name == "flip"
    assert machine.num_tapes == 1
    assert machine.get_transition("q0", ("0",)) is not None


def test_parse_valid_multi_tape_machine() -> None:
    machine = parse_machine_text(
        machine_source(
            """
            name: copy
            init: q0
            final: qf
            tapes: 2
            q0 1,_ -> q0 1,1 R,R
            q0 _,_ -> qf _,_ S,S
            """
        )
    )

    assert machine.num_tapes == 2
    assert machine.get_transition("q0", ("1", "_")) is not None


def test_parse_allows_extra_spaces_around_directives() -> None:
    machine = parse_machine_text(
        machine_source(
            """
            name   :   spaced
            init : q0
            final    :    qf
            tapes : 1
            q0 _ -> qf _ S
            """
        )
    )

    assert machine.name == "spaced"
    assert machine.initial_state == "q0"


def test_parse_move_aliases_are_normalized() -> None:
    machine = parse_machine_text(
        machine_source(
            """
            name: aliases
            init: q0
            final: qf
            q0 0 -> q1 1 >
            q1 1 -> q2 1 <
            q2 _ -> qf _ -
            """
        )
    )

    assert machine.get_transition("q0", ("0",)).moves == ("R",)
    assert machine.get_transition("q1", ("1",)).moves == ("L",)
    assert machine.get_transition("q2", ("_",)).moves == ("S",)


def test_comments_and_blank_lines_are_ignored() -> None:
    machine = parse_machine_text(
        machine_source(
            """
            ; comment at start

            name: commented ; inline note
            init: q0
            final: qf

            // comment before transition
            q0 0 -> qf 1 S // halt

            ; comment at end
            """
        )
    )

    assert machine.name == "commented"


def test_invalid_transition_syntax_is_rejected() -> None:
    with pytest.raises(MachineParseError, match="Invalid transition syntax") as excinfo:
        parse_machine_text(
            machine_source(
                """
                name: broken
                init: q0
                final: qf
                q0 0 qf 1 R
                """
            )
        )

    assert excinfo.value.line_number == 4


def test_invalid_move_is_rejected() -> None:
    with pytest.raises(MachineParseError, match="Invalid move") as excinfo:
        parse_machine_text(
            machine_source(
                """
                name: broken
                init: q0
                final: qf
                q0 0 -> qf 1 X
                """
            )
        )

    assert excinfo.value.line_number == 4


def test_duplicate_directive_is_rejected() -> None:
    with pytest.raises(MachineParseError, match="Duplicate directive") as excinfo:
        parse_machine_text(
            machine_source(
                """
                name: once
                name: twice
                init: q0
                final: qf
                q0 0 -> qf 1 S
                """
            )
        )

    assert excinfo.value.line_number == 2


@pytest.mark.parametrize(
    ("directive_line", "expected_message"),
    [
        ("tapes: nope", "Directive 'tapes' must be an integer"),
        ("tapes: 0", "Directive 'tapes' must be >= 1"),
        ("blank: ab", "Directive 'blank' must be a one-character symbol"),
    ],
)
def test_invalid_optional_directives_are_rejected(
    directive_line: str,
    expected_message: str,
) -> None:
    with pytest.raises(MachineParseError, match=expected_message):
        parse_machine_text(
            machine_source(
                f"""
                name: broken
                init: q0
                final: qf
                {directive_line}
                q0 0 -> qf 1 S
                """
            )
        )


@pytest.mark.parametrize("directive_name", ["name", "init", "final"])
def test_missing_required_directive_is_rejected(directive_name: str) -> None:
    directives = {
        "name": "name: demo",
        "init": "init: q0",
        "final": "final: qf",
    }
    directives.pop(directive_name)
    source = "\n".join([*directives.values(), "q0 0 -> qf 1 S"])

    with pytest.raises(MachineParseError, match=f"Missing required directive: {directive_name}"):
        parse_machine_text(source)


@pytest.mark.parametrize(
    ("directive_line", "expected_message"),
    [
        ("name:", "Directive 'name' must not be empty"),
        ("init:", "Directive 'init' must not be empty"),
        ("final:", "Directive 'final' must not be empty"),
        ("blank:", "Directive 'blank' must not be empty"),
    ],
)
def test_empty_directive_values_are_rejected(
    directive_line: str,
    expected_message: str,
) -> None:
    with pytest.raises(MachineParseError, match=expected_message):
        parse_machine_text(
            machine_source(
                f"""
                {directive_line}
                init: q0
                final: qf
                q0 0 -> qf 1 S
                """
                if directive_line.startswith("name")
                else f"""
                name: demo
                {directive_line}
                final: qf
                q0 0 -> qf 1 S
                """
                if directive_line.startswith("init")
                else f"""
                name: demo
                init: q0
                {directive_line}
                q0 0 -> qf 1 S
                """
                if directive_line.startswith("final")
                else f"""
                name: demo
                init: q0
                final: qf
                {directive_line}
                q0 0 -> qf 1 S
                """
            )
        )


@pytest.mark.parametrize(
    ("states_line", "expected_message"),
    [
        ("states:", "must declare at least one state"),
        ("states: q0,,qf", "contains an empty state name"),
        ("states: q0,qf,q0", "declares duplicate state"),
    ],
)
def test_states_directive_is_strict(states_line: str, expected_message: str) -> None:
    with pytest.raises(MachineParseError, match=expected_message) as excinfo:
        parse_machine_text(
            machine_source(
                f"""
                name: declared
                init: q0
                final: qf
                {states_line}
                q0 0 -> qf 1 S
                """
            )
        )

    assert excinfo.value.line_number == 4


def test_used_but_undeclared_state_reports_first_faulty_line() -> None:
    with pytest.raises(MachineParseError, match=r"State 'q1' is used but not declared") as excinfo:
        parse_machine_text(
            machine_source(
                """
                name: declared
                init: q0
                final: qf
                states: q0,qf
                q0 0 -> q1 1 R
                q1 1 -> qf 1 S
                """
            )
        )

    assert excinfo.value.line_number == 5


@pytest.mark.parametrize(
    ("transition_line", "expected_message"),
    [
        ("q0 1,_ -> qf 1 R,R", "Write field must contain exactly 2 item"),
        ("q0 1,_ -> qf 1,1 R", "Moves field must contain exactly 2 item"),
        ("q0 1,,_ -> qf 1,1 R,R", "Read field is malformed"),
    ],
)
def test_multi_tape_transition_fields_are_validated(
    transition_line: str,
    expected_message: str,
) -> None:
    with pytest.raises(MachineParseError, match=expected_message) as excinfo:
        parse_machine_text(
            machine_source(
                f"""
                name: broken
                init: q0
                final: qf
                tapes: 2
                {transition_line}
                """
            )
        )

    assert excinfo.value.line_number == 5


@pytest.mark.parametrize(
    ("source", "message"),
    [
        ("", "Machine description is empty"),
        (
            machine_source(
                """
                name: no-transitions
                init: q0
                final: qf
                """
            ),
            "At least one transition is required",
        ),
    ],
)
def test_empty_machine_or_machine_without_transition_is_rejected(
    source: str,
    message: str,
) -> None:
    with pytest.raises(MachineParseError, match=message):
        parse_machine_text(source)


def test_multi_character_transition_symbol_is_reported_as_parse_error() -> None:
    with pytest.raises(MachineParseError, match="Read symbols must be one-character tokens") as excinfo:
        parse_machine_text(
            machine_source(
                """
                name: broken
                init: q0
                final: qf
                q0 ab -> qf _ S
                """
            )
        )

    assert excinfo.value.line_number == 4


def test_parse_machine_file_on_missing_file_raises_machine_parse_error(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing.tm"

    with pytest.raises(MachineParseError, match="Machine file not found") as excinfo:
        parse_machine_file(missing_path)

    assert excinfo.value.path == missing_path


def test_parse_machine_file_rejects_invalid_utf8(tmp_path: Path) -> None:
    machine_path = tmp_path / "invalid.tm"
    machine_path.write_bytes(b"\xff\xfe\x00")

    with pytest.raises(MachineParseError, match="valid UTF-8") as excinfo:
        parse_machine_file(machine_path)

    assert excinfo.value.path == machine_path


def test_initial_configuration_for_single_tape_machine() -> None:
    machine = parse_machine_text(
        machine_source(
            """
            name: init-demo
            init: q0
            final: qf
            q0 _ -> qf _ S
            """
        )
    )

    configuration = initial_configuration(machine, "101")

    assert configuration.current_state == "q0"
    assert configuration.head_positions == [0]
    assert configuration.tapes[0].normalized_content() == "101"
    assert configuration.status == ExecutionStatus.RUNNING


def test_initial_configuration_for_multi_tape_machine_with_sequence() -> None:
    machine = parse_machine_text(
        machine_source(
            """
            name: init-multi
            init: q0
            final: qf
            tapes: 2
            q0 _,_ -> qf _,_ S,S
            """
        )
    )

    configuration = initial_configuration(machine, ["11", "00"])

    assert configuration.num_tapes == 2
    assert configuration.tapes[0].normalized_content() == "11"
    assert configuration.tapes[1].normalized_content() == "00"


def test_initial_configuration_rejects_wrong_sequence_length() -> None:
    machine = parse_machine_text(
        machine_source(
            """
            name: init-multi
            init: q0
            final: qf
            tapes: 2
            q0 _,_ -> qf _,_ S,S
            """
        )
    )

    with pytest.raises(ValueError, match="Expected 2 tape inputs"):
        initial_configuration(machine, ["11"])


def test_initial_configuration_rejects_non_sequence_multi_tape_input() -> None:
    machine = parse_machine_text(
        machine_source(
            """
            name: init-multi
            init: q0
            final: qf
            tapes: 2
            q0 _,_ -> qf _,_ S,S
            """
        )
    )

    with pytest.raises(ValueError, match="string or a sequence of strings"):
        initial_configuration(machine, 123)  # type: ignore[arg-type]
