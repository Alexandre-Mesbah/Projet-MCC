"""Tests for the sparse tape implementation."""

from __future__ import annotations

import pytest

from tm_project.ruban import Tape


@pytest.mark.parametrize("position", [-3, 0, 4])
def test_read_on_empty_tape_returns_blank_symbol(position: int) -> None:
    tape = Tape(blank_symbol="_")

    assert tape.read(position) == "_"


def test_write_valid_symbol_updates_cell() -> None:
    tape = Tape(blank_symbol="_")

    tape.write(2, "1")

    assert tape.read(2) == "1"


def test_writing_blank_symbol_removes_cell() -> None:
    tape = Tape.from_string("101", blank_symbol="_")

    tape.write(1, "_")

    assert tape.read(1) == "_"
    assert tape.non_blank_positions() == [0, 2]


def test_clone_is_independent() -> None:
    tape = Tape.from_string("10", blank_symbol="_")

    tape_clone = tape.clone()
    tape_clone.write(0, "0")
    tape_clone.write(3, "1")

    assert tape.read(0) == "1"
    assert tape.read(3) == "_"
    assert tape_clone.read(0) == "0"
    assert tape_clone.read(3) == "1"


def test_get_view_returns_window_around_head() -> None:
    tape = Tape.from_string("101", blank_symbol="_")

    assert tape.get_view(center=1, radius=2) == [
        (-1, "_"),
        (0, "1"),
        (1, "0"),
        (2, "1"),
        (3, "_"),
    ]


def test_normalized_content_on_empty_tape_is_blank_symbol() -> None:
    tape = Tape(blank_symbol="_")

    assert tape.normalized_content() == "_"


def test_normalized_content_keeps_internal_blanks() -> None:
    tape = Tape(blank_symbol="_")
    tape.write(0, "1")
    tape.write(2, "0")

    assert tape.normalized_content() == "1_0"


def test_constructor_normalizes_injected_blank_cells() -> None:
    tape = Tape(blank_symbol="_", _cells={0: "1", 1: "_", 2: "0"})

    assert tape.non_blank_positions() == [0, 2]
    assert tape.normalized_content() == "1_0"


@pytest.mark.parametrize(
    ("blank_symbol", "expected_message"),
    [
        ("", "non-empty"),
        ("ab", "one-character"),
    ],
)
def test_reject_invalid_blank_symbol(blank_symbol: str, expected_message: str) -> None:
    with pytest.raises(ValueError, match=expected_message):
        Tape(blank_symbol=blank_symbol)


@pytest.mark.parametrize(
    ("symbol", "expected_exception", "expected_message"),
    [
        ("", ValueError, "non-empty"),
        ("ab", ValueError, "one-character"),
        (1, TypeError, "strings"),
    ],
)
def test_reject_invalid_written_symbol(
    symbol: object,
    expected_exception: type[Exception],
    expected_message: str,
) -> None:
    tape = Tape(blank_symbol="_")

    with pytest.raises(expected_exception, match=expected_message):
        tape.write(0, symbol)  # type: ignore[arg-type]


def test_reject_invalid_symbol_in_injected_cells() -> None:
    with pytest.raises(ValueError, match="one-character"):
        Tape(blank_symbol="_", _cells={0: "ab"})


def test_reject_invalid_position_in_injected_cells() -> None:
    with pytest.raises(TypeError, match="positions must be integers"):
        Tape(blank_symbol="_", _cells={"0": "1"})  # type: ignore[arg-type]


@pytest.mark.parametrize("position", ["0", 1.5, True])
def test_reject_invalid_positions(position: object) -> None:
    tape = Tape(blank_symbol="_")

    with pytest.raises(TypeError, match="positions must be integers"):
        tape.read(position)  # type: ignore[arg-type]


def test_from_string_reuses_write_validation() -> None:
    tape = Tape.from_string("10_", blank_symbol="_")

    assert tape.non_blank_positions() == [0, 1]
    assert tape.read(2) == "_"
