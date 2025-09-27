from __future__ import annotations

import dataclasses
import json
import math
import sys
import typing as _t
from dataclasses import dataclass
from enum import Enum
from functools import cached_property

from syntax_diagrams._impl.vec import Vec
from syntax_diagrams.measure import TextMeasure
from syntax_diagrams.render import EndClass
from syntax_diagrams.resolver import HrefResolver

if _t.TYPE_CHECKING:
    from syntax_diagrams._impl.tree import Element

T = _t.TypeVar("T")


_DEBUG_ATTRS = [
    "display_width",
    "width",
    "content_width",
    "start_padding",
    "end_padding",
    "start_margin",
    "end_margin",
    "height",
    "up",
    "down",
    "context",
]

_IGNORE_ATTRS = {"settings"}


class Render(_t.Generic[T]):
    def __init__(self, settings: LayoutSettings[T], dump_debug_data: bool):
        self.settings = settings
        self._debug = dump_debug_data
        self._id = 0
        self._ids: dict[Element[T], str] = {}
        self._debug_data: dict[str, _t.Any] = {}
        self._debug_stack: list[str] = []

    def _make_debug_id(self, elem: Element[T]) -> str:
        if elem not in self._ids:
            self._ids[elem] = str(self._id)
            self._id += 1
        return self._ids[elem]

    def _debug_parent(self) -> str | None:
        return self._debug_stack[-1] if self._debug_stack else None

    def write(self, f=sys.stdout):
        raise NotImplementedError()

    def to_string(self):
        raise NotImplementedError()

    def debug_data(self) -> str:
        return self._DebugJSONEncoder(self).encode(
            dict(rendered=self.to_string(), debug_data=self._debug_data)
        )

    def enter(self, node: Element[_t.Any]):
        if self._debug:
            node_id = self._make_debug_id(node)
            name = node.__class__.__name__.lower()
            if hasattr(node, "_text"):
                name += f" {json.dumps(getattr(node, "_text"))}"
            data = {}
            for k in _DEBUG_ATTRS:
                data[k] = getattr(node, k, None)
            for k, v in vars(node).items():
                if k.startswith("_Element__"):
                    k = "__" + k[len("_Element__") :]
                if k not in _IGNORE_ATTRS and k not in data:
                    data[k] = v
            data["$order"] = list(data.keys())
            self._debug_data[node_id] = {
                "parent": self._debug_parent(),
                "index": self._id,
                "name": name,
                "data": data,
            }
            self._debug_stack.append(node_id)

    def exit(self):
        if self._debug:
            self._debug_stack.pop()

    def line(self, pos: Vec, reverse: bool = False, css_class: str = "") -> Line:
        raise NotImplementedError()

    def node(
        self,
        pos: Vec,
        style: NodeStyle,
        css_class: str | None,
        content_width: int,
        up: int,
        down: int,
        radius: int,
        padding: int,
        text_width: int,
        text_height: int,
        text: str,
        href: str | None,
        title: str | None,
    ):
        raise NotImplementedError()

    def group(
        self,
        pos: Vec,
        width: int,
        height: int,
        css_class: str | None,
        text_width: int,
        text_height: int,
        text: str | None,
        href: str | None,
        title: str | None,
    ):
        raise NotImplementedError()

    def left_marker(self, pos: Vec):
        raise NotImplementedError()

    def right_marker(self, pos: Vec):
        raise NotImplementedError()

    def debug(self, node: Element[_t.Any], context: RenderContext):
        pass

    def debug_pos(self, pos: Vec, css_class: str = ""):
        pass

    def debug_ridge_line(self, pos: Vec, node: Element[_t.Any], reverse: bool):
        pass

    class _DebugJSONEncoder(json.JSONEncoder):
        def __init__(self, render: Render[_t.Any]):
            super().__init__()
            self._render = render

        def default(self, o):
            from syntax_diagrams._impl.tree import Element

            if dataclasses.is_dataclass(o) and not isinstance(o, type):
                d = dataclasses.asdict(o)
                d["$order"] = list(d.keys())
                return d
            elif isinstance(o, Enum):
                return o.value
            elif isinstance(o, Element):
                return {
                    "$elem": _t.cast(Element[_t.Any], o).__class__.__qualname__,
                    "$id": self._render._make_debug_id(o),
                }
            return super().default(o)


Direction: _t.TypeAlias = _t.Literal["w", "e"]


class Line:
    _reverse: bool

    def segment_abs(
        self, x: int, arrow_begin: bool = False, arrow_end: bool = False
    ) -> Line:
        raise NotImplementedError()

    def bend_forward_abs(
        self,
        y: int,
        arrow_begin: bool = False,
        arrow_end: bool = False,
    ) -> Line:
        d = "e" if not self._reverse else "w"
        return self.bend(y, self.reverse_direction(d), d, arrow_begin, arrow_end)

    def bend_backward_abs(
        self,
        y: int,
        arrow_begin: bool = False,
        arrow_end: bool = False,
    ) -> Line:
        d = "e" if not self._reverse else "w"
        return self.bend(y, d, d, arrow_begin, arrow_end)

    def bend_backward_reverse_abs(
        self,
        y: int,
        arrow_begin: bool = False,
        arrow_end: bool = False,
    ) -> Line:
        d = "w" if not self._reverse else "e"
        return self.bend(y, d, d, arrow_begin, arrow_end)

    def bend(
        self,
        y: int,
        coming_from: Direction,
        coming_to: Direction | None,
        arrow_begin: bool = False,
        arrow_end: bool = False,
    ) -> Line:
        raise NotADirectoryError()

    @staticmethod
    def reverse_direction(d: Direction):
        return "e" if d == "w" else "w"


