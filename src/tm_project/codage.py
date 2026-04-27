"""Codage strict d'une machine de Turing mono-ruban (Q7 et Q8).

Format texte produit (Q7) :

```text
blank|initial|accept|reject|current|read|next|write|move|...
```

- séparateur unique `|` ;
- état initial codé `0`, état acceptant `1`, état rejetant `10` ;
- autres états : mots binaires distincts dans l'ordre `11`, `100`, `101`, ... ;
- symbole blanc codé `0`, autres symboles : mots binaires distincts ;
- directions : `L -> <`, `S -> -`, `R -> >`.

Format binaire produit (Q8) : ASCII 8 bits du format texte.
Format entier produit (Q8) : entier dont l'écriture binaire est ce binaire.
"""

from __future__ import annotations

from dataclasses import dataclass

from .modele import Move, Transition, TuringMachine
from .parseur_tm2 import parse_tm2file_text

TEXT_MOVE_MAP: dict[Move, str] = {"L": "<", "S": "-", "R": ">"}
REVERSE_TEXT_MOVE_MAP: dict[str, Move] = {value: key for key, value in TEXT_MOVE_MAP.items()}


@dataclass(frozen=True, slots=True)
class StrictEncodedTransition:
    """Une transition dans le codage strict de la partie 2."""

    current_state: str
    read_symbol: str
    next_state: str
    write_symbol: str
    move: str


@dataclass(frozen=True, slots=True)
class StrictEncodedMachine:
    """Machine partie 2 décodée, encore exprimée en symboles binaires."""

    blank_symbol: str
    initial_state: str
    accept_state: str
    reject_state: str
    transitions: tuple[StrictEncodedTransition, ...]

    def get_transition(self, current_state: str, read_symbol: str) -> StrictEncodedTransition | None:
        for transition in self.transitions:
            if transition.current_state == current_state and transition.read_symbol == read_symbol:
                return transition
        return None


def build_strict_state_renaming(machine: TuringMachine) -> dict[str, str]:
    """Renomme les états en mots binaires : initial=0, accept=1, reject=10, etc."""
    if machine.reject_state is None:
        raise ValueError("Le codage strict requiert un état de rejet explicite.")
    mapping: dict[str, str] = {
        machine.initial_state: "0",
        machine.final_state: "1",
        machine.reject_state: "10",
    }
    next_index = 3
    for state in sorted(machine.states):
        if state in mapping:
            continue
        mapping[state] = format(next_index, "b")
        next_index += 1
    return mapping


def build_strict_symbol_renaming(machine: TuringMachine) -> dict[str, str]:
    """Renomme les symboles de travail en mots binaires : blanc=0, autres=1,10,..."""
    symbols: set[str] = {machine.blank_symbol}
    for transition in machine.transitions.values():
        symbols.update(transition.symbols_read)
        symbols.update(transition.symbols_write)

    mapping = {machine.blank_symbol: "0"}
    next_index = 1
    for symbol in sorted(symbols):
        if symbol == machine.blank_symbol:
            continue
        mapping[symbol] = format(next_index, "b")
        next_index += 1
    return mapping


def encode_machine_strict_text(machine: TuringMachine) -> str:
    """Q7 : code une machine `tm2file` mono-ruban en texte strict."""
    _validate_strict_encoding_machine(machine)
    state_mapping = build_strict_state_renaming(machine)
    symbol_mapping = build_strict_symbol_renaming(machine)
    assert machine.reject_state is not None

    fields = [
        symbol_mapping[machine.blank_symbol],
        state_mapping[machine.initial_state],
        state_mapping[machine.final_state],
        state_mapping[machine.reject_state],
    ]
    for transition in _sorted_strict_transitions(machine, state_mapping, symbol_mapping):
        fields.extend(
            [
                state_mapping[transition.current_state],
                symbol_mapping[transition.symbols_read[0]],
                state_mapping[transition.next_state],
                symbol_mapping[transition.symbols_write[0]],
                TEXT_MOVE_MAP[transition.moves[0]],
            ]
        )
    return "|".join(fields)


