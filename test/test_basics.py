import pytest

import neat_railroad_diagrams as rr


def test_str():
    a = rr.terminal("A")
    b = rr.terminal("B")
    c = rr.terminal("C")

    assert str(rr.terminal("TOKEN")) == "TOKEN"
    assert str(rr.terminal("{")) == "'{'"
    assert str(rr.sequence(a, b, c)) == "A B C"
    assert str(rr.sequence(a, rr.choice(b, c))) == "A (B | C)"
    assert str(rr.choice(a, rr.sequence(b, c))) == "A | B C"
    assert str(rr.sequence(a, rr.optional(b))) == "A B?"
    assert str(rr.choice(a, rr.optional(b))) == "(A | B)?"
    assert str(rr.choice(rr.optional(a), b)) == "(A | B)?"
    assert str(rr.choice(rr.skip(), a, b)) == "(A | B)?"
    assert str(rr.sequence(a, rr.sequence(b, c))) == "A B C"
    assert str(rr.choice(a, rr.choice(b, c))) == "A | B | C"
    assert str(rr.one_or_more(a)) == "A+"
    assert str(rr.one_or_more(rr.sequence(a, b, c))) == "(A B C)+"
    assert str(rr.one_or_more(rr.sequence(a, b), c)) == "A B (C A B)*"
    assert str(rr.one_or_more(rr.choice(a, b), c)) == "(A | B) (C (A | B))*"
    assert str(rr.zero_or_more(a)) == "A*"
    assert str(rr.zero_or_more(rr.sequence(a, b, c))) == "(A B C)*"
    assert str(rr.zero_or_more(rr.sequence(a, b), c)) == "(A B (C A B)*)?"


def dest_seq_creation():
    a = rr.terminal("node A")
    b = rr.terminal("node B")
    c = rr.terminal("node C")

    assert rr.sequence() is rr.skip()
    assert rr.sequence(a) is a
    assert isinstance(rr.sequence(a, b, c), rr._Sequence)

    with pytest.raises(AssertionError):
        rr.sequence(a, b, linebreaks=[])

    with pytest.raises(AssertionError):
        rr.sequence(a, b, linebreaks=[rr.LineBreak.SOFT, rr.LineBreak.SOFT])
