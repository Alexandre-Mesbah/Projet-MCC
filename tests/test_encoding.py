"""Tests des codages strictes (Q7, Q8)."""

from __future__ import annotations

from tm_project.codage import binary_to_int, encode_text_to_binary


def test_encode_text_to_binary_uses_ascii_bits() -> None:
    assert encode_text_to_binary("A") == "01000001"


def test_binary_to_int_converts_bits_to_integer() -> None:
    assert binary_to_int("101") == 5
