"""Core data models for multi-tape Turing machines."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from .ruban import Tape

Symbol = str
State = str
Move = Literal["L", "R", "S"]


class MachineValidationError(ValueError):
    """Raised when a Turing machine definition is inconsistent."""


class ExecutionStatus(str, Enum):
    """Execution state of a simulation."""

    RUNNING = "running"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    BLOCKED = "blocked"
    TIMEOUT = "timeout"


def _validate_machine_name(name: str) -> None:
    """Validate a machine name."""
    if not isinstance(name, str):
        raise MachineValidationError("The machine name must be a string.")
    if not name.strip():
        raise MachineValidationError("The machine name must be a non-empty string.")
    if name != name.strip():
        raise MachineValidationError(
            "The machine name must not contain leading or trailing whitespace."
        )


def _validate_state_name(state: str, *, label: str) -> None:
    """Validate a state identifier."""
    if not isinstance(state, str):
        raise MachineValidationError(f"{label} must be a string.")
    if not state.strip():
        raise MachineValidationError(f"{label} must be a non-empty string.")
    if state != state.strip():
        raise MachineValidationError(
            f"{label} must not contain leading or trailing whitespace."
        )


def _validate_symbol(symbol: str, *, label: str) -> None:
    """Validate a one-cell tape symbol."""
    if not isinstance(symbol, str):
        raise MachineValidationError(f"{label} must be a string.")
    if symbol == "":
        raise MachineValidationError(f"{label} must be a non-empty string.")
    if len(symbol) != 1:
        raise MachineValidationError(f"{label} must be a one-character string.")


def _validate_positive_int(value: int, *, label: str) -> None:
    """Validate a positive integer."""
    if not isinstance(value, int) or isinstance(value, bool):
        raise MachineValidationError(f"{label} must be an integer.")
    if value < 1:
        raise MachineValidationError(f"{label} must be >= 1.")


def _validate_non_negative_int(value: int, *, label: str) -> None:
    """Validate a non-negative integer."""
    if not isinstance(value, int) or isinstance(value, bool):
        raise MachineValidationError(f"{label} must be an integer.")
    if value < 0:
        raise MachineValidationError(f"{label} must be non-negative.")


@dataclass(frozen=True, slots=True)
class Transition:
    """One transition of a deterministic multi-tape Turing machine."""

    current_state: State
    symbols_read: tuple[Symbol, ...]
    next_state: State
    symbols_write: tuple[Symbol, ...]
    moves: tuple[Move, ...]

    def __post_init__(self) -> None:
        """Validate local transition consistency."""
        _validate_state_name(self.current_state, label="The current state")
        _validate_state_name(self.next_state, label="The next state")
        if not self.symbols_read:
            raise MachineValidationError("A transition must read at least one symbol.")
        if len(self.symbols_read) != len(self.symbols_write):
            raise MachineValidationError(
                "The number of read symbols must match the number of written symbols."
            )
        if len(self.symbols_read) != len(self.moves):
            raise MachineValidationError(
                "The number of moves must match the number of tapes."
            )
        invalid_moves = [move for move in self.moves if move not in {"L", "R", "S"}]
        if invalid_moves:
            raise MachineValidationError(
                f"Invalid move(s) in transition {self.current_state!r}: {invalid_moves}."
            )
        for symbol in (*self.symbols_read, *self.symbols_write):
            _validate_symbol(symbol, label="Tape symbols")

    @property
    def tape_count(self) -> int:
        """Return the number of tapes handled by this transition."""
        return len(self.symbols_read)

    @property
    def key(self) -> tuple[State, tuple[Symbol, ...]]:
        """Return the dictionary key used for deterministic lookup."""
        return (self.current_state, self.symbols_read)


@dataclass(slots=True)
class TuringMachine:
    """Deterministic multi-tape Turing machine."""

    name: str
    num_tapes: int
    states: set[State]
    initial_state: State
    final_state: State
    transitions: dict[tuple[State, tuple[Symbol, ...]], Transition]
    blank_symbol: Symbol = "_"
    reject_state: State | None = None

    def __post_init__(self) -> None:
        """Validate machine consistency."""
        self.validate()

    def validate(self) -> None:
        """Check that the machine definition is coherent."""
        _validate_machine_name(self.name)
        _validate_positive_int(self.num_tapes, label="num_tapes")
        if not self.states:
            raise MachineValidationError("The machine must declare at least one state.")
        _validate_symbol(self.blank_symbol, label="The blank symbol")
        for state in self.states:
            _validate_state_name(state, label=f"Declared state {state!r}")
        _validate_state_name(self.initial_state, label="The initial state")
        _validate_state_name(self.final_state, label="The final state")
        if self.reject_state is not None:
            _validate_state_name(self.reject_state, label="The reject state")
        if self.initial_state not in self.states:
            raise MachineValidationError(
                f"Initial state {self.initial_state!r} is not declared in the state set."
            )
        if self.final_state not in self.states:
            raise MachineValidationError(
                f"Final state {self.final_state!r} is not declared in the state set."
            )
        if self.reject_state is not None and self.reject_state not in self.states:
            raise MachineValidationError(
                f"Reject state {self.reject_state!r} is not declared in the state set."
            )

        seen_keys: set[tuple[State, tuple[Symbol, ...]]] = set()
        for key, transition in self.transitions.items():
            if key != transition.key:
                raise MachineValidationError(
                    "Transition dictionary keys must match transition content."
                )
            if transition.current_state not in self.states:
                raise MachineValidationError(
                    f"Unknown current state {transition.current_state!r} in transitions."
                )
            if transition.next_state not in self.states:
                raise MachineValidationError(
                    f"Unknown next state {transition.next_state!r} in transitions."
                )
            if transition.tape_count != self.num_tapes:
                raise MachineValidationError(
                    f"Transition {transition!r} does not match num_tapes={self.num_tapes}."
                )
            if key in seen_keys:
                raise MachineValidationError(
                    f"Duplicate deterministic transition for key {key!r}."
                )
            seen_keys.add(key)

    def get_transition(
        self, current_state: State, symbols_read: tuple[Symbol, ...]
    ) -> Transition | None:
        """Return the matching transition, if any."""
        return self.transitions.get((current_state, symbols_read))

    def is_final_state(self, state: State) -> bool:
        """Tell whether a state is the designated halting state."""
        return state == self.final_state

    def is_reject_state(self, state: State) -> bool:
        """Tell whether a state is the optional rejecting state."""
        return self.reject_state is not None and state == self.reject_state


@dataclass(slots=True)
class Configuration:
    """Runtime configuration of a machine at a given step."""

    current_state: State
    tapes: list["Tape"]
    head_positions: list[int]
    halted: bool = False
    step_count: int = 0
    status: ExecutionStatus = ExecutionStatus.RUNNING
    halt_reason: str | None = None

    def __post_init__(self) -> None:
        """Check basic internal consistency."""
        _validate_state_name(self.current_state, label="The current state")
        if len(self.tapes) != len(self.head_positions):
            raise MachineValidationError(
                "The number of tapes must match the number of head positions."
            )
        if not self.tapes:
            raise MachineValidationError("A configuration must contain at least one tape.")
        from .ruban import Tape

        if any(not isinstance(tape, Tape) for tape in self.tapes):
            raise MachineValidationError(
                "Configuration tapes must be Tape instances."
            )
        if any(not isinstance(position, int) or isinstance(position, bool) for position in self.head_positions):
            raise MachineValidationError("Head positions must be integers.")
        _validate_non_negative_int(self.step_count, label="step_count")

    @property
    def num_tapes(self) -> int:
        """Return the number of tapes in the configuration."""
        return len(self.tapes)

    def read_symbols(self) -> tuple[Symbol, ...]:
        """Read all symbols currently under the heads."""
        return tuple(
            tape.read(position)
            for tape, position in zip(self.tapes, self.head_positions, strict=True)
        )

    def clone(self) -> Configuration:
        """Return a deep copy suitable for pure step-by-step simulation."""
        return Configuration(
            current_state=self.current_state,
            tapes=[tape.clone() for tape in self.tapes],
            head_positions=list(self.head_positions),
            halted=self.halted,
            step_count=self.step_count,
            status=self.status,
            halt_reason=self.halt_reason,
        )
