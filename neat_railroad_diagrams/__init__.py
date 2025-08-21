from __future__ import annotations

import io
import itertools
import math
import re
import sys
import typing as _t
from dataclasses import dataclass, field
from enum import Enum

import grapheme  # type: ignore
import wcwidth  # type: ignore

###############################################################################
# Building a diagram
###############################################################################


def sequence(
    *items: DiagramNode, linebreaks: list[LineBreak] | None = None
) -> DiagramNode:
    """
    Create a sequence of nodes.

    :param linebreaks:
        optional array of explicit line breaks. If given, ``linebreaks``
        must be one item shorter than ``items``.

    """

    return _Sequence(list(items), linebreaks)


def stack(*items: DiagramNode) -> DiagramNode:
    """
    Create a stack of nodes. That is, a sequence with a hard line break
    after each element.

    """

    return sequence(*items, linebreaks=[LineBreak.HARD] * (len(items) - 1))


def choice(*items: DiagramNode, default: int = 0):
    """
    Create a multi choice node.

    :param default:
        index of item that will be placed on the main line.

    """

    return _Choice(default, list(items))


def optional(item: DiagramNode, skip: bool = False) -> DiagramNode:
    """
    Create an optional node.

    :param skip:
        if ``True``, the node will be rendered off the main line.

    """

    return choice(_Sequence.SKIP, item, default=0 if skip else 1)


def one_or_more(item: DiagramNode, repeat: DiagramNode | None = None) -> DiagramNode:
    """
    Repeat a node one or more times.

    :param repeat:
        a node that will be placed on the backwards path.

    """

    return _OneOrMore(item, repeat)


def zero_or_more(item: DiagramNode, repeat: DiagramNode | None = None) -> DiagramNode:
    """
    Repeat a node zero or more times.

    :param repeat:
        a node that will be placed on the backwards path.

    """

    return optional(one_or_more(item, repeat))


def terminal(
    text: str,
    href: str | None = None,
    css_class: str = "node terminal",
    resolve: bool = True,
    title_is_weak: bool = False,
):
    """
    Create a terminal text node.

    :param text:
        node text. Must be a single line.
    :param href:
        optional link that will be added to the node in SVG render.
        Text renderer ignores this parameter.
    :param css_class:
        css class that will be added to the node's ``<g>`` element in SVG.
    :param resolve:
        if ``True``, node's text and href will be pre-processed
        by a :class:`HrefResolver` before rendering.
    :param title_is_weak:
        an additional parameter that will be passed to a :class:`HrefResolver`.
        Intended to indicate whether node's text is given by a user or generated
        automatically.

    """

    return _Node(_Node.Style.TERMINAL, text, href, css_class, resolve, title_is_weak)


def non_terminal(
    text: str,
    href: str | None = None,
    css_class: str = "node non-terminal",
    resolve: bool = True,
    title_is_weak: bool = False,
):
    """
    Create a non-terminal text node.

    :param text:
        node text. Must be a single line.
    :param href:
        optional link that will be added to the node in SVG render.
        Text renderer ignores this parameter.
    :param css_class:
        css class that will be added to the node's ``<g>`` element in SVG.
    :param resolve:
        if ``True``, node's text and href will be pre-processed
        by a :class:`HrefResolver` before rendering.
    :param title_is_weak:
        an additional parameter that will be passed to a :class:`HrefResolver`.
        Intended to indicate whether node's text is given by a user or generated
        automatically.

    """

    return _Node(
        _Node.Style.NON_TERMINAL, text, href, css_class, resolve, title_is_weak
    )


def comment(
    text: str,
    href: str | None = None,
    css_class: str = "node comment",
    resolve: bool = False,
    title_is_weak: bool = False,
):
    """
    Create a comment text node.

    :param text:
        node text. Must be a single line.
    :param href:
        optional link that will be added to the node in SVG render.
        Text renderer ignores this parameter.
    :param css_class:
        css class that will be added to the node's ``<g>`` element in SVG.
    :param resolve:
        if ``True``, node's text and href will be pre-processed
        by a :class:`HrefResolver` before rendering.
    :param title_is_weak:
        an additional parameter that will be passed to a :class:`HrefResolver`.
        Intended to indicate whether node's text is given by a user or generated
        automatically.

    """

    return _Node(_Node.Style.COMMENT, text, href, css_class, resolve, title_is_weak)


def skip() -> DiagramNode:
    """
    Create an empty sequence.

    Useful for making empty branches in choice nodes.

    """

    return _Sequence.SKIP


def load(structure) -> DiagramNode:
    """
    Load diagram from object (usually a parsed yaml/json).

    """

    if structure is None:
        return skip()
    elif isinstance(structure, str):
        return _load_terminal(structure, {})
    elif isinstance(structure, list):
        return _load_sequence(structure, {})
    elif isinstance(structure, dict):
        ctors = {
            "sequence": _load_sequence,
            "stack": _load_stack,
            "choice": _load_choice,
            "optional": _load_optional,
            "one_or_more": _load_one_or_more,
            "zero_or_more": _load_zero_or_more,
            "terminal": _load_terminal,
            "non_terminal": _load_non_terminal,
            "comment": _load_comment,
        }

        ctors_found = []

        for name in structure:
            if name in ctors:
                ctors_found.append(name)

        if len(ctors_found) != 1:
            raise ValueError(f"cannot determine type for {structure!r}")

        name = ctors_found[0]
        structure = structure.copy()
        arg = structure.pop(name)
        return ctors[name](arg, structure)
    else:
        raise ValueError(
            f"diagram item description should be string, "
            f"list or object, got {type(structure)} instead"
        )


def _load_sequence(a, kw) -> DiagramNode:
    return _load_generic(
        a,
        kw,
        sequence,
        (
            list,
            tuple,
        ),
        load,
        {
            "autowrap": ((bool,), None),
            "linebreaks": (
                (
                    list,
                    tuple,
                ),
                None,
            ),
        },
    )


def _load_stack(a, kw) -> DiagramNode:
    return _load_generic(
        a,
        kw,
        stack,
        (
            list,
            tuple,
        ),
        load,
        {},
    )


def _load_choice(a, kw) -> DiagramNode:
    return _load_generic(
        a,
        kw,
        choice,
        (
            list,
            tuple,
        ),
        load,
        {
            "default": ((int,), None),
        },
    )


def _load_optional(a, kw) -> DiagramNode:
    return _load_generic(
        a,
        kw,
        optional,
        (str, dict, list, tuple),
        load,
        {
            "skip": ((bool,), None),
        },
    )


def _load_one_or_more(a, kw) -> DiagramNode:
    return _load_generic(
        a,
        kw,
        one_or_more,
        (str, dict, list, tuple),
        load,
        {
            "repeat": ((str, dict, list, tuple), load),
        },
    )


def _load_zero_or_more(a, kw) -> DiagramNode:
    return _load_generic(
        a,
        kw,
        zero_or_more,
        (str, dict, list, tuple),
        load,
        {
            "repeat": ((str, dict, list, tuple), load),
        },
    )


def _load_terminal(a, kw) -> DiagramNode:
    return _load_generic(
        a,
        kw,
        terminal,
        (str,),
        None,
        {
            "href": ((str,), None),
            "css_class": ((str,), None),
            "resolve": ((bool,), None),
            "title_is_weak": ((bool,), None),
        },
    )


def _load_non_terminal(a, kw) -> DiagramNode:
    return _load_generic(
        a,
        kw,
        non_terminal,
        (str,),
        None,
        {
            "href": ((str,), None),
            "css_class": ((str,), None),
            "resolve": ((bool,), None),
            "title_is_weak": ((bool,), None),
        },
    )


def _load_comment(a, kw) -> DiagramNode:
    return _load_generic(
        a,
        kw,
        comment,
        (str,),
        None,
        {
            "href": ((str,), None),
            "css_class": ((str,), None),
            "resolve": ((bool,), None),
            "title_is_weak": ((bool,), None),
        },
    )


