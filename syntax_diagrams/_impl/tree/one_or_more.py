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
    def precedence(self) -> int:
        # OneOrMore without repeat renders as an unary operator
        return 3 if isinstance(self._repeat, Skip) else 2

    @cached_property
    def contains_choices(self) -> bool:
        return self._item.contains_choices or self._repeat.contains_choices

    def _calculate_content_layout(
        self, settings: LayoutSettings[T], context: LayoutContext
    ):
        assert self.context

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
        self._item.calculate_layout(settings, item_context)

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
        self._repeat.calculate_layout(settings, repeat_context)

        width = max(
            self._item.width
            + self._additional_start_padding
            + self._additional_end_padding,
            self._repeat.width
            - 2 * arc_size
            + self._start_arc_size
            + self._end_arc_size
            + self._additional_start_padding
            + self._additional_end_padding,
        )
        display_width = max(
            self._item.display_width
            + self._additional_start_padding
            + self._additional_end_padding,
            self._repeat.display_width
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

        self._repeat_content_width_l = self._repeat.content_width // 2
        self._repeat_content_width_r = (
            self._repeat.content_width - self._repeat_content_width_l
        )

        self.start_padding = min(
            self._item.start_padding + self._additional_start_padding,
            self._center_offset - self._repeat_content_width_l,
        )
        self.start_margin = max(
            0,
            self.start_padding
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
                self._item.start_padding
                + self._additional_start_padding
                - self._item.start_margin,
                self._center_offset
                - self._repeat_content_width_l
                - self._repeat.start_margin,
            ),
        )
        self.end_padding = max(
            0,
            width
            - max(
                self._item.start_padding
                + self._additional_start_padding
                + self._item.content_width,
                self._center_offset + self._repeat_content_width_r,
            ),
        )
        self.end_margin = max(
            0,
            max(
                self._item.start_padding
                + self._additional_start_padding
                + self._item.content_width
                + self._item.end_margin,
                self._center_offset
                + self._repeat_content_width_r
                + self._repeat.end_margin,
            )
            - (width - self.end_padding),
            self.end_padding
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

        self.display_width = display_width
        self.content_width = max(0, width - self.start_padding - self.end_padding)

        self.up = self._item.up
        self.height = self._item.height
        self.down = (
            self._item.down
            + self._vertical_choice_separation
            + self._repeat.up
            + self._repeat.height
            + self._repeat.down
        )

    def _render_content(self, render: Render[T], context: RenderContext):
        arc_radius = math.ceil(render.settings.arc_radius)
        arc_size = render.settings.arc_margin + arc_radius

        assert self.context
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

        self._item.render(render, item_context)

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
                self.width
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
            self._item.height,
        )

        center = context.pos + Vec(context.dir * self._center_offset, 0)

        repeat_context = RenderContext(
            pos=(
                center
                + Vec(
                    context.dir
                    * (self._repeat.start_padding + self._repeat_content_width_r),
                    self._item.height
                    + self._item.down
                    + self._vertical_choice_separation
                    + self._repeat.up,
                )
            ),
            start_connection_pos=repeat_end_connection_pos,
            end_connection_pos=repeat_start_connection_pos,
            reverse=not context.reverse,
        )
        self._repeat.render(render, repeat_context)

        render.debug_pos(repeat_start_connection_pos)
        render.debug_pos(repeat_end_connection_pos)
        render.debug_pos(center)

    def _calculate_top_ridge_line(self) -> RidgeLine:
        ridge_line = self._item.top_ridge_line
        if self._additional_start_padding > 0:
            return ridge_line + Vec(self._additional_start_padding, 0)
        else:
            return ridge_line

    def _calculate_bottom_ridge_line(self) -> RidgeLine:
        assert self.settings

        arc_radius = math.ceil(self.settings.arc_radius)
        repeat_start_connection_pos = (
            self._start_arc_size
            if self._need_shift_start_arc
            else (
                self._start_arc_size
                + self._additional_start_padding
                - self.settings.arc_margin
                - arc_radius
            )
        )
        repeat_end_connection_pos = self.width - (
            self._end_arc_size
            if self._need_shift_end_arc
            else (
                self._end_arc_size
                + self._additional_end_padding
                - self.settings.arc_margin
                - arc_radius
            )
        )

        x_pos = (
            self._center_offset
            + self._repeat.start_padding
            + self._repeat_content_width_r
        )
        y_pos = self._item.down + self._vertical_choice_separation + self._repeat.up
        return merge_ridge_lines(
            reverse_ridge_line(self._repeat.bottom_ridge_line, x_pos)
            + Vec(0, y_pos + self._repeat.height),
            RidgeLine(
                -self.height,
                [
                    Vec(repeat_start_connection_pos, self.down),
                    Vec(repeat_end_connection_pos, 0),
                ],
            ),
            cmp=min,
        )

    def __str__(self):
        if isinstance(self._repeat, Skip):
            return (
                f"{self._item}+"
                if self._item.precedence >= self.precedence
                else f"({self._item})+"
            )
        else:
            item = (
                f"{self._item}"
                if self._item.precedence >= self.precedence
                else f"({self._item})"
            )
            repeat = (
                f"{self._repeat}"
                if self._repeat.precedence >= self.precedence
                else f"({self._repeat})"
            )
            return f"{item} ({repeat} {item})*"
