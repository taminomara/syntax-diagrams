from __future__ import annotations

import math
import re
import typing as _t

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

    _horizontal_padding: int
    _radius: int
    _text_width: int
    _text_height: int
    _processed_text: str
    _processed_href: str | None
    _processed_title: str | None

    def __init__(
        self,
        render: NodeStyle,
        text: str,
        href: str | None = None,
        title: str | None = None,
        css_class: str | None = None,
        resolve: bool | None = None,
        resolver_data: T | None = None,
    ):
        self._style = render
        self._text = text
        self._href = href
        self._title = title
        self._resolve = resolve if resolve is not None else True
        self._resolver_data = resolver_data
        self._css_class = css_class or ""

    def _calculate_content_layout(
        self, settings: LayoutSettings[T], context: LayoutContext
    ):
        self._isolate()

        if self._resolve:
            self._processed_text, self._processed_href, self._processed_title = (
                settings.href_resolver.resolve(
                    self._text, self._href, self._title, self._resolver_data
                )
            )
        else:
            self._processed_text, self._processed_href, self._processed_title = (
                self._text,
                self._href,
                self._title,
            )

        if self._style == NodeStyle.TERMINAL:
            text_measure = settings.terminal_text_measure
            self._horizontal_padding = settings.terminal_horizontal_padding
            self._vertical_padding = settings.terminal_vertical_padding
            self._radius = settings.terminal_radius
        elif self._style == NodeStyle.NON_TERMINAL:
            text_measure = settings.non_terminal_text_measure
            self._horizontal_padding = settings.non_terminal_horizontal_padding
            self._vertical_padding = settings.non_terminal_vertical_padding
            self._radius = settings.non_terminal_radius
        else:
            text_measure = settings.comment_text_measure
            self._horizontal_padding = settings.comment_horizontal_padding
            self._vertical_padding = settings.comment_vertical_padding
            self._radius = settings.comment_radius

        self._text_width, self._text_height = text_measure.measure(self._processed_text)

        self.display_width = self.content_width = (
            self._text_width + 2 * self._horizontal_padding
        )
        self.height = 0
        self.up = self.down = math.ceil(self._text_height / 2) + self._vertical_padding
        self.start_margin = self.end_margin = settings.horizontal_seq_separation

    def _render_content(self, render: Render[T], context: RenderContext):
        if not context.reverse:
            pos = context.pos
        else:
            pos = context.pos - Vec(self.content_width, 0)
        render.node(
            pos=pos,
            style=self._style,
            css_class=self._css_class,
            content_width=self.content_width,
            up=self.up,
            down=self.down,
            radius=self._radius,
            padding=self._horizontal_padding,
            text_width=self._text_width,
            text_height=self._text_height,
            text=self._processed_text,
            href=self._processed_href,
            title=self._processed_title,
        )

    def __str__(self):
        if re.match(r"^[a-zA-Z0-9_-]+$", self._text) is not None:
            return self._text
        else:
            return repr(self._text)
