from __future__ import annotations

import dataclasses
import typing as _t
from dataclasses import dataclass, field
from enum import Enum

from syntax_diagrams.element import Element
from syntax_diagrams.measure import SimpleTextMeasure, TextMeasure
from syntax_diagrams.resolver import HrefResolver

__all__ = [
    "LoadingError",
    "EndClass",
    "TextRenderSettings",
    "render_text",
    "ArrowStyle",
    "SvgRenderSettings",
    "DEFAULT_CSS",
    "render_svg",
]

T = _t.TypeVar("T")
U = _t.TypeVar("U")


class LoadingError(ValueError):
    """
    Indicates incorrect diagram value.

    """


class EndClass(Enum):
    """
    Controls how diagram start and end look like.

    """

    SIMPLE = "SIMPLE"
    """
    A simple ``T``-shaped ending.

    .. syntax:diagram::
        :end-class: simple

        Simple

    """

    COMPLEX = "COMPLEX"
    """
    A ``T``-shaped ending with vertical line doubled.

    .. syntax:diagram::
        :end-class: complex

        Complex

    """


@dataclass(frozen=True)
class TextRenderSettings:
    """
    Settings for text rendering engine.

    """

    padding: tuple[int, int, int, int] = (0, 0, 0, 0)
    """
    Array of four positive integers denoting top, right, bottom and left
    padding between the diagram and its container.

    """

    vertical_choice_separation_outer: int = 1
    """
    Vertical space between nodes in a :func:`choice` block,
    if it contains another choice block.

    """

    vertical_choice_separation: int = 1
    """
    Vertical space between nodes in a :func:`choice` block.

    """

    vertical_seq_separation_outer: int = 1
    """
    Vertical space between nodes in a :func:`stack` block,
    if it appears outside of any choice block.

    """

    vertical_seq_separation: int = 1
    """
    Vertical space between nodes in a :func:`stack` block.

    """

    horizontal_seq_separation: int = 2
    """
    Horizontal space between adjacent nodes.

    """

    group_vertical_padding: int = 1
    """
    Vertical padding inside of group elements.

    """

    group_horizontal_padding: int = 2
    """
    Horizontal padding inside of group elements.

    """

    group_vertical_margin: int = 0
    """
    Vertical margin outside of group elements.

    """

    group_horizontal_margin: int = 2
    """
    Horizontal margin outside of group elements.

    """

    group_text_vertical_offset: int = -1
    """
    Offset from group rectangle to its heading.

    """

    group_text_horizontal_offset: int = 2
    """
    Offset from group rectangle to its heading.

    """

    end_class: EndClass = EndClass.COMPLEX
    """
    Controls how diagram start and end look like.

    """

    max_width: int = 80
    """
    Max width after which a sequence will be wrapped. This option is used to
    automatically convert sequences to stacks. Note that this is a suggestive
    option, there is no guarantee that the diagram will
    fit to its ``max_width``.

    """

    reverse: bool = False
    """
    If enabled, diagram is rendered right-to-left.

    """


@_t.overload
def render_text(
    element: Element[T],
    /,
    *,
    max_width: int | None = None,
    settings: TextRenderSettings | None = None,
    reverse: bool | None = None,
    href_resolver: HrefResolver[T] | None = None,
    convert_resolver_data: None = None,
) -> str: ...


@_t.overload
def render_text(
    element: Element[U],
    /,
    *,
    max_width: int | None = None,
    settings: TextRenderSettings | None = None,
    reverse: bool | None = None,
    href_resolver: HrefResolver[T] | None = None,
    convert_resolver_data: _t.Callable[[U | None], T | None] | None,
) -> str: ...


def render_text(
    node: Element[T],
    /,
    *,
    max_width: int | None = None,
    settings: TextRenderSettings | None = None,
    reverse: bool | None = None,
    href_resolver: HrefResolver[T] | None = None,
    convert_resolver_data: _t.Callable[[_t.Any | None], T | None] | None = None,
    _dump_debug_data: bool = False,
) -> str:
    """
    Render diagram as an SVG.

    :param node:
        root diagram node.
    :param max_width:
        if given, overrides `~SvgRenderSettings.max_width`
        from ``settings``.
    :param settings:
        rendering settings.
    :param reverse:
        if given, overrides `~SvgRenderSettings.reverse`
        from ``settings``.
    :param href_resolver:
        hyperlink resolver (may be used to transform text).
    :param convert_resolver_data:
        a custom function to parse ``resolver_data``, used when loading elements
        from JSON or other untrusted source.
    :return:
        a string with a rendered diagram.
    :throws:
        `LoadingError`

    """

    if convert_resolver_data is None:
        convert_resolver_data = lambda x: x
    if settings is None:
        settings = TextRenderSettings()
    if href_resolver is None:
        href_resolver = HrefResolver()

    # Prevent circular import.
    from syntax_diagrams._impl.load import load as _load
    from syntax_diagrams._impl.render.text import render_text as _render_text

    return _render_text(
        _load(node, convert_resolver_data),
        max_width=max_width,
        settings=settings,
        reverse=reverse,
        href_resolver=href_resolver,
        dump_debug_data=_dump_debug_data,
    )


