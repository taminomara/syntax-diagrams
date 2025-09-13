from __future__ import annotations

import math
import typing as _t
from functools import cached_property

from syntax_diagrams._impl.render import (
    ConnectionDirection,
    ConnectionType,
    LayoutContext,
    LayoutSettings,
    Render,
    RenderContext,
)
from syntax_diagrams._impl.ridge_line import (
    RidgeLine,
    merge_ridge_lines,
    reverse_ridge_line,
)
from syntax_diagrams._impl.tree import Element
from syntax_diagrams._impl.tree.barrier import Barrier
from syntax_diagrams._impl.tree.skip import Skip
from syntax_diagrams._impl.vec import Vec

T = _t.TypeVar("T")


class OneOrMore(Element[T], _t.Generic[T]):
    _item: Element[T]
    _repeat: Element[T]
    _repeat_top: bool

    # Layout info
    repeat_pos: list[int]

    def __new__(
        cls,
        item: Element[T],
        repeat: Element[T] | None = None,
        repeat_top: bool = False,
    ) -> Element[T]:
        repeat = repeat or Skip()

        if isinstance(item, Skip) and isinstance(repeat, Skip):
            return item

        self = super().__new__(cls)

        self._item = Barrier(item)
        self._repeat = repeat
        self._repeat_top = repeat_top  # TODO

        return self

    @cached_property
    def _precedence(self) -> int:
        # OneOrMore without repeat renders as an unary operator
        return 3 if isinstance(self._repeat, Skip) else 2

    @cached_property
    def _contains_choices(self) -> bool:
        return self._item._contains_choices or self._repeat._contains_choices

    def _calculate_content_layout(
        self, settings: LayoutSettings[T], context: LayoutContext
    ):
        assert self._cached_context

        # Whether it's safe to place repeat arcs at the connection points,
        # or we need to shift them inwards.
        self._need_shift_start_arc = not (
            context.start_top_is_clear and context.start_bottom_is_clear
        )
        self._need_shift_end_arc = not (
            context.end_top_is_clear and context.end_bottom_is_clear
        )

        context = self._isolate(self._need_shift_start_arc, self._need_shift_end_arc)

        if context.is_outer:
            self._vertical_choice_separation = settings.vertical_choice_separation_outer
        else:
            self._vertical_choice_separation = settings.vertical_choice_separation

        arc_radius = math.ceil(settings.arc_radius)
        arc_size = settings.arc_margin + arc_radius

        self._start_arc_size = context.start_connection.arc_size(settings)
        self._additional_start_padding = (
            arc_size
            if self._need_shift_start_arc
            else max(arc_size, self._start_arc_size) - self._start_arc_size
        )
        self._end_arc_size = context.end_connection.arc_size(settings)
        self._additional_end_padding = (
            arc_size
            if self._need_shift_end_arc
            else max(arc_size, self._end_arc_size) - self._end_arc_size
        )

        item_context = LayoutContext(
            width=max(
                0,
                context.width
                - self._additional_start_padding
                - self._additional_end_padding,
            ),
            is_outer=False,
            start_connection=context.start_connection,
            start_direction=context.start_direction,
            end_connection=context.end_connection,
            end_direction=context.end_direction,
            allow_shrinking_stacks=context.allow_shrinking_stacks,
        )
        self._item._calculate_layout(settings, item_context)

        repeat_context = LayoutContext(
            width=max(
                0,
                context.width
                - self._additional_start_padding
                - self._additional_end_padding,
            ),
            is_outer=False,
            start_connection=ConnectionType.STACK,
            start_top_is_clear=True,
            start_bottom_is_clear=context.end_bottom_is_clear
            and (
                self._need_shift_end_arc
                or context.end_direction is not ConnectionDirection.DOWN
            ),
            start_direction=ConnectionDirection.UP,
            end_connection=ConnectionType.STACK,
            end_top_is_clear=True,
            end_bottom_is_clear=context.start_bottom_is_clear
            and (
                self._need_shift_start_arc
                or context.start_direction is not ConnectionDirection.DOWN
            ),
            end_direction=ConnectionDirection.UP,
            allow_shrinking_stacks=False,
        )
        self._repeat._calculate_layout(settings, repeat_context)

        width = max(
            self._item._width
            + self._additional_start_padding
            + self._additional_end_padding,
            self._repeat._width
            - 2 * arc_size
            + self._start_arc_size
            + self._end_arc_size
            + self._additional_start_padding
            + self._additional_end_padding,
        )
        display_width = max(
            self._item._display_width
            + self._additional_start_padding
            + self._additional_end_padding,
            self._repeat._display_width
            - 2 * arc_size
            + self._start_arc_size
            + self._end_arc_size
            + self._additional_start_padding
            + self._additional_end_padding,
        )

        self._center_offset = (
            self._start_arc_size
            + self._additional_start_padding
            + width
            - self._end_arc_size
            - self._additional_end_padding
        ) // 2

        self._repeat_content_width_l = self._repeat._content_width // 2
        self._repeat_content_width_r = (
            self._repeat._content_width - self._repeat_content_width_l
        )

        self._start_padding = min(
            self._item._start_padding + self._additional_start_padding,
            self._center_offset - self._repeat_content_width_l,
        )
        self._start_margin = max(
            0,
            self._start_padding
            - min(
                (
                    self._start_arc_size + arc_radius
                    if self._need_shift_start_arc
                    else (
                        self._start_arc_size
                        + self._additional_start_padding
                        - settings.arc_margin
                    )
                )
                - settings.arc_margin
                - arc_radius,
                self._item._start_padding
                + self._additional_start_padding
                - self._item._start_margin,
                self._center_offset
                - self._repeat_content_width_l
                - self._repeat._start_margin,
            ),
        )
        self._end_padding = max(
            0,
            width
            - max(
                self._item._start_padding
                + self._additional_start_padding
                + self._item._content_width,
                self._center_offset + self._repeat_content_width_r,
            ),
        )
        self._end_margin = max(
            0,
            max(
                self._item._start_padding
                + self._additional_start_padding
                + self._item._content_width
                + self._item._end_margin,
                self._center_offset
                + self._repeat_content_width_r
                + self._repeat._end_margin,
            )
            - (width - self._end_padding),
            self._end_padding
            - (
                self._end_arc_size + arc_radius
                if self._need_shift_end_arc
                else (
                    self._end_arc_size
                    + self._additional_end_padding
                    - settings.arc_margin
                )
            )
            + arc_radius
            + settings.arc_margin,
        )

        self._display_width = display_width
        self._content_width = max(0, width - self._start_padding - self._end_padding)

        self._up = self._item._up
        self._height = self._item._height
        self._down = (
            self._item._down
            + self._vertical_choice_separation
            + self._repeat._up
            + self._repeat._height
            + self._repeat._down
        )

    def _render_content(self, render: Render[T], context: RenderContext):
        arc_radius = math.ceil(render.settings.arc_radius)
        arc_size = render.settings.arc_margin + arc_radius

        assert self._cached_context
        if self._need_shift_start_arc:
            (
                (render)
                .line(context.start_connection_pos, context.reverse)
                .segment_abs(context.start_connection_pos.x + context.dir * arc_size)
            )
        if self._need_shift_end_arc:
            (
                (render)
                .line(context.end_connection_pos, context.reverse)
                .segment_abs(context.end_connection_pos.x - context.dir * arc_size)
            )

        item_context = RenderContext(
            pos=context.pos
            + Vec(
                context.dir * self._additional_start_padding,
                0,
            ),
            reverse=context.reverse,
            start_connection_pos=(
                context.start_connection_pos
                + Vec(
                    (context.dir * arc_size if self._need_shift_start_arc else 0),
                    0,
                )
            ),
            end_connection_pos=(
                context.end_connection_pos
                - Vec(
                    (context.dir * arc_size if self._need_shift_end_arc else 0),
                    0,
                )
            ),
        )

        self._item._render(render, item_context)

        repeat_start_connection_pos = context.pos + Vec(
            context.dir
            * (
                self._start_arc_size + arc_radius
                if self._need_shift_start_arc
                else (
                    self._start_arc_size
                    + self._additional_start_padding
                    - render.settings.arc_margin
                )
            ),
            0,
        )
        repeat_end_connection_pos = context.pos + Vec(
            context.dir
            * (
                self._width
                - (
                    self._end_arc_size + arc_radius
                    if self._need_shift_end_arc
                    else (
                        self._end_arc_size
                        + self._additional_end_padding
                        - render.settings.arc_margin
                    )
                )
            ),
            self._item._height,
        )

        center = context.pos + Vec(context.dir * self._center_offset, 0)

        repeat_context = RenderContext(
            pos=(
                center
                + Vec(
                    context.dir
                    * (self._repeat._start_padding + self._repeat_content_width_r),
                    self._item._height
                    + self._item._down
                    + self._vertical_choice_separation
                    + self._repeat._up,
                )
            ),
            start_connection_pos=repeat_end_connection_pos,
            end_connection_pos=repeat_start_connection_pos,
            reverse=not context.reverse,
        )
        self._repeat._render(render, repeat_context)

        render.debug_pos(repeat_start_connection_pos)
        render.debug_pos(repeat_end_connection_pos)
        render.debug_pos(center)

    def _calculate_top_ridge_line(self) -> RidgeLine:
        ridge_line = self._item._top_ridge_line
        if self._additional_start_padding > 0:
            return ridge_line + Vec(self._additional_start_padding, 0)
        else:
            return ridge_line

    def _calculate_bottom_ridge_line(self) -> RidgeLine:
        assert self._cached_settings

        arc_radius = math.ceil(self._cached_settings.arc_radius)
        repeat_start_connection_pos = (
            self._start_arc_size
            if self._need_shift_start_arc
            else (
                self._start_arc_size
                + self._additional_start_padding
                - self._cached_settings.arc_margin
                - arc_radius
            )
        )
        repeat_end_connection_pos = self._width - (
            self._end_arc_size
            if self._need_shift_end_arc
            else (
                self._end_arc_size
                + self._additional_end_padding
                - self._cached_settings.arc_margin
                - arc_radius
            )
        )

        x_pos = (
            self._center_offset
            + self._repeat._start_padding
            + self._repeat_content_width_r
        )
        y_pos = self._item._down + self._vertical_choice_separation + self._repeat._up
        return merge_ridge_lines(
            reverse_ridge_line(self._repeat._bottom_ridge_line, x_pos)
            + Vec(0, y_pos + self._repeat._height),
            RidgeLine(
                -self._height,
                [
                    Vec(repeat_start_connection_pos, self._down),
                    Vec(repeat_end_connection_pos, 0),
                ],
            ),
            cmp=min,
        )

    def __str__(self):
        if isinstance(self._repeat, Skip):
            return (
                f"{self._item}+"
                if self._item._precedence >= self._precedence
                else f"({self._item})+"
            )
        else:
            item = (
                f"{self._item}"
                if self._item._precedence >= self._precedence
                else f"({self._item})"
            )
            repeat = (
                f"{self._repeat}"
                if self._repeat._precedence >= self._precedence
                else f"({self._repeat})"
            )
            return f"{item} ({repeat} {item})*"
