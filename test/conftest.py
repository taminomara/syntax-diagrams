import io
import os
from copy import deepcopy

import pytest
from reportlab.graphics import renderPM
from svglib import svglib  # type: ignore

import neat_railroad_diagrams as rr


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
        drawing = svglib.svg2rlg(stream)
        assert drawing
        data = renderPM.drawToString(drawing, dpi=72)
        image_regression(data, suffix=suffix)

    return regression


@pytest.fixture
def text_layout_settings():
    return rr._text_layout_settings()


@pytest.fixture
def svg_layout_settings():
    return rr._svg_layout_settings()


@pytest.fixture
def svg_css():
    css = deepcopy(rr.DEFAULT_CSS)
    css["text"]["dy"] = "4"
    return css


@pytest.fixture
def svg_render_settings(svg_css):
    return rr.SvgRenderSettings(css_style=svg_css)
