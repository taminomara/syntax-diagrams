from __future__ import annotations

import typing as _t
from dataclasses import replace

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

        self._item.calculate_layout(settings, context)

        self._text_width, self._text_height = (
            settings.group_text_measure.measure(self._text) if self._text else (0, 0)
        )

        self.content_width = max(self._item.width, self._text_width) + 2 * (
            settings.group_horizontal_padding + settings.group_thickness
        )
        self.start_padding = 0
        self.end_padding = 0
        self.start_margin = settings.group_horizontal_margin
        self.end_margin = settings.group_horizontal_margin
        self.height = self._item.height
        self.up = (
            self._item.up
            + settings.group_vertical_padding
            + settings.group_thickness
            + self._text_height
            + (settings.group_text_vertical_offset if self._text else 0)
            + settings.group_vertical_margin
        )
        self.down = (
            self._item.down
            + settings.group_vertical_padding
            + settings.group_thickness
            + settings.group_vertical_margin
        )
        self.display_width = self.width

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
        if not context.reverse:
            pos = context.pos
        else:
            pos = context.pos - Vec(self.width, 0)
        render.group(
            pos
            - Vec(
                context.dir
                * (
                    render.settings.group_horizontal_padding
                    + render.settings.group_thickness
                ),
                self._item.up
                + render.settings.group_vertical_padding
                + render.settings.group_thickness,
            ),
            self.width,
            2
            * (render.settings.group_vertical_padding + render.settings.group_thickness)
            + self._item.up
            + self._item.height
            + self._item.down,
            self._css_class,
            self._text_width,
            self._text_height,
            self._text,
            self._href,
            self._title,
        )

        self._item.render(render, context)

    def __str__(self) -> str:
        return f"<{self._text}>({self._item})"
