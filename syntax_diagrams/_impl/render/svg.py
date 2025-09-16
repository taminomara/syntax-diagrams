from __future__ import annotations

import dataclasses
import io
import json
import math
import re
import sys
import typing as _t
from dataclasses import dataclass, field
from enum import Enum

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
from syntax_diagrams.render import EndClass, SvgRenderSettings
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
        terminal_character_advance=settings.terminal_character_advance,
        terminal_wide_character_advance=settings.terminal_wide_character_advance,
        terminal_padding=settings.terminal_padding,
        terminal_radius=settings.terminal_radius,
        terminal_height=settings.terminal_height,
        non_terminal_character_advance=settings.non_terminal_character_advance,
        non_terminal_wide_character_advance=settings.non_terminal_wide_character_advance,
        non_terminal_padding=settings.non_terminal_padding,
        non_terminal_radius=settings.non_terminal_radius,
        non_terminal_height=settings.non_terminal_height,
        comment_character_advance=settings.comment_character_advance,
        comment_wide_character_advance=settings.comment_wide_character_advance,
        comment_padding=settings.comment_padding,
        comment_radius=settings.comment_radius,
        comment_height=settings.comment_height,
        group_character_advance=settings.group_character_advance,
        group_wide_character_advance=settings.group_wide_character_advance,
        group_vertical_padding=settings.group_vertical_padding,
        group_horizontal_padding=settings.group_horizontal_padding,
        group_vertical_margin=settings.group_vertical_margin,
        group_horizontal_margin=settings.group_horizontal_margin,
        group_thickness=0,
        group_radius=settings.group_radius,
        group_text_height=settings.group_text_height,
        group_text_vertical_offset=settings.group_text_vertical_offset,
        group_text_horizontal_offset=settings.group_text_horizontal_offset,
        marker_width=20,
        marker_projected_height=10,
        end_class=settings.end_class,
    )


_DEBUG_ATTRS = [
    "display_width",
    "width",
    "content_width",
    "start_padding",
    "end_padding",
    "start_margin",
    "end_margin",
    "height",
    "up",
    "down",
    "context",
]

_IGNORE_ATTRS = {"settings"}


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
        dump_debug_data: bool = False,
    ):
        self.settings = settings
        self._width = width
        self._debug = dump_debug_data
        self._id = 0
        self._ids: dict[Element[T], str] = {}
        self._debug_data: dict[str, _t.Any] = {}

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
            self._root.elem("title").children.append(title)
        if description is not None:
            self._root.elem("desc").children.append(description)

        if dump_debug_data:
            self._root.attrs["data-debug"] = self._debug_data

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
            self._style.children.append(css)

        self._elems = [self._root.elem("g")]

    def _make_id(self, elem: Element[T]) -> str:
        if elem not in self._ids:
            self._ids[elem] = str(self._id)
            self._id += 1
        return self._ids[elem]

    def write(self, f=sys.stdout):
        self._root.write_svg(f, self)
        f.flush()

    def to_string(self):
        stream = io.StringIO()
        self.write(stream)
        return stream.getvalue()

    def enter(self, node: Element[_t.Any]):
        name = node.__class__.__name__.lower()
        if hasattr(node, "_text"):
            name += f" {json.dumps(getattr(node, "_text"))}"

        attrs = {
            "class": "elem",
            "data-dbg-elem": name,
        }

        if self._debug:
            elem_id = attrs["data-dbg-id"] = self._make_id(node)
            self._id += 1
            data = {}
            for k in _DEBUG_ATTRS:
                data[k] = getattr(node, k, None)
            for k, v in vars(node).items():
                # Escape HTML special characters before setting attribute
                if k.startswith("_Element__"):
                    k = "__" + k[len("_Element__") :]
                if k not in _IGNORE_ATTRS and k not in data:
                    data[k] = v
            data["$order"] = list(data.keys())
            self._debug_data[elem_id] = {
                "parent": self._elem.attrs.get("data-dbg-id"),
                "index": self._id,
                "name": name,
                "data": data,
            }

        self._elems.append(self._elem.elem("g", attrs))

    def exit(self):
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
            case NodeStyle.NON_TERMINAL:
                css_class += " non-terminal"
            case NodeStyle.COMMENT:
                css_class += " comment"
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

        g.elem("text", {"x": pos.x + content_width / 2, "y": pos.y}, [text])

    def group(
        self,
        pos: Vec,
        width: int,
        height: int,
        css_class: str | None,
        text_width: int,
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

        g.elem(
            "text",
            {
                "x": pos.x + self.settings.group_text_horizontal_offset,
                "y": pos.y - self.settings.group_text_vertical_offset,
            },
            [text],
        )

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
        if isinstance(text, dict):
            text = self._DebugJSONEncoder(self).encode(text)
        return self._ESCAPE_RE.sub(lambda c: f"&#{ord(c[0])};", str(text))

    class _DebugJSONEncoder(json.JSONEncoder):
        def __init__(self, render: SvgRender[_t.Any]):
            super().__init__()
            self._render = render

        def default(self, o):
            if dataclasses.is_dataclass(o) and not isinstance(o, type):
                d = dataclasses.asdict(o)
                d["$order"] = list(d.keys())
                return d
            elif isinstance(o, Enum):
                return o.value
            elif isinstance(o, Element):
                return {
                    "$elem": o.__class__.__qualname__,  # type: ignore
                    "$id": self._render._make_id(o),
                }
            return super().default(o)

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
            self._elem.attrs["d"] += f"H{x}"
            self._pos.x = x
            return self

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
                    f.write(render._e(child))
            f.write(f"</{self.name}>")
