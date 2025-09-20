from __future__ import annotations

import math
import typing as _t

import grapheme
import wcwidth

try:
    from PIL.ImageFont import FreeTypeFont, ImageFont
except ImportError:
    pass

__all__ = [
    "TextMeasure",
    "SimpleTextMeasure",
    "TrueTextMeasure",
]


class TextMeasure:
    """
    An interface for measuring dimensions of rendered text.

    """

    def measure(self, text: str) -> _t.Tuple[int, int]:
        """
        Called before rendering a node to measure its text.

        Should return a tuple ``(width, height)``.

        """

        raise NotImplementedError()


class SimpleTextMeasure(TextMeasure):
    """
    A simple text measuring service that multiplies length of the text
    by average width of the character. Works best for monospace fonts.

    """

    def __init__(
        self,
        *,
        character_advance: float,
        wide_character_advance: float,
        line_height: float,
    ):
        """
        :param character_advance:
            average length of one character in the used font. Since SVG elements
            cannot expand and shrink dynamically, length of text nodes is calculated
            as number of symbols multiplied by this constant.

        :param wide_character_advance:
            average length of one wide character in the used font.

        :param line_height:
            height of a single line, equals to CSS ``line-height`` property.

        """

        self._character_advance = character_advance
        self._wide_character_advance = wide_character_advance
        self._line_height = line_height

    def measure(self, text: str) -> _t.Tuple[int, int]:
        if not text:
            return (0, math.ceil(self._line_height))

        lines = text.splitlines()
        line_width = math.ceil(
            max(
                sum(
                    (
                        self._character_advance
                        if wcwidth.wcwidth(g) == 1
                        else self._wide_character_advance
                    )
                    for g in grapheme.graphemes(line)
                )
                for line in lines
            )
        )

        return (line_width, math.ceil(len(lines) * self._line_height))


class TrueTextMeasure(TextMeasure):
    """
    A text measuring service that uses Python Image Library to calculate
    text's actual size.

    """

    def __init__(self, font: ImageFont | FreeTypeFont, line_height: float):
        """
        :param font:
            font data, see `PIL.ImageFont.ImageFont`.

        :param line_height:
            height of a single line, equals to CSS ``line-height`` property.

        """

        self._font = font
        self._line_height = line_height

    def measure(self, text: str) -> _t.Tuple[int, int]:
        if not text:
            return (0, math.ceil(self._line_height))

        lines = text.splitlines()
        line_width = math.ceil(max(self._font.getlength(line) for line in lines))
        return (line_width, math.ceil(len(lines) * self._line_height))
