from __future__ import annotations

import base64
import io
import math
import re
import sys
import typing as _t
import uuid
from dataclasses import dataclass, field

from syntax_diagrams._impl.render import (
    ConnectionDirection,
    ConnectionType,
    Direction,
    LayoutContext,
    LayoutSettings,
    Line,
    NodeStyle,
    Render,
    RenderContext,
)
from syntax_diagrams._impl.tree import Element
from syntax_diagrams._impl.tree.barrier import Barrier
from syntax_diagrams._impl.tree.end import End
from syntax_diagrams._impl.tree.sequence import Sequence
from syntax_diagrams._impl.vec import Vec
from syntax_diagrams.element import LineBreak
from syntax_diagrams.measure import TextMeasure
from syntax_diagrams.render import ArrowStyle, EndClass, SvgRenderSettings
from syntax_diagrams.resolver import HrefResolver

T = _t.TypeVar("T")


def render_svg(
    node: Element[T],
    /,
    *,
    max_width: int | None = None,
    settings: SvgRenderSettings = SvgRenderSettings(),
    reverse: bool | None = None,
    href_resolver: HrefResolver[T] = HrefResolver(),
    dump_debug_data: bool = False,
) -> str:
    if max_width is None:
        max_width = settings.max_width
    if reverse is None:
        reverse = settings.reverse

    max_width = max(0, max_width - settings.padding[3] - settings.padding[1])

    node = Sequence(
        [End(), Barrier(Sequence([node, End(reverse=True)], LineBreak.NO_BREAK))],
        LineBreak.NO_BREAK,
    )

    layout_settings = svg_layout_settings(settings)
    layout_settings.href_resolver = href_resolver
    node.calculate_layout(
        layout_settings,
        LayoutContext(
            width=max_width,
            is_outer=True,
            start_connection=ConnectionType.NULL,
            start_top_is_clear=True,
            start_bottom_is_clear=True,
            start_direction=ConnectionDirection.STRAIGHT,
            end_connection=ConnectionType.NULL,
            end_top_is_clear=True,
            end_bottom_is_clear=True,
            end_direction=ConnectionDirection.STRAIGHT,
            allow_shrinking_stacks=True,
        ),
    )

    render = SvgRender(
        (settings.padding[3] + node.display_width + settings.padding[1]),
        (
            settings.padding[0]
            + node.up
            + node.height
            + node.down
            + settings.padding[2]
            + 1
        ),
        layout_settings,
        settings.css_class,
        settings.css_style,
        settings.title,
        settings.description,
        settings.arrow_style,
        settings.arrow_length,
        settings.arrow_cross_length,
        dump_debug_data,
    )

    pos = Vec(settings.padding[3], settings.padding[0] + node.up)
    if not reverse:
        start_connection_pos = pos
        end_connection_pos = pos + Vec(node.width, node.height)
    else:
        start_connection_pos = pos + Vec(node.display_width, 0)
        end_connection_pos = pos + Vec(node.display_width - node.width, node.height)

    node.render(
        render,
        RenderContext(
            pos=start_connection_pos,
            start_connection_pos=start_connection_pos,
            end_connection_pos=end_connection_pos,
            reverse=reverse,
        ),
    )

    if dump_debug_data:
        return render.debug_data()
    else:
        return render.to_string()


def svg_layout_settings(settings: SvgRenderSettings = SvgRenderSettings()):
    return LayoutSettings(
        horizontal_seq_separation=settings.horizontal_seq_separation,
        vertical_choice_separation_outer=settings.vertical_choice_separation_outer,
        vertical_choice_separation=settings.vertical_choice_separation,
        vertical_seq_separation_outer=settings.vertical_seq_separation_outer,
        vertical_seq_separation=settings.vertical_seq_separation,
        arc_radius=settings.arc_radius,
        arc_margin=settings.arc_margin,
        terminal_text_measure=settings.terminal_text_measure,
        terminal_horizontal_padding=settings.terminal_horizontal_padding,
        terminal_radius=settings.terminal_radius,
        terminal_vertical_padding=settings.terminal_vertical_padding,
        non_terminal_text_measure=settings.non_terminal_text_measure,
        non_terminal_horizontal_padding=settings.non_terminal_horizontal_padding,
        non_terminal_radius=settings.non_terminal_radius,
        non_terminal_vertical_padding=settings.non_terminal_vertical_padding,
        comment_text_measure=settings.comment_text_measure,
        comment_horizontal_padding=settings.comment_horizontal_padding,
        comment_radius=settings.comment_radius,
        comment_vertical_padding=settings.comment_vertical_padding,
        group_text_measure=settings.group_text_measure,
        group_vertical_padding=settings.group_vertical_padding,
        group_horizontal_padding=settings.group_horizontal_padding,
        group_vertical_margin=settings.group_vertical_margin,
        group_horizontal_margin=settings.group_horizontal_margin,
        group_thickness=0,
        group_radius=settings.group_radius,
        group_text_vertical_offset=settings.group_text_vertical_offset,
        group_text_horizontal_offset=settings.group_text_horizontal_offset,
        marker_width=20,
        marker_projected_height=10,
        hidden_symbol_escape=("\0", "\0"),
        end_class=settings.end_class,
    )


