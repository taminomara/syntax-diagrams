from __future__ import annotations

import typing as _t

from syntax_diagrams._impl.render import (
    LayoutContext,
    LayoutSettings,
    Render,
    RenderContext,
)
from syntax_diagrams._impl.tree import Element
from syntax_diagrams._impl.vec import Vec

T = _t.TypeVar("T")


class End(Element[T], _t.Generic[T]):
    def __init__(self, reverse: bool = False) -> None:
        self._reverse = reverse

    def _calculate_content_layout(
        self, settings: LayoutSettings[T], context: LayoutContext
    ):
        self._isolate()

        self.display_width = self.content_width = settings.marker_width
        self.up = settings.marker_projected_height
        self.down = settings.marker_projected_height
        self.start_margin = 0  # TODO: use node margin?
        self.end_margin = 0

    def _render_content(self, render: Render[T], context: RenderContext):
        if context.reverse:
            pos = context.pos - Vec(self.content_width, 0)
        else:
            pos = context.pos
        if self._reverse ^ context.reverse:
            render.right_marker(pos)
        else:
            render.left_marker(pos)

    def __str__(self) -> str:
        return "^" if self._reverse else "$"
