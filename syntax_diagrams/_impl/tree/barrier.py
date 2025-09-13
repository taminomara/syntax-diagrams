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
    def _precedence(self) -> int:
        return self._item._precedence

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

        self._item._calculate_layout(settings, context)

        self._display_width = self._item._display_width
        self._content_width = self._item._content_width
        self._start_padding = self._item._start_padding
        self._end_padding = self._item._end_padding
        self._start_margin = self._item._start_margin
        self._end_margin = self._item._end_margin
        self._height = self._item._height
        self._up = self._item._up
        self._down = self._item._down

    def _render_content(self, render: Render[T], context: RenderContext):
        context = replace(
            context,
            opt_enter_top=None,
            opt_enter_bottom=None,
            opt_exit_top=None,
            opt_exit_bottom=None,
        )

        self._item._render(render, context)

    def _calculate_top_ridge_line(self) -> RidgeLine:
        return self._item._top_ridge_line

    def _calculate_bottom_ridge_line(self) -> RidgeLine:
        return self._item._bottom_ridge_line

    def __str__(self) -> str:
        return str(self._item)
