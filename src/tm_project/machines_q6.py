"""Strict part 1 helpers and subject machines.

This module provides:
- a small pattern-based builder for deterministic multi-tape machines;
- serializers to the project's documented `.tm` subset;
- general-purpose machines for part 1 question 6.

Language note:
The repository still uses the documented textual subset parsed by `parser_tms.py`
(`state read -> next write moves`) instead of the raw UI-oriented syntax from
https://turingmachinesimulator.com/. This is an explicit simplification kept in
code comments and README, as allowed by the project statement.
"""

from __future__ import annotations

from itertools import product
from pathlib import Path
from typing import Iterable

from .modele import Move, Transition, TuringMachine

PART1_SUBJECT_ALPHABET = ("0", "1", "#", "|", "_")
KEEP = object()
ANY = object()


class PatternMachineBuilder:
    """Pattern-based helper that expands wildcard transitions safely."""

    def __init__(
        self,
        *,
        name: str,
        num_tapes: int,
        blank_symbol: str = "_",
        alphabet: tuple[str, ...] = PART1_SUBJECT_ALPHABET,
        initial_state: str = "I",
        final_state: str = "F",
    ) -> None:
        self.name = name
        self.num_tapes = num_tapes
        self.blank_symbol = blank_symbol
        self.alphabet = alphabet
        self.initial_state = initial_state
        self.final_state = final_state
        self._states: set[str] = {initial_state, final_state}
        self._transitions: dict[tuple[str, tuple[str, ...]], Transition] = {}

    def add(
        self,
        current_state: str,
        symbols_read: tuple[str, ...],
        next_state: str,
        symbols_write: tuple[str, ...],
        moves: tuple[Move, ...],
    ) -> None:
        """Add a concrete deterministic transition."""
        transition = Transition(
            current_state=current_state,
            symbols_read=symbols_read,
            next_state=next_state,
            symbols_write=symbols_write,
            moves=moves,
        )
        if transition.key in self._transitions:
            raise ValueError(f"Duplicate transition for key {transition.key!r}.")
        self._states.update({current_state, next_state})
        self._transitions[transition.key] = transition

    def add_pattern(
        self,
        current_state: str,
        symbols_read: tuple[object, ...],
        next_state: str,
        symbols_write: tuple[object, ...],
        moves: tuple[Move, ...],
    ) -> None:
        """Expand wildcard pattern transitions.

        Each read slot accepts either:
        - a concrete symbol, e.g. `"0"`
        - an iterable of symbols, e.g. `("0", "1")`
        - `ANY`, meaning any symbol from the builder alphabet

        Each write slot accepts either:
        - a concrete symbol
        - `KEEP`, meaning "rewrite the read symbol unchanged"
        """
        if len(symbols_read) != self.num_tapes:
            raise ValueError("symbols_read does not match num_tapes.")
        if len(symbols_write) != self.num_tapes:
            raise ValueError("symbols_write does not match num_tapes.")
        if len(moves) != self.num_tapes:
            raise ValueError("moves does not match num_tapes.")

        read_choices = [self._expand_read_slot(slot) for slot in symbols_read]
        for concrete_read in product(*read_choices):
            concrete_write = tuple(
                read_symbol if write_symbol is KEEP else str(write_symbol)
                for read_symbol, write_symbol in zip(concrete_read, symbols_write, strict=True)
            )
            self.add(
                current_state,
                tuple(concrete_read),
                next_state,
                concrete_write,
                moves,
            )

    def add_loop_state(self, state: str) -> None:
        """Add a total non-halting self-loop over the subject alphabet."""
        self._states.add(state)
        for symbols in product(self.alphabet, repeat=self.num_tapes):
            if (state, tuple(symbols)) in self._transitions:
                continue
            self.add(
                state,
                tuple(symbols),
                state,
                tuple(symbols),
                tuple("S" for _ in range(self.num_tapes)),
            )

    def build(self) -> TuringMachine:
        """Finalize the machine."""
        return TuringMachine(
            name=self.name,
            num_tapes=self.num_tapes,
            states=set(self._states),
            initial_state=self.initial_state,
            final_state=self.final_state,
            transitions=dict(self._transitions),
            blank_symbol=self.blank_symbol,
        )

    def _expand_read_slot(self, slot: object) -> tuple[str, ...]:
        if slot is ANY:
            return self.alphabet
        if isinstance(slot, str):
            return (slot,)
        if isinstance(slot, Iterable):
            expanded = tuple(str(symbol) for symbol in slot)
            if not expanded:
                raise ValueError("Pattern slots cannot be empty.")
            return expanded
        raise TypeError(f"Unsupported pattern slot: {slot!r}.")


