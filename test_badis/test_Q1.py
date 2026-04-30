from pathlib import Path
import sys

BASE = Path(__file__).resolve().parent
sys.path.append(str(BASE.parent))

from projet import Configuration, Machine_turing


def test_structures():
    machine = Machine_turing({"0", "1"}, {("I", "0"): ("F", "1", "S")}, "I", "F", "_", 1)
    config = Configuration([["0", "_"]], [0], "I")

    assert machine.etat_initial == "I"
    assert machine.etat_acceptant == "F"
    assert machine.nb_rubans == 1
    assert config.rubans == [["0", "_"]]
    assert config.positions == [0]
    assert config.etat == "I"


if __name__ == "__main__":
    test_structures()
    print("Q1 ok")
