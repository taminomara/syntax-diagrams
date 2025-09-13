from __future__ import annotations

import itertools
import math
import typing as _t
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
from syntax_diagrams._impl.ridge_line import RidgeLine, merge_ridge_lines
from syntax_diagrams._impl.tree import Element
from syntax_diagrams._impl.tree.choice import Choice
from syntax_diagrams._impl.tree.skip import Skip
from syntax_diagrams._impl.vec import Vec
from syntax_diagrams.element import LineBreak

T = _t.TypeVar("T")


class Sequence(Element[T], _t.Generic[T]):
    _items: list[Element[T]]
    _linebreaks: list[LineBreak]

    _item_rows: list[list[Element[T]]]
    _item_rows_layout: list[tuple[int | None, int, int]]
    _start_connection: ConnectionType
    _end_connection: ConnectionType
    _shift_first_line: bool

    def __new__(
        cls,
        items: list[Element[T]],
        linebreaks: list[LineBreak] | LineBreak | None = None,
    ) -> Element[T]:
        if len(items) == 1:
            return items[0]
        elif len(items) == 0 or all(isinstance(item, Skip) for item in items):
            return Skip()

        if isinstance(linebreaks, LineBreak):
            linebreaks = [linebreaks] * (len(items) - 1)
        elif linebreaks is None:
            linebreaks = [LineBreak.DEFAULT] * (len(items) - 1)
        if len(items) != len(linebreaks) + 1:
            raise ValueError(
                f"number of line breaks (={len(linebreaks)}) "
                f"must be one less than number of items (={len(items)})"
            )

        self = super().__new__(cls)

        self._items = []
        self._linebreaks = []

        for item, linebreak in itertools.zip_longest(items, linebreaks):
            if isinstance(item, Sequence):
                self._items.extend(item._items)  # type: ignore
                self._linebreaks.extend(item._linebreaks)
            else:
                self._items.append(item)
            if linebreak is not None:
                self._linebreaks.append(linebreak)

        return self

    @cached_property
    def _precedence(self) -> int:
        return 2

    @cached_property
    def _contains_choices(self) -> bool:
        return any(item._contains_choices for item in self._items)

    @cached_property
    def _can_use_opt_enters(self) -> bool:
        return self._items[0]._can_use_opt_enters

    @cached_property
    def _can_use_opt_exits(self) -> bool:
        return self._items[-1]._can_use_opt_exits

    def _calculate_content_layout(
        self, settings: LayoutSettings[T], context: LayoutContext
    ):
        if LineBreak.HARD not in self._linebreaks:
            single_line_width = self._calculate_layout_single_line(settings, context)
            if single_line_width <= context.width or all(
                linebreak is LineBreak.NO_BREAK for linebreak in self._linebreaks
            ):
                self._item_rows = [self._items]
                self._calculate_layout_metrics(settings, context)
                return

        # Isolate stack to avoid intersections. We could be smarter and avoid isolation
        # by adjusting starting positions of continuation lines. However,
        # the implementation is complicated as it is now, so I'd rather not do this.
        context = self._isolate(
            context.start_direction is ConnectionDirection.DOWN
            or not context.start_bottom_is_clear,
            context.end_direction is ConnectionDirection.UP
            or not context.end_top_is_clear,
        )
        self._calculate_layout_multi_line(settings, context)
        self._calculate_layout_metrics(settings, context)

    def _calculate_layout_single_line(
        self,
        settings: LayoutSettings[T],
        context: LayoutContext,
    ):
        self._start_connection = context.start_connection
        self._end_connection = context.end_connection
        self._shift_first_line = False

        width = 0

        for i, item in enumerate(self._items):
            item_context = LayoutContext(
                width=context.width,
                is_outer=context.is_outer,
                start_top_is_clear=True,
                start_bottom_is_clear=True,
                start_direction=ConnectionDirection.STRAIGHT,
                end_top_is_clear=True,
                end_bottom_is_clear=True,
                end_direction=ConnectionDirection.STRAIGHT,
                allow_shrinking_stacks=False,
            )
            if i == 0:
                item_context.opt_enter_top = context.opt_enter_top
                item_context.opt_enter_bottom = context.opt_enter_bottom
                item_context.start_connection = self._start_connection
                item_context.start_top_is_clear = context.start_top_is_clear
                item_context.start_bottom_is_clear = context.start_bottom_is_clear
            if i == len(self._items) - 1:
                item_context.opt_exit_top = context.opt_exit_top
                item_context.opt_exit_bottom = context.opt_exit_bottom
                item_context.end_connection = self._end_connection
                item_context.end_top_is_clear = context.end_top_is_clear
                item_context.end_bottom_is_clear = context.end_bottom_is_clear
                item_context.allow_shrinking_stacks = context.allow_shrinking_stacks
            item._calculate_layout(settings, item_context)
            if i > 0:
                gap = self._calculate_gap(self._items[i - 1], item, settings)
                width += gap
            width += item._width
        return width

    def _calculate_layout_multi_line(
        self,
        settings: LayoutSettings[T],
        context: LayoutContext,
    ):
        arc_size = ConnectionType.STACK.arc_size(settings)

        # Like `NORMAL`, but adds extra gap to line up nodes in the first
        # and subsequent rows. This nicely lines up all first nodes in all rows.
        self._start_connection = (
            ConnectionType.STACK_BOUND
            if context.start_connection is ConnectionType.NORMAL
            else context.start_connection
        )
        # `context.end_connection` is `NORMAL` because we're isolated.
        self._end_connection = context.end_connection
        # Shift all lines except first by one arc radius to line them up
        # with the first one.
        self._shift_first_line = (
            isinstance(self._items[0], Choice)
            or self._start_connection is ConnectionType.SPLIT
        )

        self._item_rows = []

        current_row: list[Element[T]] = []
        current_width = 0

        last_soft_break_idx = 0
        width_at_last_soft_break = 0
        margin_after_last_soft_break = 0

        # TODO!
        # last_normal_break_idx = 0
        # width_at_last_normal_break = 0
        # margin_after_last_normal_break = 0

        for i, (item, linebreak) in enumerate(
            itertools.zip_longest(self._items, self._linebreaks)
        ):
            # Adjust line width for first line shift.
            if i == 0 and self._shift_first_line:
                max_line_width = context.width - math.floor(settings.arc_radius)
            else:
                max_line_width = context.width

            # Prepare item's layout context.
            item_context = LayoutContext(
                width=max_line_width,
                is_outer=context.is_outer,
                start_top_is_clear=True,
                start_bottom_is_clear=True,
                start_direction=ConnectionDirection.STRAIGHT,
                end_top_is_clear=True,
                end_bottom_is_clear=True,
                end_direction=ConnectionDirection.STRAIGHT,
                allow_shrinking_stacks=False,
            )
            if i == 0:
                item_context.opt_enter_top = context.opt_enter_top
                item_context.start_connection = self._start_connection
                item_context.start_top_is_clear = context.start_top_is_clear
                item_context.start_bottom_is_clear = context.start_bottom_is_clear
                item_context.start_direction = context.start_direction
            elif not current_row:
                item_context.start_connection = ConnectionType.STACK
                item_context.start_direction = ConnectionDirection.UP
            if i == len(self._items) - 1:
                item_context.opt_exit_bottom = context.opt_exit_bottom
                item_context.end_connection = self._end_connection
                item_context.end_top_is_clear = context.end_top_is_clear
                item_context.end_bottom_is_clear = context.end_bottom_is_clear
                item_context.end_direction = context.end_direction
                item_context.allow_shrinking_stacks = context.allow_shrinking_stacks

            # Calculate item's layout.
            item._calculate_layout(settings, item_context)

            # Calculate margin between current node and the previous one, if any.
            if current_row:
                margin = self._calculate_gap(current_row[-1], item, settings)
            else:
                margin = 0

            # Make a soft break, if needed and possible.
            if (
                current_row
                and current_width + margin + item._width + arc_size > max_line_width
                and last_soft_break_idx
            ):
                self._item_rows.append(current_row[:last_soft_break_idx])
                current_row = current_row[last_soft_break_idx:]
                current_width -= width_at_last_soft_break + margin_after_last_soft_break
                last_soft_break_idx = 0
                width_at_last_soft_break = 0
                margin_after_last_soft_break = 0
                max_line_width = context.width
                item_context = replace(
                    item_context,
                    width=max_line_width,
                    start_connection=ConnectionType.STACK,
                    start_direction=ConnectionDirection.UP,
                )
                if current_row:
                    # Item at `last_soft_break_idx` is now first in its row.
                    # Recalculate its layout to account for stack connection.
                    current_width -= current_row[0]._width
                    current_row[0]._calculate_layout(settings, item_context)
                    current_width += current_row[0]._width
                    margin = self._calculate_gap(current_row[-1], item, settings)
                else:
                    # Current item is now first in its row. Recalculate its layout
                    # to account for stack connection.
                    item._calculate_layout(settings, item_context)
                    margin = 0

            # If we still need a break, then a soft break wasn't possible
            # (or enough), so we'll have to break here.
            if (
                current_row
                and current_width + margin + item._width + arc_size > max_line_width
            ):
                self._item_rows.append(current_row)

                current_row = []
                current_width = 0
                last_soft_break_idx = 0
                width_at_last_soft_break = 0
                margin_after_last_soft_break = 0
                margin = 0
                max_line_width = context.width
                item_context = replace(
                    item_context,
                    width=max_line_width,
                    start_connection=ConnectionType.STACK,
                    start_direction=ConnectionDirection.UP,
                )
                # Current item is now first in its row. Recalculate its layout
                # to account for stack connection
                item._calculate_layout(settings, item_context)

            current_row.append(item)
            current_width += margin + item._width

            if linebreak is LineBreak.HARD:
                self._item_rows.append(current_row)
                current_row = []
                current_width = 0
                last_soft_break_idx = 0
                width_at_last_soft_break = 0
                margin_after_last_soft_break = 0
            elif linebreak is LineBreak.SOFT:
                last_soft_break_idx = len(current_row)
                width_at_last_soft_break = current_width
            elif i == last_soft_break_idx:
                margin_after_last_soft_break = margin

        if current_row:
            self._item_rows.append(current_row)

        # Re-calculate layout for every last item of every row except for the last one.
        # This enables stack connections for them, and gives them an opportunity
        # to use carry line as optional exit.
        #
        # Consider `A B? C`:
        #
        #     ── A ─┬─ B ─╮
        #           ↓     ↓
        #     ╭─────┴─────╯  < note: carry line used as optional exit.
        #     ↓
        #     ╰─ C ──
        for i, row in enumerate(self._item_rows[:-1]):
            item_context = row[-1]._cached_context
            assert item_context
            item_context = replace(
                item_context,
                end_connection=ConnectionType.STACK,
                end_direction=ConnectionDirection.DOWN,
                opt_exit_bottom=True,
                allow_shrinking_stacks=True,
            )
            row[-1]._calculate_layout(settings, item_context)

    def _calculate_layout_metrics(
        self, settings: LayoutSettings[T], context: LayoutContext
    ):
        self._item_rows_layout = []

        if context.is_outer:
            self._vertical_seq_separation = settings.vertical_seq_separation_outer
        else:
            self._vertical_seq_separation = settings.vertical_seq_separation

        self._line_shift = (
            math.floor(settings.arc_radius) if self._shift_first_line else 0
        )

        # Total element's width.
        width = 0
        display_width = 0
        # Width of the last row.
        row_width = 0
        # Padding between stack's left border and nearest content box.
        start_padding = None
        # Leftmost margin relative to the stack's left border. Can be negative.
        start_margin_offset = None
        # Rightmost padding relative to the stack's left border.
        end_padding_offset = None
        # Rightmost margin relative to the stack's left border.
        end_margin_offset = None

        pos = 0

        for i, row in enumerate(self._item_rows):
            row_up = 0
            row_down_offset = 0
            row_width = 0
            row_pos = 0

            line_shift = self._line_shift if i > 0 else 0
            row_width += line_shift

            for j, item in enumerate(row):
                if j == 0:
                    start_padding = (
                        item._start_padding + line_shift
                        if start_padding is None
                        else min(start_padding, item._start_padding + line_shift)
                    )
                    start_margin_offset = (
                        line_shift - item._start_margin + item._start_padding
                        if start_margin_offset is None
                        else min(
                            start_margin_offset,
                            line_shift - item._start_margin + item._start_padding,
                        )
                    )

                if j > 0:
                    gap = self._calculate_gap(row[j - 1], item, settings)
                    row_width += gap

                row_width += item._width

                if j == len(row) - 1:
                    end_padding_offset = (
                        row_width - item._end_padding
                        if end_padding_offset is None
                        else max(end_padding_offset, row_width - item._end_padding)
                    )
                    end_margin_offset = (
                        row_width + item._end_margin - item._end_padding
                        if end_margin_offset is None
                        else max(
                            end_margin_offset,
                            row_width + item._end_margin - item._end_padding,
                        )
                    )

                row_up = max(row_up, item._up - row_pos)
                row_pos += item._height
                row_down_offset = max(row_down_offset, row_pos + item._down)

            width = max(width, row_width)
            row_display_width = row_width - row[-1]._width + row[-1]._display_width
            display_width = max(display_width, row_display_width)

            if i > 0:
                row_upper_line = pos
                pos += self._vertical_seq_separation + row_up
                self._item_rows_layout.append((row_upper_line, pos, row_display_width))
            else:
                self._up = row_up
                self._item_rows_layout.append((None, pos, row_display_width))

            if i < len(self._item_rows) - 1:
                pos += row_down_offset + self._vertical_seq_separation
            else:
                pos += row_pos
                self._down = max(0, row_down_offset - row_pos)

        self._height = pos

        self._display_width = display_width

        start_padding = start_padding or 0
        if context.allow_shrinking_stacks:
            # We can use width of the last row instead of the width of the longest row.
            last_elem = self._item_rows[-1][-1]
            width = row_width
            end_padding = last_elem._end_padding
            end_margin_offset = width - last_elem._end_padding + last_elem._end_margin
        else:
            end_padding = max(0, width - (end_padding_offset or 0))

        self._content_width = max(0, width - start_padding - end_padding)
        self._start_padding = start_padding
        self._end_padding = end_padding
        if start_margin_offset is None:
            self._start_margin = 0
        else:
            self._start_margin = max(0, (-start_margin_offset) + start_padding)
        if end_margin_offset is None:
            self._end_margin = 0
        else:
            self._end_margin = max(0, (end_margin_offset - width) + end_padding)

    def _render_content(self, render: Render[T], context: RenderContext):
        arc_radius = math.ceil(render.settings.arc_radius)

        for i, row in enumerate(self._item_rows):
            row_upper_line, row_pos, _ = self._item_rows_layout[i]
            row_lower_line, next_row_pos, _ = (
                self._item_rows_layout[i + 1]
                if i < len(self._item_rows) - 1
                else (None, None, None)
            )

            if i == 0:
                pos = context.pos + Vec(0, row_pos)
            else:
                pos = context.pos + Vec(context.dir * self._line_shift, row_pos)

            for j, item in enumerate(row):
                if j > 0:
                    gap = self._calculate_gap(row[j - 1], item, render.settings)
                    render.line(pos, context.reverse).segment_abs(
                        pos.x + context.dir * gap
                    )
                    pos = pos + Vec(context.dir * gap, 0)

                if j == 0 and row_upper_line:
                    start_connection_pos = context.pos + Vec(
                        context.dir * (self._line_shift + arc_radius),
                        row_upper_line,
                    )
                elif j == 0:
                    start_connection_pos = context.start_connection_pos
                else:
                    start_connection_pos = pos

                end_pos = pos + Vec(context.dir * item._width, item._height)

                if j == len(row) - 1 and row_lower_line:
                    end_connection_pos = Vec(
                        end_pos.x - context.dir * arc_radius,
                        context.pos.y + row_lower_line,
                    )
                elif j == len(row) - 1:
                    end_connection_pos = context.end_connection_pos
                else:
                    end_connection_pos = end_pos

                item_context = RenderContext(
                    pos=pos,
                    start_connection_pos=start_connection_pos,
                    end_connection_pos=end_connection_pos,
                    reverse=context.reverse,
                )

                if i == 0 and j == 0:
                    if row_upper_line is None:
                        item_context.opt_enter_top = context.opt_enter_top
                    if row_lower_line is None:
                        item_context.opt_enter_bottom = context.opt_enter_bottom
                if i == len(self._item_rows) - 1 and j == len(row) - 1:
                    if row_upper_line is None:
                        item_context.opt_exit_top = context.opt_exit_top
                    if row_lower_line is None:
                        item_context.opt_exit_bottom = context.opt_exit_bottom
                if j == len(row) - 1 and row_lower_line is not None:
                    assert next_row_pos is not None
                    item_context.opt_exit_bottom = (
                        "w" if not context.reverse else "e",
                        (
                            context.pos
                            + Vec(
                                context.dir * (self._line_shift + arc_radius),
                                row_lower_line,
                            )
                        ),
                        (
                            context.pos
                            + Vec(
                                context.dir * self._line_shift,
                                row_lower_line
                                + min(
                                    arc_radius,
                                    math.ceil((next_row_pos - row_lower_line) / 2),
                                ),
                            )
                        ),
                    )

                item._render(render, item_context)

                pos = end_pos

            if row_lower_line is not None:
                line_start = Vec(
                    pos.x - context.dir * arc_radius,
                    context.pos.y + row_lower_line,
                )
                (
                    (render)
                    .line(line_start, context.reverse)
                    .segment_abs(
                        context.dir * self._line_shift
                        + context.pos.x
                        + context.dir * arc_radius
                    )
                )

    def _calculate_top_ridge_line(self) -> RidgeLine:
        assert self._cached_settings

        seen_width = 0

        result = RidgeLine(-self._height, [])

        for i, row in enumerate(self._item_rows):
            _, row_pos, row_display_width = self._item_rows_layout[i]

            if row_display_width < seen_width:
                continue

            if i == 0:
                pos = Vec(0, -row_pos)
            else:
                pos = Vec(self._line_shift, -row_pos)

            row_ridge = RidgeLine(-self._height, [])

            for j, item in enumerate(row):
                if j > 0:
                    gap = self._calculate_gap(row[j - 1], item, self._cached_settings)
                    pos = pos + Vec(gap, 0)

                item_ridge = item._top_ridge_line + pos
                row_ridge = merge_ridge_lines(row_ridge, item_ridge)

                end_pos = pos + Vec(item._width, -item._height)

                pos = end_pos

            seen_width = max(seen_width, row_display_width)

            row_ridge = merge_ridge_lines(
                row_ridge,
                RidgeLine(
                    self._up,
                    [
                        Vec(row_display_width, -self._height),
                    ],
                ),
                cmp=min,
            )
            result = merge_ridge_lines(result, row_ridge)

        return result

    def _calculate_bottom_ridge_line(self) -> RidgeLine:
        assert self._cached_settings

        row = self._item_rows[-1]

        pos = Vec(0, self._item_rows_layout[-1][1] - self._height)
        before = pos.y
        if len(self._item_rows) > 1:
            pos = pos + Vec(self._line_shift, 0)

        result = RidgeLine(pos.y, [])
        for i, item in enumerate(row):
            if i > 0:
                gap = self._calculate_gap(row[i - 1], item, self._cached_settings)
                pos = pos + Vec(gap, 0)
            pos = pos + Vec(0, item._height)
            item_ridge = item._bottom_ridge_line + pos
            item_ridge.before = before
            result = merge_ridge_lines(result, item_ridge)
            pos = pos + Vec(item._width, 0)

        return merge_ridge_lines(
            result,
            RidgeLine(
                -self._height,
                [
                    Vec(0, self._down),
                    Vec(self._display_width, 0),
                ],
            ),
            cmp=min,
        )

    @staticmethod
    def _calculate_gap(
        prev: Element[T], next: Element[T], settings: LayoutSettings[_t.Any]
    ) -> int:
        prev_gap = prev._end_margin - prev._end_padding - next._start_padding
        next_gap = next._start_margin - next._start_padding - prev._end_padding
        return max(0, prev_gap, next_gap, settings.arc_margin)

    def __str__(self):
        return " ".join(
            f"{item}" if item._precedence >= self._precedence else f"({item})"
            for item in self._items
        )