def serialize_machine(machine: TuringMachine, *, comment_lines: list[str] | None = None) -> str:
    """Serialize a machine using the repository `.tm` subset."""
    lines: list[str] = []
    if comment_lines:
        lines.extend(f"; {line}" for line in comment_lines)
    lines.extend(
        [
            f"name: {machine.name}",
            f"init: {machine.initial_state}",
            f"final: {machine.final_state}",
            f"blank: {machine.blank_symbol}",
        ]
    )
    if machine.num_tapes != 1:
        lines.append(f"tapes: {machine.num_tapes}")

    for transition in sorted(
        machine.transitions.values(),
        key=lambda item: (
            item.current_state,
            item.symbols_read,
            item.next_state,
            item.symbols_write,
            item.moves,
        ),
    ):
        read_symbols = ",".join(transition.symbols_read)
        write_symbols = ",".join(transition.symbols_write)
        moves = ",".join(transition.moves)
        lines.append(
            f"{transition.current_state} {read_symbols} -> {transition.next_state} {write_symbols} {moves}"
        )
    return "\n".join(lines) + "\n"


def build_compare_binary_machine() -> TuringMachine:
    """Build a 3-tape machine that halts iff x < y for binary integers x#y."""
    builder = PatternMachineBuilder(name="compare_binary", num_tapes=3)

    # Trim leading zeros while copying x to tape 2. Empty/zero-only x becomes 0.
    builder.add_pattern("I", ("0", "_", "_"), "I", (KEEP, KEEP, KEEP), ("R", "S", "S"))
    builder.add_pattern("I", ("1", "_", "_"), "COPY_X", (KEEP, "1", KEEP), ("R", "R", "S"))
    builder.add_pattern("I", ("#", "_", "_"), "COPY_Y_SKIP", (KEEP, "0", KEEP), ("R", "R", "S"))

    builder.add_pattern("COPY_X", ("0", "_", "_"), "COPY_X", (KEEP, "0", KEEP), ("R", "R", "S"))
    builder.add_pattern("COPY_X", ("1", "_", "_"), "COPY_X", (KEEP, "1", KEEP), ("R", "R", "S"))
    builder.add_pattern("COPY_X", ("#", "_", "_"), "COPY_Y_SKIP", (KEEP, KEEP, KEEP), ("R", "S", "S"))

    # Trim leading zeros while copying y to tape 3. Empty/zero-only y becomes 0.
    builder.add_pattern(
        "COPY_Y_SKIP",
        ("0", ANY, "_"),
        "COPY_Y_SKIP",
        (KEEP, KEEP, KEEP),
        ("R", "S", "S"),
    )
    builder.add_pattern(
        "COPY_Y_SKIP",
        ("1", ANY, "_"),
        "COPY_Y",
        (KEEP, KEEP, "1"),
        ("R", "S", "R"),
    )
    builder.add_pattern(
        "COPY_Y_SKIP",
        ("_", ANY, "_"),
        "REWIND_X_PRE",
        (KEEP, KEEP, "0"),
        ("S", "S", "R"),
    )

    builder.add_pattern("COPY_Y", ("0", ANY, "_"), "COPY_Y", (KEEP, KEEP, "0"), ("R", "S", "R"))
    builder.add_pattern("COPY_Y", ("1", ANY, "_"), "COPY_Y", (KEEP, KEEP, "1"), ("R", "S", "R"))
    builder.add_pattern("COPY_Y", ("_", ANY, "_"), "REWIND_X_PRE", (KEEP, KEEP, KEEP), ("S", "S", "S"))

    # Rewind normalized x and y to their starts.
    builder.add_pattern("REWIND_X_PRE", (ANY, "_", ANY), "REWIND_X", (KEEP, KEEP, KEEP), ("S", "L", "S"))
    builder.add_pattern(
        "REWIND_X",
        (ANY, ("0", "1"), ANY),
        "REWIND_X",
        (KEEP, KEEP, KEEP),
        ("S", "L", "S"),
    )
    builder.add_pattern("REWIND_X", (ANY, "_", ANY), "REWIND_Y_PRE", (KEEP, KEEP, KEEP), ("S", "R", "S"))

    builder.add_pattern("REWIND_Y_PRE", (ANY, ANY, "_"), "REWIND_Y", (KEEP, KEEP, KEEP), ("S", "S", "L"))
    builder.add_pattern(
        "REWIND_Y",
        (ANY, ANY, ("0", "1")),
        "REWIND_Y",
        (KEEP, KEEP, KEEP),
        ("S", "S", "L"),
    )
    builder.add_pattern("REWIND_Y", (ANY, ANY, "_"), "CMP_LEN", (KEEP, KEEP, KEEP), ("S", "S", "R"))

    # Compare normalized lengths first.
    builder.add_pattern(
        "CMP_LEN",
        ("_", ("0", "1"), ("0", "1")),
        "CMP_LEN",
        (KEEP, KEEP, KEEP),
        ("S", "R", "R"),
    )
    builder.add_pattern("CMP_LEN", ("_", "_", ("0", "1")), "F", (KEEP, KEEP, KEEP), ("S", "S", "S"))
    builder.add_pattern("CMP_LEN", ("_", ("0", "1"), "_"), "LOOP", (KEEP, KEEP, KEEP), ("S", "S", "S"))
    builder.add_pattern("CMP_LEN", ("_", "_", "_"), "REWIND_X2_PRE", (KEEP, KEEP, KEEP), ("S", "S", "S"))

    builder.add_pattern("REWIND_X2_PRE", (ANY, "_", ANY), "REWIND_X2", (KEEP, KEEP, KEEP), ("S", "L", "S"))
    builder.add_pattern(
        "REWIND_X2",
        (ANY, ("0", "1"), ANY),
        "REWIND_X2",
        (KEEP, KEEP, KEEP),
        ("S", "L", "S"),
    )
    builder.add_pattern("REWIND_X2", (ANY, "_", ANY), "REWIND_Y2_PRE", (KEEP, KEEP, KEEP), ("S", "R", "S"))

    builder.add_pattern("REWIND_Y2_PRE", (ANY, ANY, "_"), "REWIND_Y2", (KEEP, KEEP, KEEP), ("S", "S", "L"))
    builder.add_pattern(
        "REWIND_Y2",
        (ANY, ANY, ("0", "1")),
        "REWIND_Y2",
        (KEEP, KEEP, KEEP),
        ("S", "S", "L"),
    )
    builder.add_pattern("REWIND_Y2", (ANY, ANY, "_"), "CMP_LEX", (KEEP, KEEP, KEEP), ("S", "S", "R"))

    # Same length: compare lexicographically.
    builder.add_pattern("CMP_LEX", ("_", "0", "0"), "CMP_LEX", (KEEP, KEEP, KEEP), ("S", "R", "R"))
    builder.add_pattern("CMP_LEX", ("_", "1", "1"), "CMP_LEX", (KEEP, KEEP, KEEP), ("S", "R", "R"))
    builder.add_pattern("CMP_LEX", ("_", "0", "1"), "F", (KEEP, KEEP, KEEP), ("S", "S", "S"))
    builder.add_pattern("CMP_LEX", ("_", "1", "0"), "LOOP", (KEEP, KEEP, KEEP), ("S", "S", "S"))
    builder.add_pattern("CMP_LEX", ("_", "_", "_"), "LOOP", (KEEP, KEEP, KEEP), ("S", "S", "S"))

    builder.add_loop_state("LOOP")
    return builder.build()


