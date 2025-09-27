from __future__ import annotations

import math
import re
import typing as _t
import unicodedata

import grapheme

from syntax_diagrams._impl.render import (
    LayoutContext,
    LayoutSettings,
    NodeStyle,
    Render,
    RenderContext,
)
from syntax_diagrams._impl.tree import Element
from syntax_diagrams._impl.vec import Vec

T = _t.TypeVar("T")


class Node(Element[T], _t.Generic[T]):
    _style: NodeStyle
    _text: str
    _href: str | None
    _title: str | None
    _resolve: bool
    _resolver_data: T | None
    _css_class: str

    _horizontal_padding: int
    _radius: int
    _text_width: int
    _text_height: int
    _processed_text: str
    _processed_href: str | None
    _processed_title: str | None

    def __init__(
        self,
        render: NodeStyle,
        text: str,
        href: str | None = None,
        title: str | None = None,
        css_class: str | None = None,
        resolve: bool | None = None,
        resolver_data: T | None = None,
    ):
        self._style = render
        self._text = text
        self._href = href
        self._title = title
        self._resolve = resolve if resolve is not None else True
        self._resolver_data = resolver_data
        self._css_class = css_class or ""

    def _calculate_content_layout(
        self, settings: LayoutSettings[T], context: LayoutContext
    ):
        self._isolate()

        if self._resolve:
            self._processed_text, self._processed_href, self._processed_title = (
                settings.href_resolver.resolve(
                    self._text, self._href, self._title, self._resolver_data
                )
            )
        else:
            self._processed_text, self._processed_href, self._processed_title = (
                self._text,
                self._href,
                self._title,
            )

        self._processed_text = _reveal_hidden_symbols(
            self._processed_text, settings.hidden_symbol_escape
        )

        if self._style == NodeStyle.TERMINAL:
            text_measure = settings.terminal_text_measure
            self._horizontal_padding = settings.terminal_horizontal_padding
            self._vertical_padding = settings.terminal_vertical_padding
            self._radius = settings.terminal_radius
        elif self._style == NodeStyle.NON_TERMINAL:
            text_measure = settings.non_terminal_text_measure
            self._horizontal_padding = settings.non_terminal_horizontal_padding
            self._vertical_padding = settings.non_terminal_vertical_padding
            self._radius = settings.non_terminal_radius
        else:
            text_measure = settings.comment_text_measure
            self._horizontal_padding = settings.comment_horizontal_padding
            self._vertical_padding = settings.comment_vertical_padding
            self._radius = settings.comment_radius

        self._text_width, self._text_height = text_measure.measure(self._processed_text)

        self.display_width = self.content_width = (
            self._text_width + 2 * self._horizontal_padding
        )
        self.height = 0
        self.up = self.down = math.ceil(self._text_height / 2) + self._vertical_padding
        self.start_margin = self.end_margin = settings.horizontal_seq_separation

    def _render_content(self, render: Render[T], context: RenderContext):
        if not context.reverse:
            pos = context.pos
        else:
            pos = context.pos - Vec(self.content_width, 0)
        render.node(
            pos=pos,
            style=self._style,
            css_class=self._css_class,
            content_width=self.content_width,
            up=self.up,
            down=self.down,
            radius=self._radius,
            padding=self._horizontal_padding,
            text_width=self._text_width,
            text_height=self._text_height,
            text=self._processed_text,
            href=self._processed_href,
            title=self._processed_title,
        )

    def __str__(self):
        if re.match(r"^[a-zA-Z0-9_-]+$", self._text) is not None:
            return self._text
        else:
            return repr(self._text)


_CHAR_NAMES = {
    "\u0000": "<NUL>",
    "\u0001": "<SOH>",
    "\u0002": "<STX>",
    "\u0003": "<ETX>",
    "\u0004": "<EOT>",
    "\u0005": "<ENQ>",
    "\u0006": "<ACK>",
    "\u0007": "\\a",
    "\u0008": "\\b",
    "\u0009": "\\t",
    "\u000a": "\\n",
    "\u000b": "\\v",
    "\u000c": "\\f",
    "\u000d": "\\r",
    "\u000e": "<SO>",
    "\u000f": "<SI>",
    "\u0010": "<DLE>",
    "\u0011": "<DC1>",
    "\u0012": "<DC2>",
    "\u0013": "<DC3>",
    "\u0014": "<DC4>",
    "\u0015": "<NAK>",
    "\u0016": "<SYN>",
    "\u0017": "<ETB>",
    "\u0018": "<CAN>",
    "\u0019": "<EM>",
    "\u001a": "<SUB>",
    "\u001b": "<ESC>",
    "\u001c": "<FS>",
    "\u001d": "<GS>",
    "\u001e": "<RS>",
    "\u001f": "<US>",
    "\u007f": "<DEL>",
    "\u0080": "<PAD>",
    "\u0081": "<HOP>",
    "\u0082": "<BPH>",
    "\u0083": "<NBH>",
    "\u0084": "<IND>",
    "\u0085": "<NEL>",
    "\u0086": "<SSA>",
    "\u0087": "<ESA>",
    "\u0088": "<HTS>",
    "\u0089": "<HTJ>",
    "\u008a": "<VTS>",
    "\u008b": "<PLD>",
    "\u008c": "<PLU>",
    "\u008d": "<RI>",
    "\u008e": "<SS2>",
    "\u008f": "<SS3>",
    "\u0090": "<DCS>",
    "\u0091": "<PU1>",
    "\u0092": "<PU2>",
    "\u0093": "<STS>",
    "\u0094": "<CCH>",
    "\u0095": "<MW>",
    "\u0096": "<SPA>",
    "\u0097": "<EPA>",
    "\u0098": "<SOS>",
    "\u0099": "<SGCI>",
    "\u009a": "<SCI>",
    "\u009b": "<CSI>",
    "\u009c": "<ST>",
    "\u009d": "<OSC>",
    "\u009e": "<PM>",
    "\u009f": "<APC>",
    "\u00a0": "<NBSP>",
    "\u00ad": "<SHY>",
}


def _reveal_hidden_symbols(s: str, e: tuple[str, str], ignore: str = " ") -> str:
    res = ""
    for g in grapheme.graphemes(s):
        if len(g) > 1 and not g.isspace():
            res += g
            continue
        for c in g:
            if c in ignore:
                res += c
                continue
            if name := _CHAR_NAMES.get(c):
                res += f"{e[0]}{name}{e[1]}"
                continue
            cat = unicodedata.category(c)
            if cat[0] in "MCZ":
                name = unicodedata.name(c, None)
                if not name:
                    o = ord(c)
                    if o > 0xFFFF:
                        name = f"<U{o:08x}>"
                    else:
                        name = f"<U{o:04x}>"
                res += f"{e[0]}{name}{e[1]}"
            else:
                res += c

    return res
