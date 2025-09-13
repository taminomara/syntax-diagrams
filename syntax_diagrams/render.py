from __future__ import annotations

import typing as _t
from dataclasses import dataclass, field
from enum import Enum

from syntax_diagrams.element import Element
from syntax_diagrams.resolver import HrefResolver

__all__ = [
    "EndClass",
    "TextRenderSettings",
    "render_text",
    "SvgRenderSettings",
    "DEFAULT_CSS",
    "render_svg",
]

T = _t.TypeVar("T")


class EndClass(Enum):
    """
    Controls how diagram start and end look like.

    """

    SIMPLE = "SIMPLE"
    """
    A simple ``T``-shaped ending.

    """

    COMPLEX = "COMPLEX"
    """
    A ``T``-shaped ending with vertical line doubled.

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

    vertical_choice_separation_outer: int = 2
    """
    Vertical space between nodes in a :func:`choice` block,
    if it contains another choice block.

    """

    vertical_choice_separation: int = 1
    """
    Vertical space between nodes in a :func:`choice` block.

    """

    vertical_seq_separation_outer: int = 2
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

    group_text_height: int = 0
    """
    Height of the group text, added to the top vertical margin.

    """

    group_text_vertical_offset: int = 0
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


def render_text(
    node: Element[T],
    /,
    *,
    max_width: int | None = None,
    settings: TextRenderSettings = TextRenderSettings(),
    reverse: bool | None = None,
    href_resolver: HrefResolver[T] = HrefResolver(),
    convert_resolver_data: _t.Callable[[_t.Any | None], T | None] | None = None,
) -> str:
    """
    Render diagram as an SVG.

    :param node:
        root diagram node.
    :param max_width:
        if given, overrides :attribute:`~SvgRenderSettings.max_width`
        from ``settings``.
    :param settings:
        rendering settings.
    :param reverse:
        if given, overrides :attribute:`~SvgRenderSettings.reverse`
        from ``settings``.
    :param href_resolver:
        hyperlink resolver (may be used to transform text).
    :param convert_resolver_data:
        a custom function to parse ``resolver_data``, used when loading elements
        from JSON or other untrusted source.
    :return:
        a string with a rendered diagram.

    """

    if convert_resolver_data is None:
        convert_resolver_data = lambda x: x

    # Prevent circular import.
    from syntax_diagrams._impl.render.text import render_text as _render_text
    from syntax_diagrams._impl.load import load as _load

    return _render_text(
        _load(node, convert_resolver_data),
        max_width=max_width,
        settings=settings,
        reverse=reverse,
        href_resolver=href_resolver,
    )


DEFAULT_CSS = {
    "path": {
        "stroke-width": "1.5",
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
        "font-size": "14px",
        "font-family": "'Consolas', 'Menlo', 'Deja Vu Sans Mono', 'Bitstream Vera Sans Mono', monospace",
        "text-anchor": "middle",
        "dominant-baseline": "central",
        "font-weight": "bold",
    },
    ".group text": {
        "text-anchor": "start",
        "opacity": "0.5",
        "font-weight": "normal",
        "font-style": "italic",
        "dominant-baseline": "alphabetic",
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

    terminal_character_advance: float = 8.4
    """
    Average length of one character in the used font. Since SVG elements
    cannot expand and shrink dynamically, length of text nodes is calculated
    as number of symbols multiplied by this constant.

    """

    terminal_wide_character_advance: float = 14.36
    """
    Average length of one wide character in the used font.
    See :attribute:`~SvgRenderSettings.terminal_character_advance` for explanation.

    """

    terminal_padding: int = 10
    """
    Horizontal padding around text in terminal nodes.

    """

    terminal_radius: int = 10
    """
    Border radius in terminal nodes.

    """

    terminal_height: int = 22
    """
    Height of a terminal node.

    """

    non_terminal_character_advance: float = 8.4
    """
    Average length of one character in the used font. Since SVG elements
    cannot expand and shrink dynamically, length of text nodes is calculated
    as number of symbols multiplied by this constant.

    """

    non_terminal_wide_character_advance: float = 14.36
    """
    Average length of one wide character in the used font.
    See :attribute:`~SvgRenderSettings.non_terminal_character_advance` for explanation.

    """

    non_terminal_padding: int = 10
    """
    Horizontal padding around text in non-terminal nodes.

    """

    non_terminal_radius: int = 0
    """
    Border radius in non-terminal nodes.

    """

    non_terminal_height: int = 22
    """
    Height of a non-terminal node.

    """

    comment_character_advance: float = 8.4
    """
    Average length of one character in the used font. Since SVG elements
    cannot expand and shrink dynamically, length of text nodes is calculated
    as number of symbols multiplied by this constant.

    """

    comment_wide_character_advance: float = 14.36
    """
    Average length of one wide character in the used font.
    See :attribute:`~SvgRenderSettings.comment_character_advance` for explanation.

    """

    comment_padding: int = 3
    """
    Horizontal padding around text in comment nodes.

    """

    comment_radius: int = 0
    """
    Border radius in comment nodes.

    """

    comment_height: int = 22
    """
    Height of a comment node.

    """

    group_character_advance: int | float = 8.4
    """
    Average length of one character in the used font. Since SVG elements
    cannot expand and shrink dynamically, length of text nodes is calculated
    as number of symbols multiplied by this constant.

    """

    group_wide_character_advance: int | float = 14.36
    """
    Average length of one wide character in the used font.
    See :attribute:`~SvgRenderSettings.group_character_advance` for explanation.

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

    group_text_height: int = 8
    """
    Height of the group text, added to the top vertical margin.

    """

    group_text_vertical_offset: int = 5
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


def render_svg(
    element: Element[T],
    /,
    *,
    max_width: int | None = None,
    settings: SvgRenderSettings = SvgRenderSettings(),
    reverse: bool | None = None,
    href_resolver: HrefResolver[T] = HrefResolver(),
    convert_resolver_data: _t.Callable[[_t.Any | None], T | None] | None = None,
) -> str:
    """
    Render diagram as an SVG.

    :param node:
        root diagram node.
    :param max_width:
        if given, overrides :attribute:`~SvgRenderSettings.max_width`
        from ``settings``.
    :param settings:
        rendering settings.
    :param reverse:
        if given, overrides :attribute:`~SvgRenderSettings.reverse`
        from ``settings``.
    :param href_resolver:
        hyperlink resolver (may be used to transform text).
    :param convert_resolver_data:
        a custom function to parse ``resolver_data``, used when loading elements
        from JSON or other untrusted source.
    :return:
        a string with a rendered diagram.

    """

    if convert_resolver_data is None:
        convert_resolver_data = lambda x: x

    # Prevent circular import.
    from syntax_diagrams._impl.render.svg import render_svg as _render_svg
    from syntax_diagrams._impl.load import load as _load

    return _render_svg(
        _load(element, convert_resolver_data),
        max_width=max_width,
        settings=settings,
        reverse=reverse,
        href_resolver=href_resolver,
    )
