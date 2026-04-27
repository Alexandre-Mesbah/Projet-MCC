PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,$(shell command -v python3.14 || command -v python3.13 || command -v python3.12 || command -v python3.11 || command -v python3))
PYTEST ?= $(PYTHON) -m pytest
PROJECT_PYTHON = PYTHONPATH=src $(PYTHON)
CLI = $(PROJECT_PYTHON) -m tm_project.cli

.PHONY: \
	check-python test check clean \
	q1 q2 q3 q4 q5 q6 q7 q8 q9 q10 q11 \
	test-q1 test-q2 test-q3 test-q4 test-q5 test-q6 test-part1 test-part2 \
	generer-machines-q6 demo-run

check-python:
	@$(PYTHON) -c "import sys; sys.exit('Python 3.11+ requis' if sys.version_info < (3, 11) else 0)"

test: check-python
	@$(PYTEST) -q

check: check-python
	@$(PYTHON) -m compileall -q src tests
	@$(PYTEST) -q

generer-machines-q6: check-python
	@$(PROJECT_PYTHON) -c "from tm_project.machines_q6 import materialize_part1_question6_machines; materialize_part1_question6_machines('machines')"

q1: check-python
	@$(CLI) q1

q2: check-python
	@$(CLI) q2

q3: check-python
	@$(CLI) q3

q4: check-python
	@$(CLI) q4

q5: check-python
	@$(CLI) q5

q6: check-python generer-machines-q6
	@$(CLI) q6

q7: check-python
	@$(CLI) part2-report --machine machines/part2_flip_bits.tm2 --input 0101 --section text

q8: check-python
	@$(CLI) part2-report --machine machines/part2_flip_bits.tm2 --input 0101 --section binary

q9: check-python
	@$(CLI) strict-universal --machine machines/part2_flip_bits.tm2 --input 0101

q10: check-python
	@$(CLI) strict-bounded-universal --machine machines/part2_flip_bits.tm2 --input 0101 --steps 5

q11: check-python
	@$(CLI) q11

test-q1: check-python
	@PYTHONPATH=src $(PYTEST) -q tests/test_question1.py

test-q2: check-python
	@PYTHONPATH=src $(PYTEST) -q tests/test_question2.py

test-q3: check-python
	@PYTHONPATH=src $(PYTEST) -q tests/test_question3.py

test-q4: check-python
	@PYTHONPATH=src $(PYTEST) -q tests/test_question4.py

test-q5: check-python
	@PYTHONPATH=src $(PYTEST) -q tests/test_question5.py

test-q6: check-python generer-machines-q6
	@PYTHONPATH=src $(PYTEST) -q tests/test_question6.py

test-part1: test-q1 test-q2 test-q3 test-q4 test-q5 test-q6

test-part2: check-python
	@PYTHONPATH=src $(PYTEST) -q tests/test_part2_strict.py

demo-run: check-python
	@$(CLI) run --machine machines/demo_flip_bits.tm --input 0101

clean:
	@find . -type d -name '__pycache__' -prune -exec rm -rf {} +
	@find . -type d -name '.pytest_cache' -prune -exec rm -rf {} +
	@find . -type f -name '*.pyc' -delete
