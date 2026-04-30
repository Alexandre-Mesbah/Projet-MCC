from pathlib import Path
import sys

BASE = Path(__file__).resolve().parent
sys.path.append(str(BASE.parent))

from projet import configuration_initiale, lire_machine, un_pas


def test_un_pas():
    machine = lire_machine(BASE / "test.txt")
    config = configuration_initiale("0", machine)
    nouvelle_config = un_pas(machine, config)

    assert nouvelle_config is config
    assert config.etat == "q0"
    assert config.rubans[0] == ["1", "_"]
    assert config.positions == [1]


if __name__ == "__main__":
    test_un_pas()
    print("Q3 ok")
