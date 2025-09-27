import io
import itertools
import os
import pathlib
from copy import deepcopy

import pytest
from pytest_image_diff.plugin import DiffInfoCallableType  # type: ignore
from reportlab.graphics import renderPM
from svglib import svglib  # type: ignore

import syntax_diagrams as rr
from syntax_diagrams._impl.render.svg import svg_layout_settings as _svg_layout_settings
from syntax_diagrams._impl.render.text import (
    text_layout_settings as _text_layout_settings,
)
from syntax_diagrams.render import DEFAULT_CSS


@pytest.fixture(scope="session")
def image_diff_root() -> str:
    return os.path.dirname(__file__)


@pytest.fixture(scope="session")  # pragma: no cover
def image_diff_dir(image_diff_root: str) -> str:
    return os.path.join(image_diff_root, "image_diff")


@pytest.fixture(scope="session")
def image_diff_reference_dir(image_diff_root: str) -> str:
    return os.path.join(image_diff_root, "image_diff_reference")


@pytest.fixture
def regression(image_regression, request):
    def regression(render, suffix=None):
        stream = io.StringIO(render)
        drawing = svglib.svg2rlg(stream)  # type: ignore
        assert drawing
        data = renderPM.drawToString(drawing, dpi=72)  # type: ignore
        assert image_regression(data, threshold=0.0001, suffix=suffix)

    return regression


@pytest.fixture
def text_regression(_image_diff_info: DiffInfoCallableType, request):
    def _factory(text: str, suffix: str | None = None) -> bool:
        diff_info = _image_diff_info("", suffix)
        reference_name = pathlib.Path(
            diff_info.reference_name.removesuffix(".png") + ".txt"
        )
        reference_name.parent.mkdir(parents=True, exist_ok=True)
        if not os.path.exists(reference_name):
            reference_name.write_text(text)
            return True
        else:
            expected = reference_name.read_text()
            if text != expected:
                ll = len(text.splitlines()[0])
                rl = len(expected.splitlines()[0])
                ml = max(ll, rl)
                lines: list[str] = []
                for l, r in itertools.zip_longest(
                    text.splitlines(), expected.splitlines()
                ):
                    diff = "".join(
                        [
                            (
                                " "
                                if (cl or " ") == (cr or " ")
                                else (cl if cl != " " else cr) or "?"
                            )
                            for cl, cr in itertools.zip_longest(
                                l or ll * " ", r or rl * " "
                            )
                        ]
                    )
                    lines.append(f"{l or ll * ' '}  :  {r or rl * ' '}  :  {diff}")
                raise AssertionError(
                    f"\n{'Got:':<{ll}}  :  {'Expected:':<{rl}}  :  {'Diff:':<{ml}}\n"
                    + "\n".join(lines)
                )
        return True

    yield _factory


@pytest.fixture
def text_layout_settings():
    return _text_layout_settings()


@pytest.fixture
def svg_layout_settings():
    return _svg_layout_settings()


@pytest.fixture
def svg_css():
    css = deepcopy(DEFAULT_CSS)
    css.setdefault("text", {})["transform"] = "translate(0, -2)"
    css.setdefault(".group text", {})["transform"] = "translate(0, -2)"
    return css


@pytest.fixture
def svg_render_settings(svg_css):
    return rr.SvgRenderSettings(css_style=svg_css)


@pytest.fixture
def text_render_settings():
    return rr.TextRenderSettings()
