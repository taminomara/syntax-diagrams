from dataclasses import replace

import syntax_diagrams as rr
from syntax_diagrams._impl.load import load
from syntax_diagrams._impl.render import (
    ConnectionType,
    LayoutContext,
    RenderContext,
)
from syntax_diagrams._impl.render.svg import SvgRender
from syntax_diagrams._impl.vec import Vec
from syntax_diagrams.render import ArrowStyle


def test_line(regression, svg_layout_settings, svg_css):
    render = SvgRender(
        50, 15, svg_layout_settings, "", svg_css, None, None, ArrowStyle.NONE, 0, 0
    )
    ((render).line(Vec(10, 5)).segment_abs(40))
    ((render).line(Vec(40, 10)).segment_abs(10))
    regression(render.to_string())


def test_line_bend_reverse(regression, svg_layout_settings, svg_css):
    render = SvgRender(
        50, 210, svg_layout_settings, "", svg_css, None, None, ArrowStyle.NONE, 0, 0
    )
    (
        (render)
        .line(Vec(30, 10))
        .segment_abs(40)
        .bend_backward_reverse_abs(10)
        .segment_abs(10)
        .bend_backward_abs(10)
        .segment_abs(20)
    )
    (
        (render)
        .line(Vec(30, 30))
        .segment_abs(40)
        .bend_backward_reverse_abs(45)
        .segment_abs(10)
        .bend_backward_abs(30)
        .segment_abs(20)
    )
    (
        (render)
        .line(Vec(30, 80))
        .segment_abs(40)
        .bend_backward_reverse_abs(65)
        .segment_abs(10)
        .bend_backward_abs(80)
        .segment_abs(20)
    )
    (
        (render)
        .line(Vec(30, 100))
        .segment_abs(40)
        .bend_backward_reverse_abs(140)
        .segment_abs(10)
        .bend_backward_abs(100)
        .segment_abs(20)
    )
    (
        (render)
        .line(Vec(30, 200))
        .segment_abs(40)
        .bend_backward_reverse_abs(160)
        .segment_abs(10)
        .bend_backward_abs(200)
        .segment_abs(20)
    )
    regression(render.to_string())


def test_line_bend_forward(regression, svg_layout_settings, svg_css):
    render = SvgRender(
        50, 210, svg_layout_settings, "", svg_css, None, None, ArrowStyle.NONE, 0, 0
    )
    ((render).line(Vec(0, 10)).segment_abs(20).bend_forward_abs(10).segment_abs(50))
    ((render).line(Vec(0, 30)).segment_abs(20).bend_forward_abs(45).segment_abs(50))
    ((render).line(Vec(0, 80)).segment_abs(20).bend_forward_abs(65).segment_abs(50))
    ((render).line(Vec(0, 100)).segment_abs(20).bend_forward_abs(140).segment_abs(50))
    ((render).line(Vec(0, 200)).segment_abs(20).bend_forward_abs(160).segment_abs(50))
    regression(render.to_string())


def test_line_bend_forward_rtl(regression, svg_layout_settings, svg_css):
    render = SvgRender(
        50, 210, svg_layout_settings, "", svg_css, None, None, ArrowStyle.NONE, 0, 0
    )
    (
        (render)
        .line(Vec(50, 10), True)
        .segment_abs(30)
        .bend_forward_abs(10)
        .segment_abs(0)
    )
    (
        (render)
        .line(Vec(50, 30), True)
        .segment_abs(30)
        .bend_forward_abs(45)
        .segment_abs(0)
    )
    (
        (render)
        .line(Vec(50, 80), True)
        .segment_abs(30)
        .bend_forward_abs(65)
        .segment_abs(0)
    )
    (
        (render)
        .line(Vec(50, 100), True)
        .segment_abs(30)
        .bend_forward_abs(140)
        .segment_abs(0)
    )
    (
        (render)
        .line(Vec(50, 200), True)
        .segment_abs(30)
        .bend_forward_abs(160)
        .segment_abs(0)
    )
    regression(render.to_string())


def test_node(regression, svg_layout_settings, svg_css):
    render = SvgRender(
        200, 150, svg_layout_settings, "", svg_css, None, None, ArrowStyle.NONE, 0, 0
    )

    node = load(rr.comment("fully automated"), lambda x: x)
    node.calculate_layout(svg_layout_settings, LayoutContext(width=200, is_outer=True))
    node.render(
        render,
        RenderContext(
            pos=Vec(5, 20),
            reverse=False,
            start_connection_pos=Vec(0, 20),
            end_connection_pos=Vec(200, 20),
        ),
    )

    node = load(rr.terminal("luxury"), lambda x: x)
    node.calculate_layout(svg_layout_settings, LayoutContext(width=200, is_outer=True))
    node.render(
        render,
        RenderContext(
            pos=Vec(5, 60),
            reverse=False,
            start_connection_pos=Vec(0, 60),
            end_connection_pos=Vec(200, 60),
        ),
    )

    node = load(rr.non_terminal("gay space communism"), lambda x: x)
    node.calculate_layout(svg_layout_settings, LayoutContext(width=200, is_outer=True))
    node.render(
        render,
        RenderContext(
            pos=Vec(5, 100),
            reverse=False,
            start_connection_pos=Vec(0, 100),
            end_connection_pos=Vec(200, 100),
        ),
    )

    regression(render.to_string())


