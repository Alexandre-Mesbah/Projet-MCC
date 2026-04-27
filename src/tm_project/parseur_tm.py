"""Parser for a documented textual subset inspired by TuringMachineSimulator."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Sequence

from .modele import (
    Configuration,
    ExecutionStatus,
    MachineValidationError,
    Move,
    Transition,
    TuringMachine,
)
from .ruban import Tape

DIRECTIVE_PATTERN = re.compile(r"^(?P<key>[A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(?P<value>.*)$")
TRANSITION_PATTERN = re.compile(
    r"^(?P<current>\S+)\s+(?P<read>\S+)\s*->\s*(?P<next>\S+)\s+(?P<write>\S+)\s+(?P<moves>\S+)$"
)
MOVE_ALIASES: dict[str, Move] = {"L": "L", "R": "R", "S": "S", "<": "L", ">": "R", "-": "S"}


class MachineParseError(ValueError):
    """Raised when a machine description file is syntactically invalid."""

    def __init__(self, message: str, *, line_number: int | None = None, path: Path | None = None):
        self.message = message
        self.line_number = line_number
        self.path = path
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Render the exception message with optional location."""
        location_parts: list[str] = []
        if self.path is not None:
            location_parts.append(str(self.path))
        if self.line_number is not None:
            location_parts.append(f"line {self.line_number}")
        if not location_parts:
            return self.message
        return f"{self.message} ({', '.join(location_parts)})"


@dataclass(frozen=True, slots=True)
class _RawTransition:
    """Temporary representation of a transition line before validation."""

    line_number: int
    current_state: str
    read_symbols: tuple[str, ...]
    next_state: str
    write_symbols: tuple[str, ...]
    moves: tuple[Move, ...]


def parse_machine_file(path: str | Path) -> TuringMachine:
    """Parse a machine file from disk."""
    machine_path = Path(path)
    try:
        source = machine_path.read_text(encoding="utf-8")
    except FileNotFoundError as error:
        raise MachineParseError("Machine file not found.", path=machine_path) from error
    except UnicodeDecodeError as error:
        raise MachineParseError(
            "Machine file must be valid UTF-8 text.",
            path=machine_path,
        ) from error
    except OSError as error:
        raise MachineParseError(
            f"Cannot read machine file: {error.strerror or str(error)}",
            path=machine_path,
        ) from error
    return parse_machine_text(source, path=machine_path)


