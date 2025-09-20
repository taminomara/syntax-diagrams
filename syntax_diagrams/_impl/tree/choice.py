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
    find_distance,
    merge_ridge_lines,
)
from syntax_diagrams._impl.tree import Element
from syntax_diagrams._impl.tree.skip import Skip
from syntax_diagrams._impl.vec import Vec

T = _t.TypeVar("T")


class Choice(Element[T], _t.Generic[T]):
    _default: int
    _items: list[Element[T]]
    _has_skip: bool
    _is_optional: bool

    _connect_opt_enter: bool
    _connect_opt_exit: bool
    _layout: list[tuple[Element[T], int]]
    _start_connection: ConnectionType
    _end_connection: ConnectionType
    _upper_rail_can_use_added_opt_enters: bool
    _upper_rail_can_use_added_opt_exits: bool
    _lower_rail_can_use_added_opt_enters: bool
    _lower_rail_can_use_added_opt_exits: bool

    def __new__(cls, items: list[Element[T]], default: int) -> Element[T]:
        if len(items) == 0:
            return Skip()
        elif len(items) == 1:
            return items[0]

        assert 0 <= default < len(items)

        merged_default = 0
        merged_items: list[Element[T]] = []
        for i, item in enumerate(items):
            if isinstance(item, Choice):
                if i == default:
                    merged_default = len(merged_items) + item._default
                merged_items.extend(item._items)
            else:
                if i == default:
                    merged_default = len(merged_items)
                merged_items.append(item)

        filtered_items: list[Element[T]] = []
        filtered_default = 0
        seen_skip = isinstance(merged_items[merged_default], Skip)
        for i, item in enumerate(merged_items):
            if i == merged_default:
                filtered_default = len(filtered_items)
            elif isinstance(item, Skip):
                if seen_skip:
                    continue
                else:
                    seen_skip = True
            filtered_items.append(item)

        if len(filtered_items) == 1:
            return filtered_items[0]

        self = super().__new__(cls)
        self._items = filtered_items
        self._default = filtered_default
        self._has_skip = seen_skip
        self._is_optional = seen_skip and len(self._items) == 2

        return self

    @cached_property
    def precedence(self) -> int:
        # Optional renders as an unary operator
        return 3 if self._has_skip else 1

    @cached_property
    def contains_choices(self) -> bool:
        # Optionals are not true choices
        return not self._is_optional

    @cached_property
    def can_use_opt_enters(self) -> bool:
        return self._has_skip

    @cached_property
    def can_use_opt_exits(self) -> bool:
        return self._has_skip

    def _calculate_content_layout(
        self, settings: LayoutSettings[T], context: LayoutContext
    ):
        skip_skips = False
        self._connect_opt_enter = False
        self._connect_opt_exit = False
        if self._has_skip:
            if (context.opt_enter_top and context.opt_exit_top) or (
                context.opt_enter_bottom and context.opt_exit_bottom
            ):
                # If we have enter and exit on the same side, they belong to the same
                # line, so we can skip skips without adding new connections.
                skip_skips = True
            else:
                # Otherwise, we'll note both. We can choose either of them later.
                if context.opt_enter_top or context.opt_enter_bottom:
                    skip_skips = True
                    self._connect_opt_enter = True
                if context.opt_exit_top or context.opt_exit_bottom:
                    skip_skips = True
                    self._connect_opt_exit = True

        if skip_skips:
            items: list[Element[T]] = []
            default = 0
            for i, item in enumerate(self._items):
                if i == self._default:
                    default = len(items)
                if not isinstance(item, Skip):
                    items.append(item)
            if default >= len(items):
                default = len(items) - 1
        else:
            default = self._default
            items = self._items

        if len(items) == 1:
            self._start_connection = context.start_connection
            if (
                self._start_connection
                in (
                    ConnectionType.NORMAL,
                    ConnectionType.STACK_BOUND,
                )
                and self._connect_opt_exit
            ):
                self._start_connection = ConnectionType.SPLIT
            self._end_connection = context.end_connection
            if (
                self._end_connection
                in (
                    ConnectionType.NORMAL,
                    ConnectionType.STACK_BOUND,
                )
                and self._connect_opt_enter
            ):
                self._end_connection = ConnectionType.SPLIT
        else:
            self._start_connection = context.start_connection
            if self._start_connection in (
                ConnectionType.NORMAL,
                ConnectionType.STACK_BOUND,
            ):
                self._start_connection = ConnectionType.SPLIT
            self._end_connection = context.end_connection
            if self._end_connection in (
                ConnectionType.NORMAL,
                ConnectionType.STACK_BOUND,
            ):
                self._end_connection = ConnectionType.SPLIT

            self._upper_rail_can_use_added_opt_enters = False
            self._upper_rail_can_use_added_opt_exits = False
            self._lower_rail_can_use_added_opt_enters = False
            self._lower_rail_can_use_added_opt_exits = False

            for i, item in enumerate(items):
                if isinstance(item, Skip):
                    if i > 0:
                        upper_rail = items[i - 1]
                        self._upper_rail_can_use_added_opt_enters = (
                            upper_rail.can_use_opt_enters
                        )
                        self._upper_rail_can_use_added_opt_exits = (
                            upper_rail.can_use_opt_exits
                        )
                    if i < len(items) - 1:
                        lower_rail = items[i + 1]
                        self._lower_rail_can_use_added_opt_enters = (
                            lower_rail.can_use_opt_enters
                        )
                        self._lower_rail_can_use_added_opt_exits = (
                            lower_rail.can_use_opt_exits
                        )
                    break

            # Prevent optimizations that can break diagram's correctness: if one rail
            # uses an opt enter, another rail shouldn't use an opt exit
            # to the same opt line (and vice versa). Otherwise we risk drawing
            # `((AA? B) | (C DD?))?` like this:
            #
            #       ╭─ AA ─┬─ B ─╮
            #       ↑      ↑     ↓
            #     ──┼─────┬┴─────┼──
            #       ↓     ↑      ↑
            #       ╰─ C ─┴─ DD ─╯
            #
            # Here, `AA?` and `DD?` reuse the same opt line, leading to input `C B`
            # being erroneously allowed by the diagram.
            if self._upper_rail_can_use_added_opt_enters:
                self._lower_rail_can_use_added_opt_exits = False
            if self._lower_rail_can_use_added_opt_enters:
                self._upper_rail_can_use_added_opt_exits = False
            if self._upper_rail_can_use_added_opt_exits:
                self._lower_rail_can_use_added_opt_enters = False
            if self._lower_rail_can_use_added_opt_exits:
                self._upper_rail_can_use_added_opt_enters = False

        if any(item.contains_choices for item in self._items):
            vertical_separation = settings.vertical_choice_separation_outer
        else:
            vertical_separation = settings.vertical_choice_separation

        # Total element's width.
        width = 0
        display_width = 0
        # Padding between stack's left border and nearest content box.
        start_padding = None
        # Leftmost margin relative to the stack's left border. Can be negative.
        start_margin_offset = None
        # Padding between stack's right border and nearest content box.
        end_padding = None
        # Rightmost margin relative to the stack's left border.
        end_margin_offset = None

        current_pos = 0

        self._layout = []

        for i, item in enumerate(items):
            if i < default:
                direction = ConnectionDirection.DOWN
            elif i > default:
                direction = ConnectionDirection.UP
            else:
                direction = ConnectionDirection.STRAIGHT

            line_context = LayoutContext(
                width=context.width,
                is_outer=False,
                start_connection=self._start_connection,
                start_top_is_clear=(
                    context.start_top_is_clear
                    if (
                        i == 0
                        and (not self._connect_opt_exit or not context.opt_exit_top)
                    )
                    else False
                ),
                start_bottom_is_clear=(
                    context.start_bottom_is_clear
                    if (
                        i == len(items) - 1
                        and (not self._connect_opt_exit or not context.opt_exit_bottom)
                    )
                    else False
                ),
                start_direction=direction,
                end_connection=self._end_connection,
                end_top_is_clear=(
                    context.end_top_is_clear
                    if (
                        i == 0
                        and (not self._connect_opt_enter or not context.opt_enter_top)
                    )
                    else False
                ),
                end_bottom_is_clear=(
                    context.end_bottom_is_clear
                    if (
                        i == len(items) - 1
                        and (
                            not self._connect_opt_enter or not context.opt_enter_bottom
                        )
                    )
                    else False
                ),
                end_direction=direction,
                allow_shrinking_stacks=context.allow_shrinking_stacks and i == 0,
            )

            if i == 0:
                line_context.opt_enter_top = context.opt_enter_top
                line_context.opt_exit_top = context.opt_exit_top
            elif isinstance(items[i - 1], Skip):
                if self._lower_rail_can_use_added_opt_enters:
                    line_context.opt_enter_top = True
                if self._lower_rail_can_use_added_opt_exits:
                    line_context.opt_exit_top = True
            if i == len(items) - 1:
                line_context.opt_enter_bottom = context.opt_enter_bottom
                line_context.opt_exit_bottom = context.opt_exit_bottom
            elif isinstance(items[i + 1], Skip):
                if self._upper_rail_can_use_added_opt_enters:
                    line_context.opt_enter_bottom = True
                if self._upper_rail_can_use_added_opt_exits:
                    line_context.opt_exit_bottom = True

            item.calculate_layout(settings, line_context)

            if i == 0:
                current_pos += item.up
            else:
                current_pos += (
                    find_distance(items[i - 1].bottom_ridge_line, item.top_ridge_line)
                    + vertical_separation
                )

            if i == default:
                self._layout.append((item, current_pos))

                self.up = current_pos
                self.height = item.height

                for j, (item, pos) in enumerate(self._layout):
                    self._layout[j] = (item, pos - current_pos)

                current_pos = 0
            else:
                self._layout.append((item, current_pos))

            current_pos += item.height

            width = max(width, item.width)
            display_width = max(display_width, item.display_width)

            start_padding = (
                item.start_padding
                if start_padding is None
                else min(start_padding, item.start_padding)
            )
            start_margin_offset = (
                -item.start_margin + item.start_padding
                if start_margin_offset is None
                else min(
                    start_margin_offset,
                    -item.start_margin + item.start_padding,
                )
            )
            end_padding = (
                item.end_padding
                if end_padding is None
                else min(end_padding, item.end_padding)
            )
            end_margin_offset = (
                item.width + item.end_margin - item.end_padding
                if end_margin_offset is None
                else max(
                    end_margin_offset,
                    item.width + item.end_margin - item.end_padding,
                )
            )

        self.down = current_pos + items[-1].down - self.height

        start_padding = start_padding or 0
        end_padding = end_padding or 0

        self.display_width = display_width
        self.content_width = max(0, width - start_padding - end_padding)
        self.start_padding = start_padding
        self.end_padding = end_padding
        if start_margin_offset is None:
            self.start_margin = 0
        else:
            self.start_margin = max(0, (-start_margin_offset) + start_padding)
        if end_margin_offset is None:
            self.end_margin = 0
        else:
            self.end_margin = max(0, (end_margin_offset - width) + end_padding)

        if self._connect_opt_exit:
            self.start_margin = max(
                self.start_margin, settings.arc_margin + self.start_padding
            )
        if self._connect_opt_enter:
            self.end_margin = max(
                self.end_margin, settings.arc_margin + self.end_padding
            )

    def _render_content(self, render: Render[T], context: RenderContext):
        start_arc_size = self._start_connection.arc_size(render.settings)
        end_arc_size = self._end_connection.arc_size(render.settings)

        for i, (item, pos) in enumerate(self._layout):
            line_context = RenderContext(
                pos=context.pos + Vec(0, pos),
                start_connection_pos=context.start_connection_pos,
                end_connection_pos=context.end_connection_pos,
                reverse=context.reverse,
            )

            if i == 0:
                line_context.opt_enter_top = context.opt_enter_top
                line_context.opt_exit_top = context.opt_exit_top
            elif isinstance(self._layout[i - 1][0], Skip):
                line_pos = context.pos.y + self._layout[i - 1][1]
                if self._lower_rail_can_use_added_opt_enters:
                    line_context.opt_enter_top = (
                        "w" if not context.reverse else "e",
                        Vec(context.pos.x + context.dir * start_arc_size, line_pos),
                    )
                if self._lower_rail_can_use_added_opt_exits:
                    line_context.opt_exit_top = (
                        "e" if not context.reverse else "w",
                        Vec(
                            context.pos.x + context.dir * (self.width - end_arc_size),
                            line_pos,
                        ),
                        None,
                    )
            if i == len(self._layout) - 1:
                line_context.opt_enter_bottom = context.opt_enter_bottom
                line_context.opt_exit_bottom = context.opt_exit_bottom
            elif isinstance(self._layout[i + 1][0], Skip):
                line_pos = context.pos.y + self._layout[i + 1][1]
                if self._upper_rail_can_use_added_opt_enters:
                    line_context.opt_enter_bottom = (
                        "w" if not context.reverse else "e",
                        Vec(context.pos.x + context.dir * start_arc_size, line_pos),
                    )
                if self._upper_rail_can_use_added_opt_exits:
                    line_context.opt_exit_bottom = (
                        "e" if not context.reverse else "w",
                        Vec(
                            context.pos.x + context.dir * (self.width - end_arc_size),
                            line_pos,
                        ),
                        None,
                    )

            item.render(render, line_context)

        if self._connect_opt_enter and not (
            self._connect_opt_exit
            and context.opt_exit_bottom
            and context.opt_exit_bottom[2] is not None
        ):
            # Choose exit line.
            opt_enter = context.opt_enter_top or context.opt_enter_bottom
            assert opt_enter
            coming_to, opt_enter_pos = opt_enter

            # Determine directions and where the vertical line will end up.
            vertical_line_x = context.end_connection_pos.x
            if self._end_connection is ConnectionType.STACK:
                coming_from = "w" if not context.reverse else "e"
                if coming_from != coming_to:
                    vertical_line_x += context.dir * math.ceil(
                        2 * render.settings.arc_radius
                    )
            else:
                coming_from = "e" if not context.reverse else "w"
                if coming_from != coming_to:
                    vertical_line_x -= context.dir * math.ceil(
                        2 * render.settings.arc_radius
                    )

            (
                (render)
                .line(opt_enter_pos, context.reverse, "dbg-alternative-pos")
                .segment_abs(
                    vertical_line_x,
                    arrow_begin=True,
                    arrow_end=True,
                )
                .bend(
                    context.end_connection_pos.y,
                    coming_to,
                    coming_from,
                    arrow_begin=True,
                    arrow_end=True,
                )
            )
        elif self._connect_opt_exit:
            # Choose exit line.
            if context.opt_exit_bottom and context.opt_exit_bottom[2] is not None:
                # Prefer bottom if alternative position is available.
                opt_exit = context.opt_exit_bottom
            if context.opt_exit_top:
                # Otherwise, prefer top if it's there.
                opt_exit = context.opt_exit_top
            else:
                # Otherwise, use bottom.
                opt_exit = context.opt_exit_bottom
            assert opt_exit
            coming_to, opt_exit_pos, opt_exit_pos_alt = opt_exit

            # Determine directions and where the vertical line will end up.
            vertical_line_x = context.start_connection_pos.x
            if self._start_connection is ConnectionType.STACK:
                coming_from = "e" if not context.reverse else "w"
                vertical_line_x -= context.dir * render.settings.arc_radius
            else:
                coming_from = "w" if not context.reverse else "e"
                vertical_line_x += context.dir * render.settings.arc_radius

            # Special case for skipping stack rows: position of the vertical line
            # is close to the alternative exit.
            if opt_exit_pos_alt and (
                abs(opt_exit_pos_alt.x - vertical_line_x) <= render.settings.arc_radius
            ):
                opt_exit_pos = opt_exit_pos_alt
                coming_to = None

            # Draw the line.
            (
                (render)
                .line(
                    context.start_connection_pos, context.reverse, "dbg-alternative-pos"
                )
                .bend(
                    opt_exit_pos.y,
                    coming_from,
                    coming_to,
                    arrow_begin=True,
                    arrow_end=True,
                )
                .segment_abs(
                    opt_exit_pos.x,
                    arrow_begin=True,
                    arrow_end=True,
                )
            )

    def _calculate_top_ridge_line(self) -> RidgeLine:
        elem, pos = self._layout[0]
        return merge_ridge_lines(
            merge_ridge_lines(
                elem.top_ridge_line - Vec(0, pos),
                RidgeLine(
                    0,
                    [
                        Vec(0, -pos),
                        Vec(self.start_padding, -pos - elem.height),
                        Vec(self.width, -self.height),
                    ],
                ),
            ),
            RidgeLine(
                0,
                [
                    Vec(0, self.up),
                    Vec(self.display_width, -self.height),
                ],
            ),
            cmp=min,
        )

    def _calculate_bottom_ridge_line(self) -> RidgeLine:
        elem, pos = self._layout[-1]
        pos -= self.height
        return merge_ridge_lines(
            merge_ridge_lines(
                elem.bottom_ridge_line + Vec(0, pos + elem.height),
                RidgeLine(
                    -self.height,
                    [
                        Vec(0, pos),
                        Vec(self.start_padding, pos + elem.height),
                        Vec(self.width, 0),
                    ],
                ),
            ),
            RidgeLine(
                -self.height,
                [
                    Vec(0, self.down),
                    Vec(self.display_width, 0),
                ],
            ),
            cmp=min,
        )

    def __str__(self):
        is_optional = any(isinstance(item, Skip) for item in self._items)
        items = [
            f"{item}" if item.precedence >= self.precedence else f"({item})"
            for item in self._items
            if not isinstance(item, Skip)
        ]
        if is_optional and len(items) == 1:
            if items[0].endswith("+"):
                return items[0][:-1] + "*"
            else:
                return items[0] + "?"
        elif is_optional:
            return "(" + " | ".join(items) + ")?"
        else:
            return " | ".join(items)
