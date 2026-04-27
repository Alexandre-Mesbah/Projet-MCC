"""Formatting helpers for simulation traces."""

from __future__ import annotations

from .modele import Configuration


def format_configuration(config: Configuration, radius: int = 10) -> str:
    """Render a compact, presentation-friendly configuration."""
    _validate_radius(radius)
    lines = [
        f"Step {config.step_count} | State: {config.current_state} | Status: {config.status.value}",
    ]
    if config.halt_reason:
        lines.append(f"Reason: {config.halt_reason}")
    lines.extend(_format_tapes(config, radius=radius, detailed=False))
    return "\n".join(lines)


def format_configuration_detailed(config: Configuration, radius: int = 10) -> str:
    """Render a detailed configuration with explicit tape positions."""
    _validate_radius(radius)
    lines = [
        f"Step: {config.step_count}",
        f"State: {config.current_state}",
        f"Status: {config.status.value}",
    ]
    if config.halt_reason:
        lines.append(f"Reason: {config.halt_reason}")
    lines.extend(_format_tapes(config, radius=radius, detailed=True))
    return "\n".join(lines)


def _format_tapes(config: Configuration, *, radius: int, detailed: bool) -> list[str]:
    """Render all tapes in compact or detailed form."""
    lines: list[str] = []
    for tape_index, (tape, head_position) in enumerate(
        zip(config.tapes, config.head_positions, strict=True),
        start=1,
    ):
        positions = list(range(head_position - radius, head_position + radius + 1))
        symbols = [tape.read(position) for position in positions]

        if detailed:
            position_values = " ".join(f"{position:>2}" for position in positions)
            symbol_values = " ".join(f"{symbol:>2}" for symbol in symbols)
            tape_label = f"Tape {tape_index}"
            lines.append(f"{tape_label} positions: {position_values}")
            lines.append(f"{tape_label} symbols:   {symbol_values}")
            lines.append(" " * (len(f"{tape_label} symbols:   ") + 3 * radius + 1) + "^")
        else:
            prefix = f"Tape {tape_index}: "
            symbol_values = " ".join(symbols)
            lines.append(prefix + symbol_values)
            lines.append(" " * (len(prefix) + 2 * radius) + "^")
    return lines


def _validate_radius(radius: int) -> None:
    """Validate a display radius."""
    if not isinstance(radius, int) or isinstance(radius, bool):
        raise ValueError("radius must be an integer.")
    if radius < 0:
        raise ValueError("radius must be non-negative.")
