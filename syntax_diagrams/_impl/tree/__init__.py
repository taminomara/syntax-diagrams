from __future__ import annotations

import math
import typing as _t
from contextlib import contextmanager
from dataclasses import replace
from functools import cached_property

from syntax_diagrams._impl.render import (
    ConnectionDirection,
    ConnectionType,
    LayoutContext,
    LayoutSettings,
    Render,
    RenderContext,
)
from syntax_diagrams._impl.ridge_line import RidgeLine
from syntax_diagrams._impl.vec import Vec

T = _t.TypeVar("T")


class Element(_t.Generic[T]):
    """
    Element dimensions
    ------------------

    Elements get information about how they're connected to other elements
    via layout/rendering context. `context.start_connection` indicates how element's
    input is connected, and `context.end_connection` indicates how element's
    output is connected.

    Element can choose to draw connections itself by calling `_isolate` from
    its layout routine, or it can choose to pass this info to its children.

    In either case, element width includes space required to make these connections.
    Space for input connection is called `_start_padding`, and space for output
    connection is called `_end_padding`. Space for element's content is called
    `_content_width`. Together, these three values constitute element's full width,
    available via the `_width` property.

    Generally speaking, element's content width will include space between leftmost
    and rightmost node, while paddings account for all space necessary
    to connect them.

    Additionally, elements have margins. They control minimal spacing between nodes.
    Margin is calculated as a minimal amount of space that should separate element's
    content from other elements' contents.


    Example: normal start connection point

            ┌─────────┐      ┈┈┈
            │         │      │up
         ┈┈>X───────╮ │      ┈┈┈
            │ ╭─────╯ │      │height
            │ ╰───────┼>┈┈   ┈┈┈
            │         │      │down
            └─────────┘      ┈┈┈
        ►┆┈┈┆◄┈┈┈┈┈┈┈►┆┈┈┆◄
         ┆sm┆  width  ┆em┆

    Here, `X` is element's position, as passed to the `_render` method. `sm` and `em`
    are `start_margin` and `end_margin`. `width` is equal to `content_width`.
    `start_padding` and `end_padding` are both zero.


    Example: split start connection point

    .. code-block::

            ┆   width   ┆
            ┆◄┈┈┈┈┈┈┈┈┈►┆
            ┌─┬─────────┐      ┈┈┈
            │ │         │      │up
            X╭Z───────╮ │      ┈┈┈
            │││ ╭─────╯ │      │height
            │││ ╰───────┼>┈┈   ┈┈┈
         ┈┈>Y╯│         │      │down
            └─┴─────────┘      ┈┈┈
          ►┆┈┈┆◄┈┈┈┈┈┈┈►┆┈┈┆◄
           ┆sm┆ c.width ┆em┆

    Here, `X` is element's position, and `Y` is position of the start connection point.
    `sm` and `em` are `start_margin` and `end_margin`. `c.width` is `content_width`.
    `start_padding` is distance between `X` and `Z`.

    Note that element's width includes width of element's content, plus width
    that's required to build line from connection point (Y) to the point where
    element's content actually starts (Z).

    Note also that margin starts at element's content box, not its padding box.


    Example: stack start connection point

    .. code-block::

            ┆   width   ┆
            ┆◄┈┈┈┈┈┈┈┈┈►┆
            ┆╭Y         ┆
            ┆│          ┆
            ┌┼┬─────────┐      ┈┈┈
            │││         │      │up
            X╰Z───────╮ │      ┈┈┈
            │ │ ╭─────╯ │      │height
            │ │ ╰───────┼>┈┈   ┈┈┈
            │ │         │      │down
            └─┴─────────┘      ┈┈┈
          ►┆┈┈┆◄┈┈┈┈┈┈┈►┆┈┈┆◄
           ┆sm┆ c.width ┆em┆

    Here, the situation is similar to the split connection point, but our element
    is a part of a stack. The connection line is coming from above the element.


    Optional enter and exit lines
    -----------------------------

    When an element is part of a larger optional element, it can use optional's
    bypass line to optimize its rendering.

    Consider a diagram for `(A? B)? C`. We can naively render it as such:

    .. code-block::

         ╭────────────╮
         │╭─────╮     │
         ↑↑     ↓     ↓
        ─┴┴─ A ─┴─ B ─┴─ C ──

    However, there's a potential to make it nicer. When element `(A? B)?`
    (a.k.a. outer optional) plans its layout, it communicates to its children
    that there is a bypass line above them. Inner optional can then reuse this line
    to add optional enters and exits, leading to the following result:

    .. code-block::

         ╭─────┬─────╮
         ↑     ↓     ↓
        ─┴─ A ─┴─ B ─┴─ C ──
               ^
               note: connection from optional line
                     into the element

    Specifically, `context.opt_enter_top` and `context.opt_enter_bottom` indicate
    lines that can split off *into the element*, while `context.opt_exit_top`
    and `context.opt_exit_bottom` indicate lines that the element *can split off to*.

    In the above example, the line around `(A? B)?` was `opt_enter_top` line.
    In diagram for `A (B C?)?`, the line around `(B C?)?` is `opt_exit_top`:

    .. code-block::

              ╭─────┬─────╮
              ↑     ↑     ↓
        ── A ─┴─ B ─┴─ C ─┴─
                    ^ note: connection from element
                            into the optional line


    Rendering elements right-to-left
    --------------------------------

    When rendering elements right-to-left (i.e. ``context.reverse=True``),
    everything is simply mirrored. We avoid headaches by implementing code
    for left-to-right rendering, then multiplying all offsets by -1 when rendering
    in reverse. `context.dir` is helpful here.
    """

    display_width: int = 0
    """
    Total width this element takes up on the screen. Can be larger than `_width`
    in case of stack optimizations.

    """

    content_width: int = 0
    """
    Width of element's contents.

    """

    start_padding: int = 0
    """
    Space that's required to connect element's input to its content.

    """

    end_padding: int = 0
    """
    Space that's required to connect element's content to its output.

    """

    start_margin: int = 0
    """
    Minimal space between this node's content box and content boxes of its neighbors.

    """

    end_margin: int = 0
    """
    Minimal space between this node's content box and content boxes of its neighbors.

    """

    height: int = 0
    """
    Difference between level of element's input line and its output line.

    """

    up: int = 0
    """
    Space the element occupies above its input line.

    """

    down: int = 0
    """
    Space the element occupies below its output line.

    """

    settings: LayoutSettings[T] | None = None
    """
    Used to check if settings changed from the last layout calculation,
    and re-calculate layout only if needed.

    This is necessary because auto-wrapping frequently adjusts connection types
    of sequence's children and re-calculates their layout.

    """

    context: LayoutContext | None = None
    """
    Used to check if settings changed from the last layout calculation,
    and re-calculate layout only if needed.

    This is necessary because auto-wrapping frequently adjusts connection types
    of sequence's children and re-calculates their layout.

    """

    @property
    def width(self) -> int:
        """
        Total width of an element.

        """

        return self.start_padding + self.content_width + self.end_padding

    @cached_property
    def precedence(self) -> int:
        """
        Element's precedence, used in `__str__` method.

        """

        return 3

    @cached_property
    def contains_choices(self) -> bool:
        """
        True if there are non-trivial `_Choice` elements within this element.

        Used to choose vertical spacing in certain situations
        (see `vertical_choice_separation_outer` and `vertical_choice_separation`.)

        """

        return False

    @cached_property
    def can_use_opt_enters(self) -> bool:
        """
        Indicates that this element can benefit from giving it an optional enter line.

        """

        return False

    @cached_property
    def can_use_opt_exits(self) -> bool:
        """
        Indicates that this element can benefit from giving it an optional exit line.

        """

        return False

    def _isolate(self, start: bool = True, end: bool = True):
        """
        Calling this method from `_calculate_content_layout` enables automatic handling
        of paddings and element connections.

        If called, `_isolate` returns a new version of context with adjusted enter
        and exit types and available width. After `_calculate_content_layout` finishes,
        element's paddings are expanded to accommodate connections. `_render_content`
        will receive a context with adjusted positions as well.

        """

        self.__isolated_start = start
        self.__isolated_end = end
        assert self.context
        return replace(
            self.context,
            width=max(
                0,
                self.context.width
                - (self.__start_arc_size if start else 0)
                - (self.__end_arc_size if end else 0),
            ),
            start_connection=(
                (
                    ConnectionType.NORMAL
                    if self.__start_connection is not ConnectionType.NULL
                    else ConnectionType.NULL
                )
                if start
                else self.context.start_connection
            ),
            start_top_is_clear=(True if start else self.context.start_top_is_clear),
            start_bottom_is_clear=(
                True if start else self.context.start_bottom_is_clear
            ),
            start_direction=(
                ConnectionDirection.STRAIGHT if start else self.context.start_direction
            ),
            end_connection=(
                (
                    ConnectionType.NORMAL
                    if self.__end_connection is not ConnectionType.NULL
                    else ConnectionType.NULL
                )
                if end
                else self.context.end_connection
            ),
            end_top_is_clear=(True if end else self.context.end_top_is_clear),
            end_bottom_is_clear=(True if end else self.context.end_bottom_is_clear),
            end_direction=(
                ConnectionDirection.STRAIGHT if end else self.context.end_direction
            ),
        )

    def calculate_layout(self, settings: LayoutSettings[T], context: LayoutContext):
        """
        Run layout calculation.

        """

        if settings == self.settings and context == self.context:
            return

        self.settings = settings
        self.context = context
        self.display_width = 0
        self.content_width = 0
        self.start_padding = 0
        self.start_margin = 0
        self.end_margin = 0
        self.end_padding = 0
        self.height = 0
        self.up = 0
        self.down = 0
        self.__dict__.pop("top_ridge_line", None)
        self.__dict__.pop("bottom_ridge_line", None)

        self.__start_connection = context.start_connection
        self.__start_arc_size = self.__start_connection.arc_size(settings)
        self.__end_connection = context.end_connection
        self.__end_arc_size = self.__end_connection.arc_size(settings)

        self.__isolated_start = False
        self.__isolated_end = False
        self._calculate_content_layout(settings, context)

        self.__width_before_adjustments = self.width
        self.__start_padding_before_adjustments = self.start_padding
        self.__end_padding_before_adjustments = self.end_padding
        self.__start_margin_before_adjustments = self.start_margin
        self.__end_margin_before_adjustments = self.end_margin

        if self.__isolated_start:
            self.start_padding += self.__start_arc_size
            self.display_width += self.__start_arc_size
            if self.__start_connection in (ConnectionType.STACK, ConnectionType.SPLIT):
                self.start_margin = max(
                    self.start_padding + settings.arc_margin, self.start_margin
                )
        if self.__isolated_end:
            self.end_padding += self.__end_arc_size
            self.display_width += self.__end_arc_size
            if self.__end_connection in (ConnectionType.STACK, ConnectionType.SPLIT):
                self.end_margin = max(
                    self.end_padding + settings.arc_margin, self.end_margin
                )

    def _calculate_content_layout(
        self, settings: LayoutSettings[T], context: LayoutContext
    ):
        """
        Actual layout logic implementation, called from `_calculate_layout`.

        """

        raise NotImplementedError()

    def render(self, render: Render[T], context: RenderContext):
        """
        Render the element.

        """

        render.enter(self)
        render.debug_ridge_line(context.pos, self, context.reverse)

        if self.__isolated_start:
            start_content_pos = context.pos + Vec(
                context.dir * self.__start_arc_size, 0
            )
            start_connection_pos = start_content_pos
            match self.__start_connection:
                case ConnectionType.NULL:
                    pass
                case ConnectionType.NORMAL | ConnectionType.STACK_BOUND:
                    (
                        (render)
                        .line(
                            context.start_connection_pos,
                            context.reverse,
                            "dbg-isolated-line",
                        )
                        .segment_abs(start_content_pos.x)
                    )
                case ConnectionType.STACK:
                    (
                        (render)
                        .line(
                            context.start_connection_pos,
                            context.reverse,
                            "dbg-isolated-line",
                        )
                        .bend_backward_abs(start_content_pos.y, arrow_begin=True)
                        .segment_abs(start_content_pos.x, arrow_begin=True)
                    )
                case ConnectionType.SPLIT:
                    (
                        (render)
                        .line(
                            context.start_connection_pos,
                            context.reverse,
                            "dbg-isolated-line",
                        )
                        .bend_forward_abs(start_content_pos.y, arrow_begin=True)
                        .segment_abs(start_content_pos.x, arrow_begin=True)
                    )
        else:
            start_content_pos = context.pos
            start_connection_pos = context.start_connection_pos

        if self.__isolated_end:
            end_connection_pos = start_content_pos + Vec(
                context.dir * self.__width_before_adjustments, self.height
            )
        else:
            end_connection_pos = context.end_connection_pos

        content_context = replace(
            context,
            pos=start_content_pos,
            start_connection_pos=start_connection_pos,
            end_connection_pos=end_connection_pos,
        )

        with self.__isolated_context():
            self._render_content(render, content_context)

        if self.__isolated_end:
            match self.__end_connection:
                case ConnectionType.NULL:
                    pass
                case ConnectionType.NORMAL | ConnectionType.STACK_BOUND:
                    (
                        (render)
                        .line(end_connection_pos, context.reverse, "dbg-isolated-line")
                        .segment_abs(context.end_connection_pos.x)
                    )
                case ConnectionType.STACK:
                    (
                        (render)
                        .line(end_connection_pos, context.reverse, "dbg-isolated-line")
                        .segment_abs(context.end_connection_pos.x, arrow_end=True)
                        .bend_backward_reverse_abs(
                            context.end_connection_pos.y, arrow_end=True
                        )
                    )
                case ConnectionType.SPLIT:
                    arc_radius = context.dir * math.ceil(2 * render.settings.arc_radius)
                    (
                        (render)
                        .line(end_connection_pos, context.reverse, "dbg-isolated-line")
                        .segment_abs(
                            context.end_connection_pos.x - arc_radius, arrow_end=True
                        )
                        .bend_forward_abs(context.end_connection_pos.y, arrow_end=True)
                    )

        render.debug(self, context)
        render.debug_pos(context.pos, "dbg-primary-pos")
        render.debug_pos(start_connection_pos, "dbg-isolated-pos")
        render.debug_pos(end_connection_pos, "dbg-isolated-pos")
        for opt in [
            context.opt_enter_top,
            context.opt_enter_bottom,
            context.opt_exit_top,
            context.opt_exit_bottom,
        ]:
            if opt:
                for pos in opt[1:]:
                    if pos:
                        render.debug_pos(pos, "dbg-alternative-pos")
        render.debug_pos(context.start_connection_pos, "dbg-primary-pos")
        render.debug_pos(context.end_connection_pos, "dbg-primary-pos")
        render.exit()

    def _render_content(self, render: Render[T], context: RenderContext):
        """
        Actual element rendering, called from `_render`.

        """

        raise NotImplementedError()

    @cached_property
    def top_ridge_line(self) -> RidgeLine:
        """
        Distances from input line to topmost element at the given coordinate.

        """

        with self.__isolated_context():
            ridge_line = self._calculate_top_ridge_line()
        if self.__isolated_start and self.__start_arc_size > 0:
            ridge_line = ridge_line + Vec(self.__start_arc_size, 0)
        return ridge_line

    def _calculate_top_ridge_line(self) -> RidgeLine:
        return RidgeLine(
            0,
            [
                Vec(self.start_padding, self.up),
                Vec(self.width - self.end_padding, -self.height),
            ],
        )

    @cached_property
    def bottom_ridge_line(self) -> RidgeLine:
        """
        Distances from output line to bottommost element at the given coordinate.

        """

        with self.__isolated_context():
            ridge_line = self._calculate_bottom_ridge_line()
        if self.__isolated_start and self.__start_arc_size > 0:
            ridge_line = ridge_line + Vec(self.__start_arc_size, 0)
        return ridge_line

    def _calculate_bottom_ridge_line(self) -> RidgeLine:
        return RidgeLine(
            -self.height,
            [
                Vec(self.start_padding, self.down),
                Vec(self.width - self.end_padding, 0),
            ],
        )

    @contextmanager
    def __isolated_context(self):
        start_padding = self.start_padding
        self.start_padding = self.__start_padding_before_adjustments
        end_padding = self.end_padding
        self.end_padding = self.__end_padding_before_adjustments
        start_margin = self.start_margin
        self.start_margin = self.__start_margin_before_adjustments
        end_margin = self.end_margin
        self.end_margin = self.__end_margin_before_adjustments

        yield

        self.start_padding = start_padding
        self.end_padding = end_padding
        self.start_margin = start_margin
        self.end_margin = end_margin
