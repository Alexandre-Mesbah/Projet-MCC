from pathlib import Path
import sys

BASE = Path(__file__).resolve().parent
sys.path.append(str(BASE.parent))

from projet import lire_machine, simuler_mot


def test_machine():
    machine = lire_machine(BASE / "test.txt")
    etat, resultat = simuler_mot("0011", machine)

    assert resultat is True
    assert etat.etat == "qf"
    assert etat.rubans[0] == ["1", "1", "0", "0", "_"]


if __name__ == "__main__":
    test_machine()
    print("Q4 ok")