def build_search_list_machine() -> TuringMachine:
    """Build a 2-tape machine that halts iff x occurs in x#w1#...#wl."""
    builder = PatternMachineBuilder(name="search_list", num_tapes=2)

    # Copy x to tape 2. Empty x is handled by a dedicated branch.
    builder.add_pattern("I", ("0", "_"), "COPY_X", (KEEP, "0"), ("R", "R"))
    builder.add_pattern("I", ("1", "_"), "COPY_X", (KEEP, "1"), ("R", "R"))
    builder.add_pattern("I", ("#", "_"), "COMPARE_EMPTY_X", (KEEP, KEEP), ("R", "S"))

    builder.add_pattern("COPY_X", ("0", "_"), "COPY_X", (KEEP, "0"), ("R", "R"))
    builder.add_pattern("COPY_X", ("1", "_"), "COPY_X", (KEEP, "1"), ("R", "R"))
    builder.add_pattern("COPY_X", ("#", "_"), "REWIND_X_PRE", (KEEP, KEEP), ("R", "L"))

    builder.add_pattern("REWIND_X_PRE", (ANY, ANY), "REWIND_X", (KEEP, KEEP), ("S", "S"))
    builder.add_pattern("REWIND_X", (ANY, ("0", "1")), "REWIND_X", (KEEP, KEEP), ("S", "L"))
    builder.add_pattern("REWIND_X", (ANY, "_"), "COMPARE", (KEEP, KEEP), ("S", "R"))

    # x is empty: accept on an empty candidate, otherwise skip to the next one.
    builder.add_pattern("COMPARE_EMPTY_X", ("#", ANY), "F", (KEEP, KEEP), ("S", "S"))
    builder.add_pattern("COMPARE_EMPTY_X", ("_", ANY), "F", (KEEP, KEEP), ("S", "S"))
    builder.add_pattern(
        "COMPARE_EMPTY_X",
        (("0", "1"), ANY),
        "SKIP_EMPTY_X",
        (KEEP, KEEP),
        ("S", "S"),
    )
    builder.add_pattern(
        "SKIP_EMPTY_X",
        (("0", "1"), ANY),
        "SKIP_EMPTY_X",
        (KEEP, KEEP),
        ("R", "S"),
    )
    builder.add_pattern("SKIP_EMPTY_X", ("#", ANY), "COMPARE_EMPTY_X", (KEEP, KEEP), ("R", "S"))
    builder.add_pattern("SKIP_EMPTY_X", ("_", ANY), "LOOP", (KEEP, KEEP), ("S", "S"))

    # Non-empty x: compare current candidate with x stored on tape 2.
    builder.add_pattern("COMPARE", ("0", "0"), "COMPARE", (KEEP, KEEP), ("R", "R"))
    builder.add_pattern("COMPARE", ("1", "1"), "COMPARE", (KEEP, KEEP), ("R", "R"))
    builder.add_pattern("COMPARE", ("#", "_"), "F", (KEEP, KEEP), ("S", "S"))
    builder.add_pattern("COMPARE", ("_", "_"), "F", (KEEP, KEEP), ("S", "S"))

    # Candidate ended early: move to the next candidate, otherwise no match.
    builder.add_pattern("COMPARE", ("#", ("0", "1")), "REWIND_AFTER_FAIL_PRE", (KEEP, KEEP), ("R", "L"))
    builder.add_pattern("COMPARE", ("_", ("0", "1")), "LOOP", (KEEP, KEEP), ("S", "S"))

    # Candidate longer or symbol mismatch: skip the rest of the current candidate first.
    builder.add_pattern("COMPARE", ("0", "1"), "SKIP_CANDIDATE", (KEEP, KEEP), ("S", "S"))
    builder.add_pattern("COMPARE", ("1", "0"), "SKIP_CANDIDATE", (KEEP, KEEP), ("S", "S"))
    builder.add_pattern("COMPARE", (("0", "1"), "_"), "SKIP_CANDIDATE", (KEEP, KEEP), ("S", "S"))

    builder.add_pattern(
        "SKIP_CANDIDATE",
        (("0", "1"), ANY),
        "SKIP_CANDIDATE",
        (KEEP, KEEP),
        ("R", "S"),
    )
    builder.add_pattern("SKIP_CANDIDATE", ("#", ANY), "REWIND_AFTER_FAIL_PRE", (KEEP, KEEP), ("R", "L"))
    builder.add_pattern("SKIP_CANDIDATE", ("_", ANY), "LOOP", (KEEP, KEEP), ("S", "S"))

    builder.add_pattern("REWIND_AFTER_FAIL_PRE", (ANY, ANY), "REWIND_AFTER_FAIL", (KEEP, KEEP), ("S", "S"))
    builder.add_pattern(
        "REWIND_AFTER_FAIL",
        (ANY, ("0", "1")),
        "REWIND_AFTER_FAIL",
        (KEEP, KEEP),
        ("S", "L"),
    )
    builder.add_pattern("REWIND_AFTER_FAIL", (ANY, "_"), "COMPARE", (KEEP, KEEP), ("S", "R"))

    builder.add_loop_state("LOOP")
    return builder.build()


