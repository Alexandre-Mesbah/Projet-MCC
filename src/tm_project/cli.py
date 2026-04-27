"""Interface en ligne de commande unifiée du projet (questions Q1 à Q11)."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from .affichage import format_configuration, format_configuration_detailed
from .codage import (
    encode_input_word_strict,
    encode_machine_strict_binary,
    encode_machine_strict_integer,
    encode_machine_strict_text,
)
from .decidabilite import get_decidability_notes
from .machines_q6 import materialize_part1_question6_machines
from .modele import Configuration, Transition, TuringMachine
from .parseur_tm import MachineParseError, initial_configuration, parse_machine_file
from .parseur_tm2 import parse_tm2file_file
from .ruban import Tape
from .simulateur import MachineRuntimeError, run, run_stream, step
from .universelle import (
    strict_bounded_universal_simulate_word,
    strict_universal_simulate_word,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MACHINES_DIR = PROJECT_ROOT / "machines"


def build_parser() -> argparse.ArgumentParser:
    """Construit l'analyseur d'arguments de la CLI unifiée."""
    parser = argparse.ArgumentParser(prog="tm_project.cli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- Partie 1 : Q1 à Q6 ---------------------------------------------------
    q1_parser = subparsers.add_parser("q1", help="Q1 : montrer une instance de MT et de Configuration.")
    q1_parser.set_defaults(handler=_handle_q1)

    for command_name, default_input in (("q2", "0101"), ("q3", "0"), ("q4", "0101"), ("q5", "0101")):
        question_parser = subparsers.add_parser(
            command_name,
            help=f"{command_name.upper()} : démonstration partie 1.",
        )
        question_parser.add_argument(
            "--machine",
            type=Path,
            default=MACHINES_DIR / "strict_flip_bits.tm",
            help="Fichier .tm utilisé pour la démonstration.",
        )
        question_parser.add_argument("--input", default=default_input, help="Mot d'entrée.")
        question_parser.add_argument("--max-steps", type=int, default=None)
        question_parser.add_argument("--radius", type=int, default=6)

    subparsers.choices["q2"].set_defaults(handler=_handle_q2)
    subparsers.choices["q3"].set_defaults(handler=_handle_q3)
    subparsers.choices["q4"].set_defaults(handler=_handle_q4)
    subparsers.choices["q5"].set_defaults(handler=_handle_q5)

    q6_parser = subparsers.add_parser("q6", help="Q6 : exécuter les machines réponses.")
    q6_parser.add_argument("--max-steps", type=int, default=5000)
    q6_parser.set_defaults(handler=_handle_q6)

    # --- Partie 2 : Q7 à Q11 --------------------------------------------------
    part2_parser = subparsers.add_parser(
        "part2-report",
        help="Affiche les codages texte/binaire/entier d'une machine tm2file.",
    )
    part2_parser.add_argument("--machine", required=True, type=Path, help="Chemin d'une machine tm2file.")
    part2_parser.add_argument("--input", default="", help="Mot d'entrée pour les Q9/Q10.")
    part2_parser.add_argument("--steps", type=int, default=5, help="Borne d'étapes pour Q10.")
    part2_parser.add_argument(
        "--section",
        choices=("all", "text", "binary"),
        default="all",
        help="Sortie : 'text' pour Q7, 'binary' pour Q8, 'all' pour les deux.",
    )
    part2_parser.set_defaults(handler=_handle_part2_report)

    strict_universal_parser = subparsers.add_parser(
        "strict-universal",
        help="Q9 : machine universelle stricte 3 rubans sur une machine tm2file.",
    )
    strict_universal_parser.add_argument("--machine", required=True, type=Path)
    strict_universal_parser.add_argument("--input", required=True)
    strict_universal_parser.set_defaults(handler=_handle_strict_universal)

    strict_bounded_parser = subparsers.add_parser(
        "strict-bounded-universal",
        help="Q10 : machine universelle stricte 4 rubans avec compteur n.",
    )
    strict_bounded_parser.add_argument("--machine", required=True, type=Path)
    strict_bounded_parser.add_argument("--input", required=True)
    strict_bounded_parser.add_argument("--steps", required=True, type=int)
    strict_bounded_parser.set_defaults(handler=_handle_strict_bounded_universal)

    q11_parser = subparsers.add_parser("q11", help="Q11 : afficher les preuves de décidabilité.")
    q11_parser.set_defaults(handler=_handle_q11)

    # --- Commande générique ---------------------------------------------------
    run_parser = subparsers.add_parser("run", help="Exécuter une machine .tm sur un mot.")
    run_parser.add_argument("--machine", required=True, type=Path)
    run_parser.add_argument("--input", required=True)
    run_parser.add_argument("--verbose", action="store_true")
    run_parser.add_argument("--max-steps", type=int, default=None)
    run_parser.add_argument("--radius", type=int, default=10)
    run_parser.set_defaults(handler=_handle_run)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Point d'entrée `python -m tm_project.cli`."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except (MachineParseError, MachineRuntimeError, ValueError) as error:
        parser.exit(status=2, message=f"error: {error}\n")


# --- Partie 1 ----------------------------------------------------------------


def _handle_q1(args: argparse.Namespace) -> int:
    """Q1 : montrer concrètement les classes MT et Configuration."""
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

    print("Machine:")
    print(machine)
    print()
    print("Configuration:")
    print(format_configuration_detailed(configuration, radius=2))
    return 0


def _handle_q2(args: argparse.Namespace) -> int:
    """Q2 : parse un fichier machine et affiche la configuration initiale."""
    machine = parse_machine_file(args.machine)
    configuration = initial_configuration(machine, args.input)
    print(format_configuration_detailed(configuration, radius=args.radius))
    return 0


def _handle_q3(args: argparse.Namespace) -> int:
    """Q3 : exécute un seul pas de calcul."""
    machine = parse_machine_file(args.machine)
    configuration = initial_configuration(machine, args.input)
    next_configuration = step(machine, configuration)
    print(format_configuration_detailed(next_configuration, radius=args.radius))
    return 0


def _handle_q4(args: argparse.Namespace) -> int:
    """Q4 : exécute la machine jusqu'à l'état final ou la borne."""
    machine = parse_machine_file(args.machine)
    final_configuration = run(machine, args.input, max_steps=args.max_steps)
    print(format_configuration_detailed(final_configuration, radius=args.radius))
    return 0


def _handle_q5(args: argparse.Namespace) -> int:
    """Q5 : affiche les configurations au fur et à mesure."""
    machine = parse_machine_file(args.machine)
    first = True
    for configuration in run_stream(machine, args.input, max_steps=args.max_steps):
        if not first:
            print()
        print(format_configuration(configuration, radius=args.radius))
        first = False
    return 0


def _handle_q6(args: argparse.Namespace) -> int:
    """Q6 : régénère et exécute les machines réponses."""
    written_paths = materialize_part1_question6_machines(MACHINES_DIR)
    print("Machines générées :")
    for path in written_paths:
        print(path)
    print()

    compare_machine = parse_machine_file(MACHINES_DIR / "compare_binary.tm")
    compare_accept = run(compare_machine, "10#11", max_steps=args.max_steps)
    compare_loop = run(compare_machine, "11#10", max_steps=args.max_steps)
    print("Comparaison :")
    print(f"10#11 -> {compare_accept.status.value}")
    print(f"11#10 -> {compare_loop.status.value}")
    print()

    search_machine = parse_machine_file(MACHINES_DIR / "search_list.tm")
    search_accept = run(search_machine, "10#0#10#11", max_steps=args.max_steps)
    search_loop = run(search_machine, "10#0#1#11", max_steps=args.max_steps)
    print("Recherche :")
    print(f"10#0#10#11 -> {search_accept.status.value}")
    print(f"10#0#1#11 -> {search_loop.status.value}")
    print()

    multiply_machine = parse_machine_file(MACHINES_DIR / "unary_multiply.tm")
    multiply_result = run(multiply_machine, "11#111", max_steps=args.max_steps)
    print("Multiplication unaire :")
    print(f"11#111 -> {multiply_result.tapes[0].normalized_content()}")
    return 0


# --- Partie 2 ----------------------------------------------------------------


def _handle_part2_report(args: argparse.Namespace) -> int:
    """Q7/Q8 : affiche les codages texte, binaire et entier."""
    machine = parse_tm2file_file(args.machine)
    text_encoding = encode_machine_strict_text(machine)
    encoded_input = encode_input_word_strict(machine, args.input)
    encoded_steps = _encode_non_negative_int(args.steps)
    section = getattr(args, "section", "all")

    if section in ("all", "text"):
        print(f"Strict Text: {text_encoding}")

    if section in ("all", "binary"):
        binary_encoding = encode_machine_strict_binary(machine)
        integer_encoding = encode_machine_strict_integer(machine)
        print(f"Strict Binary: {binary_encoding}")
        print(f"Strict Integer: {integer_encoding}")

    if section == "all":
        print(f"Q9 input <M>#x: {text_encoding}#{encoded_input}")
        print(f"Q10 input <M>#x#n: {text_encoding}#{encoded_input}#{encoded_steps}")
    return 0


def _handle_strict_universal(args: argparse.Namespace) -> int:
    """Q9 : simulation universelle stricte 3 rubans."""
    machine = parse_tm2file_file(args.machine)
    encoded_machine = encode_machine_strict_text(machine)
    encoded_input = encode_input_word_strict(machine, args.input)
    word = f"{encoded_machine}#{encoded_input}"
    result = strict_universal_simulate_word(word)

    print("Simulation universelle stricte (3 rubans)")
    print(f"Entrée <M>#x : {word}")
    print(f"Statut : {result.status.value}")
    print(f"Étapes : {result.step_count}")
    print(f"Ruban 1 (machine)  : {result.machine_description_tape.normalized_content()}")
    print(f"Ruban 2 (simulé)   : {result.simulated_tape.normalized_content()}")
    print(f"Ruban 3 (travail)  : {result.work_tape.normalized_content()}")
    return 0


def _handle_strict_bounded_universal(args: argparse.Namespace) -> int:
    """Q10 : simulation universelle stricte bornée 4 rubans."""
    machine = parse_tm2file_file(args.machine)
    encoded_machine = encode_machine_strict_text(machine)
    encoded_input = encode_input_word_strict(machine, args.input)
    encoded_steps = _encode_non_negative_int(args.steps)
    word = f"{encoded_machine}#{encoded_input}#{encoded_steps}"
    result = strict_bounded_universal_simulate_word(word)

    print("Simulation universelle stricte bornée (4 rubans)")
    print(f"Entrée <M>#x#n : {word}")
    print(f"Statut : {result.status.value}")
    print(f"Étapes : {result.step_count}")
    print(f"Ruban 1 (machine)  : {result.machine_description_tape.normalized_content()}")
    print(f"Ruban 2 (simulé)   : {result.simulated_tape.normalized_content()}")
    print(f"Ruban 3 (travail)  : {result.work_tape.normalized_content()}")
    print(f"Ruban 4 (compteur) : {result.counter_tape.normalized_content()}")
    return 0


def _handle_q11(args: argparse.Namespace) -> int:
    """Q11 : affiche les preuves de décidabilité."""
    print(get_decidability_notes())
    return 0


# --- Commande générique -------------------------------------------------------


def _handle_run(args: argparse.Namespace) -> int:
    """Exécute une machine .tm sur un mot d'entrée."""
    machine = parse_machine_file(args.machine)
    if args.verbose:
        first = True
        for config in run_stream(machine, args.input, max_steps=args.max_steps):
            if not first:
                print()
            print(format_configuration(config, radius=args.radius))
            first = False
        return 0

    final_configuration = run(machine, args.input, max_steps=args.max_steps)
    print(format_configuration_detailed(final_configuration, radius=args.radius))
    return 0


def _encode_non_negative_int(value: int) -> str:
    """Encode un entier non négatif en mot binaire."""
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError("steps doit être un entier.")
    if value < 0:
        raise ValueError("steps doit être positif ou nul.")
    return format(value, "b")


if __name__ == "__main__":
    raise SystemExit(main())
