from __future__ import annotations

import math
import typing as _t

from syntax_diagrams._impl.render import (
    ConnectionType,
    LayoutContext,
    LayoutSettings,
    Render,
    RenderContext,
)
from syntax_diagrams._impl.tree import Element
from syntax_diagrams._impl.vec import Vec

T = _t.TypeVar("T")


class Skip(Element[T], _t.Generic[T]):
    def _calculate_content_layout(
        self, settings: LayoutSettings[T], context: LayoutContext
    ):
        self.__start_connection = context.start_connection
        self.__start_arc_size = self.__start_connection.arc_size(settings)
        self.__end_connection = context.end_connection
        self.__end_arc_size = self.__end_connection.arc_size(settings)

        self._isolate()

    def render(self, render: Render[T], context: RenderContext):
        render.enter(self)
        render.debug_ridge_line(context.pos, self, context.reverse)

        start_content_pos = context.pos + Vec(context.dir * self.__start_arc_size, 0)
        match self.__start_connection:
            case (
                ConnectionType.NULL | ConnectionType.NORMAL | ConnectionType.STACK_BOUND
            ):
                line = (render).line(
                    context.start_connection_pos,
                    context.reverse,
                    "dbg-isolated-line",
                )
            case ConnectionType.STACK:
                line = (
                    (render)
                    .line(
                        context.start_connection_pos,
                        context.reverse,
                        "dbg-isolated-line",
                    )
                    .bend_backward_abs(start_content_pos.y, arrow_begin=True)
                )
            case ConnectionType.SPLIT:
                line = (
                    (render)
                    .line(
                        context.start_connection_pos,
                        context.reverse,
                        "dbg-isolated-line",
                    )
                    .bend_forward_abs(start_content_pos.y, arrow_begin=True)
                )

        match self.__end_connection:
            case ConnectionType.NULL:
                pass
            case ConnectionType.NORMAL | ConnectionType.STACK_BOUND:
                (
                    (line).segment_abs(
                        context.end_connection_pos.x, arrow_begin=True, arrow_end=True
                    )
                )
            case ConnectionType.STACK:
                (
                    (line)
                    .segment_abs(
                        context.end_connection_pos.x, arrow_begin=True, arrow_end=True
                    )
                    .bend_backward_reverse_abs(
                        context.end_connection_pos.y, arrow_end=True
                    )
                )
            case ConnectionType.SPLIT:
                arc_radius = context.dir * math.ceil(2 * render.settings.arc_radius)
                (
                    (line)
                    .segment_abs(
                        context.end_connection_pos.x - arc_radius,
                        arrow_begin=True,
                        arrow_end=True,
                    )
                    .bend_forward_abs(context.end_connection_pos.y, arrow_end=True)
                )

        render.debug_pos(context.pos, "dbg-primary-pos")
        render.debug_pos(context.start_connection_pos, "dbg-primary-pos")
        render.debug_pos(context.end_connection_pos, "dbg-primary-pos")
        render.exit()

    def _render_content(self, render: Render[T], context: RenderContext):
        pass

    def __str__(self) -> str:
        return "<SKIP>"