DEFAULT_CSS = {
    "path": {
        "stroke-width": "1.5",
        "stroke": "black",
        "fill": "none",
        "stroke-linecap": "round",
    },
    ".arrow": {
        "stroke": "none",
        "fill": "black",
    },
    ".arrow.arrow-barb": {
        "stroke": "black",
        "fill": "none",
    },
    "a": {
        "text-decoration": "none",
    },
    "rect": {
        "stroke-width": "1.5",
        "stroke": "black",
        "fill": "none",
    },
    "g.comment rect": {
        "stroke": "none",
    },
    "text": {
        "font-family": "Consolas, Menlo, monospace",
        "text-anchor": "middle",
        # "dominant-baseline": "central",
        "font-weight": "bold",
    },
    "tspan": {
        "font-family": "Consolas, Menlo, monospace",
    },
    ".escape": {
        "fill": "brown",
    },
    ".group text": {
        "text-anchor": "start",
        "opacity": "0.5",
        "font-weight": "normal",
        "font-style": "italic",
        # "dominant-baseline": "alphabetic",
    },
    ".group rect": {
        "opacity": "0.3",
    },
    "g.comment text": {
        "font-weight": "normal",
        "font-style": "italic",
    },
    ".dbg-content, .dbg-display, .dbg-content-main, .dbg-padding, .dbg-margin, .dbg-position, .dbg-ridge-line": {
        "stroke": "none",
    },
}


# Measured for Menlo, 14px. Consolas is a bit narrower, but not too much.
_DEFAULT_TEXT_MEASURE_FACTORY = lambda: SimpleTextMeasure(
    character_advance=8.44,
    wide_character_advance=14.34,
    font_size=14,
    line_height=14 * 1.1,
    ascent=12,
)


class ArrowStyle(Enum):
    """
    Arrow shapes for SVG diagrams.

    """

    NONE = "NONE"
    """
    Arrows are not rendered.

    .. syntax:diagram::
        :svg-arrow-style: none
        :svg-padding: 10 10 10 10

        optional: "node"
        skip: true

    """

    TRIANGLE = "TRIANGLE"
    """
    Simple triangle arrows.

    .. syntax:diagram::
        :svg-arrow-style: triangle
        :svg-padding: 10 10 10 10

        optional: "node"
        skip: true

    """

    STEALTH = "STEALTH"
    """
    Pointier triangle arrows.

    .. syntax:diagram::
        :svg-arrow-style: stealth
        :svg-padding: 10 10 10 10

        optional: "node"
        skip: true

    """

    BARB = "BARB"
    """
    An error that consists of two lines.

    .. syntax:diagram::
        :svg-arrow-style: barb
        :svg-padding: 10 10 10 10

        optional: "node"
        skip: true

    """

    HARPOON = "HARPOON"
    """
    Half of a triangle arrow.

    .. syntax:diagram::
        :svg-arrow-style: harpoon
        :svg-padding: 10 10 10 10

        optional: "node"
        skip: true

    """

    HARPOON_UP = "HARPOON_UP"
    """
    Another half of a triangle arrow.

    .. syntax:diagram::
        :svg-arrow-style: harpoon-up
        :svg-padding: 10 10 10 10

        optional: "node"
        skip: true

    """


