from io import StringIO
from pathlib import Path
from contextlib import redirect_stdout
import sys

BASE = Path(__file__).resolve().parent
sys.path.append(str(BASE.parent))

from projet import lire_machine, simuler_mot_affichage


def test_affichage():
    machine = lire_machine(BASE / "test.txt")
    sortie = StringIO()

    # On capture l'affichage pour verifier le contenu sans polluer le terminal.
    with redirect_stdout(sortie):
        config, accepte = simuler_mot_affichage("0", machine)

    texte = sortie.getvalue()
    assert accepte is True
    assert "Etat" in texte
    assert "Ruban 1" in texte


if __name__ == "__main__":
    test_affichage()
    print("Q5 ok")
