"""Strict tests for part 2 tm2file parsing, encoding, and universal simulation."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from tm_project.cli import main
from tm_project.codage import (
    binary_to_int,
    encode_input_word_strict,
    encode_machine_strict_text,
    encode_text_to_binary,
    encode_tm2file_text_to_binary,
)
from tm_project.modele import ExecutionStatus
from tm_project.parseur_tm2 import parse_tm2file_file, parse_tm2file_text
from tm_project.parseur_tm import MachineParseError
from tm_project.simulateur import run
from tm_project.universelle import (
    strict_bounded_universal_simulate_word,
    strict_universal_simulate_word,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MACHINES_DIR = PROJECT_ROOT / "machines"


def tm2_source(source: str) -> str:
    """Normalize tm2file snippets for stable tests."""
    return dedent(source).strip() + "\n"


def test_parse_tm2file_accepts_header_and_reject_state() -> None:
    machine = parse_tm2file_text(
        tm2_source(
            """
            _ q0 qA qR
            q0 0 qA 1 R
            """
        )
    )

    assert machine.blank_symbol == "_"
    assert machine.initial_state == "q0"
    assert machine.final_state == "qA"
    assert machine.reject_state == "qR"


def test_parse_tm2file_expands_read_alternatives_and_dot_write() -> None:
    machine = parse_tm2file_text(
        tm2_source(
            """
            _ q0 qA qR
            q0 0,1 qA . R  ignored comment text
            """
        )
    )

    assert machine.get_transition("q0", ("0",)).symbols_write == ("0",)
    assert machine.get_transition("q0", ("1",)).symbols_write == ("1",)


def test_parse_tm2file_blank_line_ends_transition_section() -> None:
    machine = parse_tm2file_text(
        "_ q0 qA qR\n"
        "q0 0 qA 0 R\n"
        "\n"
        "q0 1 qA 1 R\n"
    )

    assert machine.get_transition("q0", ("0",)) is not None
    assert machine.get_transition("q0", ("1",)) is None


def test_parse_tm2file_rejects_bad_header() -> None:
    with pytest.raises(MachineParseError, match="header"):
        parse_tm2file_text("q0 qA qR\n")


def test_tm2file_missing_transition_defaults_to_reject() -> None:
    machine = parse_tm2file_text(
        tm2_source(
            """
            _ q0 qA qR
            q0 0 qA 0 R
            """
        )
    )

    result = run(machine, "1")

    assert result.status == ExecutionStatus.REJECTED
    assert result.current_state == "qR"


def test_strict_encoding_uses_binary_states_symbols_and_single_separator() -> None:
    machine = parse_tm2file_file(MACHINES_DIR / "part2_flip_bits.tm2")

    encoded = encode_machine_strict_text(machine)

    assert encoded == "0|0|1|10|0|0|1|0|>|0|1|0|10|>|0|10|0|1|>"
    assert "blank=" not in encoded
    assert "||" not in encoded


def test_strict_encoding_accepts_non_ascii_work_alphabet_by_renaming() -> None:
    machine = parse_tm2file_text(
        tm2_source(
            """
            _ q0 qA qR
            q0 é qA é R
            """
        )
    )

    encoded = encode_machine_strict_text(machine)

    assert encoded == "0|0|1|10|0|1|1|1|>"


def test_encode_tm2file_text_to_binary_is_single_q8_function() -> None:
    source = tm2_source(
        """
        _ q0 qA qR
        q0 _ qA _ R
        """
    )

    text_encoding = encode_machine_strict_text(parse_tm2file_text(source))
    binary_encoding = encode_tm2file_text_to_binary(source)

    assert binary_encoding == encode_text_to_binary(text_encoding)
    assert binary_to_int(binary_encoding) > 0


def test_strict_universal_word_matches_direct_run() -> None:
    machine = parse_tm2file_file(MACHINES_DIR / "part2_flip_bits.tm2")
    encoded_machine = encode_machine_strict_text(machine)
    encoded_input = encode_input_word_strict(machine, "0101")

    direct = run(machine, "0101")
    universal = strict_universal_simulate_word(f"{encoded_machine}#{encoded_input}")

    assert universal.status == direct.status
    assert universal.tape_symbols == ("10", "1", "10", "1")
    assert universal.machine_description_tape.normalized_content() == encoded_machine
    assert universal.simulated_tape.normalized_content() == "10|1|10|1"


def test_strict_universal_missing_transition_rejects() -> None:
    machine = parse_tm2file_file(MACHINES_DIR / "part2_flip_bits.tm2")
    encoded_machine = encode_machine_strict_text(machine)

    result = strict_universal_simulate_word(f"{encoded_machine}#11")

    assert result.status == ExecutionStatus.REJECTED
    assert result.current_state == "10"


def test_strict_bounded_universal_times_out_and_exposes_counter_tape() -> None:
    machine = parse_tm2file_file(MACHINES_DIR / "part2_flip_bits.tm2")
    encoded_machine = encode_machine_strict_text(machine)
    encoded_input = encode_input_word_strict(machine, "0101")

    result = strict_bounded_universal_simulate_word(f"{encoded_machine}#{encoded_input}#1")

    assert result.status == ExecutionStatus.TIMEOUT
    assert result.step_count == 1
    assert result.counter_tape.normalized_content() == "_"


def test_strict_bounded_universal_keeps_remaining_unary_counter_on_accept() -> None:
    machine = parse_tm2file_file(MACHINES_DIR / "part2_flip_bits.tm2")
    encoded_machine = encode_machine_strict_text(machine)

    result = strict_bounded_universal_simulate_word(f"{encoded_machine}##11")

    assert result.status == ExecutionStatus.ACCEPTED
    assert result.counter_tape.normalized_content() == "11"


def test_strict_bounded_universal_rejects_bad_binary_bound() -> None:
    machine = parse_tm2file_file(MACHINES_DIR / "part2_flip_bits.tm2")
    encoded_machine = encode_machine_strict_text(machine)

    with pytest.raises(ValueError, match="binary"):
        strict_bounded_universal_simulate_word(f"{encoded_machine}##2")


def test_part2_report_cli_prints_strict_encodings(capsys: pytest.CaptureFixture[str]) -> None:
    status = main(
        [
            "part2-report",
            "--machine",
            str(MACHINES_DIR / "part2_flip_bits.tm2"),
            "--input",
            "0101",
            "--steps",
            "5",
        ]
    )

    output = capsys.readouterr().out
    assert status == 0
    assert "Strict Text:" in output
    assert "Strict Binary:" in output
    assert "Strict Integer:" in output
    assert "Q9 input <M>#x:" in output
    assert "Q10 input <M>#x#n:" in output