def _ensure_type(name, x, *types):
    if not isinstance(x, types):
        types_str = ", ".join([t.__name__ for t in types])
        raise ValueError(
            f"{name} should be {types_str}, " f"got {type(x)} (={x!r}) instead"
        )


def _ensure_empty_dict(name, x):
    if x:
        keys = ", ".join(x.keys())
        raise ValueError(f"{name} got unexpected parameters: {keys}")


def _load_generic(
    user_a,
    user_kw,
    ctor,
    primary_type,
    primary_loader,
    spec: dict[str, tuple[tuple[type, ...], _t.Callable[[_t.Any], _t.Any] | None]],
):
    _ensure_type(f"{ctor.__name__} content", user_a, *primary_type)

    a = primary_loader(user_a)
    kw = {}

    user_kw = user_kw.copy()

    for name, (types, loader) in spec.items():
        if name not in user_kw:
            continue

        arg = user_kw.pop(name)

        if arg is None:
            continue

        _ensure_type(f"{ctor.__name__}'s parameter {name}", arg, *types)

        if loader is not None:
            arg = loader(arg)

        kw[name] = arg

    _ensure_empty_dict(ctor.__name__, user_kw)

    return ctor(*a, **kw)


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

    NO_BREAK = "NO_BREAK"
    """
    Never breaks a line in this position.

    """


###############################################################################
# Rendering diagram
###############################################################################


class InternalAlignment(Enum):
    """
    Controls how to align nodes within a single railroad.

    """

    CENTER = "CENTER"
    """
    Nodes are kept in the center.

    """

    LEFT = "LEFT"
    """
    Nodes are flushed left.

    """

    RIGHT = "RIGHT"
    """
    Nodes are flushed right.

    """


class EndClass(Enum):
    """
    Controls how diagram start and end look like.

    """

    SIMPLE = "SIMPLE"
    """
    A simple ``T``-shaped ending.

    """

    COMPLEX = "COMPLEX"
    """
    A ``T``-shaped ending with vertical line doubled.

    """


class HrefResolver:
    """
    An interface that allows pre-processing all hyperlinks in nodes.

    """

    def resolve(self, text: str, href: str | None, title_is_weak: bool):
        """
        Called before rendering a node.

        Should return a tuple ``(text, href)``, possibly modified.

        """

        return text, href


###############################################################################
# Diagram tree
###############################################################################


class DiagramNode:
    """
    An opaque node representing an element of a diagram.

    """

    # Layout info:
    #
    #
    #     ┌─────────┐      ┈┈┈
    #     │         │      │up
    # ┈┈─>┼───────╮ │      ┈┈┈
    #     │ ╭─────╯ │      │height
    #     │ ╰───────┼>─    ┈┈┈
    #     │         │      │down
    #     └─────────┘      ┈┈┈
    # ►┆┈┈┆◄┈┈┈┈┈┈┈►┆┈┈┆◄
    #  ┆  ┆  width  ┆  ┆
    #   margin_l     margin_r

    _min_width: int = 0
    _max_width: int = 0
    _width: int = 0
    _height: int = 0
    _up: int = 0
    _down: int = 0
    _margin_l: int = 0
    _margin_r: int = 0

    @property
    def _precedence(self) -> int:
        return 3

    def _get_node_with_layout_info(
        self, width: int, layout_settings: _LayoutSettings
    ) -> DiagramNode:
        self_with_layout_info = self._copy_for_layout_info()
        self_with_layout_info._calculate_minmax_width(layout_settings)
        self_with_layout_info._calculate_layout(width, layout_settings)
        return self_with_layout_info

    def _copy_for_layout_info(self):
        raise NotImplementedError()

    def _calculate_minmax_width(self, layout_settings: _LayoutSettings):
        raise NotImplementedError()

    def _calculate_layout(self, width: int, layout_settings: _LayoutSettings):
        raise NotImplementedError()

    def _render(self, render: _Render, x: int, y: int, reverse: bool):
        raise NotImplementedError()


