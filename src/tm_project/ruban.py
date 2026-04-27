"""Sparse infinite tape implementation for Turing machines."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Tape:
    """Infinite tape backed by a sparse dictionary of non-blank cells."""

    blank_symbol: str = "_"
    _cells: dict[int, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Ensure the blank symbol is usable."""
        self._validate_blank_symbol(self.blank_symbol)

        raw_cells = dict(self._cells)
        self._cells.clear()
        for position, symbol in raw_cells.items():
            self.write(position, symbol)

    @classmethod
    def from_string(cls, content: str, blank_symbol: str = "_") -> Tape:
        """Create a tape whose index 0 starts with the given content."""
        if not isinstance(content, str):
            raise TypeError("Tape content must be a string.")
        tape = cls(blank_symbol=blank_symbol)
        for position, symbol in enumerate(content):
            tape.write(position, symbol)
        return tape

    def clone(self) -> Tape:
        """Return an independent copy of the tape."""
        return Tape(blank_symbol=self.blank_symbol, _cells=dict(self._cells))

    def read(self, position: int) -> str:
        """Read the symbol at the given position."""
        self._validate_position(position)
        return self._cells.get(position, self.blank_symbol)

    def write(self, position: int, symbol: str) -> None:
        """Write a symbol at the given position."""
        self._validate_position(position)
        self._validate_symbol(symbol)
        if symbol == self.blank_symbol:
            self._cells.pop(position, None)
            return
        self._cells[position] = symbol

    def get_view(self, center: int, radius: int) -> list[tuple[int, str]]:
        """Return a local window around a head position."""
        self._validate_position(center)
        self._validate_radius(radius)
        if radius < 0:
            raise ValueError("radius must be non-negative.")
        return [
            (position, self.read(position))
            for position in range(center - radius, center + radius + 1)
        ]

    def render_segment(self, start: int, end: int) -> str:
        """Render an inclusive tape segment as a compact string."""
        self._validate_position(start)
        self._validate_position(end)
        if end < start:
            raise ValueError("end must be greater than or equal to start.")
        return "".join(self.read(position) for position in range(start, end + 1))

    def normalized_bounds(self) -> tuple[int, int]:
        """Return the smallest interval containing all non-blank cells."""
        if not self._cells:
            return (0, 0)
        return (min(self._cells), max(self._cells))

    def normalized_content(self) -> str:
        """Render the useful content of the tape without external blank padding."""
        if not self._cells:
            return self.blank_symbol
        start, end = self.normalized_bounds()
        return self.render_segment(start, end)

    def non_blank_positions(self) -> list[int]:
        """Return sorted positions that differ from the blank symbol."""
        return sorted(self._cells)

    @staticmethod
    def _validate_symbol(symbol: str) -> None:
        """Validate a tape cell symbol."""
        if not isinstance(symbol, str):
            raise TypeError("Tape symbols must be strings.")
        if symbol == "":
            raise ValueError("Tape symbols must be non-empty strings.")
        if len(symbol) != 1:
            raise ValueError("Tape symbols must be one-character strings.")

    @staticmethod
    def _validate_blank_symbol(symbol: str) -> None:
        """Validate the tape blank symbol."""
        if not isinstance(symbol, str):
            raise TypeError("The blank symbol must be a string.")
        if symbol == "":
            raise ValueError("The blank symbol must be a non-empty string.")
        if len(symbol) != 1:
            raise ValueError("The blank symbol must be a one-character string.")

    @staticmethod
    def _validate_position(position: int) -> None:
        """Validate a tape position."""
        if not isinstance(position, int) or isinstance(position, bool):
            raise TypeError("Tape positions must be integers.")

    @staticmethod
    def _validate_radius(radius: int) -> None:
        """Validate a view radius."""
        if not isinstance(radius, int) or isinstance(radius, bool):
            raise TypeError("radius must be an integer.")
