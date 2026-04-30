from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))
from projet import *

def test_machine():
    machine = lire_machine("test.txt")
    etat, resultat = simuler_mot("0011", machine)
    print("Etat final :", etat.rubans[0])
    print("Résultat :", resultat)

test_machine()