def build_unary_multiply_machine() -> TuringMachine:
    """Build a 3-tape machine computing 1^n#1^m -> 1^(n*m) on tape 1."""
    builder = PatternMachineBuilder(name="unary_multiply", num_tapes=3)

    # Copy the right factor to tape 2.
    builder.add_pattern("I", ("1", ANY, ANY), "I", (KEEP, KEEP, KEEP), ("R", "S", "S"))
    builder.add_pattern("I", ("#", ANY, ANY), "COPY_M", (KEEP, KEEP, KEEP), ("R", "S", "S"))

    builder.add_pattern("COPY_M", ("1", "_", ANY), "COPY_M", (KEEP, "1", KEEP), ("R", "R", "S"))
    builder.add_pattern("COPY_M", ("_", "_", ANY), "REWIND_T1_PRE", (KEEP, KEEP, KEEP), ("S", "S", "S"))

    # Rewind tape 1 to the start of the left factor and tape 2 to the start of m.
    builder.add_pattern("REWIND_T1_PRE", (ANY, ANY, ANY), "REWIND_T1", (KEEP, KEEP, KEEP), ("L", "S", "S"))
    builder.add_pattern(
        "REWIND_T1",
        (("1", "#"), ANY, ANY),
        "REWIND_T1",
        (KEEP, KEEP, KEEP),
        ("L", "S", "S"),
    )
    builder.add_pattern("REWIND_T1", ("_", ANY, ANY), "REWIND_T2_PRE", (KEEP, KEEP, KEEP), ("R", "S", "S"))

    builder.add_pattern("REWIND_T2_PRE", (ANY, ANY, ANY), "REWIND_T2", (KEEP, KEEP, KEEP), ("S", "L", "S"))
    builder.add_pattern("REWIND_T2", (ANY, "1", ANY), "REWIND_T2", (KEEP, KEEP, KEEP), ("S", "L", "S"))
    builder.add_pattern("REWIND_T2", (ANY, "_", ANY), "SCAN_LEFT", (KEEP, KEEP, KEEP), ("S", "R", "S"))

    # Process each remaining 1 on the left factor by appending one copy of m to tape 3.
    builder.add_pattern("SCAN_LEFT", ("1", ANY, ANY), "COPY_MULT", ("|", KEEP, KEEP), ("S", "S", "S"))
    builder.add_pattern("SCAN_LEFT", ("|", ANY, ANY), "SCAN_LEFT", (KEEP, KEEP, KEEP), ("R", "S", "S"))
    builder.add_pattern("SCAN_LEFT", ("#", ANY, ANY), "OUTPUT_REWIND_T1_PRE", (KEEP, KEEP, KEEP), ("S", "S", "S"))

    builder.add_pattern("COPY_MULT", ("|", "1", "_"), "COPY_MULT", (KEEP, KEEP, "1"), ("S", "R", "R"))
    builder.add_pattern("COPY_MULT", ("|", "_", ANY), "REWIND_T2_AFTER_COPY_PRE", (KEEP, KEEP, KEEP), ("S", "L", "S"))

    builder.add_pattern(
        "REWIND_T2_AFTER_COPY_PRE",
        (ANY, ANY, ANY),
        "REWIND_T2_AFTER_COPY",
        (KEEP, KEEP, KEEP),
        ("S", "S", "S"),
    )
    builder.add_pattern(
        "REWIND_T2_AFTER_COPY",
        (ANY, "1", ANY),
        "REWIND_T2_AFTER_COPY",
        (KEEP, KEEP, KEEP),
        ("S", "L", "S"),
    )
    builder.add_pattern(
        "REWIND_T2_AFTER_COPY",
        (ANY, "_", ANY),
        "REWIND_T1_AFTER_COPY_PRE",
        (KEEP, KEEP, KEEP),
        ("S", "R", "S"),
    )

    builder.add_pattern(
        "REWIND_T1_AFTER_COPY_PRE",
        (ANY, ANY, ANY),
        "REWIND_T1_AFTER_COPY",
        (KEEP, KEEP, KEEP),
        ("L", "S", "S"),
    )
    builder.add_pattern(
        "REWIND_T1_AFTER_COPY",
        (("1", "|"), ANY, ANY),
        "REWIND_T1_AFTER_COPY",
        (KEEP, KEEP, KEEP),
        ("L", "S", "S"),
    )
    builder.add_pattern(
        "REWIND_T1_AFTER_COPY",
        ("_", ANY, ANY),
        "SCAN_LEFT",
        (KEEP, KEEP, KEEP),
        ("R", "S", "S"),
    )

    # Prepare output: rewind tape 1 to its left edge and tape 3 to the start of the product.
    builder.add_pattern(
        "OUTPUT_REWIND_T1_PRE",
        (ANY, ANY, ANY),
        "OUTPUT_REWIND_T1",
        (KEEP, KEEP, KEEP),
        ("L", "S", "S"),
    )
    builder.add_pattern(
        "OUTPUT_REWIND_T1",
        (("|", "1"), ANY, ANY),
        "OUTPUT_REWIND_T1",
        (KEEP, KEEP, KEEP),
        ("L", "S", "S"),
    )
    builder.add_pattern(
        "OUTPUT_REWIND_T1",
        ("_", ANY, ANY),
        "OUTPUT_REWIND_T3_PRE",
        (KEEP, KEEP, KEEP),
        ("R", "S", "S"),
    )

    builder.add_pattern(
        "OUTPUT_REWIND_T3_PRE",
        (ANY, ANY, ANY),
        "OUTPUT_REWIND_T3",
        (KEEP, KEEP, KEEP),
        ("S", "S", "L"),
    )
    builder.add_pattern(
        "OUTPUT_REWIND_T3",
        (ANY, ANY, "1"),
        "OUTPUT_REWIND_T3",
        (KEEP, KEEP, KEEP),
        ("S", "S", "L"),
    )
    builder.add_pattern(
        "OUTPUT_REWIND_T3",
        (ANY, ANY, "_"),
        "OUTPUT_COPY",
        (KEEP, KEEP, KEEP),
        ("S", "S", "R"),
    )

    builder.add_pattern(
        "OUTPUT_COPY",
        (ANY, ANY, "1"),
        "OUTPUT_COPY",
        ("1", KEEP, KEEP),
        ("R", "S", "R"),
    )
    builder.add_pattern(
        "OUTPUT_COPY",
        (ANY, ANY, "_"),
        "OUTPUT_CLEAR_TAIL",
        (KEEP, KEEP, KEEP),
        ("S", "S", "S"),
    )

    builder.add_pattern(
        "OUTPUT_CLEAR_TAIL",
        (("1", "|", "#"), ANY, ANY),
        "OUTPUT_CLEAR_TAIL",
        ("_", KEEP, KEEP),
        ("R", "S", "S"),
    )
    builder.add_pattern(
        "OUTPUT_CLEAR_TAIL",
        ("_", ANY, ANY),
        "F",
        (KEEP, KEEP, KEEP),
        ("S", "S", "S"),
    )

    return builder.build()