class _Sequence(DiagramNode):
    SKIP: _t.ClassVar[_Sequence]

    _items: list[DiagramNode]
    _linebreaks: list[LineBreak]

    _seq_width: int
    _stack_width: int
    _item_rows: list[list[DiagramNode]]
    _item_row_y_coordinates: list[tuple[int | None, int, int | None]]

    def __new__(
        cls, items: list[DiagramNode], linebreaks: list[LineBreak] | None = None
    ):
        if len(items) == 1:
            return items[0]
        elif len(items) == 0 or all(item is _Sequence.SKIP for item in items):
            return _Sequence.SKIP

        self = super().__new__(cls)

        items = items
        linebreaks = linebreaks or [LineBreak.NO_BREAK] * (len(items) - 1)
        assert len(items) == len(linebreaks) + 1

        self._items = []
        self._linebreaks = []

        for item, linebreak in itertools.zip_longest(items, linebreaks):
            if isinstance(item, _Sequence):
                self._items.extend(item._items)
                self._linebreaks.extend(item._linebreaks)
            else:
                self._items.append(item)
            if linebreak is not None:
                self._linebreaks.append(linebreak)

        return self

    @property
    def _precedence(self) -> int:
        return 2

    def _copy_for_layout_info(self):
        if self is _Sequence.SKIP:
            return _Sequence.SKIP

        copy = object.__new__(_Sequence)
        copy._items = [item._copy_for_layout_info() for item in self._items]
        copy._linebreaks = self._linebreaks
        return copy

    def _calculate_minmax_width(self, layout_settings: _LayoutSettings):
        arc_size = layout_settings.arc_margin + math.ceil(layout_settings.arc_radius)

        self._seq_width = 0
        self._stack_width = 0

        current_row_width = 0
        has_hard_linebreaks = False

        for i, (item, linebreak) in enumerate(
            itertools.zip_longest(self._items, self._linebreaks)
        ):
            item._calculate_minmax_width(layout_settings)

            if i > 0:
                margin = max(self._items[i - 1]._margin_r, item._margin_l)
            else:
                margin = 0
            current_row_width += margin + item._max_width

            if linebreak is LineBreak.HARD:
                self._seq_width = max(self._seq_width, 2 * arc_size + current_row_width)
                current_row_width = 0
                has_hard_linebreaks = True

            self._stack_width = max(self._stack_width, 2 * arc_size + item._min_width)

        if current_row_width and has_hard_linebreaks:
            # last row has only one turn at the beginning
            self._seq_width = max(self._seq_width, 1 * arc_size + current_row_width)
        elif current_row_width:
            self._seq_width = max(self._seq_width, current_row_width)

        # if turn radius is too high, having all nodes in a sequence
        # can actually result in smaller width
        self._max_width = max(self._seq_width, self._stack_width)
        self._min_width = min(self._seq_width, self._stack_width)

    def _calculate_layout(self, width: int, layout_settings: _LayoutSettings):
        if self._min_width > width:
            width = self._min_width

        if self._seq_width <= width and LineBreak.HARD not in self._linebreaks:
            arc_size = 0
            available_width = width
        else:
            arc_size = layout_settings.arc_margin + math.ceil(
                layout_settings.arc_radius
            )
            available_width = width - 2 * arc_size

        self._item_rows = []

        current_row: list[DiagramNode] = []
        current_width = 0

        last_soft_break_idx = 0
        width_at_last_soft_break = 0
        margin_after_last_soft_break = 0

        width_before_last_row = 0
        width_of_last_row = 0

        for i, (item, linebreak) in enumerate(
            itertools.zip_longest(self._items, self._linebreaks)
        ):
            item._calculate_layout(available_width, layout_settings)

            # Calculate margin between current node and the previous one, if any
            if current_row:
                margin = max(current_row[-1]._margin_r, item._margin_l)
            else:
                margin = 0

            # make a soft break, if needed and possible
            if (
                current_row
                and current_width + margin + item._width > available_width
                and last_soft_break_idx
            ):
                self._item_rows.append(current_row[:last_soft_break_idx])
                self._width = max(self._width, width_at_last_soft_break + 2 * arc_size)
                current_row = current_row[last_soft_break_idx:]
                current_width -= width_at_last_soft_break + margin_after_last_soft_break
                last_soft_break_idx = 0
                width_at_last_soft_break = 0
                margin_after_last_soft_break = 0
                margin = max(current_row[-1]._margin_r, item._margin_l)

            # if we still need a break, then a soft break wasn't possible
            # (or enough), so we'll have to break here
            if current_row and current_width + margin + item._width > available_width:
                self._item_rows.append(current_row)
                self._width = max(self._width, current_width + 2 * arc_size)
                current_row = []
                current_width = 0
                last_soft_break_idx = 0
                width_at_last_soft_break = 0
                margin_after_last_soft_break = 0
                margin = 0

            current_row.append(item)
            current_width += margin + item._width

            if linebreak is LineBreak.HARD:
                self._item_rows.append(current_row)
                self._width = max(self._width, current_width + 2 * arc_size)
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
            width_before_last_row = self._width
            # last row has only one turn at the beginning
            width_of_last_row = current_width + 1 * arc_size
            self._width = max(self._width, width_of_last_row)

        assert (arc_size > 0) == (len(self._item_rows) > 1)

        self._item_row_y_coordinates = []
        current_y = 0
        for i, row in enumerate(self._item_rows):
            row_height = 0
            row_upper_point = 0
            row_lower_point = 0
            for item in row:
                row_upper_point = max(row_upper_point, item._up - row_height)
                row_height += item._height
                row_lower_point = max(row_lower_point, item._down + row_height)
            row_up = row_upper_point
            row_down = row_lower_point - row_height

            if i == 0:
                self._up = row_up
                prev_reverse_line_pos = None
            else:
                self._height += row_up
                prev_reverse_line_pos = current_y
                current_y += layout_settings.vertical_seq_separation + row_up

            self._height += row_height

            if i == len(self._item_rows) - 1:
                self._down = row_down
            else:
                self._height += row_down + 2 * layout_settings.vertical_seq_separation

            row_pos = current_y
            current_y += row_height + row_down + layout_settings.vertical_seq_separation
            reverse_line_pos = current_y if i != len(self._item_rows) - 1 else None

            self._item_row_y_coordinates.append(
                (prev_reverse_line_pos, row_pos, reverse_line_pos)
            )

        if self._item_rows:
            self._margin_l = max(0, self._item_rows[0][0]._margin_l - arc_size)
            if arc_size > 0:
                self._margin_l = max(self._margin_l, layout_settings.arc_margin)
            self._margin_r = (
                max(
                    width_before_last_row + layout_settings.arc_margin,
                    width_of_last_row + self._item_rows[-1][-1]._margin_r,
                )
                - self._width
            )

    def _render(self, render: _Render, x: int, y: int, reverse: bool):
        if len(self._item_rows) > 1:
            arc_radius = math.ceil(render.layout_settings.arc_radius)
            arc_size = render.layout_settings.arc_margin + arc_radius
        else:
            arc_radius = 0
            arc_size = 0

        if not reverse:
            seq_anchor = x
            seq_end_anchor = x + self._width
            line_anchor = x + arc_radius
            node_anchor = x + arc_size
        else:
            seq_anchor = x + self._width
            seq_end_anchor = x
            node_anchor = x + self._width - arc_size
            line_anchor = x + self._width - arc_radius

        for row, (prev_reverse_line_pos, row_pos, reverse_line_pos) in zip(
            self._item_rows, self._item_row_y_coordinates
        ):
            if prev_reverse_line_pos is not None:
                render.line(node_anchor, y + prev_reverse_line_pos).segment_abs(
                    line_anchor
                ).bend_reverse_abs(
                    y + row_pos, "e" if not reverse else "w"
                ).segment_abs(
                    node_anchor
                )
            else:
                render.line(seq_anchor, y).segment_abs(node_anchor)

            current_x_shift = 0
            current_y_shift = row_pos

            for i, item in enumerate(row):
                if i > 0:
                    margin = max(item._margin_l, row[i - 1]._margin_r)
                else:
                    margin = 0

                if not reverse:
                    item_x = node_anchor + current_x_shift + margin
                    item_y = y + current_y_shift

                    prev_item_exit_x = node_anchor + current_x_shift
                    item_enter_x = node_anchor + current_x_shift + margin
                else:
                    item_x = node_anchor - current_x_shift - margin - item._width
                    item_y = y + current_y_shift

                    prev_item_exit_x = node_anchor - current_x_shift - margin
                    item_enter_x = node_anchor - current_x_shift

                render.line(prev_item_exit_x, item_y).segment_abs(item_enter_x)

                item._render(render, item_x, item_y, reverse)

                current_x_shift += margin + item._width
                current_y_shift += item._height

            if not reverse:
                item_exit_x = node_anchor + current_x_shift
                bend_x = item_exit_x + render.layout_settings.arc_margin
                item_exit_y = y + current_y_shift
            else:
                item_exit_x = node_anchor - current_x_shift
                bend_x = item_exit_x - render.layout_settings.arc_margin
                item_exit_y = y + current_y_shift

            if reverse_line_pos is not None:
                render.line(item_exit_x, item_exit_y).segment_abs(
                    bend_x
                ).bend_reverse_abs(
                    y + reverse_line_pos, "w" if not reverse else "e"
                ).segment_abs(
                    node_anchor
                )
            else:
                render.line(item_exit_x, item_exit_y).segment_abs(seq_end_anchor)

    def __str__(self):
        if self is _Sequence.SKIP:
            return "<SKIP>"

        return " ".join(
            f"{item}" if item._precedence >= self._precedence else f"({item})"
            for item in self._items
        )


_Sequence.SKIP = object.__new__(_Sequence)
_Sequence.SKIP._items = []
_Sequence.SKIP._linebreaks = []


