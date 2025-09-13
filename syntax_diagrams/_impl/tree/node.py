from __future__ import annotations

import math
import re
import typing as _t

import grapheme  # type: ignore
import wcwidth  # type: ignore

from syntax_diagrams._impl.render import (
    LayoutContext,
    LayoutSettings,
    NodeStyle,
    Render,
    RenderContext,
)
from syntax_diagrams._impl.tree import Element
from syntax_diagrams._impl.vec import Vec

T = _t.TypeVar("T")


class Node(Element[T], _t.Generic[T]):
    _style: NodeStyle
    _text: str
    _href: str | None
    _title: str | None
    _resolve: bool
    _resolver_data: T | None
    _css_class: str

    _padding: int
    _radius: int

    def __init__(
        self,
        render: NodeStyle,
        text: str,
        href: str | None = None,
        title: str | None = None,
        css_class: str | None = None,
        resolve: bool = True,
        resolver_data: T | None = None,
    ):
        self._style = render
        self._text = text
        self._href = href
        self._title = title
        self._resolve = resolve
        self._text_is_weak = resolver_data
        self._css_class = css_class or ""

    def _calculate_content_layout(
        self, settings: LayoutSettings[T], context: LayoutContext
    ):
        self._isolate()

        if self._resolve:
            self._text, self._href, self._title = settings.href_resolver.resolve(
                self._text, self._href, self._title, self._resolver_data
            )

        if self._style == NodeStyle.TERMINAL:
            height = settings.terminal_height
            character_advance = settings.terminal_character_advance
            wide_character_advance = settings.terminal_wide_character_advance
            self._padding = padding = settings.terminal_padding
            self._radius = settings.terminal_radius
        elif self._style == NodeStyle.NON_TERMINAL:
            height = settings.non_terminal_height
            character_advance = settings.non_terminal_character_advance
            wide_character_advance = settings.non_terminal_wide_character_advance
            self._padding = padding = settings.non_terminal_padding
            self._radius = settings.non_terminal_radius
        else:
            height = settings.comment_height
            character_advance = settings.comment_character_advance
            wide_character_advance = settings.comment_wide_character_advance
            self._padding = padding = settings.comment_padding
            self._radius = settings.comment_radius

        text_width = math.ceil(
            sum(
                (
                    character_advance
                    if wcwidth.wcwidth(g) == 1  # type: ignore
                    else wide_character_advance
                )
                for g in grapheme.graphemes(self._text)  # type: ignore
            )
        )

        self._display_width = self._content_width = text_width + 2 * padding
        self._height = 0
        self._up = math.ceil(height / 2)
        self._down = math.floor(height / 2)
        self._start_margin = self._end_margin = settings.horizontal_seq_separation

    def _render_content(self, render: Render[T], context: RenderContext):
        if not context.reverse:
            pos = context.pos
        else:
            pos = context.pos - Vec(self._content_width, 0)
        render.node(
            pos=pos,
            style=self._style,
            css_class=self._css_class,
            content_width=self._content_width,
            up=self._up,
            down=self._down,
            radius=self._radius,
            padding=self._padding,
            text=self._text,
            href=self._href,
            title=self._title,
        )

    def __str__(self):
        if re.match(r"^[a-zA-Z0-9_-]+$", self._text) is not None:
            return self._text
        else:
            return repr(self._text)
