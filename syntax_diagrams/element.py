from __future__ import annotations

import textwrap
import types
import typing as _t
from dataclasses import dataclass
from enum import Enum

__all__ = [
    "Element",
    "Terminal",
    "NonTerminal",
    "Comment",
    "Sequence",
    "Stack",
    "NoBreak",
    "Choice",
    "Optional",
    "OneOrMore",
    "ZeroOrMore",
    "Barrier",
    "Group",
    "LineBreak",
    "skip",
    "terminal",
    "non_terminal",
    "comment",
    "sequence",
    "stack",
    "no_break",
    "choice",
    "optional",
    "one_or_more",
    "zero_or_more",
    "barrier",
    "group",
]

T = _t.TypeVar("T")


@dataclass(frozen=True, kw_only=True)
class _Annotation:
    name: str | None = None
    description: str | None = None


class Terminal(_t.TypedDict, _t.Generic[T], total=False):
    terminal: _t.Annotated[
        _t.Required[str],
        _Annotation(
            description="Describes a terminal node with optional additional settings.",
        ),
    ]

    href: _t.Annotated[
        str | None,
        _Annotation(
            description="Makes text node into a hyperlink.",
        ),
    ]

    title: _t.Annotated[
        str | None,
        _Annotation(
            description="Title for hyperlink.",
        ),
    ]

    css_class: _t.Annotated[
        str | None,
        _Annotation(
            description="Adds CSS class to node's ``<g>`` element.",
        ),
    ]

    resolve: _t.Annotated[
        bool | None,
        _Annotation(
            description="If set to `False`, this node will not be passed to `HrefResolver`",
        ),
    ]

    resolver_data: _t.Annotated[
        T | None,
        _Annotation(
            description="Additional data for `HrefResolver`.",
        ),
    ]


class NonTerminal(_t.TypedDict, _t.Generic[T], total=False):
    non_terminal: _t.Annotated[
        _t.Required[str],
        _Annotation(
            description="Describes a non-terminal node with optional additional settings.",
        ),
    ]

    href: _t.Annotated[
        str | None,
        _Annotation(
            description="Makes text node into a hyperlink.",
        ),
    ]

    title: _t.Annotated[
        str | None,
        _Annotation(
            description="Title for hyperlink.",
        ),
    ]

    css_class: _t.Annotated[
        str | None,
        _Annotation(
            description="Adds CSS class to node's ``<g>`` element.",
        ),
    ]

    resolve: _t.Annotated[
        bool | None,
        _Annotation(
            description="If set to `False`, this node will not be passed to `HrefResolver`",
        ),
    ]

    resolver_data: _t.Annotated[
        T | None,
        _Annotation(
            description="Additional data for `HrefResolver`.",
        ),
    ]


class Comment(_t.TypedDict, _t.Generic[T], total=False):
    comment: _t.Annotated[
        _t.Required[str],
        _Annotation(
            description="Describes a comment node with optional additional settings.",
        ),
    ]

    href: _t.Annotated[
        str | None,
        _Annotation(
            description="Makes text node into a hyperlink.",
        ),
    ]

    title: _t.Annotated[
        str | None,
        _Annotation(
            description="Title for hyperlink.",
        ),
    ]

    css_class: _t.Annotated[
        str | None,
        _Annotation(
            description="Adds CSS class to node's ``<g>`` element.",
        ),
    ]

    resolve: _t.Annotated[
        bool | None,
        _Annotation(
            description="If set to `False`, this node will not be passed to `HrefResolver`",
        ),
    ]

    resolver_data: _t.Annotated[
        T | None,
        _Annotation(
            description="Additional data for `HrefResolver`.",
        ),
    ]


class Sequence(_t.TypedDict, _t.Generic[T], total=False):
    sequence: _t.Annotated[
        _t.Required[list[Element[T]]],
        _Annotation(
            description="Describes an automatically wrapped sequence of elements.",
        ),
    ]

    linebreaks: _t.Annotated[
        (
            _t.Literal["HARD", "SOFT", "DEFAULT", "NO_BREAK"]
            | LineBreak
            | list[_t.Literal["HARD", "SOFT", "DEFAULT", "NO_BREAK"] | LineBreak]
        )
        | None,
        _Annotation(
            description="Specifies line breaks after each element of the sequence.",
        ),
    ]


