"""Smoke tests pour la CLI unifiée."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MACHINES_DIR = PROJECT_ROOT / "machines"


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(PROJECT_ROOT / "src")
    return subprocess.run(
        [sys.executable, "-m", "tm_project.cli", *args],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def test_cli_run_command_succeeds() -> None:
    result = _run_cli(
        "run",
        "--machine",
        str(MACHINES_DIR / "demo_flip_bits.tm"),
        "--input",
        "0101",
    )

    assert result.returncode == 0
    assert "Status: accepted" in result.stdout


def test_cli_part2_report_text_section() -> None:
    result = _run_cli(
        "part2-report",
        "--machine",
        str(MACHINES_DIR / "part2_flip_bits.tm2"),
        "--input",
        "0101",
        "--section",
        "text",
    )

    assert result.returncode == 0
    assert "Strict Text:" in result.stdout
    assert "Strict Binary:" not in result.stdout


def test_cli_strict_bounded_universal_reports_timeout() -> None:
    result = _run_cli(
        "strict-bounded-universal",
        "--machine",
        str(MACHINES_DIR / "part2_flip_bits.tm2"),
        "--input",
        "0101",
        "--steps",
        "0",
    )

    assert result.returncode == 0
    assert "timeout" in result.stdout.lower()