class _Choice(DiagramNode):
    _default: int
    _items: list[DiagramNode]

    # Layout info
    _items_pos: list[int]

    def __new__(cls, default: int, items: list[DiagramNode]):
        if len(items) == 0:
            return _Sequence.SKIP
        elif len(items) == 1:
            return items[0]
        elif all(item is _Sequence.SKIP for item in items):
            return _Sequence.SKIP

        self = super().__new__(cls)

        assert 0 <= default < len(items)

        self._default = 0
        self._items = []

        if _Sequence.SKIP in items and items[default] != _Sequence.SKIP:
            self._items.append(_Sequence.SKIP)

        for i, item in enumerate(items):
            if i != default and item is _Sequence.SKIP:
                continue

            if isinstance(item, _Choice):
                if i == default:
                    self._default = len(self._items) + item._default
                self._items.extend(item._items)
            else:
                if i == default:
                    self._default = len(self._items)
                self._items.append(item)

        return self

    @property
    def _precedence(self) -> int:
        # Optional renders as an unary operator
        return 3 if _Sequence.SKIP in self._items else 1

    def _copy_for_layout_info(self):
        copy = object.__new__(_Choice)
        copy._default = self._default
        copy._items = [item._copy_for_layout_info() for item in self._items]
        return copy

    def _calculate_minmax_width(self, layout_settings: _LayoutSettings):
        arc_size = layout_settings.arc_margin + math.ceil(
            2 * layout_settings.arc_radius
        )

        for item in self._items:
            item._calculate_minmax_width(layout_settings)

        self._min_width = min(item._min_width for item in self._items) + 2 * arc_size
        self._max_width = max(item._min_width for item in self._items) + 2 * arc_size

    def _calculate_layout(self, width: int, layout_settings: _LayoutSettings):
        if self._min_width > width:
            width = self._min_width

        double_arc_radius = math.ceil(2 * layout_settings.arc_radius)
        arc_size = layout_settings.arc_margin + double_arc_radius

        available_width = width - 2 * arc_size

        items_width = 0
        items_margin_l = 0
        items_margin_r = 0
        current_pos = 0

        self._items_pos = []

        for i, item in enumerate(self._items):
            item._calculate_layout(available_width, layout_settings)

            current_pos += item._up

            if i == self._default:
                self._items_pos.append(current_pos)

                self._up = current_pos
                self._height = item._height

                for j in range(len(self._items_pos)):
                    self._items_pos[j] -= current_pos

                current_pos = 0
            else:
                self._items_pos.append(current_pos)

            current_pos += item._height
            current_pos += item._down
            current_pos += layout_settings.vertical_choice_separation

            items_width = max(items_width, item._width)
            items_margin_l = max(items_margin_l, item._margin_l)
            items_margin_r = max(items_margin_r, item._margin_r)

        self._width = items_width + 2 * arc_size
        self._down = (
            current_pos - self._height - layout_settings.vertical_choice_separation
        )
        self._margin_l = max(layout_settings.arc_margin, items_margin_l - arc_size)
        self._margin_r = max(layout_settings.arc_margin, items_margin_r - arc_size)

    def _render(self, render: _Render, x: int, y: int, reverse: bool):
        double_arc_radius = math.ceil(2 * render.layout_settings.arc_radius)
        arc_size = render.layout_settings.arc_margin + double_arc_radius

        node_left_anchor = x + arc_size

        if not reverse:
            main_line_enter_x = x
            main_line_enter_y = y

            main_line_exit_x = x + self._width
            main_line_exit_y = y + self._height
        else:
            main_line_enter_x = x
            main_line_enter_y = y + self._height

            main_line_exit_x = x + self._width
            main_line_exit_y = y

        for item, pos in zip(self._items, self._items_pos):
            item_gap = self._width - 2 * arc_size - item._width

            if not reverse:
                item_x = node_left_anchor
                item_y = y + pos

                item_enter_x = item_x
                item_enter_y = item_y

                item_exit_x = item_x + item._width
                item_exit_y = item_y + item._height
            else:
                item_x = node_left_anchor + item_gap
                item_y = y + pos

                item_enter_x = item_x
                item_enter_y = item_y + item._height

                item_exit_x = item_x + item._width
                item_exit_y = item_y

            render.line(main_line_enter_x, main_line_enter_y, reverse).bend_forward_abs(
                item_enter_y, arrow_begin=True
            ).segment_abs(item_enter_x, arrow_begin=True)

            item._render(render, item_x, item_y, reverse)

            render.line(item_exit_x, item_exit_y, reverse).segment_abs(
                main_line_exit_x - double_arc_radius, arrow_end=True
            ).bend_forward_abs(main_line_exit_y, arrow_end=True)

    def __str__(self):
        is_optional = _Sequence.SKIP in self._items
        items = [
            f"{item}" if item._precedence >= self._precedence else f"({item})"
            for item in self._items
            if item is not _Sequence.SKIP
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


class _OneOrMore(DiagramNode):
    _item: DiagramNode
    _repeat: list[DiagramNode]
    _repeat_orig: DiagramNode

    # Layout info
    repeat_pos: list[int]

    def __new__(cls, item: DiagramNode, repeat: DiagramNode | None = None):
        repeat = repeat or _Sequence.SKIP

        if item is _Sequence.SKIP and repeat is _Sequence.SKIP:
            return item

        self = super().__new__(cls)

        self._item = item
        if isinstance(repeat, _Choice):
            self._repeat = repeat._items
        else:
            self._repeat = [repeat]
        self._repeat_orig = repeat

        return self

    @property
    def _precedence(self) -> int:
        # OneOrMore without repeat renders as an unary operator
        return 3 if self._repeat_orig is _Sequence.SKIP else 2

    def _copy_for_layout_info(self):
        copy = object.__new__(_OneOrMore)
        copy._item = self._item._copy_for_layout_info()
        copy._repeat = [repeat._copy_for_layout_info() for repeat in self._repeat]
        return copy

    def _calculate_minmax_width(self, layout_settings: _LayoutSettings):
        arc_size = layout_settings.arc_margin + math.ceil(layout_settings.arc_radius)

        self._item._calculate_minmax_width(layout_settings)

        self._min_width = self._item._min_width
        self._max_width = self._item._max_width

        for repeat in self._repeat:
            repeat._calculate_minmax_width(layout_settings)
            self._min_width = min(self._min_width, repeat._min_width)
            self._max_width = max(self._max_width, repeat._max_width)

        self._min_width += 2 * arc_size
        self._max_width += 2 * arc_size

    def _calculate_layout(self, width: int, layout_settings: _LayoutSettings):
        if self._min_width > width:
            width = self._min_width

        arc_size = layout_settings.arc_margin + math.ceil(layout_settings.arc_radius)

        available_width = width - 2 * arc_size

        self._item._calculate_layout(available_width, layout_settings)

        items_width = self._item._width

        current_height = self._item._height + self._item._down
        self.repeat_pos = []
        for repeat in self._repeat:
            repeat._calculate_layout(available_width, layout_settings)
            items_width = max(items_width, repeat._width)

            current_height += layout_settings.vertical_choice_separation + repeat._up
            self.repeat_pos.append(current_height)
            current_height += repeat._height + repeat._down

        self._width = items_width + 2 * arc_size
        self._height = self._item._height
        self._up = self._item._up
        self._down = current_height - self._item._height
        self._margin_l = max(
            layout_settings.arc_margin, self._item._margin_l - arc_size
        )
        self._margin_r = max(
            layout_settings.arc_margin, self._item._margin_r - arc_size
        )

    def _render(self, render: _Render, x: int, y: int, reverse: bool):
        arc_radius = math.ceil(render.layout_settings.arc_radius)
        arc_size = render.layout_settings.arc_margin + arc_radius

        if not reverse:
            main_line_enter_x = x
            main_line_enter_y = y

            main_line_exit_x = x + self._width
            main_line_exit_y = y + self._height
        else:
            main_line_enter_x = x
            main_line_enter_y = y + self._height

            main_line_exit_x = x + self._width
            main_line_exit_y = y

        # item

        item_gap = math.floor((self._width - 2 * arc_size - self._item._width) / 2)

        item_x = x + arc_size + item_gap
        item_y = y

        if not reverse:
            item_enter_x = item_x

            item_exit_x = item_x + self._item._width
            item_exit_y = item_y + self._item._height
        else:
            item_enter_x = item_x

            item_exit_x = item_x + self._item._width
            item_exit_y = item_y

        render.line(main_line_enter_x, main_line_enter_y, reverse).segment(
            arc_radius
        ).segment_abs(item_enter_x, arrow_begin=True)

        self._item._render(render, item_x, item_y, reverse)

        render.line(item_exit_x, item_exit_y, reverse).segment_abs(
            main_line_exit_x - arc_radius, arrow_end=True
        ).segment(arc_radius)

        # reverse

        if len(self._repeat) - self._repeat.count(_Sequence.SKIP) <= 1:
            align = "c"
        elif not reverse:
            align = "r"
        else:
            align = "l"

        for repeat, pos in zip(self._repeat, self.repeat_pos):
            if align == "c":
                repeat_gap = math.floor(
                    (self._width - 2 * arc_size - repeat._width) / 2
                )
            elif align == "l":
                repeat_gap = 0
            else:
                repeat_gap = self._width - 2 * arc_size - repeat._width

            repeat_x = x + arc_size + repeat_gap
            repeat_y = y + pos

            if not reverse:
                repeat_enter_x = repeat_x
                repeat_enter_y = repeat_y + repeat._height

                repeat_exit_x = repeat_x + repeat._width
                repeat_exit_y = repeat_y
            else:
                repeat_enter_x = repeat_x
                repeat_enter_y = repeat_y

                repeat_exit_x = repeat_x + repeat._width
                repeat_exit_y = repeat_y + repeat._height

            render.line(
                main_line_enter_x + arc_radius, main_line_enter_y, not reverse
            ).bend_reverse_abs(repeat_enter_y, "e", arrow_begin=True).segment_abs(
                repeat_enter_x, arrow_begin=True
            )

            repeat._render(render, repeat_x, repeat_y, not reverse)

            render.line(repeat_exit_x, repeat_exit_y, not reverse).segment_abs(
                main_line_exit_x - arc_radius, arrow_end=True
            ).bend_reverse_abs(main_line_exit_y, "w", arrow_end=True)

    def __str__(self):
        if self._repeat_orig is _Sequence.SKIP:
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
                f"{self._repeat_orig}"
                if self._repeat_orig._precedence >= self._precedence
                else f"({self._repeat_orig})"
            )
            return f"{item} ({repeat} {item})*"