class Stack(_t.TypedDict, _t.Generic[T], total=False):
    stack: _t.Annotated[
        _t.Required[list[Element[T]]],
        _Annotation(
            description="Describes a sequence of elements that wraps after each element.",
        ),
    ]


class NoBreak(_t.TypedDict, _t.Generic[T], total=False):
    no_break: _t.Annotated[
        _t.Required[list[Element[T]]],
        _Annotation(
            description="Describes a sequence of elements that doesn't wrap.",
        ),
    ]


class Choice(_t.TypedDict, _t.Generic[T], total=False):
    choice: _t.Annotated[
        _t.Required[list[Element[T]]],
        _Annotation(
            description="Describes a choice between several elements.",
        ),
    ]

    default: _t.Annotated[
        int | None,
        _Annotation(
            description="Index of item that will be placed on the main line.",
        ),
    ]


class Optional(_t.TypedDict, _t.Generic[T], total=False):
    optional: _t.Annotated[
        _t.Required[Element[T]],
        _Annotation(
            description="Describes an optional element.",
        ),
    ]

    skip: _t.Annotated[
        bool | None,
        _Annotation(
            description="If set to `True`, the optional element will be rendered off the main line.",
        ),
    ]

    skip_bottom: _t.Annotated[
        bool | None,
        _Annotation(
            description="If set to `True`, the skip line will be rendered below the skipped element.",
        ),
    ]


class OneOrMore(_t.TypedDict, _t.Generic[T], total=False):
    one_or_more: _t.Annotated[
        _t.Required[Element[T]],
        _Annotation(
            description="Describes a repeated element.",
        ),
    ]

    repeat: _t.Annotated[
        Element[T] | None,
        _Annotation(
            description="An element that will be placed on the backwards path.",
        ),
    ]

    # repeat_top: _t.Annotated[
    #     bool | None,
    #     _Annotation(
    #         description="If set to `True`, the repeat element will be rendered above the repeated one.",
    #     ),
    # ]


class ZeroOrMore(_t.TypedDict, _t.Generic[T], total=False):
    zero_or_more: _t.Annotated[
        _t.Required[Element[T]],
        _Annotation(
            description="Describes an optional repeated element.",
        ),
    ]

    repeat: _t.Annotated[
        Element[T] | None,
        _Annotation(
            description="An element that will be placed on the backwards path.",
        ),
    ]

    # repeat_top: _t.Annotated[
    #     bool | None,
    #     _Annotation(
    #         description="If set to `True`, the repeat element will be rendered above the repeated one.",
    #     ),
    # ]

    skip: _t.Annotated[
        bool | None,
        _Annotation(
            description="If set to `True`, the optional repeated element will be rendered off the main line.",
        ),
    ]

    skip_bottom: _t.Annotated[
        bool | None,
        _Annotation(
            description="If set to `True`, the skip line will be rendered below the skipped element.",
        ),
    ]


class Barrier(_t.TypedDict, _t.Generic[T], total=False):
    barrier: _t.Annotated[
        _t.Required[Element[T]],
        _Annotation(
            description=(
                "Isolates an element and disables optimizations that merge "
                "lines between this element and the rest of the diagram."
            )
        ),
    ]


class Group(_t.TypedDict, _t.Generic[T], total=False):
    group: _t.Annotated[
        _t.Required[Element[T]],
        _Annotation(
            description="Draws a box around some element.",
        ),
    ]

    text: _t.Annotated[
        str | None,
        _Annotation(
            description="Group's text.",
        ),
    ]

    href: _t.Annotated[
        str | None,
        _Annotation(
            description="Makes text into a hyperlink.",
        ),
    ]

    title: _t.Annotated[
        str | None,
        _Annotation(
            description="Title for hyperlink.",
        ),
    ]

    css_class: _t.Annotated[
        str | None,
        _Annotation(
            description="Adds CSS class to group's ``<g>`` element.",
        ),
    ]


Element: _t.TypeAlias = _t.Annotated[
    None
    | str
    | list["Element[T]"]
    | Terminal[T]
    | NonTerminal[T]
    | Comment[T]
    | Sequence[T]
    | Stack[T]
    | NoBreak[T]
    | Choice[T]
    | Optional[T]
    | OneOrMore[T]
    | ZeroOrMore[T]
    | Barrier[T]
    | Group[T],
    _Annotation(name="Element"),
]


