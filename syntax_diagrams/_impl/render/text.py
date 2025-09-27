from __future__ import annotations

import io
import itertools
import sys
import typing as _t

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
from syntax_diagrams.measure import SimpleTextMeasure
from syntax_diagrams.render import EndClass, TextRenderSettings
from syntax_diagrams.resolver import HrefResolver

T = _t.TypeVar("T")


def render_text(
    node: Element[T],
    /,
    *,
    max_width: int | None = None,
    settings: TextRenderSettings = TextRenderSettings(),
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

    layout_settings = text_layout_settings(settings)
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

    render = TextRender(
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


_TEXT_MEASURE = SimpleTextMeasure(
    character_advance=1,
    font_size=1,
    wide_character_advance=2,
    line_height=1,
    ascent=1,
)


def text_layout_settings(settings: TextRenderSettings = TextRenderSettings()):
    return LayoutSettings(
        horizontal_seq_separation=settings.horizontal_seq_separation,
        vertical_choice_separation_outer=settings.vertical_choice_separation_outer,
        vertical_choice_separation=settings.vertical_choice_separation,
        vertical_seq_separation_outer=settings.vertical_seq_separation_outer,
        vertical_seq_separation=settings.vertical_seq_separation,
        arc_radius=0.5,
        arc_margin=1,
        terminal_horizontal_padding=2,
        terminal_vertical_padding=0,
        terminal_radius=0,
        non_terminal_horizontal_padding=2,
        non_terminal_vertical_padding=0,
        non_terminal_radius=0,
        comment_horizontal_padding=2,
        comment_vertical_padding=0,
        comment_radius=0,
        terminal_text_measure=_TEXT_MEASURE,
        non_terminal_text_measure=_TEXT_MEASURE,
        comment_text_measure=_TEXT_MEASURE,
        group_text_measure=_TEXT_MEASURE,
        group_vertical_padding=settings.group_vertical_padding,
        group_horizontal_padding=settings.group_horizontal_padding,
        group_vertical_margin=settings.group_vertical_margin,
        group_horizontal_margin=settings.group_horizontal_margin,
        group_thickness=1,
        group_radius=0,
        group_text_vertical_offset=settings.group_text_vertical_offset,
        group_text_horizontal_offset=settings.group_text_horizontal_offset,
        marker_width=4,
        marker_projected_height=0,
        hidden_symbol_escape=("", ""),
        end_class=settings.end_class,
    )


_SYMBOL_TO_DIRECTION: dict[str, frozenset[str]] = {
    " ": frozenset(""),
    "↓": frozenset("ns"),
    "↑": frozenset("ns"),
    "→": frozenset("ew"),
    "←": frozenset("ew"),
    "─": frozenset("ew"),
    "━": frozenset("EW"),
    "│": frozenset("ns"),
    "┃": frozenset("NS"),
    "┌": frozenset("es"),
    "┍": frozenset("Es"),
    "┎": frozenset("eS"),
    "┏": frozenset("ES"),
    "┐": frozenset("sw"),
    "┑": frozenset("sW"),
    "┒": frozenset("Sw"),
    "┓": frozenset("SW"),
    "└": frozenset("ne"),
    "┕": frozenset("nE"),
    "┖": frozenset("Ne"),
    "┗": frozenset("NE"),
    "┘": frozenset("wn"),
    "┙": frozenset("Wn"),
    "┚": frozenset("wN"),
    "┛": frozenset("WN"),
    "├": frozenset("nes"),
    "┝": frozenset("nEs"),
    "┞": frozenset("Nes"),
    "┟": frozenset("neS"),
    "┠": frozenset("NeS"),
    "┡": frozenset("NEs"),
    "┢": frozenset("nES"),
    "┣": frozenset("NES"),
    "┤": frozenset("nsw"),
    "┥": frozenset("nsW"),
    "┦": frozenset("Nsw"),
    "┧": frozenset("nSw"),
    "┨": frozenset("NSw"),
    "┩": frozenset("NsW"),
    "┪": frozenset("nSW"),
    "┫": frozenset("NSW"),
    "┬": frozenset("esw"),
    "┭": frozenset("Esw"),
    "┮": frozenset("esW"),
    "┯": frozenset("EsW"),
    "┰": frozenset("eSw"),
    "┱": frozenset("ESw"),
    "┲": frozenset("eSW"),
    "┳": frozenset("ESW"),
    "┴": frozenset("new"),
    "┵": frozenset("neW"),
    "┶": frozenset("nEw"),
    "┷": frozenset("nEW"),
    "┸": frozenset("New"),
    "┹": frozenset("NeW"),
    "┺": frozenset("NEw"),
    "┻": frozenset("NEW"),
    "┼": frozenset("nesw"),
    "┽": frozenset("nEsw"),
    "┾": frozenset("nesW"),
    "┿": frozenset("nEsW"),
    "╀": frozenset("Nesw"),
    "╁": frozenset("neSw"),
    "╂": frozenset("NeSw"),
    "╃": frozenset("NesW"),
    "╄": frozenset("NEsw"),
    "╅": frozenset("neSW"),
    "╆": frozenset("nESw"),
    "╇": frozenset("NesW"),
    "╈": frozenset("nESW"),
    "╉": frozenset("NeSW"),
    "╊": frozenset("NESw"),
    "╋": frozenset("NESW"),
    "╴": frozenset("w"),
    "╵": frozenset("n"),
    "╶": frozenset("e"),
    "╷": frozenset("s"),
    "╸": frozenset("W"),
    "╹": frozenset("N"),
    "╺": frozenset("E"),
    "╻": frozenset("S"),
    "╼": frozenset("Ew"),
    "╽": frozenset("nS"),
    "╾": frozenset("eW"),
    "╿": frozenset("Ns"),
    "╭": frozenset("es"),
    "╮": frozenset("sw"),
    "╰": frozenset("ne"),
    "╯": frozenset("wn"),
}


_DIRECTION_TO_SYMBOL = {v: k for k, v in _SYMBOL_TO_DIRECTION.items()}

s = frozenset("NESW")
for k, v in list(_DIRECTION_TO_SYMBOL.items()):
    symbols = "".join(k & s).lower()
    for i in range(len(symbols)):
        for comb in itertools.combinations(symbols, i + 1):
            _DIRECTION_TO_SYMBOL[k | frozenset(comb)] = v
del s


class TextRender(Render[T], _t.Generic[T]):
    def __init__(
        self,
        width: int,
        height: int,
        settings: LayoutSettings[T],
        dump_debug_data: bool = False,
    ):
        super().__init__(settings, dump_debug_data)

        self._pos = Vec(0, 0)
        self._field = [[" "] * width for _ in range(height)]

    def write(self, f=sys.stdout):
        for line in self._field:
            for g in line:
                f.write(g)
            f.write("\n")
        f.flush()

    def to_string(self):
        stream = io.StringIO()
        self.write(stream)
        return stream.getvalue()

    def line(self, pos: Vec, reverse: bool = False, css_class: str = "") -> Line:
        return TextRender._TextLine(self, pos, reverse)

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
        if style == NodeStyle.TERMINAL:
            ch = "┤├┌┐└┘─│"
        elif style == NodeStyle.NON_TERMINAL:
            ch = "╢╟╔╗╚╝═║"
        else:
            ch = "╴╶      "

        lines = text.splitlines()
        height = len(lines)
        offset_top = height // 2
        offset_bottom = height - offset_top

        for j, line in enumerate(lines):
            line_width, _ = _TEXT_MEASURE.measure(line)
            x = pos.x + padding
            y = pos.y - offset_top + j
            self._field[y][x] = line
            self._field[y][pos.x] = ch[7]
            self._field[y][pos.x + content_width - 1] = ch[7]
            for j in range(1, line_width):
                self._field[y][x + j] = ""

        self._field[pos.y - offset_top - 1][pos.x] = ch[2]
        for i in range(1, content_width):
            self._field[pos.y - offset_top - 1][pos.x + i] = ch[6]
        self._field[pos.y - offset_top - 1][pos.x + content_width - 1] = ch[3]

        self._field[pos.y + offset_bottom][pos.x] = ch[4]
        for i in range(1, content_width):
            self._field[pos.y + offset_bottom][pos.x + i] = ch[6]
        self._field[pos.y + offset_bottom][pos.x + content_width - 1] = ch[5]

        self._field[pos.y][pos.x] = ch[0]
        self._field[pos.y][pos.x + content_width - 1] = ch[1]

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
        self._write_cell(pos, "ES")
        self._write_cell(pos + Vec(width - 1, 0), "SW")
        self._write_cell(pos + Vec(0, height), "NE")
        self._write_cell(pos + Vec(width - 1, height), "NW")
        for x in range(pos.x + 1, pos.x + width - 1):
            self._write_cell(Vec(x, pos.y), "EW")
            self._write_cell(Vec(x, pos.y + height), "EW")
        for y in range(pos.y + 1, pos.y + height):
            self._write_cell(Vec(pos.x, y), "NS")
            self._write_cell(Vec(pos.x + width - 1, y), "NS")

        if not text:
            return

        lines = text.splitlines()
        text_pos = pos + Vec(
            self.settings.group_text_horizontal_offset + self.settings.group_thickness,
            -self.settings.group_text_vertical_offset - len(lines),
        )
        for i, line in enumerate(lines):
            line_width, _ = _TEXT_MEASURE.measure(line)
            y = text_pos.y + i
            self._field[y][text_pos.x] = line
            for j in range(1, line_width):
                self._field[y][text_pos.x + j] = ""
            if y == pos.y:
                if self.settings.group_text_horizontal_offset > 0:
                    self._field[y][text_pos.x - 1] = "╸"
                elif self.settings.group_text_horizontal_offset == 0:
                    self._field[y][text_pos.x - 1] = "╻"
                self._field[y][text_pos.x + line_width] = "╺"

    def left_marker(self, pos: Vec):
        w = self.settings.marker_width

        for i in range(w):
            self._field[pos.y][pos.x + i] = "─"

        if self.settings.end_class == EndClass.SIMPLE:
            self._field[pos.y][pos.x] = "├"
        elif self.settings.end_class == EndClass.COMPLEX:
            self._field[pos.y][pos.x] = "├"
            self._field[pos.y][pos.x + 1] = "┼"
        else:
            raise NotImplementedError(f"unknown end class {self.settings.end_class}")

    def right_marker(self, pos: Vec):
        w = self.settings.marker_width

        for i in range(w):
            self._field[pos.y][pos.x + i] = "─"

        if self.settings.end_class == EndClass.SIMPLE:
            self._field[pos.y][pos.x + w - 1] = "┤"
        elif self.settings.end_class == EndClass.COMPLEX:
            self._field[pos.y][pos.x + w - 1] = "┤"
            self._field[pos.y][pos.x + w - 2] = "┼"
        else:
            raise NotImplementedError(f"unknown end class {self.settings.end_class}")

    def _write_cell(self, pos: Vec, d: str):
        if self._field[pos.y][pos.x] not in _SYMBOL_TO_DIRECTION:
            pass
        elif self._field[pos.y][pos.x] == " ":
            self._field[pos.y][pos.x] = _DIRECTION_TO_SYMBOL[frozenset(d)]
        else:
            old_d = frozenset(d)
            new_d = old_d | _SYMBOL_TO_DIRECTION.get(
                self._field[pos.y][pos.x], frozenset()
            )
            if old_d != new_d:
                self._field[pos.y][pos.x] = _DIRECTION_TO_SYMBOL[new_d]

    class _TextLine(Line):
        def __init__(self, render: TextRender[_t.Any], pos: Vec, reverse: bool):
            self._render = render
            self._pos = Vec(pos.x, pos.y)
            self._reverse = reverse

        def segment_abs(
            self, x: int, arrow_begin: bool = False, arrow_end: bool = False
        ) -> Line:
            w = x - self._pos.x

            if w > 0:
                for i in range(w):
                    self._render._write_cell(self._pos + Vec(i, 0), "we")

                if arrow_begin:
                    self._render._field[self._pos.y][self._pos.x] = "→"

                self._pos.x += w

                if arrow_end:
                    self._render._field[self._pos.y][self._pos.x - 1] = "→"
            elif w < 0:
                for i in range(-1, w - 1, -1):
                    self._render._write_cell(self._pos + Vec(i, 0), "we")

                if arrow_begin:
                    self._render._field[self._pos.y][self._pos.x - 1] = "←"

                self._pos.x += w

                if arrow_end:
                    self._render._field[self._pos.y][self._pos.x] = "←"

            return self

        def bend(
            self,
            y: int,
            coming_from: Direction,
            coming_to: Direction | None,
            arrow_begin: bool = False,
            arrow_end: bool = False,
        ) -> Line:
            h = y - self._pos.y

            if coming_from == "e":
                self._pos.x -= 1

            s = "↓" if h > 0 else "↑"

            if arrow_begin:
                if h > 0:
                    self._render._field[self._pos.y + 1][self._pos.x] = s
                elif h < 0:
                    self._render._field[self._pos.y - 1][self._pos.x] = s

            if h == 0:
                self._render._write_cell(self._pos, coming_from + (coming_to or ""))
            elif h > 0:
                for i in range(1, h):
                    self._render._write_cell(self._pos + Vec(0, i), "ns")
                self._render._write_cell(self._pos, coming_from + "s")
                self._render._write_cell(self._pos + Vec(0, h), "n" + (coming_to or ""))
            else:
                for i in range(-1, h, -1):
                    self._render._write_cell(self._pos + Vec(0, i), "ns")
                self._render._write_cell(self._pos, coming_from + "n")
                self._render._write_cell(self._pos + Vec(0, h), "s" + (coming_to or ""))

            self._pos.y += h

            if arrow_end:
                if h > 0:
                    self._render._field[self._pos.y - 1][self._pos.x] = s
                elif h < 0:
                    self._render._field[self._pos.y + 1][self._pos.x] = s

            if coming_to == "e":
                self._pos.x += 1

            return self
