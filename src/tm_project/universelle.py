"""Strict part 2 universal simulations over encoded tape-symbol words."""

from __future__ import annotations

from dataclasses import dataclass

from .codage import (
    REVERSE_TEXT_MOVE_MAP,
    StrictEncodedMachine,
    StrictEncodedTransition,
    decode_machine_strict_text,
)
from .modele import ExecutionStatus
from .ruban import Tape


@dataclass(frozen=True, slots=True)
class StrictUniversalSimulationResult:
    """Result for the strict 3-tape universal simulation."""

    input_word: str
    encoded_machine: str
    encoded_input: str
    decoded_machine: StrictEncodedMachine
    status: ExecutionStatus
    current_state: str
    step_count: int
    tape_symbols: tuple[str, ...]
    machine_description_tape: Tape
    simulated_tape: Tape
    work_tape: Tape


@dataclass(frozen=True, slots=True)
class StrictBoundedUniversalSimulationResult(StrictUniversalSimulationResult):
    """Result for the strict bounded 4-tape universal simulation."""

    bound: int
    counter_tape: Tape


def strict_universal_simulate_word(word: str) -> StrictUniversalSimulationResult:
    """Run the strict 3-tape universal machine on a single ``<M>#x`` word."""
    encoded_machine, encoded_input = _split_universal_word(word)
    decoded_machine = decode_machine_strict_text(encoded_machine)
    run_result = _run_encoded_machine(decoded_machine, encoded_input, max_steps=None)
    return StrictUniversalSimulationResult(
        input_word=word,
        encoded_machine=encoded_machine,
        encoded_input=encoded_input,
        decoded_machine=decoded_machine,
        status=run_result.status,
        current_state=run_result.current_state,
        step_count=run_result.step_count,
        tape_symbols=run_result.tape_symbols,
        machine_description_tape=Tape.from_string(encoded_machine),
        simulated_tape=Tape.from_string(_render_symbol_tape(run_result.tape_symbols)),
        work_tape=Tape.from_string(_render_work_tape(run_result)),
    )


def strict_bounded_universal_simulate_word(word: str) -> StrictBoundedUniversalSimulationResult:
    """Run the strict bounded 4-tape universal machine on ``<M>#x#n``."""
    encoded_machine, encoded_input, encoded_bound = _split_bounded_word(word)
    if not encoded_bound or any(bit not in {"0", "1"} for bit in encoded_bound):
        raise ValueError("Bound n must be a non-empty binary word.")
    bound = int(encoded_bound, 2)
    decoded_machine = decode_machine_strict_text(encoded_machine)
    run_result = _run_encoded_machine(decoded_machine, encoded_input, max_steps=bound)
    remaining = max(bound - run_result.step_count, 0)
    return StrictBoundedUniversalSimulationResult(
        input_word=word,
        encoded_machine=encoded_machine,
        encoded_input=encoded_input,
        decoded_machine=decoded_machine,
        status=run_result.status,
        current_state=run_result.current_state,
        step_count=run_result.step_count,
        tape_symbols=run_result.tape_symbols,
        machine_description_tape=Tape.from_string(encoded_machine),
        simulated_tape=Tape.from_string(_render_symbol_tape(run_result.tape_symbols)),
        work_tape=Tape.from_string(_render_work_tape(run_result)),
        bound=bound,
        counter_tape=Tape.from_string("1" * remaining),
    )


@dataclass(frozen=True, slots=True)
class _EncodedRunResult:
    """Internal encoded-tape simulation result."""

    status: ExecutionStatus
    current_state: str
    step_count: int
    tape_symbols: tuple[str, ...]
    last_transition: StrictEncodedTransition | None