class LineBreak(Enum):
    """
    Type of a line break that can be specified when creating a sequence.

    """

    HARD = "HARD"
    """
    Always breaks a line in this position.

    """

    SOFT = "SOFT"
    """
    Breaks a line in this position if the sequence can't fit
    in allowed dimensions.

    """

    DEFAULT = "DEFAULT"
    """
    Prefers not to break line in this position unless necessary.

    """

    NO_BREAK = "NO_BREAK"
    """
    Disables breaking in this position.

    """


def skip() -> Element[T]:
    """
    Create an element that renders as a single line without content.

    See `Element` for more information.

    """

    return None


def terminal(
    text: str,
    *,
    href: str | None = None,
    title: str | None = None,
    css_class: str | None = None,
    resolve: bool | None = None,
    resolver_data: T | None = None,
) -> Element[T]:
    """
    Create a terminal node with optional additional settings.

    See `Terminal` for description of parameters.

    """
    return {
        "terminal": text,
        "href": href,
        "title": title,
        "css_class": css_class,
        "resolve": resolve,
        "resolver_data": resolver_data,
    }


def non_terminal(
    text: str,
    *,
    href: str | None = None,
    title: str | None = None,
    css_class: str | None = None,
    resolve: bool | None = None,
    resolver_data: T | None = None,
) -> Element[T]:
    """
    Create a non-terminal node with optional additional settings.

    See `NonTerminal` for description of parameters.

    """

    return {
        "non_terminal": text,
        "href": href,
        "title": title,
        "css_class": css_class,
        "resolve": resolve,
        "resolver_data": resolver_data,
    }


def comment(
    text: str,
    *,
    href: str | None = None,
    title: str | None = None,
    css_class: str | None = None,
    resolve: bool | None = None,
    resolver_data: T | None = None,
) -> Element[T]:
    """
    Create a comment node with optional additional settings.

    See `Comment` for description of parameters.

    """

    return {
        "comment": text,
        "href": href,
        "title": title,
        "css_class": css_class,
        "resolve": resolve,
        "resolver_data": resolver_data,
    }


def sequence(
    *items: Element[T],
    linebreaks: (
        _t.Literal["HARD", "SOFT", "DEFAULT", "NO_BREAK"]
        | LineBreak
        | list[_t.Literal["HARD", "SOFT", "DEFAULT", "NO_BREAK"] | LineBreak]
        | None
    ) = None,
) -> Element[T]:
    """
    Create an automatically wrapped sequence of elements.

    See `Sequence` for description of parameters.

    """

    return {
        "sequence": list(items),
        "linebreaks": linebreaks,
    }


def stack(*items: Element[T]) -> Element[T]:
    """
    Create a sequence of elements that wraps after each element.

    See `Stack` for description of parameters.

    """

    return {
        "stack": list(items),
    }


def no_break(*items: Element[T]) -> Element[T]:
    """
    Create a sequence of elements that doesn't wrap.

    See `NoBreak` for description of parameters.

    """

    return {
        "no_break": list(items),
    }


def choice(*items: Element[T], default: int = 0) -> Element[T]:
    """
    Create a choice between several elements.

    See `Choice` for description of parameters.

    """

    return {
        "choice": list(items),
        "default": default,
    }


def optional(
    *items: Element[T], skip: bool = False, skip_bottom: bool = False
) -> Element[T]:
    """
    Create an optional element.

    See `Optional` for description of parameters.

    """

    return {
        "optional": list(items),
        "skip": skip,
        "skip_bottom": skip_bottom,
    }


def one_or_more(
    *items: Element[T],
    repeat: Element[T] | None = None,
    # repeat_top: bool = False,
) -> Element[T]:
    """
    Create a repeated element.

    See `OneOrMore` for description of parameters.

    """

    return {
        "one_or_more": list(items),
        "repeat": repeat,
        # "repeat_top": repeat_top,
    }


def zero_or_more(
    *items: Element[T],
    repeat: Element[T] | None = None,
    # repeat_top: bool = False,
    skip: bool = False,
    skip_bottom: bool = False,
) -> Element[T]:
    """
    Create an optional repeated element.

    See `ZeroOrMore` for description of parameters.

    """

    return {
        "zero_or_more": list(items),
        "repeat": repeat,
        # "repeat_top": repeat_top,
        "skip": skip,
        "skip_bottom": skip_bottom,
    }


def barrier(
    *items: Element[T],
) -> Element[T]:
    """
    Create a barrier element.

    See `Barrier` for description of parameters.

    """

    return {
        "barrier": list(items),
    }


