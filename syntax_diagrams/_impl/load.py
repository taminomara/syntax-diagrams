from __future__ import annotations

import typing as _t
from types import NoneType

from syntax_diagrams._impl.render import NodeStyle
from syntax_diagrams._impl.tree import Element as _Output
from syntax_diagrams._impl.tree.barrier import Barrier
from syntax_diagrams._impl.tree.choice import Choice
from syntax_diagrams._impl.tree.group import Group
from syntax_diagrams._impl.tree.node import Node
from syntax_diagrams._impl.tree.one_or_more import OneOrMore
from syntax_diagrams._impl.tree.sequence import Sequence
from syntax_diagrams._impl.tree.skip import Skip
from syntax_diagrams.element import Element as _Input
from syntax_diagrams.element import LineBreak
from syntax_diagrams.render import LoadingError

T = _t.TypeVar("T")


def load(
    element: _Input[T], convert_resolver_data: _t.Callable[[_t.Any | None], T | None]
) -> _Output[T]:
    if element is None:
        return Skip()
    elif isinstance(element, str):
        return _load_terminal(element, {}, convert_resolver_data)
    elif isinstance(element, list):
        return _load_sequence(element, {}, convert_resolver_data)
    elif isinstance(element, dict):
        ctors = {
            "sequence": _load_sequence,
            "stack": _load_stack,
            "no_break": _load_no_break,
            "choice": _load_choice,
            "optional": _load_optional,
            "one_or_more": _load_one_or_more,
            "zero_or_more": _load_zero_or_more,
            "barrier": _load_barrier,
            "terminal": _load_terminal,
            "non_terminal": _load_non_terminal,
            "comment": _load_comment,
            "group": _load_group,
        }

        ctors_found: list[str] = []

        for name in element:
            if name in ctors:
                ctors_found.append(name)

        if len(ctors_found) != 1:
            raise LoadingError(f"cannot determine type for {element!r}")

        name = ctors_found[0]
        element = element.copy()
        arg = element.pop(name)
        return ctors[name](
            arg, _t.cast(dict[str, _t.Any], element), convert_resolver_data
        )
    else:
        raise LoadingError(
            f"diagram item description should be string, "
            f"list or object, got {type(element)} instead"
        )


def _load_linebreaks(linebreak: _t.Any) -> LineBreak | list[LineBreak] | None:
    if linebreak is None:
        return None
    if isinstance(linebreak, LineBreak):
        return linebreak
    if isinstance(linebreak, str):
        return LineBreak(linebreak.upper())
    else:
        for i, x in enumerate(linebreak):
            _ensure_type(f"linebreaks[{i}]", x, str, LineBreak)
        return [LineBreak(x) for x in linebreak]


def _load_sequence(
    a: _t.Any,
    kw: dict[str, _t.Any],
    convert_resolver_data: _t.Callable[[_t.Any | None], T | None],
) -> _Output[T]:
    element = Sequence(
        [load(x, convert_resolver_data) for x in _ensure_type("sequence", a, list)],
        _load_linebreaks(kw.pop("linebreaks", None)),
    )
    _ensure_empty_dict("sequence", kw)
    return element


def _load_stack(
    a: _t.Any,
    kw: dict[str, _t.Any],
    convert_resolver_data: _t.Callable[[_t.Any | None], T | None],
) -> _Output[T]:
    element = Sequence(
        [load(x, convert_resolver_data) for x in _ensure_type("sequence", a, list)],
        LineBreak.HARD,
    )
    _ensure_empty_dict("sequence", kw)
    return element


def _load_no_break(
    a: _t.Any,
    kw: dict[str, _t.Any],
    convert_resolver_data: _t.Callable[[_t.Any | None], T | None],
) -> _Output[T]:
    element = Sequence(
        [load(x, convert_resolver_data) for x in _ensure_type("sequence", a, list)],
        LineBreak.NO_BREAK,
    )
    _ensure_empty_dict("sequence", kw)
    return element


def _load_choice(
    a: _t.Any,
    kw: dict[str, _t.Any],
    convert_resolver_data: _t.Callable[[_t.Any | None], T | None],
) -> _Output[T]:
    element = Choice(
        [load(x, convert_resolver_data) for x in _ensure_type("choice", a, list)],
        default=_ensure_type("default", kw.pop("default", None), int, NoneType) or 0,
    )
    _ensure_empty_dict("choice", kw)
    return element


def _load_optional(
    a: _t.Any,
    kw: dict[str, _t.Any],
    convert_resolver_data: _t.Callable[[_t.Any | None], T | None],
) -> _Output[T]:
    element = load(a, convert_resolver_data)
    skip = _ensure_type("skip", kw.pop("skip", None), bool, NoneType) or False
    skip_bottom = (
        _ensure_type("skip_bottom", kw.pop("skip_bottom", None), bool, NoneType)
        or False
    )
    _ensure_empty_dict("optional", kw)
    if skip_bottom:
        return Choice([element, Skip()], 1 if skip else 0)
    else:
        return Choice([Skip(), element], 0 if skip else 1)


