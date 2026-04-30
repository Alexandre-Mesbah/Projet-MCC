from pathlib import Path
import sys

BASE = Path(__file__).resolve().parent
sys.path.append(str(BASE.parent))

from projet import lire_machine, configuration_initiale


def test_lecture_fichier():
    # On utilise un chemin absolu pour que le test marche depuis n'importe quel dossier.
    machine = lire_machine(BASE / "test.txt")
    config = configuration_initiale("0011", machine)

    assert machine.etat_initial == "q0"
    assert machine.etat_acceptant == "qf"
    assert machine.nb_rubans == 1
    assert len(machine.transitions) == 3
    assert config.rubans[0] == ["0", "0", "1", "1", "_"]
    assert config.positions == [0]


if __name__ == "__main__":
    test_lecture_fichier()
    print("Q2 ok")
