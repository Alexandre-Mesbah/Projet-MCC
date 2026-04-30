from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))
from projet import *

def test_Q8():
    code_binaire = lire_machine_binaire("test.txt")
    print(code_binaire)
    print(convertie_binaire(code_binaire))

test_Q8()