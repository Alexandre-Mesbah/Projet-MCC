from pathlib import Path
import sys

BASE = Path(__file__).resolve().parent
sys.path.append(str(BASE.parent))

from projet import machine_universelle


def test_machine_universelle():
    ruban1, ruban2, ruban3, accepte = machine_universelle(
        "0|0|1|>|0|0|1|0|>|0|0|_|_|-|1#0011"
    )

    assert accepte is True
    assert ruban2.endswith("#1")
    assert ruban3 == "1 1 0 0 _*"


if __name__ == "__main__":
    test_machine_universelle()
    print("Q9 ok")