def materialize_part1_question6_machines(output_dir: str | Path) -> list[Path]:
    """Write strict part 1 question 6 machines to disk."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    machine_specs = [
        (
            build_compare_binary_machine(),
            output_path / "compare_binary.tm",
            [
                "General binary integer comparator.",
                "Input: x#y where x and y are binary integers.",
                "Behavior: halt iff x < y, loop forever otherwise.",
                "Leading zeros are ignored during the internal comparison.",
            ],
        ),
        (
            build_search_list_machine(),
            output_path / "search_list.tm",
            [
                "General list membership machine.",
                "Input: x#w1#w2#...#wl with x and all wi in {0,1}*.",
                "Behavior: halt iff x = wi for some i, loop forever otherwise.",
            ],
        ),
        (
            build_unary_multiply_machine(),
            output_path / "unary_multiply.tm",
            [
                "General unary multiplication machine.",
                "Input: 1^n#1^m.",
                "Behavior: leave exactly 1^(n*m) on tape 1 and halt.",
                "This machine uses 3 tapes and the working alphabet {1,#,|,_}.",
            ],
        ),
    ]

    written_paths: list[Path] = []
    for machine, path, comments in machine_specs:
        path.write_text(serialize_machine(machine, comment_lines=comments), encoding="utf-8")
        written_paths.append(path)
    return written_paths