def decode_machine_strict_text(encoded_text: str) -> StrictEncodedMachine:
    """Décode le codage texte strict de la partie 2."""
    if not isinstance(encoded_text, str):
        raise ValueError("encoded_text doit être une chaîne.")
    if encoded_text == "":
        raise ValueError("encoded_text ne doit pas être vide.")
    fields = encoded_text.split("|")
    if len(fields) < 4 or (len(fields) - 4) % 5 != 0:
        raise ValueError("Le codage strict doit avoir 4 champs d'en-tête puis des 5-uplets.")
    if any(field == "" for field in fields):
        raise ValueError("Le codage strict ne doit pas contenir de champ vide.")

    blank_symbol, initial_state, accept_state, reject_state = fields[:4]
    for field in (blank_symbol, initial_state, accept_state, reject_state):
        _validate_binary_word(field, "Champs d'en-tête stricts")

    transitions: list[StrictEncodedTransition] = []
    seen_keys: set[tuple[str, str]] = set()
    for index in range(4, len(fields), 5):
        current_state, read_symbol, next_state, write_symbol, raw_move = fields[index : index + 5]
        for field in (current_state, read_symbol, next_state, write_symbol):
            _validate_binary_word(field, "Champs de transition stricts")
        if raw_move not in REVERSE_TEXT_MOVE_MAP:
            raise ValueError(f"Direction codée inconnue {raw_move!r}.")
        key = (current_state, read_symbol)
        if key in seen_keys:
            raise ValueError(f"Transition codée stricte en double pour {key!r}.")
        seen_keys.add(key)
        transitions.append(
            StrictEncodedTransition(
                current_state=current_state,
                read_symbol=read_symbol,
                next_state=next_state,
                write_symbol=write_symbol,
                move=raw_move,
            )
        )

    return StrictEncodedMachine(
        blank_symbol=blank_symbol,
        initial_state=initial_state,
        accept_state=accept_state,
        reject_state=reject_state,
        transitions=tuple(transitions),
    )


def encode_tm2file_text_to_binary(source: str) -> str:
    """Parse un texte `tm2file` et renvoie son codage binaire strict."""
    return encode_text_to_binary(encode_machine_strict_text(parse_tm2file_text(source)))


def encode_machine_strict_binary(machine: TuringMachine) -> str:
    """Q8 : code la machine en texte strict puis en bits ASCII."""
    return encode_text_to_binary(encode_machine_strict_text(machine))


def encode_machine_strict_integer(machine: TuringMachine) -> int:
    """Q8 : interprète le codage binaire strict comme un entier."""
    return binary_to_int(encode_machine_strict_binary(machine))


def encode_input_word_strict(machine: TuringMachine, input_word: str) -> str:
    """Code un mot d'entrée comme codes binaires de symboles séparés par `|`."""
    if not isinstance(input_word, str):
        raise ValueError("input_word doit être une chaîne.")
    symbol_mapping = build_strict_symbol_renaming(machine)
    unknown = sorted({symbol for symbol in input_word if symbol not in symbol_mapping})
    if unknown:
        raise ValueError(f"Symbole(s) hors alphabet codé : {unknown!r}.")
    return "|".join(symbol_mapping[symbol] for symbol in input_word)


def encode_text_to_binary(encoded_text: str) -> str:
    """Encode une chaîne texte en bits ASCII 8 bits."""
    if not isinstance(encoded_text, str):
        raise ValueError("encoded_text doit être une chaîne.")
    if encoded_text == "":
        raise ValueError("encoded_text ne doit pas être vide.")
    try:
        encoded_bytes = encoded_text.encode("ascii")
    except UnicodeEncodeError as error:
        raise ValueError("encoded_text doit être ASCII.") from error
    return "".join(f"{byte:08b}" for byte in encoded_bytes)


def binary_to_int(binary_string: str) -> int:
    """Convertit une chaîne binaire en entier non négatif."""
    if not isinstance(binary_string, str):
        raise ValueError("binary_string doit être une chaîne.")
    if binary_string == "":
        raise ValueError("binary_string ne doit pas être vide.")
    if any(bit not in {"0", "1"} for bit in binary_string):
        raise ValueError("binary_string ne doit contenir que 0 et 1.")
    return int(binary_string, 2)


def _validate_strict_encoding_machine(machine: TuringMachine) -> None:
    """Vérifie qu'une machine est compatible avec le codage strict."""
    if machine.num_tapes != 1:
        raise ValueError("Le codage strict n'est défini que pour les machines mono-ruban.")
    if machine.initial_state == machine.final_state:
        raise ValueError("Le codage strict requiert des états initial et acceptant distincts.")
    if machine.reject_state is None:
        raise ValueError("Le codage strict requiert un état de rejet explicite.")
    if machine.reject_state in {machine.initial_state, machine.final_state}:
        raise ValueError("Les états initial, acceptant et rejetant doivent être distincts.")


def _sorted_strict_transitions(
    machine: TuringMachine,
    state_mapping: dict[str, str],
    symbol_mapping: dict[str, str],
) -> list[Transition]:
    """Renvoie les transitions dans un ordre déterministe."""
    return sorted(
        machine.transitions.values(),
        key=lambda transition: (
            int(state_mapping[transition.current_state], 2),
            int(symbol_mapping[transition.symbols_read[0]], 2),
            int(state_mapping[transition.next_state], 2),
            int(symbol_mapping[transition.symbols_write[0]], 2),
            TEXT_MOVE_MAP[transition.moves[0]],
        ),
    )


def _validate_binary_word(value: str, label: str) -> None:
    """Valide qu'une chaîne est un mot binaire non vide."""
    if value == "" or any(bit not in {"0", "1"} for bit in value):
        raise ValueError(f"{label} doit être un mot non vide sur {{0,1}} : {value!r}.")
