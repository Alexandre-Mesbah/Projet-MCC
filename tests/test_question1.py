"""Strict tests for part 1, question 1."""

from __future__ import annotations

from tm_project.modele import Configuration, Transition, TuringMachine
from tm_project.ruban import Tape


def test_question1_structures_represent_a_machine_and_a_configuration() -> None:
    transition = Transition(
        current_state="I",
        symbols_read=("0",),
        next_state="F",
        symbols_write=("1",),
        moves=("S",),
    )
    machine = TuringMachine(
        name="q1_demo",
        num_tapes=1,
        states={"I", "F"},
        initial_state="I",
        final_state="F",
        transitions={transition.key: transition},
        blank_symbol="_",
    )
    configuration = Configuration(
        current_state="I",
        tapes=[Tape.from_string("0", blank_symbol="_")],
        head_positions=[0],
    )

    assert machine.initial_state == "I"
    assert machine.final_state == "F"
    assert machine.get_transition("I", ("0",)) == transition
    assert configuration.read_symbols() == ("0",)