def parse_machine_text(source: str, *, path: Path | None = None) -> TuringMachine:
    """Parse a machine from raw text.

    Accepted format:
    - directive lines: ``name: Demo``, ``init: q0``, ``final: qf``, ``blank: _``, ``tapes: 2``
    - optional ``states: q0,q1,qf``
    - transition lines: ``q0 1,_ -> q1 0,1 R,S``

    Comments are supported on lines starting with ``;`` or ``//`` and as inline suffixes
    introduced by `` ;`` or `` //``. The symbol ``#`` remains available as a tape symbol.
    """
    directives: dict[str, tuple[int, str]] = {}
    raw_transition_lines: list[tuple[int, str]] = []

    for line_number, raw_line in enumerate(source.splitlines(), start=1):
        stripped_line = _strip_comments(raw_line).strip()
        if not stripped_line:
            continue
        directive_match = DIRECTIVE_PATTERN.match(stripped_line)
        if directive_match and "->" not in stripped_line:
            key = directive_match.group("key").lower()
            value = directive_match.group("value").strip()
            if key in directives:
                raise MachineParseError(
                    f"Duplicate directive: {key}.",
                    line_number=line_number,
                    path=path,
                )
            directives[key] = (line_number, value)
            continue
        raw_transition_lines.append((line_number, stripped_line))

    if not directives and not raw_transition_lines:
        raise MachineParseError("Machine description is empty.", path=path)

    name = _required_directive("name", directives, path)
    initial_state = _required_directive("init", directives, path)
    final_state = _required_directive("final", directives, path)
    state_usage_lines: dict[str, int] = {
        initial_state: directives["init"][0],
        final_state: directives["final"][0],
    }
    blank_symbol = directives.get("blank", (0, "_"))[1]
    if "blank" in directives and blank_symbol == "":
        raise MachineParseError(
            "Directive 'blank' must not be empty.",
            line_number=directives["blank"][0],
            path=path,
        )
    if len(blank_symbol) != 1:
        raise MachineParseError(
            "Directive 'blank' must be a one-character symbol.",
            line_number=directives.get("blank", (None, ""))[0],
            path=path,
        )

    num_tapes = 1
    if "tapes" in directives:
        line_number, raw_num_tapes = directives["tapes"]
        try:
            num_tapes = int(raw_num_tapes)
        except ValueError as error:
            raise MachineParseError(
                f"Directive 'tapes' must be an integer, got {raw_num_tapes!r}.",
                line_number=line_number,
                path=path,
            ) from error
        if num_tapes < 1:
            raise MachineParseError(
                "Directive 'tapes' must be >= 1.",
                line_number=line_number,
                path=path,
            )

    declared_states: set[str] | None = None
    if "states" in directives:
        line_number, raw_states = directives["states"]
        declared_states = _parse_states_directive(
            raw_states,
            line_number=line_number,
            path=path,
        )

    raw_transitions = [
        _parse_transition_line(line, line_number=line_number, num_tapes=num_tapes, path=path)
        for line_number, line in raw_transition_lines
    ]

    if not raw_transitions:
        raise MachineParseError("At least one transition is required.", path=path)

    inferred_states: set[str] = {initial_state, final_state}
    transitions: dict[tuple[str, tuple[str, ...]], Transition] = {}
    for raw_transition in raw_transitions:
        inferred_states.add(raw_transition.current_state)
        inferred_states.add(raw_transition.next_state)
        state_usage_lines.setdefault(raw_transition.current_state, raw_transition.line_number)
        state_usage_lines.setdefault(raw_transition.next_state, raw_transition.line_number)
        try:
            transition = Transition(
                current_state=raw_transition.current_state,
                symbols_read=raw_transition.read_symbols,
                next_state=raw_transition.next_state,
                symbols_write=raw_transition.write_symbols,
                moves=raw_transition.moves,
            )
        except MachineValidationError as error:
            raise MachineParseError(
                f"Invalid transition: {error}",
                line_number=raw_transition.line_number,
                path=path,
            ) from error
        if transition.key in transitions:
            raise MachineParseError(
                f"Duplicate transition for state {transition.current_state!r} "
                f"and symbols {transition.symbols_read!r}",
                line_number=raw_transition.line_number,
                path=path,
            )
        transitions[transition.key] = transition

    states = declared_states if declared_states is not None else inferred_states
    if declared_states is not None:
        undeclared = inferred_states - declared_states
        if undeclared:
            first_unknown = min(
                undeclared,
                key=lambda state: (state_usage_lines.get(state, float("inf")), state),
            )
            raise MachineParseError(
                f"State {first_unknown!r} is used but not declared in `states:`.",
                line_number=state_usage_lines.get(first_unknown),
                path=path,
            )

    try:
        return TuringMachine(
            name=name,
            num_tapes=num_tapes,
            states=states,
            initial_state=initial_state,
            final_state=final_state,
            transitions=transitions,
            blank_symbol=blank_symbol,
        )
    except MachineValidationError as error:
        raise MachineParseError(f"Invalid machine definition: {error}", path=path) from error


def initial_configuration(
    machine: TuringMachine, input_word: str | Sequence[str]
) -> Configuration:
    """Create the initial configuration for a machine.

    For mono-tape machines, ``input_word`` is a plain string placed on tape 1.
    For multi-tape machines, a sequence of length ``machine.num_tapes`` can be supplied.
    Missing extra tapes are not auto-populated in sequence form: the caller must be explicit.
    """
    tape_inputs = _normalize_input_word(machine, input_word)
    tapes = [
        Tape.from_string(content=tape_input, blank_symbol=machine.blank_symbol)
        for tape_input in tape_inputs
    ]
    halted = machine.is_final_state(machine.initial_state)
    return Configuration(
        current_state=machine.initial_state,
        tapes=tapes,
        head_positions=[0 for _ in range(machine.num_tapes)],
        halted=halted,
        step_count=0,
        status=ExecutionStatus.ACCEPTED if halted else ExecutionStatus.RUNNING,
        halt_reason="Initial state is already final." if halted else None,
    )


def _required_directive(
    key: str, directives: dict[str, tuple[int, str]], path: Path | None
) -> str:
    """Fetch a mandatory directive or raise a parse error."""
    if key not in directives:
        raise MachineParseError(f"Missing required directive: {key}.", path=path)
    line_number, value = directives[key]
    if value == "":
        raise MachineParseError(
            f"Directive '{key}' must not be empty.",
            line_number=line_number,
            path=path,
        )
    return value


