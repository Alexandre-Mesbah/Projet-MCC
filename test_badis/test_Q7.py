from pathlib import Path
import sys

BASE = Path(__file__).resolve().parent
sys.path.append(str(BASE.parent))

from projet import lire_machine2


def test_lecture_2():
    code_machine = lire_machine2(BASE / "test.txt")

    assert code_machine == "0|0|1|R|0|0|1|0|R|0|0|_|_|S|1"


if __name__ == "__main__":
    test_lecture_2()
    print("Q7 ok")
