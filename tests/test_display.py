"""Tests for configuration display helpers."""

from __future__ import annotations

from tm_project.affichage import format_configuration, format_configuration_detailed
from tm_project.parseur_tm import parse_machine_text
from tm_project.simulateur import run


def test_format_configuration_contains_core_runtime_information() -> None:
    machine = parse_machine_text(
        """
        name: flip
        init: q0
        final: qf
        q0 0 -> qf 1 S
        """
    )
    config = run(machine, "0")

    rendered = format_configuration(config, radius=2)

    assert "Step 1" in rendered
    assert "State: qf" in rendered
    assert "Status: accepted" in rendered
    assert "Tape 1:" in rendered
    assert "^" in rendered


def test_format_configuration_detailed_shows_positions_and_reason() -> None:
    machine = parse_machine_text(
        """
        name: blocked
        init: q0
        final: qf
        q0 0 -> qf 1 S
        """
    )
    config = run(machine, "1")

    rendered = format_configuration_detailed(config, radius=1)

    assert "Step:" in rendered
    assert "Status: blocked" in rendered
    assert "Reason:" in rendered
    assert "Tape 1 positions:" in rendered
    assert "Tape 1 symbols:" in rendered
    assert "^" in rendered
