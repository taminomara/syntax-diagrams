from dataclasses import replace

import neat_railroad_diagrams as rr


def test_line(regression, svg_layout_settings, svg_css):
    render = rr._SvgRender(50, 15, svg_layout_settings, "", svg_css)
    render.line(10, 5).segment(30)
    render.line(40, 10).segment(-30)
    regression(render.to_string())


def test_line_bend_reverse(regression, svg_layout_settings, svg_css):
    render = rr._SvgRender(50, 210, svg_layout_settings, "", svg_css)
    render.line(30, 10).segment(10).bend_reverse(0, "w").segment(-30).bend_reverse(
        00, "e"
    ).segment(10)
    render.line(30, 30).segment(10).bend_reverse(15, "w").segment(-30).bend_reverse(
        -15, "e"
    ).segment(10)
    render.line(30, 80).segment(10).bend_reverse(-15, "w").segment(-30).bend_reverse(
        15, "e"
    ).segment(10)
    render.line(30, 100).segment(10).bend_reverse(40, "w").segment(-30).bend_reverse(
        -40, "e"
    ).segment(10)
    render.line(30, 200).segment(10).bend_reverse(-40, "w").segment(-30).bend_reverse(
        40, "e"
    ).segment(10)
    regression(render.to_string())


def test_line_bend_forward(regression, svg_layout_settings, svg_css):
    render = rr._SvgRender(50, 210, svg_layout_settings, "", svg_css)
    render.line(0, 10).segment(20).bend_forward(0).segment(20)
    render.line(0, 30).segment(20).bend_forward(15).segment(20)
    render.line(0, 80).segment(20).bend_forward(-15).segment(20)
    render.line(0, 100).segment(20).bend_forward(40).segment(20)
    render.line(0, 200).segment(20).bend_forward(-40).segment(20)
    regression(render.to_string())


def test_line_bend_forward_rtl(regression, svg_layout_settings, svg_css):
    render = rr._SvgRender(50, 210, svg_layout_settings, "", svg_css)
    render.line(50, 10).segment(-20).bend_forward(0, "w").segment(-20)
    render.line(50, 30).segment(-20).bend_forward(15, "w").segment(-20)
    render.line(50, 80).segment(-20).bend_forward(-15, "w").segment(-20)
    render.line(50, 100).segment(-20).bend_forward(40, "w").segment(-20)
    render.line(50, 200).segment(-20).bend_forward(-40, "w").segment(-20)
    regression(render.to_string())


def test_node(regression, svg_layout_settings, svg_css):
    render = rr._SvgRender(400, 150, svg_layout_settings, "", svg_css)

    node = rr.comment("fully automated")._make_node_with_layout_info(
        25, svg_layout_settings
    )
    node._render(render, 5, 20, False)

    node = rr.terminal("luxury")._make_node_with_layout_info(25, svg_layout_settings)
    node._render(render, 5, 60, False)

    node = rr.non_terminal("gay space communism")._make_node_with_layout_info(
        25, svg_layout_settings
    )
    node._render(render, 5, 100, False)

    regression(render.to_string())


