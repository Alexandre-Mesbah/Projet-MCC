"""Execution engine for deterministic multi-tape Turing machines."""

from __future__ import annotations

from typing import Sequence

from .modele import Configuration, ExecutionStatus, Move, Transition, TuringMachine
from .parseur_tm import initial_configuration


class MachineRuntimeError(RuntimeError):
    """Raised when runtime data is incompatible with a machine definition."""


def step(machine: TuringMachine, config: Configuration) -> Configuration:
    """Execute one transition and return a new configuration.

    The input configuration is never mutated. If the configuration is already halted,
    a cloned configuration is returned unchanged.
    """
    _validate_runtime_compatibility(machine, config)

    next_config = config.clone()
    if next_config.halted or next_config.status != ExecutionStatus.RUNNING:
        return next_config

    if machine.is_final_state(next_config.current_state):
        return _mark_halted(
            next_config,
            status=ExecutionStatus.ACCEPTED,
            halt_reason="Current state is final.",
        )
    if machine.is_reject_state(next_config.current_state):
        return _mark_halted(
            next_config,
            status=ExecutionStatus.REJECTED,
            halt_reason="Current state is reject.",
        )

    transition = machine.get_transition(next_config.current_state, next_config.read_symbols())
    if transition is None:
        if machine.reject_state is not None:
            next_config.current_state = machine.reject_state
            return _mark_halted(
                next_config,
                status=ExecutionStatus.REJECTED,
                halt_reason=(
                    f"No transition for state {config.current_state!r} and "
                    f"symbols {config.read_symbols()!r}; defaulted to reject state."
                ),
            )
        return _mark_halted(
            next_config,
            status=ExecutionStatus.BLOCKED,
            halt_reason=(
                f"No transition for state {next_config.current_state!r} and "
                f"symbols {next_config.read_symbols()!r}."
            ),
        )

    _apply_transition(next_config, transition)
    next_config.step_count += 1

    if machine.is_final_state(next_config.current_state):
        return _mark_halted(
            next_config,
            status=ExecutionStatus.ACCEPTED,
            halt_reason="Reached the final state.",
        )
    if machine.is_reject_state(next_config.current_state):
        return _mark_halted(
            next_config,
            status=ExecutionStatus.REJECTED,
            halt_reason="Reached the reject state.",
        )

    next_config.halted = False
    next_config.status = ExecutionStatus.RUNNING
    next_config.halt_reason = None
    return next_config


def run(
    machine: TuringMachine,
    input_word: str | Sequence[str],
    max_steps: int | None = None,
) -> Configuration:
    """Run a machine from its initial configuration until it halts or times out."""
    return _run_internal(
        machine,
        initial_configuration(machine, input_word),
        max_steps=max_steps,
        collect_history=False,
    )


def run_verbose(
    machine: TuringMachine,
    input_word: str | Sequence[str],
    max_steps: int | None = None,
) -> list[Configuration]:
    """Run a machine and return all visited configurations."""
    return _run_internal(
        machine,
        initial_configuration(machine, input_word),
        max_steps=max_steps,
        collect_history=True,
    )


def run_stream(
    machine: TuringMachine,
    input_word: str | Sequence[str],
    max_steps: int | None = None,
):
    """Yield configurations as they are produced during a run."""
    _validate_max_steps(max_steps)

    current = initial_configuration(machine, input_word).clone()
    if current.status != ExecutionStatus.RUNNING:
        yield current
        return

    if max_steps is not None and current.step_count >= max_steps:
        yield _mark_timeout(current, max_steps).clone()
        return

    yield current.clone()
    while current.status == ExecutionStatus.RUNNING:
        current = step(machine, current)
        if current.status == ExecutionStatus.RUNNING and max_steps is not None:
            if current.step_count >= max_steps:
                current = _mark_timeout(current, max_steps)
        yield current.clone()
        if current.status != ExecutionStatus.RUNNING:
            break


def _run_internal(
    machine: TuringMachine,
    initial_config: Configuration,
    *,
    max_steps: int | None,
    collect_history: bool,
) -> Configuration | list[Configuration]:
    """Drive a simulation from an initial configuration."""
    _validate_max_steps(max_steps)

    current = initial_config.clone()
    history: list[Configuration] = [current.clone()] if collect_history else []

    if current.status != ExecutionStatus.RUNNING:
        return history if collect_history else current

    if max_steps is not None and current.step_count >= max_steps:
        current = _mark_timeout(current, max_steps)
        if collect_history:
            history[-1] = current.clone()
            return history
        return current

    while current.status == ExecutionStatus.RUNNING:
        current = step(machine, current)
        if collect_history:
            history.append(current.clone())

        if current.status != ExecutionStatus.RUNNING:
            break

        if max_steps is not None and current.step_count >= max_steps:
            current = _mark_timeout(current, max_steps)
            if collect_history:
                history[-1] = current.clone()
            break

    return history if collect_history else current


def _validate_runtime_compatibility(machine: TuringMachine, config: Configuration) -> None:
    """Ensure that a runtime configuration matches its machine."""
    if config.num_tapes != machine.num_tapes:
        raise MachineRuntimeError(
            f"Configuration has {config.num_tapes} tape(s), expected {machine.num_tapes}."
        )
    if config.current_state not in machine.states:
        raise MachineRuntimeError(
            f"Unknown runtime state {config.current_state!r} for machine {machine.name!r}."
        )
    for index, tape in enumerate(config.tapes, start=1):
        if tape.blank_symbol != machine.blank_symbol:
            raise MachineRuntimeError(
                f"Tape {index} uses blank symbol {tape.blank_symbol!r}, "
                f"expected {machine.blank_symbol!r}."
            )


def _apply_transition(config: Configuration, transition: Transition) -> None:
    """Apply a transition in place to a cloned configuration."""
    for tape, position, symbol, move in zip(
        config.tapes,
        config.head_positions,
        transition.symbols_write,
        transition.moves,
        strict=True,
    ):
        tape.write(position, symbol)

    for index, move in enumerate(transition.moves):
        config.head_positions[index] = _move_head(config.head_positions[index], move)

    config.current_state = transition.next_state


def _move_head(position: int, move: Move) -> int:
    """Compute the next head position from a move symbol."""
    if move == "L":
        return position - 1
    if move == "R":
        return position + 1
    return position


def _mark_halted(
    config: Configuration,
    *,
    status: ExecutionStatus,
    halt_reason: str,
) -> Configuration:
    """Mark a configuration as halted and return it."""
    config.halted = True
    config.status = status
    config.halt_reason = halt_reason
    return config


def _mark_timeout(config: Configuration, max_steps: int) -> Configuration:
    """Mark a configuration as stopped by the execution bound."""
    config.halted = False
    config.status = ExecutionStatus.TIMEOUT
    config.halt_reason = f"Execution did not halt within {max_steps} step(s)."
    return config


def _validate_max_steps(max_steps: int | None) -> None:
    """Validate the step bound passed to run helpers."""
    if max_steps is None:
        return
    if not isinstance(max_steps, int) or isinstance(max_steps, bool):
        raise ValueError("max_steps must be an integer or None.")
    if max_steps < 0:
        raise ValueError("max_steps must be non-negative.")
