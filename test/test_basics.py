import pytest

import syntax_diagrams as rr
from syntax_diagrams._impl.load import load
from syntax_diagrams._impl.tree.node import Node
from syntax_diagrams._impl.tree.sequence import Sequence
from syntax_diagrams._impl.tree.skip import Skip


def test_str():
    a = rr.terminal("A")
    b = rr.terminal("B")
    c = rr.terminal("C")

    assert str(load(rr.terminal("TOKEN"), lambda x: x)) == "TOKEN"
    assert str(load(rr.terminal("{"), lambda x: x)) == "'{'"
    assert str(load(rr.sequence(a, b, c), lambda x: x)) == "A B C"
    assert str(load(rr.sequence(a, rr.choice(b, c)), lambda x: x)) == "A (B | C)"
    assert str(load(rr.choice(a, rr.sequence(b, c)), lambda x: x)) == "A | B C"
    assert str(load(rr.sequence(a, rr.optional(b)), lambda x: x)) == "A B?"
    assert str(load(rr.choice(a, rr.optional(b)), lambda x: x)) == "(A | B)?"
    assert str(load(rr.choice(rr.optional(a), b), lambda x: x)) == "(A | B)?"
    assert str(load(rr.choice(rr.skip(), a, b), lambda x: x)) == "(A | B)?"
    assert str(load(rr.sequence(a, rr.sequence(b, c)), lambda x: x)) == "A B C"
    assert str(load(rr.choice(a, rr.choice(b, c)), lambda x: x)) == "A | B | C"
    assert str(load(rr.one_or_more(a), lambda x: x)) == "A+"
    assert str(load(rr.one_or_more(rr.sequence(a, b, c)), lambda x: x)) == "(A B C)+"
    assert (
        str(load(rr.one_or_more(rr.sequence(a, b), repeat=c), lambda x: x))
        == "A B (C A B)*"
    )
    assert (
        str(load(rr.one_or_more(rr.choice(a, b), repeat=c), lambda x: x))
        == "(A | B) (C (A | B))*"
    )
    assert str(load(rr.zero_or_more(a), lambda x: x)) == "A*"
    assert str(load(rr.zero_or_more(rr.sequence(a, b, c)), lambda x: x)) == "(A B C)*"
    assert (
        str(load(rr.zero_or_more(rr.sequence(a, b), repeat=c), lambda x: x))
        == "(A B (C A B)*)?"
    )


def test_seq_creation():
    a = rr.terminal("node A")
    b = rr.terminal("node B")
    c = rr.terminal("node C")

    assert isinstance(load(rr.sequence(), lambda x: x), Skip)
    assert isinstance(load(rr.sequence(a), lambda x: x), Node)
    assert isinstance(load(rr.sequence(a, b, c), lambda x: x), Sequence)

    with pytest.raises(ValueError):
        load(rr.sequence(a, b, linebreaks=[]), lambda x: x)

    with pytest.raises(ValueError):
        load(
            rr.sequence(a, b, linebreaks=[rr.LineBreak.SOFT, rr.LineBreak.SOFT]),
            lambda x: x,
        )
