"""Package du projet Machine de Turing.

Sommaire des modules (un fichier ↔ un sujet de l'énoncé) :

- ``modele``        : Q1 — classes ``TuringMachine`` et ``Configuration``
- ``ruban``         : structure ``Tape``, support de ``modele``
- ``parseur_tm``    : Q2 — sous-format documenté ``.tm``
- ``parseur_tm2``   : Q2/partie 2 — format brut ``.tm2`` du site
- ``simulateur``    : Q3, Q4 — ``step``, ``run``, ``run_stream``
- ``affichage``     : Q5 — ``format_configuration*``
- ``machines_q6``   : Q6 — machines réponses (comparaison, recherche, mult.)
- ``codage``        : Q7, Q8 — codages texte/binaire/entier de ⟨M⟩
- ``universelle``   : Q9, Q10 — machine universelle 3 rubans et variante 4 rubans
- ``decidabilite``  : Q11 — preuves L1, L2, L3
- ``cli``           : interface en ligne de commande unique
"""

from .affichage import format_configuration, format_configuration_detailed
from .codage import (
    binary_to_int,
    encode_input_word_strict,
    encode_machine_strict_binary,
    encode_machine_strict_integer,
    encode_machine_strict_text,
    encode_text_to_binary,
    encode_tm2file_text_to_binary,
)
from .modele import Configuration, ExecutionStatus, Transition, TuringMachine
from .parseur_tm import MachineParseError, initial_configuration, parse_machine_file
from .parseur_tm2 import parse_tm2file_file, parse_tm2file_text
from .ruban import Tape
from .simulateur import MachineRuntimeError, run, run_stream, run_verbose, step
from .universelle import (
    StrictBoundedUniversalSimulationResult,
    StrictUniversalSimulationResult,
    strict_bounded_universal_simulate_word,
    strict_universal_simulate_word,
)

__all__ = [
    "Configuration",
    "ExecutionStatus",
    "MachineParseError",
    "MachineRuntimeError",
    "StrictBoundedUniversalSimulationResult",
    "StrictUniversalSimulationResult",
    "Tape",
    "Transition",
    "TuringMachine",
    "binary_to_int",
    "encode_input_word_strict",
    "encode_machine_strict_binary",
    "encode_machine_strict_integer",
    "encode_machine_strict_text",
    "encode_text_to_binary",
    "encode_tm2file_text_to_binary",
    "format_configuration",
    "format_configuration_detailed",
    "initial_configuration",
    "parse_machine_file",
    "parse_tm2file_file",
    "parse_tm2file_text",
    "run",
    "run_stream",
    "run_verbose",
    "step",
    "strict_bounded_universal_simulate_word",
    "strict_universal_simulate_word",
]