@dataclass(frozen=True)
class SvgRenderSettings:
    """
    Settings for SVG rendering engine.

    """

    padding: tuple[int, int, int, int] = (1, 1, 1, 1)
    """
    Array of four positive integers denoting top, right, bottom and left
    padding between the diagram and its container.

    """

    title: str | None = None
    """
    Title text that will be added to ``<title>`` element and ``aria-label`` attribute.

    """

    description: str | None = None
    """
    Title text that will be added to ``<desc>`` element.

    """

    vertical_choice_separation_outer: int = 9
    """
    Vertical space between nodes in a :func:`choice` block,
    if it contains another choice block.

    """

    vertical_choice_separation: int = 9
    """
    Vertical space between nodes in a :func:`choice` block.

    """

    vertical_seq_separation_outer: int = 18
    """
    Vertical space between nodes in a :func:`stack` block,
    if it appears outside of any choice block.

    """

    vertical_seq_separation: int = 18
    """
    Vertical space between nodes in a :func:`stack` block.

    """

    horizontal_seq_separation: int = 10
    """
    Horizontal space between adjacent nodes.

    """

    end_class: EndClass = EndClass.COMPLEX
    """
    Controls how diagram start and end look like.

    """

    arrow_style: ArrowStyle = ArrowStyle.NONE
    """
    Style of arrows to draw.

    """

    arrow_length: int = 10
    """
    Length of an arrow along its line.

    """

    arrow_cross_length: int = 4
    """
    Length of an arrow across its line.

    """

    max_width: int = 600
    """
    Max width after which a sequence will be wrapped. This option is used to
    automatically convert sequences to stacks. Note that this is a suggestive
    option, there is no guarantee that the diagram will
    fit to its ``max_width``.

    """

    arc_radius: int = 10
    """
    Arc radius of railroads. 10px by default.

    """

    arc_margin: int = 5
    """
    Margin around arcs.

    """

    terminal_text_measure: TextMeasure = dataclasses.field(
        default_factory=_DEFAULT_TEXT_MEASURE_FACTORY
    )
    """
    Service used to measure size of text inside of text nodes.

    By default, set up to match default CSS settings.

    """

    terminal_horizontal_padding: int = 10
    """
    Horizontal padding around text in terminal nodes.

    """

    terminal_vertical_padding: int = 3
    """
    Vertical padding around text in terminal nodes.

    """

    terminal_radius: int = 10
    """
    Border radius in terminal nodes.

    """

    non_terminal_text_measure: TextMeasure = dataclasses.field(
        default_factory=_DEFAULT_TEXT_MEASURE_FACTORY
    )
    """
    Service used to measure size of text inside of text nodes.

    By default, set up to match default CSS settings.

    """

    non_terminal_horizontal_padding: int = 10
    """
    Horizontal padding around text in non-terminal nodes.

    """

    non_terminal_vertical_padding: int = 3
    """
    Vertical padding around text in non-terminal nodes.

    """

    non_terminal_radius: int = 0
    """
    Border radius in non-terminal nodes.

    """

    comment_text_measure: TextMeasure = dataclasses.field(
        default_factory=_DEFAULT_TEXT_MEASURE_FACTORY
    )
    """
    Service used to measure size of text inside of text nodes.

    By default, set up to match default CSS settings.

    """

    comment_horizontal_padding: int = 3
    """
    Horizontal padding around text in comment nodes.

    """

    comment_vertical_padding: int = 3
    """
    Vertical padding around text in comment nodes.

    """

    comment_radius: int = 0
    """
    Border radius in comment nodes.

    """

    group_text_measure: TextMeasure = dataclasses.field(
        default_factory=_DEFAULT_TEXT_MEASURE_FACTORY
    )
    """
    Service used to measure size of text of groups.

    By default, set up to match default CSS settings.

    """

    group_vertical_padding: int = 10
    """
    Vertical padding inside of group elements.

    """

    group_horizontal_padding: int = 10
    """
    Horizontal padding inside of group elements.

    """

    group_vertical_margin: int = 5
    """
    Vertical margin outside of group elements.

    """

    group_horizontal_margin: int = 10
    """
    Horizontal margin outside of group elements.

    """

    group_radius: int = 0
    """
    Border radius in groups.

    """

    group_text_vertical_offset: int = 0
    """
    Offset from group rectangle to its heading.

    """

    group_text_horizontal_offset: int = 10
    """
    Offset from group rectangle to its heading.

    """

    css_class: str = ""
    """
    Class attribute for the ``<svg>`` element.

    """

    css_style: dict[str, dict[str, str]] | str | None = field(
        default_factory=lambda: DEFAULT_CSS
    )
    """
    CSS style that should be embedded into the diagram.

    """

    reverse: bool = False
    """
    If enabled, diagram is rendered right-to-left.

    """


@_t.overload
def render_svg(
    element: Element[T],
    /,
    *,
    max_width: int | None = None,
    settings: SvgRenderSettings | None = None,
    reverse: bool | None = None,
    href_resolver: HrefResolver[T] | None = None,
    convert_resolver_data: None = None,
) -> str: ...


@_t.overload
def render_svg(
    element: Element[U],
    /,
    *,
    max_width: int | None = None,
    settings: SvgRenderSettings | None = None,
    reverse: bool | None = None,
    href_resolver: HrefResolver[T] | None = None,
    convert_resolver_data: _t.Callable[[U | None], T | None] | None,
) -> str: ...


def render_svg(
    element: Element[T],
    /,
    *,
    max_width: int | None = None,
    settings: SvgRenderSettings | None = None,
    reverse: bool | None = None,
    href_resolver: HrefResolver[T] | None = None,
    convert_resolver_data: _t.Callable[[T | None], T | None] | None = None,
    _dump_debug_data: bool = False,
) -> str:
    """
    Render diagram as an SVG.

    :param node:
        root diagram node.
    :param max_width:
        if given, overrides `~SvgRenderSettings.max_width`
        from ``settings``.
    :param settings:
        rendering settings.
    :param reverse:
        if given, overrides `~SvgRenderSettings.reverse`
        from ``settings``.
    :param href_resolver:
        hyperlink resolver (may be used to transform text).
    :param convert_resolver_data:
        a custom function to parse ``resolver_data``, used when loading elements
        from JSON or other untrusted source.
    :return:
        a string with a rendered diagram.
    :throws:
        `LoadingError`

    """

    if convert_resolver_data is None:
        convert_resolver_data = lambda x: x
    if settings is None:
        settings = SvgRenderSettings()
    if href_resolver is None:
        href_resolver = HrefResolver()

    # Prevent circular import.
    from syntax_diagrams._impl.load import load as _load
    from syntax_diagrams._impl.render.svg import render_svg as _render_svg

    return _render_svg(
        _load(element, convert_resolver_data),
        max_width=max_width,
        settings=settings,
        reverse=reverse,
        href_resolver=href_resolver,
        dump_debug_data=_dump_debug_data,
    )
