from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Vec:
    x: int
    y: int

    def __add__(self, rhs: Vec):
        return Vec(self.x + rhs.x, self.y + rhs.y)

    def __sub__(self, rhs: Vec):
        return Vec(self.x - rhs.x, self.y - rhs.y)

    def __mul__(self, rhs: int):
        return Vec(self.x * rhs, self.y * rhs)