def group(
    *items: Element[T],
    text: str | None = None,
    href: str | None = None,
    title: str | None = None,
    css_class: str | None = None,
) -> Element[T]:
    """
    Create a group element.

    See `Group` for description of parameters.

    """

    return {
        "group": list(items),
        "text": text,
        "href": href,
        "title": title,
        "css_class": css_class,
    }


def _to_json_schema(
    cls,
    globals,
    locals,
) -> dict[str, _t.Any]:
    # Based on https://github.com/Udzu/dataglasses

    defs: dict[str, _t.Any] = {}
    saved: dict[_t.Any, str] = {}

    def _json_schema(
        cls: _t.Any,
    ) -> dict[str, _t.Any]:
        basic_types = {
            bool: "boolean",
            int: "integer",
            float: "number",
            str: "string",
            types.NoneType: "null",
        }

        if cls is None:
            cls = types.NoneType

        if cls in basic_types:
            return {"type": basic_types[cls]}

        if cls in saved:
            return {"$ref": f"#/$defs/{saved[cls]}"}

        origin = _t.get_origin(cls)

        if _t.is_typeddict(origin):
            if cls.__qualname__ not in defs:
                defn: dict[str, _t.Any] = {
                    "type": "object",
                    "properties": {},
                    "required": [],
                    "additionalProperties": False,
                    "description": textwrap.dedent(
                        origin.__doc__ or cls.__qualname__
                    ).strip(),
                }
                defs[cls.__qualname__] = defn

                for name, ann in _t.get_type_hints(
                    origin, globals, locals, include_extras=True
                ).items():
                    if _t.get_origin(ann) is _t.Required:
                        defn["required"].append(name)
                    defn["properties"][name] = _json_schema(ann)

            return {"$ref": f"#/$defs/{cls.__qualname__}"}

        if isinstance(cls, (str, _t.ForwardRef)):
            ref = _t.ForwardRef(cls) if isinstance(cls, str) else cls
            evaluated_type = ref._evaluate(globals, locals, recursive_guard=frozenset())
            return _json_schema(evaluated_type)
        elif origin is list:
            sequence_type = _t.get_args(cls)[0]
            return {"type": "array", "items": _json_schema(sequence_type)}
        elif origin is dict:
            key_type, value_type = _t.get_args(cls)
            if key_type is not str:
                raise ValueError(f"Unsupported non-string mapping key type: {key_type}")
            return {
                "type": "object",
                "patternProperties": {"^.*$": _json_schema(value_type)},
            }
        elif origin in (_t.Union, types.UnionType, _t.Required, _t.NotRequired):
            union_types = _t.get_args(cls)
            return {"anyOf": [_json_schema(t) for t in union_types]}
        elif origin is tuple:
            tuple_types = _t.get_args(cls)
            if len(tuple_types) == 2 and tuple_types[1] == Ellipsis:
                return {
                    "type": "array",
                    "items": _json_schema(tuple_types[0]),
                }
            else:
                return {
                    "type": "array",
                    "prefixItems": [_json_schema(t) for t in tuple_types],
                    "minItems": len(tuple_types),
                    "maxItems": len(tuple_types),
                }
        elif origin == _t.Literal:
            return {"enum": list(_t.get_args(cls))}
        elif origin == _t.Annotated:
            annotated_type, data = _t.get_args(cls)
            if not isinstance(data, _Annotation):
                return _json_schema(annotated_type)
            if data.name:
                saved[cls] = data.name

            defn = _json_schema(annotated_type)
            defn["description"] = data.description

            if data.name:
                defs[data.name] = defn
                return {"$ref": f"#/$defs/{data.name}"}
            else:
                return defn
        elif isinstance(cls, type) and issubclass(cls, Enum):
            return {"enum": [e.value for e in cls]}
        elif isinstance(cls, _t.TypeVar):
            return {}
        else:
            raise ValueError(f"Unsupported type {cls}")

    schema: dict[str, _t.Any] = {}
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    schema.update(_json_schema(cls))
    schema["$defs"] = defs
    return schema


def _main():
    import argparse
    import json
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument("-o", type=argparse.FileType("w"), default=sys.stdout)
    args = parser.parse_args()

    print(
        json.dumps(_to_json_schema(Element, globals(), locals()), indent=2), file=args.o
    )


if __name__ == "__main__":
    _main()
