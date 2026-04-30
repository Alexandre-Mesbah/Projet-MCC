from pathlib import Path
import sys

BASE = Path(__file__).resolve().parent
sys.path.append(str(BASE.parent))

from projet import preuves_q11


def test_preuves_q11():
    texte = preuves_q11()

    assert "L1" in texte
    assert "L2" in texte
    assert "L3" in texte
    assert "decidable" in texte
    assert "indecidable" in texte


if __name__ == "__main__":
    test_preuves_q11()
    print("Q11 ok")
