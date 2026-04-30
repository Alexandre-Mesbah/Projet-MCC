from pathlib import Path
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
sys.path.append(str(ROOT))

from projet import lire_machine, simuler_mot


def contenu_sans_blancs(config):
    return "".join(config.rubans[0]).strip("_")


def test_comparaison_binaire():
    machine = lire_machine(BASE / "comparaison_x_inf_y.txt")

    config, accepte = simuler_mot("10#11", machine, max_etapes=1000)
    assert accepte is True

    config, accepte = simuler_mot("11#10", machine, max_etapes=200)
    assert accepte is False


def test_recherche_liste():
    machine = lire_machine(BASE / "recherche_dans_liste.txt")

    config, accepte = simuler_mot("10#0#10#11", machine, max_etapes=1000)
    assert accepte is True

    config, accepte = simuler_mot("10#0#1#11", machine, max_etapes=200)
    assert accepte is False


def test_multiplication_unaire():
    machine = lire_machine(ROOT / "machines" / "unary_multiply.tm")

    config, accepte = simuler_mot("11#111", machine, max_etapes=5000)
    assert accepte is True
    assert contenu_sans_blancs(config) == "111111"


if __name__ == "__main__":
    test_comparaison_binaire()
    test_recherche_liste()
    test_multiplication_unaire()
    print("Q6 ok")