class SvgRender(Render[T], _t.Generic[T]):
    def __init__(
        self,
        width: int,
        height: int,
        settings: LayoutSettings[T],
        css_class: str,
        css: str | dict[str, dict[str, str]] | None,
        title: str | None,
        description: str | None,
        arrow_style: ArrowStyle,
        arrow_length: int,
        arrow_cross_length: int,
        dump_debug_data: bool = False,
    ):
        super().__init__(settings, dump_debug_data)

        self._width = width

        self._root = SvgRender._SvgElement(
            "svg",
            {
                "xmlns": "http://www.w3.org/2000/svg",
                "xmlns:xlink": "http://www.w3.org/1999/xlink",
                "width": width,
                "height": height,
                "class": css_class,
                "viewBox": f"0 0 {width} {height}",
                "role": "img",
            },
        )

        if title is not None:
            self._root.attrs["aria-label"] = title
            self._root.elem("title").children.append(self._e(title))
        if description is not None:
            self._root.elem("desc").children.append(self._e(description))

        self._arrow_style = arrow_style
        self._arrow_length = arrow_length
        self._arrow_cross_length = arrow_cross_length
        self._arrow_id = (
            f"arrow-{base64.urlsafe_b64encode(uuid.uuid4().bytes).decode()}"
        )
        self._arrow_class = f"arrow arrow-{str(arrow_style.value).lower()}"

        defs = self._root.elem("defs")
        match self._arrow_style:
            case ArrowStyle.NONE:
                pass
            case ArrowStyle.TRIANGLE:
                defs.elem(
                    "path",
                    {
                        "id": self._arrow_id,
                        "class": self._arrow_class,
                        "d": f"M 0 0 L -{arrow_length} -{arrow_cross_length} L -{arrow_length} {arrow_cross_length} z",
                    },
                )
            case ArrowStyle.STEALTH:
                defs.elem(
                    "path",
                    {
                        "id": self._arrow_id,
                        "class": self._arrow_class,
                        "d": f"M 0 0 L -{arrow_length} -{arrow_cross_length} L -{3 * arrow_length / 4} 0 L -{arrow_length} {arrow_cross_length} z",
                    },
                )
            case ArrowStyle.BARB:
                defs.elem(
                    "path",
                    {
                        "id": self._arrow_id,
                        "class": self._arrow_class,
                        "d": f"M 0 0 L -{arrow_length} -{arrow_cross_length} M 0 0 L -{arrow_length} {arrow_cross_length}",
                    },
                )
            case ArrowStyle.HARPOON:
                defs.elem(
                    "path",
                    {
                        "id": self._arrow_id,
                        "class": self._arrow_class,
                        "d": f"M 0 0 L -{arrow_length} {arrow_cross_length} L -{3 * arrow_length / 4} 0 z",
                    },
                )
            case ArrowStyle.HARPOON_UP:
                defs.elem(
                    "path",
                    {
                        "id": self._arrow_id,
                        "class": self._arrow_class,
                        "d": f"M 0 0 L -{arrow_length} -{arrow_cross_length} L -{3 * arrow_length / 4} 0 z",
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
            self._style.children.append(self._e(css))

        self._elems = [self._root.elem("g")]

    def write(self, f=sys.stdout):
        self._root.write_svg(f, self)
        f.flush()

    def to_string(self):
        stream = io.StringIO()
        self.write(stream)
        return stream.getvalue()

    def enter(self, node: Element[_t.Any]):
        super().enter(node)

        attrs = {
            "class": "elem",
        }

        if self._debug:
            attrs["data-dbg-id"] = self._make_debug_id(node)

        self._elems.append(self._elem.elem("g", attrs))

    def exit(self):
        super().exit()

        self._elems.pop()

    @property
    def _elem(self) -> SvgRender._SvgElement:
        return self._elems[-1]

    def line(self, pos: Vec, reverse: bool = False, css_class: str = "") -> Line:
        return SvgRender._SvgLine(self, pos, reverse, css_class)

    def node(
        self,
        pos: Vec,
        style: NodeStyle,
        css_class: str | None,
        content_width: int,
        up: int,
        down: int,
        radius: int,
        padding: int,
        text_width: int,
        text_height: int,
        text: str,
        href: str | None,
        title: str | None,
    ):
        if css_class:
            css_class += " node "
        else:
            css_class = "node "
        match style:
            case NodeStyle.TERMINAL:
                css_class += " terminal"
                measure = self.settings.terminal_text_measure
            case NodeStyle.NON_TERMINAL:
                css_class += " non-terminal"
                measure = self.settings.non_terminal_text_measure
            case NodeStyle.COMMENT:
                css_class += " comment"
                measure = self.settings.comment_text_measure
        g = self._elem.elem(
            "g",
            {
                "class": css_class,
            },
        )

        g.elem(
            "rect",
            {
                "x": pos.x,
                "y": pos.y - up,
                "width": content_width,
                "height": up + down,
                "rx": radius,
                "ry": radius,
            },
        )

        if href:
            g = g.elem(
                "a",
                {
                    "xlink:href": href,
                    "title": title,
                },
            )

        self._make_text(
            pos.x + content_width / 2, pos.y, text, text_height, measure
        ).add_to(g)

    def group(
        self,
        pos: Vec,
        width: int,
        height: int,
        css_class: str | None,
        text_width: int,
        text_height: int,
        text: str | None,
        href: str | None,
        title: str | None,
    ):
        if css_class:
            css_class += " group "
        else:
            css_class = "group "

        g = self._elem.elem(
            "g",
            {
                "class": css_class,
            },
        )

        g.elem(
            "rect",
            {
                "x": pos.x,
                "y": pos.y,
                "width": width,
                "height": height,
                "rx": self.settings.group_radius,
                "ry": self.settings.group_radius,
            },
        )

        if not text:
            return

        if href:
            g = g.elem(
                "a",
                {
                    "xlink:href": href,
                    "title": title,
                },
            )

        self._make_text(
            pos.x + self.settings.group_text_horizontal_offset,
            pos.y - self.settings.group_text_vertical_offset,
            text,
            text_height,
            self.settings.group_text_measure,
            vertical_center=False,
        ).add_to(g)

    _UNESCAPE_RE = re.compile(r"\0(.*?)\0")

    def _make_text(
        self,
        x: float,
        y: float,
        text: str,
        text_height: int,
        measure: TextMeasure,
        vertical_center: bool = True,
    ) -> _SvgElement:
        style = f"font-size: {measure.font_size}px"

        lines = text.splitlines()
        line_height = text_height / len(lines) if lines else 0
        if vertical_center:
            # Pain =(
            ascent = measure.ascent + (measure.line_height - measure.font_size) / 2
            text_offset = text_height / 2 - ascent
        else:
            text_offset = text_height - line_height / 2

        g = SvgRender._SvgElement("g", {}, [])
        for i, line in enumerate(lines):
            e = g.elem(
                "text",
                {"x": x, "y": y - text_offset + i * line_height, "style": style},
            )

            j = 0
            for esc in self._UNESCAPE_RE.finditer(line):
                if part := line[j : esc.start()]:
                    e.children.append(self._e(part))
                j = esc.end()
                e.elem("tspan", {"class": "escape"}, [self._e(esc.group(1))])
            if part := line[j:]:
                e.children.append(self._e(part))

        return g

    def left_marker(self, pos: Vec):
        w = self.settings.marker_width
        h = self.settings.marker_projected_height
        dh = 2 * self.settings.marker_projected_height

        path = self._elem.elem("path")

        if self.settings.end_class == EndClass.SIMPLE:
            path.attrs["d"] = f"M{pos.x} {pos.y}h{w}m{-dh} {-h}v{dh}"
        elif self.settings.end_class == EndClass.COMPLEX:
            path.attrs["d"] = f"M{pos.x} {pos.y}h{w}m{-dh} {-h}v{dh}m10 {-dh}v{dh}"
        else:
            raise NotImplementedError(f"unknown end class {self.settings.end_class}")

    def right_marker(self, pos: Vec):
        w = self.settings.marker_width
        h = self.settings.marker_projected_height
        dh = 2 * self.settings.marker_projected_height

        path = self._elem.elem("path")

        if self.settings.end_class == EndClass.SIMPLE:
            path.attrs["d"] = f"M{pos.x} {pos.y}h{w}m0 {-h}v{dh}"
        elif self.settings.end_class == EndClass.COMPLEX:
            path.attrs["d"] = f"M{pos.x} {pos.y}h{w}m0 {-h}v{dh}m-10 {-dh}v{dh}"
        else:
            raise NotImplementedError(f"unknown end class {self.settings.end_class}")

    def debug(self, node: Element[_t.Any], context: RenderContext):
        if not self._debug:
            return

        if not context.reverse:
            pos = context.pos

            left_padding_box = pos.x
            right_padding_box = pos.x + node.width

            left_display_box = pos.x
            right_display_box = pos.x + node.display_width

            left_content_box = left_padding_box + node.start_padding
            right_content_box = right_padding_box - node.end_padding

            left_margin_box = left_content_box - node.start_margin
            right_margin_box = right_content_box + node.end_margin
        else:
            pos = context.pos - Vec(node.width, 0)

            left_padding_box = pos.x
            right_padding_box = pos.x + node.width

            left_display_box = pos.x
            right_display_box = pos.x + node.display_width

            left_content_box = left_padding_box + node.end_padding
            right_content_box = right_padding_box - node.start_padding

            left_margin_box = left_content_box - node.end_margin
            right_margin_box = right_content_box + node.start_margin

        self._debug_box(
            left_display_box,
            right_display_box,
            pos.y - node.up,
            node.up + node.height + node.down,
            "dbg-display",
        )
        self._debug_box(
            left_content_box,
            right_content_box,
            pos.y - node.up,
            node.up,
            "dbg-content",
        )
        self._debug_box(
            left_content_box, right_content_box, pos.y, node.height, "dbg-content-main"
        )
        self._debug_box(
            left_content_box,
            right_content_box,
            pos.y + node.height,
            node.down,
            "dbg-content",
        )
        self._debug_box(
            left_padding_box,
            right_padding_box,
            pos.y - node.up,
            node.up + node.height + node.down,
            "dbg-padding",
        )
        self._debug_box(
            left_margin_box,
            right_margin_box,
            pos.y - node.up,
            node.up + node.height + node.down,
            "dbg-margin",
        )

    def _debug_box(self, left: float, right: float, y: float, h: float, css_class: str):
        if h == 0:
            y -= 0.5
            h = 0.5
        self._elem.elem(
            "rect",
            {
                "x": left,
                "y": y,
                "width": right - left,
                "height": h,
                "class": css_class,
            },
        )

    def debug_pos(self, pos: Vec, css_class: str = ""):
        if not self._debug:
            return

        if css_class:
            css_class = f"dbg-position {css_class}"
        else:
            css_class = "dbg-position"
        self._elem.elem(
            "path",
            {
                "d": f"M{pos.x} {pos.y}h-5h10h-5v-5v10v-5",
                "class": css_class,
            },
        )

    def debug_ridge_line(self, pos: Vec, node: Element[_t.Any], reverse: bool):
        if not self._debug:
            return

        if not reverse:
            start = 0
            end = self._width
            dir = 1
        else:
            start = self._width
            end = 0
            dir = -1

        d = f"M{start} {pos.y - node.top_ridge_line.before}"
        for p in node.top_ridge_line.ridge:
            d += f"H{pos.x + dir * p.x}V{pos.y - p.y}"
        d += f"H{end}"
        pos = pos + Vec(0, node.height)
        for p in reversed(node.bottom_ridge_line.ridge):
            d += f"V{pos.y + p.y}H{pos.x + dir * p.x}"
        d += f"V{pos.y + node.bottom_ridge_line.before}H{start}Z"

        self._elem.elem(
            "path",
            {
                "d": d,
                "class": "dbg-ridge-line",
            },
        )

    _ESCAPE_RE = re.compile(r"[*_`\[\]<&\"]", re.UNICODE)

    def _e(self, text: _t.Any):
        return self._ESCAPE_RE.sub(lambda c: f"&#{ord(c[0])};", str(text))

    class _SvgLine(Line):
        def __init__(
            self, render: SvgRender[_t.Any], pos: Vec, reverse: bool, css_class: str
        ):
            self._render = render
            self._pos = Vec(pos.x, pos.y)
            self._reverse = reverse
            self._elem = render._elem.elem("path")
            self._elem.attrs["d"] = f"M{pos.x} {pos.y}"
            if css_class:
                self._elem.attrs["class"] = css_class

        def segment_abs(
            self, x: int, arrow_begin: bool = False, arrow_end: bool = False
        ) -> Line:
            w = x - self._pos.x

            if arrow_begin and abs(w) >= self._render._arrow_length:
                self._arrow("e" if w >= 0 else "w")

            self._elem.attrs["d"] += f"H{x}"
            self._pos.x = x

            if arrow_end and abs(w) >= self._render._arrow_length:
                self._arrow("e" if w >= 0 else "w", end=True)

            return self

        def _arrow(self, d: Direction, end: bool = False):
            if self._render._arrow_style is ArrowStyle.NONE:
                return
            transform = f"translate({self._pos.x}, {self._pos.y})"
            if d == "w":
                transform += f" scale(-1, 1)"
            if not end:
                transform += f" translate({self._render._arrow_length}, 0)"
            self._render._elem.elem(
                "use",
                {
                    "href": f"#{self._render._arrow_id}",
                    "class": self._render._arrow_class,
                    "transform": transform,
                },
            )

        def bend(
            self,
            y: int,
            coming_from: Direction,
            coming_to: Direction | None,
            arrow_begin: bool = False,
            arrow_end: bool = False,
        ):
            h = y - self._pos.y

            double_arc_radius = math.ceil(2 * self._render.settings.arc_radius)

            if abs(h) < double_arc_radius:
                return self._bend_bezier(h, coming_from, coming_to)
            elif h > 0:
                h -= double_arc_radius
                intermediate_d = ("s", "n")
            else:
                h += double_arc_radius
                intermediate_d = ("n", "s")

            self._arc(coming_from, intermediate_d[0])

            if coming_to is not None:
                self._elem.attrs["d"] += f"v{h}"
                self._pos.y += h
                self._arc(intermediate_d[1], coming_to)
            else:
                arc_radius = math.ceil(self._render.settings.arc_radius)
                self._elem.attrs["d"] += f"v{h + arc_radius}"
                self._pos.y += h + arc_radius

            return self

        def _arc(self, coming_from: str, coming_to: str):
            arc_radius = math.ceil(self._render.settings.arc_radius)

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

            self._pos.x += x
            self._pos.y += y

            return self

        def _bend_bezier(self, h: int, coming_from: str, coming_to: str | None):
            double_arc_radius = math.ceil(2 * self._render.settings.arc_radius)

            interm_x_1: float = self._pos.x
            interm_y_1: float = self._pos.y
            interm_x_2: float = self._pos.x
            interm_y_2: float = self._pos.y + h
            out_x = self._pos.x
            out_y = self._pos.y + h

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
            elif coming_from == coming_to == "e":
                interm_x_1 -= 2 * double_arc_radius / 3
                interm_x_2 -= 2 * double_arc_radius / 3
            elif coming_from == "w":
                interm_x_1 += double_arc_radius / 2
                interm_x_2 += double_arc_radius / 2
                interm_y_2 = self._pos.y + h / 2
                out_x += math.ceil(self._render.settings.arc_radius)
            elif coming_from == "e":
                interm_x_1 -= double_arc_radius / 2
                interm_x_2 -= double_arc_radius / 2
                interm_y_2 = self._pos.y + h / 2
                out_x -= math.ceil(self._render.settings.arc_radius)

            self._elem.attrs[
                "d"
            ] += f"C{interm_x_1} {interm_y_1} {interm_x_2} {interm_y_2} {out_x} {out_y}"

            self._pos.x = out_x
            self._pos.y += h

            return self

    @dataclass
    class _SvgElement:
        name: str
        """Name of SVG node"""

        attrs: dict[str, _t.Any] = field(default_factory=dict)
        """SVG node attributes"""

        children: list[SvgRender._SvgElement | str] = field(default_factory=list)
        """Children SVG nodes"""

        def elem(
            self,
            name: str,
            attrs: dict[str, _t.Any] | None = None,
            children: list[SvgRender._SvgElement | str] | None = None,
        ):
            return SvgRender._SvgElement(name, attrs or {}, children or []).add_to(self)

        def add_to(self, parent: SvgRender._SvgElement) -> SvgRender._SvgElement:
            parent.children.append(self)
            return self

        def write_svg(self, f: _t.TextIO, render: SvgRender[_t.Any]):
            f.write(f"<{self.name}")
            for name, value in sorted(self.attrs.items()):
                if value is not None:
                    f.write(f' {name}="{render._e(value)}"')
            f.write(">")
            for child in self.children:
                if isinstance(child, SvgRender._SvgElement):
                    child.write_svg(f, render)
                else:
                    f.write(str(child))
            f.write(f"</{self.name}>")
