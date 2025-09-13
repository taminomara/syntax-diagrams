from __future__ import annotations

import typing as _t

from syntax_diagrams._impl.render import (
    LayoutContext,
    LayoutSettings,
    Render,
    RenderContext,
)
from syntax_diagrams._impl.tree import Element

T = _t.TypeVar("T")


class Skip(Element[T], _t.Generic[T]):
    def _calculate_content_layout(
        self, settings: LayoutSettings[T], context: LayoutContext
    ):
        self._isolate()

    def _render_content(self, render: Render[T], context: RenderContext):
        pass

    def __str__(self) -> str:
        return "<SKIP>"
