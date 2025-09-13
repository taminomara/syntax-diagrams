from __future__ import annotations

import math
import sys
import typing as _t
from dataclasses import dataclass
from enum import Enum
from functools import cached_property

from syntax_diagrams._impl.vec import Vec
from syntax_diagrams.render import EndClass
from syntax_diagrams.resolver import HrefResolver

if _t.TYPE_CHECKING:
    from syntax_diagrams._impl.tree import Element

T = _t.TypeVar("T")


class Render(_t.Generic[T]):
    settings: LayoutSettings[T]

    def write(self, f=sys.stdout):
        raise NotImplementedError()

    def to_string(self):
        raise NotImplementedError()

    def enter(self, node: Element[_t.Any]):
        pass

    def exit(self):
        pass

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

    terminal_character_advance: int | float
    terminal_wide_character_advance: int | float
    terminal_padding: int
    terminal_height: int
    terminal_radius: int

    non_terminal_character_advance: int | float
    non_terminal_wide_character_advance: int | float
    non_terminal_padding: int
    non_terminal_height: int
    non_terminal_radius: int

    comment_character_advance: int | float
    comment_wide_character_advance: int | float
    comment_padding: int
    comment_height: int
    comment_radius: int

    group_character_advance: int | float
    group_wide_character_advance: int | float
    group_vertical_padding: int
    group_horizontal_padding: int
    group_vertical_margin: int
    group_horizontal_margin: int
    group_thickness: int
    group_radius: int
    group_text_height: int
    group_text_vertical_offset: int
    group_text_horizontal_offset: int

    marker_width: int
    marker_projected_height: int

    end_class: EndClass

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