def _parse_states_directive(
    raw_states: str, *, line_number: int, path: Path | None
) -> set[str]:
    """Parse and validate the `states:` directive."""
    if raw_states == "":
        raise MachineParseError(
            "Directive 'states' must declare at least one state.",
            line_number=line_number,
            path=path,
        )

    states: set[str] = set()
    for raw_state in raw_states.split(","):
        state = raw_state.strip()
        if state == "":
            raise MachineParseError(
                "Directive 'states' contains an empty state name.",
                line_number=line_number,
                path=path,
            )
        if state in states:
            raise MachineParseError(
                f"Directive 'states' declares duplicate state {state!r}.",
                line_number=line_number,
                path=path,
            )
        states.add(state)
    return states


def _normalize_input_word(
    machine: TuringMachine, input_word: str | Sequence[str]
) -> list[str]:
    """Normalize caller input for tape initialization."""
    if isinstance(input_word, str):
        if machine.num_tapes != 1:
            return [input_word] + ["" for _ in range(machine.num_tapes - 1)]
        return [input_word]

    try:
        tape_inputs = list(input_word)
    except TypeError as error:
        raise ValueError(
            "Tape inputs must be provided as a string or a sequence of strings."
        ) from error
    if len(tape_inputs) != machine.num_tapes:
        raise ValueError(
            f"Expected {machine.num_tapes} tape inputs, got {len(tape_inputs)}."
        )
    if any(not isinstance(tape_input, str) for tape_input in tape_inputs):
        raise ValueError("Each tape input must be a string.")
    return tape_inputs


def _parse_transition_line(
    line: str,
    *,
    line_number: int,
    num_tapes: int,
    path: Path | None,
) -> _RawTransition:
    """Parse one transition line."""
    match = TRANSITION_PATTERN.match(line)
    if match is None:
        raise MachineParseError(
            f"Invalid transition syntax: {line!r}.",
            line_number=line_number,
            path=path,
        )

    read_symbols = _split_tuple(
        match.group("read"),
        expected=num_tapes,
        line_number=line_number,
        path=path,
        field_name="Read",
        require_single_char=True,
    )
    write_symbols = _split_tuple(
        match.group("write"),
        expected=num_tapes,
        line_number=line_number,
        path=path,
        field_name="Write",
        require_single_char=True,
    )
    moves = tuple(
        _parse_move(token, line_number=line_number, path=path)
        for token in _split_tuple(
            match.group("moves"),
            expected=num_tapes,
            line_number=line_number,
            path=path,
            field_name="Moves",
        )
    )

    return _RawTransition(
        line_number=line_number,
        current_state=match.group("current"),
        read_symbols=read_symbols,
        next_state=match.group("next"),
        write_symbols=write_symbols,
        moves=moves,
    )


def _split_tuple(
    raw_value: str,
    *,
    expected: int,
    line_number: int,
    path: Path | None,
    field_name: str,
    require_single_char: bool = False,
) -> tuple[str, ...]:
    """Split a transition field into a fixed-size tuple."""
    if expected == 1 and "," not in raw_value:
        tokens = [raw_value]
    else:
        tokens = [token.strip() for token in raw_value.split(",")]

    if any(token == "" for token in tokens):
        raise MachineParseError(
            f"{field_name} field is malformed: {raw_value!r}.",
            line_number=line_number,
            path=path,
        )
    if len(tokens) != expected:
        raise MachineParseError(
            f"{field_name} field must contain exactly {expected} item(s), got {len(tokens)} in {raw_value!r}.",
            line_number=line_number,
            path=path,
        )
    if require_single_char:
        invalid_tokens = [token for token in tokens if len(token) != 1]
        if invalid_tokens:
            raise MachineParseError(
                f"{field_name} symbols must be one-character tokens: {raw_value!r}.",
                line_number=line_number,
                path=path,
            )
    return tuple(tokens)


def _parse_move(raw_move: str, *, line_number: int, path: Path | None) -> Move:
    """Normalize a move token."""
    try:
        return MOVE_ALIASES[raw_move]
    except KeyError as error:
        raise MachineParseError(
            f"Invalid move {raw_move!r}. Use L/R/S or </>/-.",
            line_number=line_number,
            path=path,
        ) from error


def _strip_comments(raw_line: str) -> str:
    """Remove full-line and inline comments while preserving # as a tape symbol."""
    stripped = raw_line.lstrip()
    if stripped.startswith(";") or stripped.startswith("//"):
        return ""

    for marker in (" ;", " //"):
        comment_start = raw_line.find(marker)
        if comment_start != -1:
            return raw_line[:comment_start]
    return raw_line