def _run_encoded_machine(
    machine: StrictEncodedMachine,
    encoded_input: str,
    *,
    max_steps: int | None,
) -> _EncodedRunResult:
    """Simulate an encoded mono-tape machine over symbol-code cells."""
    if max_steps is not None and max_steps < 0:
        raise ValueError("max_steps must be non-negative.")

    input_symbols = _parse_encoded_input(encoded_input)
    cells = {
        position: symbol
        for position, symbol in enumerate(input_symbols)
        if symbol != machine.blank_symbol
    }
    current_state = machine.initial_state
    head_position = 0
    step_count = 0
    last_transition: StrictEncodedTransition | None = None

    while True:
        if current_state == machine.accept_state:
            return _build_result(
                ExecutionStatus.ACCEPTED,
                current_state,
                step_count,
                cells,
                machine.blank_symbol,
                last_transition,
            )
        if current_state == machine.reject_state:
            return _build_result(
                ExecutionStatus.REJECTED,
                current_state,
                step_count,
                cells,
                machine.blank_symbol,
                last_transition,
            )
        if max_steps is not None and step_count >= max_steps:
            return _build_result(
                ExecutionStatus.TIMEOUT,
                current_state,
                step_count,
                cells,
                machine.blank_symbol,
                last_transition,
            )

        read_symbol = cells.get(head_position, machine.blank_symbol)
        transition = machine.get_transition(current_state, read_symbol)
        if transition is None:
            current_state = machine.reject_state
            return _build_result(
                ExecutionStatus.REJECTED,
                current_state,
                step_count,
                cells,
                machine.blank_symbol,
                last_transition,
            )

        last_transition = transition
        if transition.write_symbol == machine.blank_symbol:
            cells.pop(head_position, None)
        else:
            cells[head_position] = transition.write_symbol
        current_state = transition.next_state
        head_position = _move_head(head_position, transition.move)
        step_count += 1


def _parse_encoded_input(encoded_input: str) -> tuple[str, ...]:
    """Parse a `|`-separated encoded input word."""
    if encoded_input == "":
        return ()
    symbols = tuple(encoded_input.split("|"))
    for symbol in symbols:
        if not symbol or any(bit not in {"0", "1"} for bit in symbol):
            raise ValueError(f"Encoded input symbol must be a non-empty binary word: {symbol!r}.")
    return symbols


def _build_result(
    status: ExecutionStatus,
    current_state: str,
    step_count: int,
    cells: dict[int, str],
    blank_symbol: str,
    last_transition: StrictEncodedTransition | None,
) -> _EncodedRunResult:
    """Build a normalized internal result."""
    return _EncodedRunResult(
        status=status,
        current_state=current_state,
        step_count=step_count,
        tape_symbols=_normalize_cells(cells, blank_symbol),
        last_transition=last_transition,
    )


def _normalize_cells(cells: dict[int, str], blank_symbol: str) -> tuple[str, ...]:
    """Render the useful encoded tape content as symbol-code cells."""
    if not cells:
        return (blank_symbol,)
    start = min(cells)
    end = max(cells)
    return tuple(cells.get(position, blank_symbol) for position in range(start, end + 1))


def _move_head(position: int, encoded_move: str) -> int:
    """Move the simulated head according to a strict encoded direction."""
    move = REVERSE_TEXT_MOVE_MAP[encoded_move]
    if move == "L":
        return position - 1
    if move == "R":
        return position + 1
    return position


def _split_universal_word(word: str) -> tuple[str, str]:
    """Split the single strict Q9 input word."""
    if not isinstance(word, str):
        raise ValueError("word must be a string.")
    parts = word.split("#")
    if len(parts) != 2:
        raise ValueError("Strict universal input must have the form <M>#x.")
    return parts[0], parts[1]


def _split_bounded_word(word: str) -> tuple[str, str, str]:
    """Split the single strict Q10 input word."""
    if not isinstance(word, str):
        raise ValueError("word must be a string.")
    parts = word.split("#")
    if len(parts) != 3:
        raise ValueError("Strict bounded universal input must have the form <M>#x#n.")
    return parts[0], parts[1], parts[2]


def _render_symbol_tape(symbols: tuple[str, ...]) -> str:
    """Render encoded symbols for the diagnostic simulated tape."""
    return "|".join(symbols)


def _render_work_tape(result: _EncodedRunResult) -> str:
    """Render the strict work tape snapshot."""
    transition = (
        "none"
        if result.last_transition is None
        else (
            f"{result.last_transition.current_state},"
            f"{result.last_transition.read_symbol}->"
            f"{result.last_transition.next_state},"
            f"{result.last_transition.write_symbol},"
            f"{result.last_transition.move}"
        )
    )
    return (
        f"state={result.current_state};"
        f"step={result.step_count};"
        f"status={result.status.value};"
        f"transition={transition}"
    )