class _Node(DiagramNode):
    class Style(Enum):
        TERMINAL = "TERMINAL"
        NON_TERMINAL = "NON_TERMINAL"
        COMMENT = "COMMENT"

    _style: Style
    _text: str
    _href: str | None
    _resolve: bool
    _title_is_weak: bool
    _css_class: str

    _padding: int
    _radius: int

    def __init__(
        self,
        render: Style,
        text,
        href=None,
        css_class="",
        resolve=True,
        title_is_weak=False,
    ):
        self._style = render
        self._text = text
        self._href = href
        self._resolve = resolve
        self._title_is_weak = title_is_weak
        self._css_class = css_class

    def _copy_for_layout_info(self):
        copy = object.__new__(_Node)
        copy._style = self._style
        copy._text = self._text
        copy._href = self._href
        copy._resolve = self._resolve
        copy._title_is_weak = self._title_is_weak
        copy._css_class = self._css_class
        return copy

    def _calculate_minmax_width(self, layout_settings: _LayoutSettings):
        if self._resolve:
            self._text, self._href = layout_settings.href_resolver.resolve(
                self._text, self._href, self._title_is_weak
            )
        text_width = math.ceil(
            sum(
                (
                    layout_settings.character_advance
                    if wcwidth.wcwidth(g) == 1
                    else layout_settings.wide_character_advance
                )
                for g in grapheme.graphemes(self._text)
            )
        )

        if self._style == _Node.Style.TERMINAL:
            height = layout_settings.terminal_height
            self._padding = padding = layout_settings.terminal_padding
            self._radius = layout_settings.terminal_radius
        elif self._style == _Node.Style.NON_TERMINAL:
            height = layout_settings.non_terminal_height
            self._padding = padding = layout_settings.non_terminal_padding
            self._radius = layout_settings.non_terminal_radius
        else:
            height = layout_settings.comment_height
            self._padding = padding = layout_settings.comment_padding
            self._radius = layout_settings.comment_radius

        self._width = self._min_width = self._max_width = text_width + 2 * padding
        self._height = 0
        self._up = math.ceil(height / 2)
        self._down = math.floor(height / 2)
        self._margin_l = self._margin_r = layout_settings.horizontal_seq_separation

    def _calculate_layout(self, width: int, layout_settings: _LayoutSettings):
        pass

    def _render(self, render: _Render, x: int, y: int, reverse: bool):
        render.node(x, y, self)

    def __str__(self):
        if re.match(r"^[a-zA-Z0-9_-]+$", self._text) is not None:
            return self._text
        else:
            return repr(self._text)


class _Diagram(DiagramNode):
    def __init__(self, node: DiagramNode):
        self._node = node

    def _copy_for_layout_info(self):
        return _Diagram(self._node._copy_for_layout_info())

    def _calculate_minmax_width(self, layout_settings: _LayoutSettings):
        self._node._calculate_minmax_width(layout_settings)
        self._min_width = self._node._min_width + 2 * layout_settings.marker_width
        self._max_width = self._node._max_width + 2 * layout_settings.marker_width

        self._margin_l = self._margin_r = layout_settings.horizontal_seq_separation

    def _calculate_layout(self, width: int, layout_settings: _LayoutSettings):
        self._node._calculate_layout(
            width - 2 * layout_settings.marker_width, layout_settings
        )
        self._width = self._node._width + 2 * layout_settings.marker_width
        self._height = self._node._height
        self._up = max(layout_settings.marker_projected_height, self._node._up)
        self._down = max(layout_settings.marker_projected_height, self._node._down)
        self._margin_l = 0
        self._margin_r = 0

    def _render(self, render: _Render, x: int, y: int, reverse: bool):
        render.start(x, y + self._node._height if reverse else y)

        self._node._render(render, x + render.layout_settings.marker_width, y, reverse)

        render.end(
            x + render.layout_settings.marker_width + self._node._width,
            y if reverse else y + self._node._height,
        )


###############################################################################
# Rendering API
###############################################################################


@dataclass
class _LayoutSettings:
    horizontal_seq_separation: int
    vertical_choice_separation: int
    vertical_seq_separation: int

    arc_radius: int | float
    arc_margin: int

    character_advance: int | float
    wide_character_advance: int | float

    terminal_padding: int
    terminal_height: int
    terminal_radius: int

    non_terminal_padding: int
    non_terminal_height: int
    non_terminal_radius: int

    comment_padding: int
    comment_height: int
    comment_radius: int

    marker_width: int
    marker_projected_height: int

    end_class: EndClass

    href_resolver: HrefResolver = HrefResolver()


class _Render:
    @property
    def layout_settings(self) -> _LayoutSettings:
        raise NotImplementedError()

    def write(self, f=sys.stdout):
        raise NotImplementedError()

    def to_string(self):
        raise NotImplementedError()

    def line(self, x: int, y: int, reverse: bool = False) -> _Line:
        raise NotImplementedError()

    def node(self, x: int, y: int, node: _Node):
        raise NotImplementedError()

    def start(self, x: int, y: int):
        raise NotImplementedError()

    def end(self, x: int, y: int):
        raise NotImplementedError()


class _Line:
    Direction = _t.Literal["w", "e"]

    @staticmethod
    def reverse_direction(d: _Line.Direction):
        return "w" if d == "e" else "e"

    def segment(
        self, w: int, arrow_begin: bool = False, arrow_end: bool = False
    ) -> _Line:
        raise NotImplementedError()

    def segment_abs(
        self, x: int, arrow_begin: bool = False, arrow_end: bool = False
    ) -> _Line:
        raise NotImplementedError()

    def bend_forward(
        self,
        h: int,
        d: Direction = "e",
        arrow_begin: bool = False,
        arrow_end: bool = False,
    ) -> _Line:
        raise NotImplementedError()

    def bend_forward_abs(
        self,
        y: int,
        d: Direction = "e",
        arrow_begin: bool = False,
        arrow_end: bool = False,
    ) -> _Line:
        raise NotImplementedError()

    def bend_reverse(
        self,
        h: int,
        d: Direction = "e",
        arrow_begin: bool = False,
        arrow_end: bool = False,
    ) -> _Line:
        raise NotImplementedError()

    def bend_reverse_abs(
        self,
        y: int,
        d: Direction = "e",
        arrow_begin: bool = False,
        arrow_end: bool = False,
    ) -> _Line:
        raise NotImplementedError()


###############################################################################
# Rendering text
###############################################################################


@dataclass(frozen=True)
class TextRenderSettings:
    padding: tuple[int, int, int, int] = (0, 0, 0, 0)
    """
    Array of four positive integers denoting top, right, bottom and left
    padding between the diagram and its container.

    """

    vertical_choice_separation: int = 1
    """
    Vertical space between nodes in a :func:`choice` block.

    """

    vertical_seq_separation: int = 2
    """
    Vertical space between nodes in a :func:`stack` block.

    """

    horizontal_seq_separation: int = 2
    """
    Horizontal space between adjacent nodes.

    """

    end_class: EndClass = EndClass.COMPLEX
    """
    Controls how diagram start and end look like.

    """

    alignment: InternalAlignment = InternalAlignment.LEFT
    """
    Determines how nodes aligned within a single diagram line.

    """

    max_width: int = 80
    """
    Max width after which a sequence will be wrapped. This option is used to
    automatically convert sequences to stacks. Note that this is a suggestive
    option, there is no guarantee that the diagram will
    fit to its ``max_width``.

    """


