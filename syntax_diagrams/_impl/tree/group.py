from __future__ import annotations

import math
import typing as _t
from dataclasses import replace

import grapheme  # type: ignore
import wcwidth  # type: ignore

from syntax_diagrams._impl.render import (
    LayoutContext,
    LayoutSettings,
    Render,
    RenderContext,
)
from syntax_diagrams._impl.tree import Element
from syntax_diagrams._impl.tree.barrier import Barrier
from syntax_diagrams._impl.vec import Vec

T = _t.TypeVar("T")


class Group(Element[T], _t.Generic[T]):
    _text_width: int

    def __init__(
        self,
        item: Element[T],
        text: str | None = None,
        css_class: str | None = None,
        href: str | None = None,
        title: str | None = None,
    ):
        self._text = text
        self._item = Barrier(item)
        self._css_class = css_class
        self._href = href
        self._title = title

    def _calculate_content_layout(
        self, settings: LayoutSettings[T], context: LayoutContext
    ):
        context = self._isolate()
        context = replace(
            context,
            width=max(
                0,
                context.width
                - 2 * (settings.group_vertical_padding + settings.group_thickness),
            ),
            allow_shrinking_stacks=False,
        )

        self._item._calculate_layout(settings, context)

        self._text_width = (
            math.ceil(
                sum(
                    (
                        settings.group_character_advance
                        if wcwidth.wcwidth(g) == 1  # type: ignore
                        else settings.group_wide_character_advance
                    )
                    for g in grapheme.graphemes(self._text)  # type: ignore
                )
            )
            if self._text
            else 0
        )
        self._group_text_vertical_offset = (
            settings.group_text_vertical_offset + settings.group_text_height
            if self._text
            else 0
        )

        self._content_width = max(self._item._width, self._text_width) + 2 * (
            settings.group_horizontal_padding + settings.group_thickness
        )
        self._start_padding = 0
        self._end_padding = 0
        self._start_margin = settings.group_horizontal_margin
        self._end_margin = settings.group_horizontal_margin
        self._height = self._item._height
        self._up = (
            self._item._up
            + settings.group_vertical_padding
            + settings.group_thickness
            + self._group_text_vertical_offset
            + settings.group_vertical_margin
        )
        self._down = (
            self._item._down
            + settings.group_vertical_padding
            + settings.group_thickness
            + settings.group_vertical_margin
        )
        self._display_width = self._width

    def _render_content(self, render: Render[T], context: RenderContext):
        context = replace(
            context,
            pos=context.pos
            + Vec(
                context.dir
                * (
                    render.settings.group_horizontal_padding
                    + render.settings.group_thickness
                ),
                0,
            ),
        )
        self._item._render(render, context)

        render.group(
            context.pos
            - Vec(
                context.dir
                * (
                    render.settings.group_horizontal_padding
                    + render.settings.group_thickness
                ),
                self._item._up
                + render.settings.group_vertical_padding
                + render.settings.group_thickness,
            ),
            self._width,
            2
            * (render.settings.group_vertical_padding + render.settings.group_thickness)
            + self._item._up
            + self._item._height
            + self._item._down,
            self._css_class,
            self._text_width,
            self._text,
            self._href,
            self._title,
        )

    def __str__(self) -> str:
        return f"<{self._text}>({self._item})"
