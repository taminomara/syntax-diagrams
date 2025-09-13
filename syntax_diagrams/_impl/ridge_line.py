from dataclasses import dataclass

from syntax_diagrams._impl.vec import Vec


@dataclass(slots=True)
class RidgeLine:
    """
    Represents a ridge line.

    """

    before: int
    ridge: list[Vec]

    def __add__(self, rhs: Vec):
        return RidgeLine(self.before + rhs.y, [p + rhs for p in self.ridge])

    def __sub__(self, rhs: Vec):
        return RidgeLine(self.before - rhs.y, [p - rhs for p in self.ridge])


def merge_ridge_lines(lhs: RidgeLine, rhs: RidgeLine, cmp=max) -> RidgeLine:
    """
    Merge two ridge lines by taking the maximum height at each position.

    """

    before = cmp(lhs.before, rhs.before)

    l = lhs.ridge
    r = rhs.ridge
    result: list[Vec] = []
    i = j = 0
    current_l_height = lhs.before
    current_r_height = rhs.before

    while i < len(l) or j < len(r):
        if i >= len(l):
            x = r[j].x
        elif j >= len(r):
            x = l[i].x
        else:
            x = min(l[i].x, r[j].x)

        if i < len(l) and l[i].x == x:
            current_l_height = l[i].y
            i += 1
        if j < len(r) and r[j].x == x:
            current_r_height = r[j].y
            j += 1

        merged_height = cmp(current_l_height, current_r_height)

        if not result or result[-1].y != merged_height:
            result.append(Vec(x, merged_height))

    return RidgeLine(before, result)


def reverse_ridge_line(lhs: RidgeLine, pivot: int) -> RidgeLine:
    if not lhs.ridge:
        return lhs

    before = lhs.ridge[-1].y
    result: list[Vec] = []
    for i, p in enumerate(lhs.ridge):
        if i == 0:
            y = lhs.before
        else:
            y = lhs.ridge[i - 1].y
        result.append(Vec(pivot - p.x, y))
    result.reverse()

    return RidgeLine(before, result)


def find_distance(lhs: RidgeLine, rhs: RidgeLine) -> int:
    l = lhs.ridge
    r = rhs.ridge
    i = j = 0
    current_l_height = lhs.before
    current_r_height = rhs.before

    d = current_l_height + current_r_height

    while i < len(l) or j < len(r):
        if i >= len(l):
            x = r[j].x
        elif j >= len(r):
            x = l[i].x
        else:
            x = min(l[i].x, r[j].x)

        if i < len(l) and l[i].x == x:
            current_l_height = l[i].y
            i += 1
        if j < len(r) and r[j].x == x:
            current_r_height = r[j].y
            j += 1

        d = max(d, current_l_height + current_r_height)

    return d