def test_node_enter(regression, svg_layout_settings, svg_css):
    render = SvgRender(
        200, 100, svg_layout_settings, "", svg_css, None, None, ArrowStyle.NONE, 0, 0
    )
    node = load(rr.terminal("XXX"), lambda x: x)
    node.calculate_layout(svg_layout_settings, LayoutContext(width=200, is_outer=True))
    node.render(
        render,
        RenderContext(
            pos=Vec(10, 50),
            reverse=False,
            start_connection_pos=Vec(0, 50),
            end_connection_pos=Vec(200, 50),
        ),
    )
    regression(render.to_string(), "normal")

    render = SvgRender(
        200, 100, svg_layout_settings, "", svg_css, None, None, ArrowStyle.NONE, 0, 0
    )
    node = load(rr.terminal("XXX"), lambda x: x)
    node.calculate_layout(
        svg_layout_settings,
        LayoutContext(
            width=200,
            is_outer=True,
            start_connection=ConnectionType.SPLIT,
            end_connection=ConnectionType.SPLIT,
        ),
    )
    node.render(
        render,
        RenderContext(
            pos=Vec(10, 50),
            reverse=False,
            start_connection_pos=Vec(0, 0),
            end_connection_pos=Vec(200, 100),
        ),
    )
    regression(render.to_string(), "split")

    render = SvgRender(
        200, 100, svg_layout_settings, "", svg_css, None, None, ArrowStyle.NONE, 0, 0
    )
    node = load(rr.terminal("XXX"), lambda x: x)
    node.calculate_layout(
        svg_layout_settings,
        LayoutContext(
            width=200,
            is_outer=True,
            start_connection=ConnectionType.STACK,
            end_connection=ConnectionType.STACK,
        ),
    )
    node.render(
        render,
        RenderContext(
            pos=Vec(10, 50),
            reverse=False,
            start_connection_pos=Vec(10, 0),
            end_connection_pos=Vec(190, 100),
        ),
    )
    regression(render.to_string(), "stack")


def test_end_class(regression, svg_render_settings):
    rendered = rr.render_svg(
        rr.skip(),
        max_width=400,
        settings=replace(svg_render_settings, end_class=rr.EndClass.SIMPLE),
    )
    regression(rendered, "simple")

    rendered = rr.render_svg(
        rr.skip(),
        max_width=400,
        settings=replace(svg_render_settings, end_class=rr.EndClass.COMPLEX),
    )
    regression(rendered, "complex")


class TestArcRadius:
    def test_r10(self, regression, svg_render_settings):
        rendered = rr.render_svg(
            rr.choice(
                rr.terminal("A"),
                rr.terminal("B"),
            ),
            max_width=400,
            settings=replace(svg_render_settings, arc_radius=10),
        )
        regression(rendered)

    def test_r5(self, regression, svg_render_settings):
        rendered = rr.render_svg(
            rr.choice(
                rr.terminal("A"),
                rr.terminal("B"),
            ),
            max_width=400,
            settings=replace(svg_render_settings, arc_radius=5),
        )
        regression(rendered)

    def test_r0(self, regression, svg_render_settings):
        rendered = rr.render_svg(
            rr.choice(
                rr.terminal("A"),
                rr.terminal("B"),
            ),
            max_width=400,
            settings=replace(svg_render_settings, arc_radius=0),
        )
        regression(rendered)

    def test_r0_no_margin(self, regression, svg_render_settings):
        rendered = rr.render_svg(
            rr.choice(
                rr.terminal("A"),
                rr.terminal("B"),
            ),
            max_width=400,
            settings=replace(svg_render_settings, arc_radius=0, arc_margin=0),
        )
        regression(rendered)


class TestSeq:
    def test_break(self, regression, svg_render_settings):
        rendered = rr.render_svg(
            rr.sequence(
                rr.terminal("A"),
                rr.terminal("B"),
                rr.terminal("C"),
                rr.terminal("D"),
            ),
            max_width=200,
            settings=svg_render_settings,
        )
        regression(rendered)

    def test_soft_break(self, regression, svg_render_settings):
        rendered = rr.render_svg(
            rr.sequence(
                rr.terminal("A"),
                rr.terminal("B"),
                rr.terminal("C"),
                rr.terminal("D"),
                linebreaks=[
                    rr.LineBreak.SOFT,
                    rr.LineBreak.NO_BREAK,
                    rr.LineBreak.NO_BREAK,
                ],
            ),
            max_width=200,
            settings=svg_render_settings,
        )
        regression(rendered)

    def test_hard_break(self, regression, svg_render_settings):
        rendered = rr.render_svg(
            rr.sequence(
                rr.terminal("A"),
                rr.terminal("B"),
                rr.terminal("C"),
                rr.terminal("D"),
                linebreaks=[
                    rr.LineBreak.NO_BREAK,
                    rr.LineBreak.HARD,
                    rr.LineBreak.NO_BREAK,
                ],
            ),
            max_width=400,
            settings=svg_render_settings,
        )
        regression(rendered)