def render_text(
    node: DiagramNode,
    /,
    *,
    max_width: int | None = None,
    settings: TextRenderSettings = TextRenderSettings(),
    reverse=False,
    href_resolver: HrefResolver = HrefResolver(),
) -> str:
    """
    Render diagram as text.

    :param node:
            root diagram node.
    :param max_width:
            if given, overrides :attribute:`~TextRenderSettings.max_width`
            from ``settings``.
    :param settings:
            rendering settings.
    :param reverse:
            if enabled, diagram is rendered right-to-left.
    :param href_resolver:
            hyperlink resolver (may be used to transform text).
    :return:
            a string with a rendered diagram.

    """

    if max_width is None:
        max_width = settings.max_width

    node = _Diagram(node)

    layout_settings = _text_layout_settings(settings)
    layout_settings.href_resolver = href_resolver

    max_width = max(0, max_width - settings.padding[3] - settings.padding[1])

    node_with_layout_info = node._get_node_with_layout_info(max_width, layout_settings)

    render = _TextRender(
        (settings.padding[3] + node_with_layout_info._width + settings.padding[1]),
        (
            settings.padding[0]
            + node_with_layout_info._up
            + node_with_layout_info._height
            + node_with_layout_info._down
            + settings.padding[2]
            + 1
        ),
        layout_settings,
    )

    node_with_layout_info._render(
        render,
        settings.padding[3],
        settings.padding[0] + node_with_layout_info._up,
        reverse,
    )

    return render.to_string()


def _text_layout_settings(settings: TextRenderSettings = TextRenderSettings()):
    return _LayoutSettings(
        horizontal_seq_separation=settings.horizontal_seq_separation,
        vertical_choice_separation=settings.vertical_choice_separation,
        vertical_seq_separation=settings.vertical_seq_separation,
        arc_radius=0.5,
        arc_margin=1,
        terminal_padding=2,
        terminal_height=2,
        terminal_radius=0,
        non_terminal_padding=2,
        non_terminal_height=2,
        non_terminal_radius=0,
        comment_padding=2,
        comment_height=2,
        comment_radius=0,
        character_advance=1,
        wide_character_advance=2,
        marker_width=4,
        marker_projected_height=0,
        end_class=settings.end_class,
    )


class _TextRender(_Render):
    def __init__(self, width: int, height: int, layout_settings: _LayoutSettings):
        self._x = self._y = 0
        self._layout_settings = layout_settings
        self._field = [[" "] * width for _ in range(height)]

    @property
    def layout_settings(self) -> _LayoutSettings:
        return self._layout_settings

    def write(self, f=sys.stdout):
        for line in self._field:
            for g in line:
                f.write(g)
            f.write("\n")
        f.flush()

    def to_string(self):
        stream = io.StringIO()
        self.write(stream)
        return stream.getvalue()

    def line(self, x: int, y: int, reverse: bool = False) -> _Line:
        return _TextLine(self, x, y, reverse)

    def node(self, x: int, y: int, node: _Node):
        if node._style == _Node.Style.TERMINAL:
            ch = "┤├┌┐└┘─"
        elif node._style == _Node.Style.NON_TERMINAL:
            ch = "╢╟╔╗╚╝═"
        else:
            ch = "╴╶     "

        pad = " " * (node._padding - 1)
        self._field[y][x + 1] = f"{pad}{node._text}{pad}"
        for i in range(2, node._width):
            self._field[y][x + i] = ""

        self._field[y - 1][x] = ch[2]
        for i in range(1, node._width):
            self._field[y - 1][x + i] = ch[6]
        self._field[y - 1][x + node._width - 1] = ch[3]

        self._field[y][x] = ch[0]
        self._field[y][x + node._width - 1] = ch[1]

        self._field[y + 1][x] = ch[4]
        for i in range(1, node._width):
            self._field[y + 1][x + i] = ch[6]
        self._field[y + 1][x + node._width - 1] = ch[5]

    def start(self, x: int, y: int):
        w = self.layout_settings.marker_width

        for i in range(w):
            self._field[y][x + i] = "─"

        if self.layout_settings.end_class == EndClass.SIMPLE:
            self._field[y][x] = "├"
        elif self.layout_settings.end_class == EndClass.COMPLEX:
            self._field[y][x] = "├"
            self._field[y][x + 1] = "┼"
        else:
            raise NotImplementedError(
                f"unknown end class {self.layout_settings.end_class}"
            )

    def end(self, x: int, y: int):
        w = self.layout_settings.marker_width

        for i in range(w):
            self._field[y][x + i] = "─"

        if self.layout_settings.end_class == EndClass.SIMPLE:
            self._field[y][x + w - 1] = "┤"
        elif self.layout_settings.end_class == EndClass.COMPLEX:
            self._field[y][x + w - 1] = "┤"
            self._field[y][x + w - 2] = "┼"
        else:
            raise NotImplementedError(
                f"unknown end class {self.layout_settings.end_class}"
            )


class _TextLine(_Line):
    _SYMBOL_TO_DIRECTION = {
        " ": frozenset(),
        "╴": frozenset("w"),
        "╶": frozenset("e"),
        "╵": frozenset("n"),
        "╷": frozenset("s"),
        "│": frozenset("ns"),
        "─": frozenset("ew"),
        "╭": frozenset("es"),
        "╮": frozenset("sw"),
        "╯": frozenset("nw"),
        "╰": frozenset("en"),
        "┬": frozenset("esw"),
        "├": frozenset("ens"),
        "┼": frozenset("ensw"),
        "┤": frozenset("nsw"),
        "┴": frozenset("enw"),
    }

    _DIRECTION_TO_SYMBOL = {v: k for k, v in _SYMBOL_TO_DIRECTION.items()}

    def __init__(self, render: _TextRender, x: int, y: int, reverse: bool):
        self._render = render
        self._x = x
        self._y = y
        self._reverse = reverse

    def segment(
        self, w: int, arrow_begin: bool = False, arrow_end: bool = False
    ) -> _Line:
        if w >= 0:
            s = "→" if not self._reverse else "←"

            for i in range(w):
                self._write_cell(self._x + i, self._y, "we")

            if arrow_begin:
                self._render._field[self._y][self._x] = s

            self._x += w

            if arrow_end:
                self._render._field[self._y][self._x - 1] = s
        else:
            s = "←" if not self._reverse else "→"

            for i in range(-1, w - 1, -1):
                self._write_cell(self._x + i, self._y, "we")

            if arrow_begin:
                self._render._field[self._y][self._x - 1] = s

            self._x += w

            if arrow_end:
                self._render._field[self._y][self._x] = s

        return self

    def segment_abs(
        self, x: int, arrow_begin: bool = False, arrow_end: bool = False
    ) -> _Line:
        return self.segment(x - self._x, arrow_begin, arrow_end)

    def bend_forward(
        self,
        h: int,
        d: _Line.Direction = "e",
        arrow_begin: bool = False,
        arrow_end: bool = False,
    ) -> _Line:
        return self._bend(h, self.reverse_direction(d), d, arrow_begin, arrow_end)

    def bend_forward_abs(
        self,
        y: int,
        d: _Line.Direction = "e",
        arrow_begin: bool = False,
        arrow_end: bool = False,
    ) -> _Line:
        return self.bend_forward(y - self._y, d, arrow_begin, arrow_end)

    def bend_reverse(
        self,
        h: int,
        d: _Line.Direction = "e",
        arrow_begin: bool = False,
        arrow_end: bool = False,
    ) -> _Line:
        return self._bend(h, d, d, arrow_begin, arrow_end)

    def bend_reverse_abs(
        self,
        y: int,
        d: _Line.Direction = "e",
        arrow_begin: bool = False,
        arrow_end: bool = False,
    ) -> _Line:
        return self.bend_reverse(y - self._y, d, arrow_begin, arrow_end)

    def _bend(
        self,
        h: int,
        coming_from: str,
        coming_to: str,
        arrow_begin: bool = False,
        arrow_end: bool = False,
    ) -> _Line:
        if coming_from == "e":
            self._x -= 1

        if h > 0:
            s = "↓" if not self._reverse else "↑"
        else:
            s = "↑" if not self._reverse else "↓"

        if arrow_begin:
            if h > 0:
                self._render._field[self._y + 1][self._x] = s
            elif h < 0:
                self._render._field[self._y - 1][self._x] = s

        if h == 0:
            self._write_cell(self._x, self._y, coming_from + coming_to)
        elif h > 0:
            for i in range(1, h):
                self._write_cell(self._x, self._y + i, "ns")
            self._write_cell(self._x, self._y, coming_from + "s")
            self._write_cell(self._x, self._y + h, "n" + coming_to)
        else:
            for i in range(-1, h, -1):
                self._write_cell(self._x, self._y + i, "ns")
            self._write_cell(self._x, self._y, coming_from + "n")
            self._write_cell(self._x, self._y + h, "s" + coming_to)

        self._y += h

        if arrow_end:
            if h > 0:
                self._render._field[self._y - 1][self._x] = s
            elif h < 0:
                self._render._field[self._y + 1][self._x] = s

        if coming_to == "e":
            self._x += 1

        return self

    def _write_cell(self, x: int, y: int, d: str):
        if self._render._field[y][x] not in self._SYMBOL_TO_DIRECTION:
            pass
        elif self._render._field[y][x] == " ":
            self._render._field[y][x] = self._DIRECTION_TO_SYMBOL[frozenset(d)]
        else:
            self._render._field[y][x] = self._DIRECTION_TO_SYMBOL[
                frozenset(d)
                | self._SYMBOL_TO_DIRECTION.get(self._render._field[y][x], frozenset())
            ]


