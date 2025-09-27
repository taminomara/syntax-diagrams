from __future__ import annotations

import abc
import math
import pathlib
import typing as _t

import grapheme
import wcwidth

try:
    from PIL.ImageFont import FreeTypeFont
except ImportError:
    pass

__all__ = [
    "TextMeasure",
    "SimpleTextMeasure",
    "TrueTextMeasure",
]


class TextMeasure(metaclass=abc.ABCMeta):
    """
    An interface for measuring dimensions of rendered text.

    """

    @abc.abstractmethod
    def measure(self, text: str) -> _t.Tuple[int, int]:
        """
        Called before rendering a node to measure its text.

        Should return a tuple ``(width, height)``.

        """

    @property
    @abc.abstractmethod
    def font_size(self) -> float:
        """
        Font size.

        """

    @property
    @abc.abstractmethod
    def line_height(self) -> float:
        """
        Height of a single line, equals to CSS ``line-height`` property.

        """

    @property
    @abc.abstractmethod
    def ascent(self) -> float:
        """
        Distance from the baseline to the highest outline point.

        """


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
        font_size: float,
        line_height: float,
        ascent: float,
    ):
        """
        :param character_advance:
            average length of one character in the used font. Since SVG elements
            cannot expand and shrink dynamically, length of text nodes is calculated
            as number of symbols multiplied by this constant.

        :param wide_character_advance:
            average length of one wide character in the used font.

        :param font_size:
            font size.

        :param line_height:
            height of a single line, equals to CSS ``line-height`` property.

        :param ascent:
            the distance from the baseline to the highest outline point.

            This is required because Chrome, Firefox and Safari all treat
            ``dominant-baseline`` attribute in a slightly different way.

        """

        self._character_advance = character_advance
        self._wide_character_advance = wide_character_advance
        self._font_size = font_size
        self._line_height = line_height
        self._ascent = ascent

    def measure(self, text: str) -> _t.Tuple[int, int]:
        if not text:
            return (0, math.ceil(self._line_height))

        lines = text.splitlines()
        line_width = math.ceil(
            max(
                sum(
                    (
                        self._character_advance
                        if (width := wcwidth.wcswidth(g)) == 1
                        else (self._wide_character_advance if width == 2 else 0)
                    )
                    for g in grapheme.graphemes(line)
                )
                for line in lines
            )
        )

        return (line_width, math.ceil(len(lines) * self._line_height))

    @property
    def font_size(self) -> float:
        return self._font_size

    @property
    def line_height(self) -> float:
        return self._line_height

    @property
    def ascent(self) -> float:
        return self._ascent

    def __eq__(self, rhs):
        if not isinstance(rhs, SimpleTextMeasure):
            return False
        else:
            return (
                self._character_advance,
                self._wide_character_advance,
                self._font_size,
                self._line_height,
            ) == (
                rhs._character_advance,
                rhs._wide_character_advance,
                rhs._font_size,
                rhs._line_height,
            )


class TrueTextMeasure(TextMeasure):
    """
    A text measuring service that uses Python Image Library to calculate
    text's actual size.

    """

    def __init__(
        self,
        font: FreeTypeFont | str | pathlib.Path,
        font_size: float,
        line_height: float,
    ):
        """
        :param font:
            font data, a path to a font file, or a font file name.

            .. seealso::

                `PIL.ImageFont.ImageFont`, `PIL.ImageFont.truetype`

        :param font_size:
            font size.

        :param line_height:
            height of a single line, equals to CSS ``line-height`` property.

        """

        self._font = font

        if isinstance(font, (str, pathlib.Path)):
            import PIL.ImageFont

            self._font_data = PIL.ImageFont.truetype(font, size=font_size)
        else:
            self._font_data = font

        self._font_size = font_size
        self._line_height = line_height

        self._ascent = self._font_data.getmetrics()[0]

    def measure(self, text: str) -> _t.Tuple[int, int]:
        if not text:
            return (0, math.ceil(self._line_height))

        lines = text.splitlines()
        line_width = math.ceil(max(self._font_data.getlength(line) for line in lines))
        return (line_width, math.ceil(len(lines) * self._line_height))

    @property
    def font_size(self) -> float:
        return self._font_size

    @property
    def ascent(self) -> float:
        return self._ascent

    @property
    def line_height(self) -> float:
        return self._line_height

    def __eq__(self, rhs):
        if not isinstance(rhs, TrueTextMeasure):
            return False
        else:
            return (
                self._font,
                self._font_size,
                self._line_height,
            ) == (
                rhs._font,
                rhs._font_size,
                rhs._line_height,
            )


def _main():
    import argparse
    import textwrap

    import PIL.ImageFont

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--size", type=int, default=14)
    parser.add_argument("font", type=argparse.FileType("rb"))
    args = parser.parse_args()

    tm = TrueTextMeasure(
        PIL.ImageFont.truetype(args.font, size=args.size), args.size, 1.1 * args.size
    )
    character_advance = tm.measure("x" * 1000)[0] / 1000
    wide_character_advance = tm.measure("🥲" * 1000)[0] / 1000
    font_size = args.size
    line_height = 1.1 * args.size
    ascent = tm.ascent

    print(
        textwrap.dedent(
            f"""
                SimpleTextMeasure(
                    character_advance={character_advance!r},
                    wide_character_advance={wide_character_advance!r},
                    font_size={font_size!r},
                    line_height={line_height!r},
                    ascent={ascent!r},
                )
            """
        ).strip()
    )


if __name__ == "__main__":
    _main()
