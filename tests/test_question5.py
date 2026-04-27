"""Strict tests for part 1, question 5."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

from tm_project.modele import ExecutionStatus
from tm_project.parseur_tm import parse_machine_file
from tm_project.simulateur import run_stream

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MACHINES_DIR = PROJECT_ROOT / "machines"


def test_question5_run_stream_yields_configurations_progressively() -> None:
    machine = parse_machine_file(MACHINES_DIR / "strict_flip_bits.tm")
    history = list(run_stream(machine, "01"))

    assert [configuration.step_count for configuration in history] == [0, 1, 2, 3]
    assert history[-1].status == ExecutionStatus.ACCEPTED


def test_question5_cli_streams_multiple_configurations() -> None:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(PROJECT_ROOT / "src")
    result = subprocess.run(
        [sys.executable, "-m", "tm_project.cli", "q5", "--input", "01"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    assert result.returncode == 0
    assert result.stdout.count("Step ") >= 4
    assert "Status: accepted" in result.stdout
