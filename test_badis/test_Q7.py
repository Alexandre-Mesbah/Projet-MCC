from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))
from projet import *

def test_lecture_2():
    machine = lire_machine2("test.txt")
    print(machine)

test_lecture_2()