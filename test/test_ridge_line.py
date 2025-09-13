from syntax_diagrams._impl.ridge_line import (
    RidgeLine,
    find_distance,
    merge_ridge_lines,
    reverse_ridge_line,
)
from syntax_diagrams._impl.vec import Vec


def test_empty_lines():
    empty = RidgeLine(0, [])
    line = RidgeLine(0, [Vec(0, 10), Vec(5, 20)])

    assert merge_ridge_lines(empty, line) == line
    assert merge_ridge_lines(line, empty) == line
    assert merge_ridge_lines(empty, empty) == empty


def test_single_point_lines():
    line1 = RidgeLine(0, [Vec(5, 10)])
    line2 = RidgeLine(0, [Vec(5, 20)])
    line3 = RidgeLine(0, [Vec(10, 15)])

    # Same x, different heights
    assert merge_ridge_lines(line1, line2) == RidgeLine(0, [Vec(5, 20)])

    # Different x positions
    assert merge_ridge_lines(line1, line3) == RidgeLine(0, [Vec(5, 10), Vec(10, 15)])


def test_non_overlapping_lines():
    left = RidgeLine(0, [Vec(0, 10), Vec(2, 15)])
    right = RidgeLine(0, [Vec(5, 20), Vec(7, 25)])

    expected = RidgeLine(0, [Vec(0, 10), Vec(2, 15), Vec(5, 20), Vec(7, 25)])
    assert merge_ridge_lines(left, right) == expected


def test_overlapping_lines_merge():
    line1 = RidgeLine(0, [Vec(0, 10), Vec(5, 20), Vec(10, 15)])
    line2 = RidgeLine(5, [Vec(2, 5), Vec(6, 25), Vec(8, 30)])

    expected = RidgeLine(5, [Vec(0, 10), Vec(5, 20), Vec(6, 25), Vec(8, 30)])
    result = merge_ridge_lines(line1, line2)
    assert result == expected


def test_overlapping_lines_step():
    line1 = RidgeLine(0, [Vec(0, 10), Vec(5, 20), Vec(8, 5)])
    line2 = RidgeLine(0, [Vec(2, 5), Vec(6, 10), Vec(10, 30)])

    expected = RidgeLine(0, [Vec(0, 10), Vec(5, 20), Vec(8, 10), Vec(10, 30)])
    result = merge_ridge_lines(line1, line2)
    assert result == expected


def test_identical_lines():
    line = RidgeLine(0, [Vec(0, 10), Vec(5, 20), Vec(10, 15)])

    assert merge_ridge_lines(line, line) == line


def test_same_x_different_heights():
    line1 = RidgeLine(0, [Vec(0, 10), Vec(5, 20), Vec(10, 30)])
    line2 = RidgeLine(0, [Vec(0, 15), Vec(5, 10), Vec(10, 25)])

    assert merge_ridge_lines(line1, line2) == RidgeLine(
        0, [Vec(0, 15), Vec(5, 20), Vec(10, 30)]
    )


def test_reverse_ridge_line_empty():
    empty = RidgeLine(0, [])

    expected = RidgeLine(0, [])
    assert reverse_ridge_line(empty, 0) == expected


def test_reverse_ridge_line_single_point():
    empty = RidgeLine(5, [Vec(10, 0)])

    expected = RidgeLine(0, [Vec(-10, 5)])
    assert reverse_ridge_line(empty, 0) == expected


def test_reverse_ridge_line():
    line = RidgeLine(0, [Vec(0, 10), Vec(5, 20), Vec(10, 15)])

    expected = RidgeLine(15, [Vec(-10, 20), Vec(-5, 10), Vec(0, 0)])
    assert reverse_ridge_line(line, 0) == expected


def test_reverse_ridge_line_pivot():
    line = RidgeLine(0, [Vec(0, 10), Vec(5, 20), Vec(10, 15)])

    expected = RidgeLine(15, [Vec(0, 20), Vec(5, 10), Vec(10, 0)])
    assert reverse_ridge_line(line, 10) == expected


def test_find_distance_empty():
    line1 = RidgeLine(5, [])
    line2 = RidgeLine(10, [])

    assert find_distance(line1, line2) == 15


def test_find_distance_step_up():
    line1 = RidgeLine(5, [Vec(5, 10)])
    line2 = RidgeLine(10, [])

    assert find_distance(line1, line2) == 20


def test_find_distance_step_down():
    line1 = RidgeLine(5, [Vec(5, 0)])
    line2 = RidgeLine(10, [])

    assert find_distance(line1, line2) == 15


def test_find_distance_single_point():
    line1 = RidgeLine(5, [Vec(5, 0)])
    line2 = RidgeLine(10, [Vec(5, 25)])

    assert find_distance(line1, line2) == 25


def test_find_distance_overlapping_lines():
    line1 = RidgeLine(5, [Vec(5, 0), Vec(10, -5), Vec(15, 15)])
    line2 = RidgeLine(0, [Vec(3, 5), Vec(5, 0), Vec(15, -6)])

    assert find_distance(line1, line2) == 10