###############################################################################
# Rendering SVG
###############################################################################


DEFAULT_CSS = {
    "path": {
        "stroke-width": "1.5",
        "stroke": "black",
        "fill": "none",
    },
    "a": {
        "text-decoration": "none",
    },
    "rect": {
        "stroke-width": "1.5",
        "stroke": "black",
        "fill": "none",
    },
    # "g.terminal rect": {
    #     "rx": "10",
    #     "ry": "10",
    # },
    "g.comment rect": {
        "stroke": "none",
    },
    "text": {
        "font-size": "14px",
        "font-family": "'Consolas', 'Menlo', 'Deja Vu Sans Mono', 'Bitstream Vera Sans Mono', monospace",
        "text-anchor": "middle",
        "dominant-baseline": "central",
        "font-weight": "bold",
    },
    "g.comment text": {
        "font-weight": "normal",
        "font-style": "italic",
    },
}


@dataclass(frozen=True)
class SvgRenderSettings:
    padding: tuple[int, int, int, int] = (1, 1, 1, 1)
    """
    Array of four positive integers denoting top, right, bottom and left
    padding between the diagram and its container.

    """

    vertical_choice_separation: int = 9
    """
    Vertical space between nodes in a :func:`choice` block.

    """

    vertical_seq_separation: int = 16
    """
    Vertical space between nodes in a :func:`stack` block.

    """

    horizontal_seq_separation: int = 20
    """
    Horizontal space between adjacent nodes.

    """

    end_class: EndClass = EndClass.COMPLEX
    """
    Controls how diagram start and end look like.

    """

    alignment: InternalAlignment = InternalAlignment.LEFT
    """
    Determines how nodes aligned within a single diagram line.

    """

    max_width: int = 600
    """
    Max width after which a sequence will be wrapped. This option is used to
    automatically convert sequences to stacks. Note that this is a suggestive
    option, there is no guarantee that the diagram will
    fit to its ``max_width``.

    """

    arc_radius: int = 10
    """
    Arc radius of railroads. 10px by default.

    """

    arc_margin: int = 5
    """
    Margin around arcs.

    """

    character_advance: float = 8.4
    """
    Average length of one character in the used font. Since SVG elements
    cannot expand and shrink dynamically, length of text nodes is calculated
    as number of symbols multiplied by this constant.

    """

    wide_character_advance: float = 14.36
    """
    Average length of one wide character in the used font.
    See :attribute:`~SvgRenderSettings.character_advance` for explanation.

    """

    terminal_padding: int = 10
    """
    Horizontal padding around text in terminal nodes.

    """

    terminal_radius: int = 10
    """
    Border radius in terminal nodes.

    """

    terminal_height: int = 22
    """
    Height of a terminal node.

    """

    non_terminal_padding: int = 10
    """
    Horizontal padding around text in non-terminal nodes.

    """

    non_terminal_radius: int = 0
    """
    Border radius in non-terminal nodes.

    """

    non_terminal_height: int = 22
    """
    Height of a non-terminal node.

    """

    comment_padding: int = 3
    """
    Horizontal padding around text in comment nodes.

    """

    comment_radius: int = 0
    """
    Border radius in comment nodes.

    """

    comment_height: int = 22
    """
    Height of a comment node.

    """

    css_class: str = ""
    """
    Class attribute for the ``<svg>`` element.

    """

    css_style: dict[str, dict[str, str]] | str | None = field(
        default_factory=lambda: DEFAULT_CSS
    )
    """
    CSS style that should be embedded into the diagram.

    """


def render_svg(
    node: DiagramNode,
    /,
    *,
    max_width: int | None = None,
    settings: SvgRenderSettings = SvgRenderSettings(),
    reverse=False,
    href_resolver: HrefResolver = HrefResolver(),
) -> str:
    """
    Render diagram as an SVG.

    :param node:
            root diagram node.
    :param max_width:
            if given, overrides :attribute:`~SvgRenderSettings.max_width`
            from ``settings``.
    :param settings:
            rendering settings.
    :param reverse:
            if enabled, diagram is rendered right-to-left.
    :param href_resolver:
            hyperlink resolver (may be used to transform text).
    :return:
            a string with a rendered diagram.

    """

    if max_width is None:
        max_width = settings.max_width

    node = _Diagram(node)

    layout_settings = _svg_layout_settings(settings)
    layout_settings.href_resolver = href_resolver

    max_width = max(0, max_width - settings.padding[3] - settings.padding[1])

    node_with_layout_info = node._get_node_with_layout_info(max_width, layout_settings)

    render = _SvgRender(
        (settings.padding[3] + node_with_layout_info._width + settings.padding[1]),
        (
            settings.padding[0]
            + node_with_layout_info._up
            + node_with_layout_info._height
            + node_with_layout_info._down
            + settings.padding[2]
            + 1
        ),
        layout_settings,
        settings.css_class,
        settings.css_style,
    )

    node_with_layout_info._render(
        render,
        settings.padding[3],
        settings.padding[0] + node_with_layout_info._up,
        reverse,
    )

    return render.to_string()


def _svg_layout_settings(settings: SvgRenderSettings = SvgRenderSettings()):
    return _LayoutSettings(
        horizontal_seq_separation=settings.horizontal_seq_separation,
        vertical_choice_separation=settings.vertical_choice_separation,
        vertical_seq_separation=settings.vertical_seq_separation,
        arc_radius=settings.arc_radius,
        arc_margin=settings.arc_margin,
        terminal_padding=settings.terminal_padding,
        terminal_radius=settings.terminal_radius,
        terminal_height=settings.terminal_height,
        non_terminal_padding=settings.non_terminal_padding,
        non_terminal_radius=settings.non_terminal_radius,
        non_terminal_height=settings.non_terminal_height,
        comment_padding=settings.comment_padding,
        comment_radius=settings.comment_radius,
        comment_height=settings.comment_height,
        character_advance=settings.character_advance,
        wide_character_advance=settings.wide_character_advance,
        marker_width=20,
        marker_projected_height=10,
        end_class=settings.end_class,
    )


