"""Strict parser for the TMSim tm2file format used in part 2."""

from __future__ import annotations

from pathlib import Path

from .modele import MachineValidationError, Move, Transition, TuringMachine
from .parseur_tm import MachineParseError


def parse_tm2file_file(path: str | Path) -> TuringMachine:
    """Parse a tm2file machine from disk."""
    machine_path = Path(path)
    try:
        source = machine_path.read_text(encoding="utf-8")
    except FileNotFoundError as error:
        raise MachineParseError("tm2file machine file not found.", path=machine_path) from error
    except UnicodeDecodeError as error:
        raise MachineParseError(
            "tm2file machine file must be valid UTF-8 text.",
            path=machine_path,
        ) from error
    except OSError as error:
        raise MachineParseError(
            f"Cannot read tm2file machine file: {error.strerror or str(error)}",
            path=machine_path,
        ) from error
    return parse_tm2file_text(source, name=machine_path.stem, path=machine_path)


def parse_tm2file_text(
    source: str,
    *,
    name: str = "tm2file_machine",
    path: Path | None = None,
) -> TuringMachine:
    """Parse the strict TMSim tm2file format.

    The first non-empty line is ``blank initial accept reject``. Each following
    non-empty line contributes its first five whitespace-separated fields:
    ``current read next write direction``. Text after the fifth field is ignored.
    A blank line after the header ends the transition section.
    """
    if not isinstance(source, str):
        raise MachineParseError("tm2file source must be a string.", path=path)

    lines = source.splitlines()
    header_index = _find_header_index(lines)
    if header_index is None:
        raise MachineParseError("tm2file description is empty.", path=path)

    blank_symbol, initial_state, accept_state, reject_state = _parse_header(
        lines[header_index],
        line_number=header_index + 1,
        path=path,
    )
    states = {initial_state, accept_state, reject_state}
    transitions: dict[tuple[str, tuple[str, ...]], Transition] = {}

    for line_number, raw_line in enumerate(lines[header_index + 1 :], start=header_index + 2):
        stripped = raw_line.strip()
        if not stripped:
            break
        current_state, raw_reads, next_state, raw_write, raw_direction = _parse_transition_fields(
            stripped,
            line_number=line_number,
            path=path,
        )
        states.update({current_state, next_state})
        for read_symbol in _parse_read_symbols(raw_reads, line_number=line_number, path=path):
            write_symbol = read_symbol if raw_write == "." else raw_write
            try:
                transition = Transition(
                    current_state=current_state,
                    symbols_read=(read_symbol,),
                    next_state=next_state,
                    symbols_write=(write_symbol,),
                    moves=(_parse_direction(raw_direction, line_number=line_number, path=path),),
                )
            except MachineValidationError as error:
                raise MachineParseError(
                    f"Invalid tm2file transition: {error}",
                    line_number=line_number,
                    path=path,
                ) from error
            if transition.key in transitions:
                raise MachineParseError(
                    f"Duplicate tm2file transition for state {current_state!r} and symbol {read_symbol!r}.",
                    line_number=line_number,
                    path=path,
                )
            transitions[transition.key] = transition

    try:
        return TuringMachine(
            name=name,
            num_tapes=1,
            states=states,
            initial_state=initial_state,
            final_state=accept_state,
            transitions=transitions,
            blank_symbol=blank_symbol,
            reject_state=reject_state,
        )
    except MachineValidationError as error:
        raise MachineParseError(f"Invalid tm2file machine definition: {error}", path=path) from error


def _find_header_index(lines: list[str]) -> int | None:
    """Return the first non-empty line index."""
    for index, raw_line in enumerate(lines):
        if raw_line.strip():
            return index
    return None


def _parse_header(
    raw_line: str,
    *,
    line_number: int,
    path: Path | None,
) -> tuple[str, str, str, str]:
    """Parse the tm2file header."""
    fields = raw_line.split()
    if len(fields) != 4:
        raise MachineParseError(
            "tm2file header must contain exactly 4 fields: blank initial accept reject.",
            line_number=line_number,
            path=path,
        )
    blank_symbol, initial_state, accept_state, reject_state = fields
    if len(blank_symbol) != 1:
        raise MachineParseError(
            "tm2file blank symbol must be exactly one character.",
            line_number=line_number,
            path=path,
        )
    return blank_symbol, initial_state, accept_state, reject_state


def _parse_transition_fields(
    stripped_line: str,
    *,
    line_number: int,
    path: Path | None,
) -> tuple[str, str, str, str, str]:
    """Parse the first five fields of a transition line."""
    fields = stripped_line.split()
    if len(fields) < 5:
        raise MachineParseError(
            f"tm2file transition must contain at least 5 fields: {stripped_line!r}.",
            line_number=line_number,
            path=path,
        )
    return fields[0], fields[1], fields[2], fields[3], fields[4]


def _parse_read_symbols(raw_reads: str, *, line_number: int, path: Path | None) -> tuple[str, ...]:
    """Parse comma-separated read alternatives."""
    symbols = tuple(raw_reads.split(","))
    if not symbols or any(symbol == "" for symbol in symbols):
        raise MachineParseError(
            f"tm2file read symbols are malformed: {raw_reads!r}.",
            line_number=line_number,
            path=path,
        )
    invalid_symbols = [symbol for symbol in symbols if len(symbol) != 1]
    if invalid_symbols:
        raise MachineParseError(
            f"tm2file read symbols must be one-character tokens: {raw_reads!r}.",
            line_number=line_number,
            path=path,
        )
    return symbols


def _parse_direction(raw_direction: str, *, line_number: int, path: Path | None) -> Move:
    """Parse the tm2file L/R direction token."""
    if raw_direction == "L":
        return "L"
    if raw_direction == "R":
        return "R"
    raise MachineParseError(
        f"tm2file direction must be L or R, got {raw_direction!r}.",
        line_number=line_number,
        path=path,
    )