def test_end_class(regression, svg_render_settings):
    rendered = rr.render_svg(
        rr.skip(),
        max_width=400,
        settings=replace(
            svg_render_settings,
            end_class=rr.EndClass.SIMPLE,
        ),
    )
    regression(rendered, "simple")

    rendered = rr.render_svg(
        rr.skip(),
        max_width=400,
        settings=replace(
            svg_render_settings,
            end_class=rr.EndClass.COMPLEX,
        ),
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
    def test_skip(self, regression, svg_render_settings):
        rendered = rr.render_svg(
            rr.skip(),
            max_width=400,
            settings=svg_render_settings,
        )
        regression(rendered)

    def test_wrapped_skip(self, regression, svg_render_settings):
        rendered = rr.render_svg(
            rr.sequence(rr.skip()),
            max_width=400,
            settings=svg_render_settings,
        )
        regression(rendered, "one")

        rendered = rr.render_svg(
            rr.sequence(rr.skip(), rr.skip(), rr.skip()),
            max_width=400,
            settings=svg_render_settings,
        )
        regression(rendered, "several")

    def test_normal(self, regression, svg_render_settings):
        rendered = rr.render_svg(
            rr.sequence(
                rr.terminal("A"),
                rr.non_terminal("B"),
            ),
            max_width=400,
            settings=svg_render_settings,
        )
        regression(rendered)

    def test_long_seq(self, regression, svg_render_settings):
        rendered = rr.render_svg(
            rr.sequence(
                rr.terminal("if"),
                rr.non_terminal("expr"),
                rr.terminal("{"),
                rr.non_terminal("body"),
                rr.terminal("}"),
                rr.terminal("else"),
                rr.terminal("{"),
                rr.non_terminal("body"),
                rr.terminal("}"),
            ),
            max_width=400,
            settings=svg_render_settings,
        )
        regression(rendered)

    def test_long_seq_reverse(self, regression, svg_render_settings):
        rendered = rr.render_svg(
            rr.sequence(
                rr.terminal("if"),
                rr.non_terminal("expr"),
                rr.terminal("{"),
                rr.non_terminal("body"),
                rr.terminal("}"),
                rr.terminal("else"),
                rr.terminal("{"),
                rr.non_terminal("body"),
                rr.terminal("}"),
            ),
            max_width=400,
            settings=svg_render_settings,
            reverse=True,
        )
        regression(rendered)

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

    def test_arc_radius_too_big_to_break(self, regression, svg_render_settings):
        rendered = rr.render_svg(
            rr.sequence(
                rr.terminal("A"),
                rr.terminal("B"),
                rr.terminal("C"),
                rr.terminal("D"),
            ),
            max_width=50,
            settings=replace(
                svg_render_settings,
                arc_radius=500,
            ),
        )
        regression(rendered)

    def test_up_down_height(self, regression, svg_render_settings):
        rendered = rr.render_svg(
            rr.choice(
                rr.terminal("XX"),
                rr.sequence(
                    rr.terminal("A"),
                    rr.terminal("B"),
                    linebreaks=[
                        rr.LineBreak.HARD,
                    ],
                ),
                rr.terminal("XX"),
                default=1,
            ),
            max_width=400,
            settings=svg_render_settings,
        )
        regression(rendered)

    def test_stack(self, regression, svg_render_settings):
        rendered = rr.render_svg(
            rr.stack(
                rr.sequence(rr.terminal("A"), rr.terminal("B")),
                rr.sequence(rr.terminal("C"), rr.terminal("D")),
            ),
            max_width=400,
            settings=svg_render_settings,
        )
        regression(rendered)


class TestChoice:
    def test_skip(self, regression, svg_render_settings):
        rendered = rr.render_svg(
            rr.optional(
                rr.skip(),
            ),
            max_width=400,
            settings=svg_render_settings,
        )
        regression(rendered)

    def test_multiple_skips(self, regression, svg_render_settings):
        rendered = rr.render_svg(
            rr.choice(
                rr.terminal("A"),
                rr.skip(),
                rr.terminal("B"),
                rr.skip(),
            ),
            max_width=400,
            settings=svg_render_settings,
        )
        regression(rendered)

    def test_multiple_skips_default(self, regression, svg_render_settings):
        rendered = rr.render_svg(
            rr.choice(
                rr.terminal("A"),
                rr.skip(),
                rr.terminal("B"),
                rr.skip(),
                default=1,
            ),
            max_width=400,
            settings=svg_render_settings,
        )
        regression(rendered)

    def test_optional(self, regression, svg_render_settings):
        rendered = rr.render_svg(
            rr.optional(
                rr.terminal("A"),
            ),
            max_width=400,
            settings=svg_render_settings,
        )
        regression(rendered)

    def test_optional_skip(self, regression, svg_render_settings):
        rendered = rr.render_svg(
            rr.optional(
                rr.terminal("A"),
                skip=True,
            ),
            max_width=400,
            settings=svg_render_settings,
        )
        regression(rendered)

    def test_default_0(self, regression, svg_render_settings):
        rendered = rr.render_svg(
            rr.choice(
                rr.terminal("A"),
                rr.terminal("B"),
                rr.terminal("C"),
                default=0,
            ),
            max_width=400,
            settings=svg_render_settings,
        )
        regression(rendered)

    def test_default_1(self, regression, svg_render_settings):
        rendered = rr.render_svg(
            rr.choice(
                rr.terminal("A"),
                rr.terminal("B"),
                rr.terminal("C"),
                default=1,
            ),
            max_width=400,
            settings=svg_render_settings,
        )
        regression(rendered)

    def test_default_2(self, regression, svg_render_settings):
        rendered = rr.render_svg(
            rr.choice(
                rr.terminal("A"),
                rr.terminal("B"),
                rr.terminal("C"),
                default=2,
            ),
            max_width=400,
            settings=svg_render_settings,
        )
        regression(rendered)

    def test_reverse(self, regression, svg_render_settings):
        rendered = rr.render_svg(
            rr.choice(
                rr.sequence(
                    rr.terminal("A"),
                    rr.terminal("B"),
                ),
                rr.stack(
                    rr.sequence(
                        rr.terminal("C"),
                        rr.terminal("D"),
                    ),
                    rr.terminal("E"),
                ),
                rr.terminal("F"),
                default=1,
            ),
            max_width=400,
            settings=svg_render_settings,
            reverse=True,
        )
        regression(rendered)

    def test_up_down_height(self, regression, svg_render_settings):
        stack = rr.stack(rr.terminal("A"), rr.terminal("B"))

        rendered = rr.render_svg(
            rr.choice(
                rr.terminal("XX"),
                stack,
                stack,
                stack,
                rr.terminal("YY"),
                default=1,
            ),
            max_width=400,
            settings=svg_render_settings,
        )
        regression(rendered)


class TestOneOrMore:
    def test_skip(self, regression, svg_render_settings):
        rendered = rr.render_svg(
            rr.zero_or_more(
                rr.skip(),
            ),
            max_width=400,
            settings=svg_render_settings,
        )
        regression(rendered)

    def test_skip_nonempty_repeat(self, regression, svg_render_settings):
        rendered = rr.render_svg(
            rr.zero_or_more(rr.skip(), repeat=rr.terminal("A")),
            max_width=400,
            settings=svg_render_settings,
        )
        regression(rendered)

    def test_zero_or_more(self, regression, svg_render_settings):
        rendered = rr.render_svg(
            rr.zero_or_more(
                rr.terminal("A"),
            ),
            max_width=400,
            settings=svg_render_settings,
        )
        regression(rendered)

    def test_zero_or_more_repeat(self, regression, svg_render_settings):
        rendered = rr.render_svg(
            rr.zero_or_more(
                rr.terminal("A"),
                repeat=rr.terminal("B"),
            ),
            max_width=400,
            settings=svg_render_settings,
        )
        regression(rendered)

    def test_normal(self, regression, svg_render_settings):
        rendered = rr.render_svg(
            rr.one_or_more(
                rr.sequence(
                    rr.terminal("A"),
                    rr.terminal("B"),
                    rr.terminal("C"),
                ),
            ),
            max_width=400,
            settings=svg_render_settings,
        )
        regression(rendered)

    def test_repeat(self, regression, svg_render_settings):
        rendered = rr.render_svg(
            rr.one_or_more(
                rr.sequence(
                    rr.terminal("A"),
                    rr.terminal("B"),
                    rr.terminal("C"),
                ),
                repeat=rr.sequence(
                    rr.terminal("D"),
                    rr.terminal("E"),
                    rr.terminal("F"),
                ),
            ),
            max_width=400,
            settings=svg_render_settings,
        )
        regression(rendered)

    def test_repeat_choice(self, regression, svg_render_settings):
        rendered = rr.render_svg(
            rr.one_or_more(
                rr.non_terminal("arg"),
                repeat=rr.choice(
                    rr.terminal(","),
                    rr.terminal(";"),
                ),
            ),
            max_width=400,
            settings=svg_render_settings,
        )
        regression(rendered)

    def test_repeat_choice_reverse(self, regression, svg_render_settings):
        rendered = rr.render_svg(
            rr.one_or_more(
                rr.non_terminal("arg"),
                repeat=rr.sequence(
                    rr.one_or_more(
                        rr.non_terminal("arg"),
                        repeat=rr.choice(
                            rr.terminal(","),
                            rr.terminal(";"),
                        ),
                    ),
                    rr.choice(
                        rr.terminal(","),
                        rr.terminal(";"),
                    ),
                ),
            ),
            max_width=400,
            settings=svg_render_settings,
        )
        regression(rendered)

    def test_up_down_height(self, regression, svg_render_settings):
        rendered = rr.render_svg(
            rr.one_or_more(
                rr.stack(
                    rr.sequence(
                        rr.terminal("A"),
                        rr.terminal("B"),
                    ),
                    rr.terminal("C"),
                ),
                repeat=rr.stack(
                    rr.sequence(
                        rr.terminal("D"),
                        rr.terminal("E"),
                    ),
                    rr.terminal("F"),
                ),
            ),
            max_width=400,
            settings=svg_render_settings,
        )
        regression(rendered)
