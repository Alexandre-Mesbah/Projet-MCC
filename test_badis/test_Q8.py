from pathlib import Path
import sys

BASE = Path(__file__).resolve().parent
sys.path.append(str(BASE.parent))

from projet import coder_binaire, convertie_binaire, lire_machine2, lire_machine_binaire


def test_Q8():
    code_machine = lire_machine2(BASE / "test.txt")
    code_binaire = lire_machine_binaire(BASE / "test.txt")

    assert code_binaire != ""
    assert code_binaire == coder_binaire(code_machine)
    assert convertie_binaire(code_binaire) > 0


if __name__ == "__main__":
    test_Q8()
    print("Q8 ok")
