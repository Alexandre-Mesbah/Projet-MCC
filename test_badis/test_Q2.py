from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))
from projet import *

def test_lecture_fichier():
    machine = lire_machine("test.txt")
    print("alphabet :", machine.alphabet)
    print("états final:", machine.etat_acceptant)
    print("nombre de rubans :", machine.nb_rubans)
    print("transition machine lue :", machine.transitions)

test_lecture_fichier()