@dataclass
class LayoutSettings(_t.Generic[T]):
    horizontal_seq_separation: int
    vertical_choice_separation_outer: int
    vertical_choice_separation: int
    vertical_seq_separation_outer: int
    vertical_seq_separation: int

    arc_radius: int | float
    arc_margin: int

    terminal_text_measure: TextMeasure
    terminal_horizontal_padding: int
    terminal_vertical_padding: int
    terminal_radius: int

    non_terminal_text_measure: TextMeasure
    non_terminal_horizontal_padding: int
    non_terminal_vertical_padding: int
    non_terminal_radius: int

    comment_text_measure: TextMeasure
    comment_horizontal_padding: int
    comment_vertical_padding: int
    comment_radius: int

    group_text_measure: TextMeasure
    group_vertical_padding: int
    group_horizontal_padding: int
    group_vertical_margin: int
    group_horizontal_margin: int
    group_thickness: int
    group_radius: int
    group_text_vertical_offset: int
    group_text_horizontal_offset: int

    marker_width: int
    marker_projected_height: int

    end_class: EndClass

    hidden_symbol_escape: tuple[str, str]

    href_resolver: HrefResolver[T] = HrefResolver()


class NodeStyle(Enum):
    """
    Style used to draw a node.
    """

    TERMINAL = "TERMINAL"
    NON_TERMINAL = "NON_TERMINAL"
    COMMENT = "COMMENT"


class ConnectionType(Enum):
    """
    Kind of curve that connects this element to the next/previous one.

    """

    NULL = "NULL"
    """
    Element is not connected. Happens at the edges of diagram.

    .. code-block::

       NODE

            ^ end connection is NULL

    """

    NORMAL = "NORMAL"
    """
    Element is connected by a straight line.

    .. code-block::

       NODE ──

            ^ end connection is NORMAL

    """

    STACK_BOUND = "STACK_BOUND"
    """
    Element is connected by a straight line. Like `NORMAL`, but longer.

    .. code-block::

       NODE ────

            ^ end connection is STACK_BOUND

    """

    STACK = "STACK"
    """
    Element is attached to a stack, i.e. the line makes a reverse turn before/after it.

    .. code-block::

            ╮
            ↑
       NODE ╯

            ^ end connection is STACK

    """

    SPLIT = "SPLIT"
    """
    Element is attached to a choice, i.e. the line makes a forward turn before/after it.

    .. code-block::

            ╭
            ↑
       NODE ╯

            ^ end connection is SPLIT

    """

    def arc_size(self, settings: LayoutSettings[_t.Any]) -> int:
        match self:
            case ConnectionType.NORMAL | ConnectionType.NULL:
                return 0
            case ConnectionType.STACK | ConnectionType.STACK_BOUND:
                return math.ceil(settings.arc_radius) + settings.arc_margin
            case ConnectionType.SPLIT:
                return math.ceil(2 * settings.arc_radius) + settings.arc_margin


class ConnectionDirection(Enum):
    """
    Indicates where connection makes a turn before/after the element.

    """

    UP = "UP"
    """
    Connection goes up.

    """

    DOWN = "DOWN"
    """
    Connection goes down.

    """

    STRAIGHT = "STRAIGHT"
    """
    Connection goes straight.

    """


ClearOfIntersections: _t.TypeAlias = bool
"""
Indicates whether element's connection intersects with other connections.

.. code-block::

         ╮
         ↑
    NODE ╯

        ^ end connection is STACK and it's clear of any intersections.

.. code-block::

         ╮
         ↑ <┈ end connection goes up
    NODE ┤
         ↑ <┈ there are some intersections, meaning that
              OneOrMore can't reuse end connection for its repeat loop.

         ^ end connection is STACK and there are intersections.

"""


@dataclass(kw_only=True)
class LayoutContext:
    width: int
    is_outer: bool
    start_connection: ConnectionType = ConnectionType.NORMAL
    start_top_is_clear: ClearOfIntersections = False
    start_bottom_is_clear: ClearOfIntersections = False
    start_direction: ConnectionDirection = ConnectionDirection.STRAIGHT
    end_connection: ConnectionType = ConnectionType.NORMAL
    end_top_is_clear: ClearOfIntersections = False
    end_bottom_is_clear: ClearOfIntersections = False
    end_direction: ConnectionDirection = ConnectionDirection.STRAIGHT
    allow_shrinking_stacks: bool = False
    opt_enter_top: bool = False
    opt_enter_bottom: bool = False
    opt_exit_top: bool = False
    opt_exit_bottom: bool = False


@dataclass(kw_only=True)
class RenderContext:
    pos: Vec
    start_connection_pos: Vec
    end_connection_pos: Vec
    reverse: bool
    opt_enter_top: tuple[Direction, Vec] | None = None
    opt_enter_bottom: tuple[Direction, Vec] | None = None
    opt_exit_top: tuple[Direction, Vec, Vec | None] | None = None
    opt_exit_bottom: tuple[Direction, Vec, Vec | None] | None = None

    @cached_property
    def dir(self):
        # Direction
        return 1 if not self.reverse else -1