class _SvgRender(_Render):
    def __init__(
        self,
        width: int,
        height: int,
        layout_settings: _LayoutSettings,
        css_class: str,
        css: str | dict[str, dict[str, str]] | None,
    ):
        self._layout_settings = layout_settings
        self._root = _SvgElement(
            "svg",
            {
                "width": width,
                "height": height,
                "class": css_class,
                "viewBox": f"0 0 {width} {height}",
            },
        )

        if css:
            if not isinstance(css, str):
                stream = io.StringIO()
                for rule, items in css.items():
                    stream.write(rule)
                    stream.write("{")
                    for name, value in items.items():
                        stream.write(name)
                        stream.write(":")
                        stream.write(value)
                        stream.write(";")
                    stream.write("}")
                css = stream.getvalue()

            self._style = self._root.elem("style")
            self._style.children.append(css)

    @property
    def layout_settings(self) -> _LayoutSettings:
        return self._layout_settings

    def write(self, f=sys.stdout):
        self._root.write_svg(f)
        f.flush()

    def to_string(self):
        stream = io.StringIO()
        self.write(stream)
        return stream.getvalue()

    def line(self, x: int, y: int, reverse: bool = False) -> _Line:
        return _SvgLine(self, x, y)

    def node(self, x: int, y: int, node: _Node):
        g = self._root.elem(
            "g",
            {
                "class": node._css_class,
            },
        )

        g.elem(
            "rect",
            {
                "x": x,
                "y": y - node._up,
                "width": node._width,
                "height": node._up + node._down,
                "rx": node._radius,
                "ry": node._radius,
            },
        )

        if node._href:
            g = g.elem(
                "a",
                {
                    "xlink:href": node._href,
                },
            )

        g.elem("text", {"x": x + node._width / 2, "y": y}, [node._text])

    def start(self, x: int, y: int):
        w = self.layout_settings.marker_width
        h = self.layout_settings.marker_projected_height
        dh = 2 * self.layout_settings.marker_projected_height

        path = self._root.elem("path")

        if self.layout_settings.end_class == EndClass.SIMPLE:
            path.attrs["d"] = f"M{x} {y}h{w}m{-dh} {-h}v{dh}"
        elif self.layout_settings.end_class == EndClass.COMPLEX:
            path.attrs["d"] = f"M{x} {y}h{w}m{-dh} {-h}v{dh}m10 {-dh}v{dh}"
        else:
            raise NotImplementedError(
                f"unknown end class {self.layout_settings.end_class}"
            )

    def end(self, x: int, y: int):
        w = self.layout_settings.marker_width
        h = self.layout_settings.marker_projected_height
        dh = 2 * self.layout_settings.marker_projected_height

        path = self._root.elem("path")

        if self.layout_settings.end_class == EndClass.SIMPLE:
            path.attrs["d"] = f"M{x} {y}h{w}m0 {-h}v{dh}"
        elif self.layout_settings.end_class == EndClass.COMPLEX:
            path.attrs["d"] = f"M{x} {y}h{w}m0 {-h}v{dh}m-10 {-dh}v{dh}"
        else:
            raise NotImplementedError(
                f"unknown end class {self.layout_settings.end_class}"
            )


class _SvgLine(_Line):
    def __init__(self, render: _SvgRender, x: int, y: int):
        self._render = render
        self._x = x
        self._y = y
        self._elem = render._root.elem("path")
        self._elem.attrs["d"] = f"M{x} {y}"

    def segment(
        self, w: int, arrow_begin: bool = False, arrow_end: bool = False
    ) -> _Line:
        return self.segment_abs(self._x + w, arrow_begin, arrow_end)

    def segment_abs(
        self, x: int, arrow_begin: bool = False, arrow_end: bool = False
    ) -> _Line:
        self._elem.attrs["d"] += f"H{x}"
        self._x = x
        return self

    def bend_forward(
        self,
        h: int,
        d: _Line.Direction = "e",
        arrow_begin: bool = False,
        arrow_end: bool = False,
    ) -> _Line:
        return self._bend(h, self.reverse_direction(d), d)

    def bend_forward_abs(
        self,
        y: int,
        d: _Line.Direction = "e",
        arrow_begin: bool = False,
        arrow_end: bool = False,
    ) -> _Line:
        return self.bend_forward(y - self._y, d, arrow_begin, arrow_end)

    def bend_reverse(
        self,
        h: int,
        d: _Line.Direction = "e",
        arrow_begin: bool = False,
        arrow_end: bool = False,
    ) -> _Line:
        return self._bend(h, d, d)

    def bend_reverse_abs(
        self,
        y: int,
        d: _Line.Direction = "e",
        arrow_begin: bool = False,
        arrow_end: bool = False,
    ) -> _Line:
        return self.bend_reverse(y - self._y, d, arrow_begin, arrow_end)

    def _bend(self, h: int, coming_from: str, coming_to: str):
        double_arc_radius = math.ceil(2 * self._render.layout_settings.arc_radius)

        if abs(h) < double_arc_radius:
            return self._bend_bezier(h, coming_from, coming_to)
        elif h > 0:
            h -= double_arc_radius
            intermediate_d = ("s", "n")
        else:
            h += double_arc_radius
            intermediate_d = ("n", "s")

        self._arc(coming_from, intermediate_d[0])

        self._elem.attrs["d"] += f"v{h}"
        self._y += h

        self._arc(intermediate_d[1], coming_to)

        return self

    def _arc(self, coming_from: str, coming_to: str):
        arc_radius = math.ceil(self._render.layout_settings.arc_radius)

        x = arc_radius
        y = arc_radius
        if coming_from == "e" or coming_to == "w":
            x = -x
        if coming_from == "s" or coming_to == "n":
            y = -y

        sf = (
            0
            if (coming_from, coming_to)
            in [("n", "e"), ("e", "s"), ("s", "w"), ("w", "n")]
            else 1
        )

        self._elem.attrs["d"] += f"a{arc_radius} {arc_radius} 0 0 {sf} {x} {y}"

        self._x += x
        self._y += y

        return self

    def _bend_bezier(self, h: int, coming_from: str, coming_to: str):
        double_arc_radius = math.ceil(2 * self._render.layout_settings.arc_radius)

        interm_x_1: float = self._x
        interm_y_1 = self._y
        interm_x_2: float = self._x
        interm_y_2 = self._y + h
        out_x = self._x
        out_y = self._y + h

        if coming_from == "w" and coming_to == "e":
            interm_x_1 += 2 * double_arc_radius / 3
            interm_x_2 += double_arc_radius / 3
            out_x += double_arc_radius
        elif coming_from == "e" and coming_to == "w":
            interm_x_1 -= 2 * double_arc_radius / 3
            interm_x_2 -= double_arc_radius / 3
            out_x -= double_arc_radius
        elif coming_from == coming_to == "w":
            interm_x_1 += 2 * double_arc_radius / 3
            interm_x_2 += 2 * double_arc_radius / 3
        else:
            interm_x_1 -= 2 * double_arc_radius / 3
            interm_x_2 -= 2 * double_arc_radius / 3

        self._elem.attrs[
            "d"
        ] += f"C{interm_x_1} {interm_y_1} {interm_x_2} {interm_y_2} {out_x} {out_y}"

        self._x = out_x
        self._y += h

        return self


@dataclass
class _SvgElement:
    name: str
    """Name of SVG node"""

    attrs: dict[str, _t.Any] = field(default_factory=dict)
    """SVG node attributes"""

    children: list[_SvgElement | str] = field(default_factory=list)
    """Children SVG nodes"""

    def elem(self, name: str, *args):
        return _SvgElement(name, *args).add_to(self)

    def add_to(self, parent: _SvgElement) -> _SvgElement:
        parent.children.append(self)
        return self

    def write_svg(self, f: _t.TextIO):
        f.write(f"<{self.name}")
        for name, value in sorted(self.attrs.items()):
            f.write(f' {name}="{self._e(value)}"')
        f.write(">")
        for child in self.children:
            if isinstance(child, _SvgElement):
                child.write_svg(f)
            else:
                f.write(self._e(child))
        f.write(f"</{self.name}>")

    _ESCAPE_RE = re.compile(r"[*_`\[\]<&]", re.UNICODE)

    @staticmethod
    def _e(text):
        return _SvgElement._ESCAPE_RE.sub(lambda c: f"&#{ord(c[0])};", str(text))