def _load_one_or_more(
    a: _t.Any,
    kw: dict[str, _t.Any],
    convert_resolver_data: _t.Callable[[_t.Any | None], T | None],
) -> _Output[T]:
    element = OneOrMore(
        load(a, convert_resolver_data),
        repeat=load(kw.pop("repeat", None), convert_resolver_data),
        repeat_top=_ensure_type(
            "repeat_top", kw.pop("repeat_top", None), bool, NoneType
        )
        or False,
    )
    _ensure_empty_dict("one_or_more", kw)
    return element


def _load_zero_or_more(
    a: _t.Any,
    kw: dict[str, _t.Any],
    convert_resolver_data: _t.Callable[[_t.Any | None], T | None],
) -> _Output[T]:
    element = OneOrMore(
        load(a, convert_resolver_data),
        repeat=load(kw.pop("repeat", None), convert_resolver_data),
        repeat_top=_ensure_type(
            "repeat_top", kw.pop("repeat_top", None), bool, NoneType
        )
        or False,
    )
    skip = _ensure_type("skip", kw.pop("skip", None), bool, NoneType) or False
    skip_bottom = (
        _ensure_type("skip_bottom", kw.pop("skip_bottom", None), bool, NoneType)
        or False
    )
    _ensure_empty_dict("zero_or_more", kw)
    if skip_bottom:
        return Choice([element, Skip()], 1 if skip else 0)
    else:
        return Choice([Skip(), element], 0 if skip else 1)


def _load_barrier(
    a: _t.Any,
    kw: dict[str, _t.Any],
    convert_resolver_data: _t.Callable[[_t.Any | None], T | None],
) -> _Output[T]:
    element = Barrier(
        load(a, convert_resolver_data),
    )
    _ensure_empty_dict("barrier", kw)
    return element


def _load_terminal(
    a: _t.Any,
    kw: dict[str, _t.Any],
    convert_resolver_data: _t.Callable[[_t.Any | None], T | None],
) -> _Output[T]:
    element = Node(
        NodeStyle.TERMINAL,
        _ensure_type("terminal", a, str),
        href=_ensure_type("href", kw.pop("href", None), str, NoneType),
        title=_ensure_type("title", kw.pop("title", None), str, NoneType),
        css_class=_ensure_type("css_class", kw.pop("css_class", None), str, NoneType),
        resolve=_ensure_type("resolve", kw.pop("resolve", None), bool, NoneType),
        resolver_data=convert_resolver_data(kw.pop("resolver_data", None)),
    )
    _ensure_empty_dict("terminal", kw)
    return element


def _load_non_terminal(
    a: _t.Any,
    kw: dict[str, _t.Any],
    convert_resolver_data: _t.Callable[[_t.Any | None], T | None],
) -> _Output[T]:
    element = Node(
        NodeStyle.NON_TERMINAL,
        _ensure_type("non_terminal", a, str),
        href=_ensure_type("href", kw.pop("href", None), str, NoneType),
        title=_ensure_type("title", kw.pop("title", None), str, NoneType),
        css_class=_ensure_type("css_class", kw.pop("css_class", None), str, NoneType),
        resolve=_ensure_type("resolve", kw.pop("resolve", None), bool, NoneType),
        resolver_data=convert_resolver_data(kw.pop("resolver_data", None)),
    )
    _ensure_empty_dict("non_terminal", kw)
    return element


def _load_comment(
    a: _t.Any,
    kw: dict[str, _t.Any],
    convert_resolver_data: _t.Callable[[_t.Any | None], T | None],
) -> _Output[T]:
    element = Node(
        NodeStyle.COMMENT,
        _ensure_type("comment", a, str),
        href=_ensure_type("href", kw.pop("href", None), str, NoneType),
        title=_ensure_type("title", kw.pop("title", None), str, NoneType),
        css_class=_ensure_type("css_class", kw.pop("css_class", None), str, NoneType),
        resolve=_ensure_type("resolve", kw.pop("resolve", None), bool, NoneType),
        resolver_data=convert_resolver_data(kw.pop("resolver_data", None)),
    )
    _ensure_empty_dict("comment", kw)
    return element


def _load_group(
    a: _t.Any,
    kw: dict[str, _t.Any],
    convert_resolver_data: _t.Callable[[_t.Any | None], T | None],
) -> _Output[T]:
    element = Group(
        load(a, convert_resolver_data),
        text=_ensure_type("text", kw.pop("text", None), str, NoneType),
        href=_ensure_type("href", kw.pop("href", None), str, NoneType),
        title=_ensure_type("title", kw.pop("title", None), str, NoneType),
        css_class=_ensure_type("css_class", kw.pop("css_class", None), str, NoneType),
    )
    _ensure_empty_dict("comment", kw)
    return element


def _ensure_type(name: str, x: _t.Any, *types: type[T]) -> T:
    if not isinstance(x, types):
        types_str = ", ".join([t.__name__ for t in types])
        raise LoadingError(
            f"{name} should be {types_str}, got {type(x)} (={x!r}) instead"
        )
    return x


def _ensure_empty_dict(name: str, x: dict[str, _t.Any]):
    if x:
        keys = ", ".join(x.keys())
        raise LoadingError(f"{name} got unexpected parameters: {keys}")
