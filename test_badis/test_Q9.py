from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))
from projet import *

def test_machine_universelle():
    ruban1, ruban2, ruban3, accepte = machine_universelle(
        "0|0|1|>|0|0|1|0|>|0|0|_|_|-|1#0011",
        affichage=True
    )

    print("Accepte :", accepte)
    print("Ruban 3 final :", ruban3)

test_machine_universelle()