from __future__ import annotations

import typing as _t
from dataclasses import replace
from functools import cached_property

from syntax_diagrams._impl.render import (
    LayoutContext,
    LayoutSettings,
    Render,
    RenderContext,
)
from syntax_diagrams._impl.ridge_line import RidgeLine
from syntax_diagrams._impl.tree import Element
from syntax_diagrams._impl.tree.skip import Skip

T = _t.TypeVar("T")


class Barrier(Element[T], _t.Generic[T]):
    _item: Element[T]

    def __new__(cls, item: Element[T]) -> Element[T]:
        if isinstance(item, (Barrier, Skip)):
            return item

        self = super().__new__(cls)
        self._item = item
        return self

    @cached_property
    def precedence(self) -> int:
        return self._item.precedence

    def _calculate_content_layout(
        self, settings: LayoutSettings[T], context: LayoutContext
    ):
        context = self._isolate()
        context = replace(
            context,
            opt_enter_top=None,
            opt_enter_bottom=None,
            opt_exit_top=None,
            opt_exit_bottom=None,
        )

        self._item.calculate_layout(settings, context)

        self.display_width = self._item.display_width
        self.content_width = self._item.content_width
        self.start_padding = self._item.start_padding
        self.end_padding = self._item.end_padding
        self.start_margin = self._item.start_margin
        self.end_margin = self._item.end_margin
        self.height = self._item.height
        self.up = self._item.up
        self.down = self._item.down

    def _render_content(self, render: Render[T], context: RenderContext):
        context = replace(
            context,
            opt_enter_top=None,
            opt_enter_bottom=None,
            opt_exit_top=None,
            opt_exit_bottom=None,
        )

        self._item.render(render, context)

    def _calculate_top_ridge_line(self) -> RidgeLine:
        return self._item.top_ridge_line

    def _calculate_bottom_ridge_line(self) -> RidgeLine:
        return self._item.bottom_ridge_line

    def __str__(self) -> str:
        return str(self._item)
