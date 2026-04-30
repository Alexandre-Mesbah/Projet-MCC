from pathlib import Path
import sys

BASE = Path(__file__).resolve().parent
sys.path.append(str(BASE.parent))

from projet import machine_universelle_n_etapes


def test_machine_n_etapes_true():
    ruban1, ruban2, ruban3, ruban4, accepte = machine_universelle_n_etapes(
        "0|0|1|>|0|0|1|0|>|0|0|_|_|-|1#0011#5"
    )

    assert accepte is True
    assert ruban2.endswith("#1")
    assert ruban3 == "1 1 0 0 _*"
    assert ruban4 == "_"


def test_machine_n_etapes_false():
    ruban1, ruban2, ruban3, ruban4, accepte = machine_universelle_n_etapes(
        "0|0|1|>|0|0|1|0|>|0|0|_|_|-|1#0011#3"
    )

    assert accepte is False
    assert ruban2.endswith("#0")
    assert ruban3 == "1 1 0 1* _"
    assert ruban4 == "_"


if __name__ == "__main__":
    test_machine_n_etapes_true()
    test_machine_n_etapes_false()
    print("Q10 ok")
