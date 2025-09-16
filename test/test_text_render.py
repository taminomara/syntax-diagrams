import syntax_diagrams as rr
from syntax_diagrams._impl.load import load
from syntax_diagrams._impl.render import (
    ConnectionType,
    LayoutContext,
    RenderContext,
)
from syntax_diagrams._impl.render.text import TextRender
from syntax_diagrams._impl.vec import Vec


def test_line(text_layout_settings):
    render = TextRender(5, 2, text_layout_settings)
    ((render).line(Vec(1, 0)).segment_abs(4))
    ((render).line(Vec(4, 1)).segment_abs(1))
    # fmt: off
    expected = (
        " ─── \n"
        " ─── \n"
    )
    # fmt: on
    assert render.to_string() == expected


def test_line_arrow(text_layout_settings):
    render = TextRender(5, 4, text_layout_settings)
    ((render).line(Vec(0, 0)).segment_abs(5, arrow_begin=True))
    ((render).line(Vec(0, 1)).segment_abs(5, arrow_end=True))
    ((render).line(Vec(5, 2)).segment_abs(0, arrow_begin=True))
    ((render).line(Vec(5, 3)).segment_abs(0, arrow_end=True))
    # fmt: off
    expected = (
        "→────\n"
        "────→\n"
        "────←\n"
        "←────\n"
    )
    # fmt: on
    assert render.to_string() == expected


def test_line_bend_reverse(text_layout_settings):
    render = TextRender(5, 11, text_layout_settings)
    (
        (render)
        .line(Vec(3, 0))
        .segment_abs(4)
        .bend_backward_reverse_abs(0)
        .segment_abs(1)
        .bend_backward_abs(0)
        .segment_abs(2)
    )
    (
        (render)
        .line(Vec(3, 1))
        .segment_abs(4)
        .bend_backward_reverse_abs(2)
        .segment_abs(1)
        .bend_backward_abs(1)
        .segment_abs(2)
    )
    (
        (render)
        .line(Vec(3, 4))
        .segment_abs(4)
        .bend_backward_reverse_abs(3)
        .segment_abs(1)
        .bend_backward_abs(4)
        .segment_abs(2)
    )
    (
        (render)
        .line(Vec(3, 5))
        .segment_abs(4)
        .bend_backward_reverse_abs(7)
        .segment_abs(1)
        .bend_backward_abs(5)
        .segment_abs(2)
    )
    (
        (render)
        .line(Vec(3, 10))
        .segment_abs(4)
        .bend_backward_reverse_abs(8)
        .segment_abs(1)
        .bend_backward_abs(10)
        .segment_abs(2)
    )
    # fmt: off
    expected = (
        "╶───╴\n"
        "╭─ ─╮\n"
        "╰───╯\n"
        "╭───╮\n"
        "╰─ ─╯\n"
        "╭─ ─╮\n"
        "│   │\n"
        "╰───╯\n"
        "╭───╮\n"
        "│   │\n"
        "╰─ ─╯\n"
    )
    # fmt: on
    assert render.to_string() == expected


def test_line_bend_forward(text_layout_settings):
    render = TextRender(5, 11, text_layout_settings)
    ((render).line(Vec(0, 0)).segment_abs(2).bend_forward_abs(0).segment_abs(5))
    ((render).line(Vec(0, 1)).segment_abs(2).bend_forward_abs(2).segment_abs(5))
    ((render).line(Vec(0, 4)).segment_abs(2).bend_forward_abs(3).segment_abs(5))
    ((render).line(Vec(0, 5)).segment_abs(2).bend_forward_abs(7).segment_abs(5))
    ((render).line(Vec(0, 10)).segment_abs(2).bend_forward_abs(8).segment_abs(5))
    # fmt: off
    expected = (
        "─────\n"
        "──╮  \n"
        "  ╰──\n"
        "  ╭──\n"
        "──╯  \n"
        "──╮  \n"
        "  │  \n"
        "  ╰──\n"
        "  ╭──\n"
        "  │  \n"
        "──╯  \n"
    )
    # fmt: on
    assert render.to_string() == expected


def test_node(text_layout_settings):
    render = TextRender(27, 9, text_layout_settings)

    node = load(rr.comment("fully automated"), lambda x: x)
    node.calculate_layout(text_layout_settings, LayoutContext(width=25, is_outer=True))
    node.render(
        render,
        RenderContext(
            pos=Vec(0, 1),
            reverse=False,
            start_connection_pos=Vec(0, 1),
            end_connection_pos=Vec(27, 1),
        ),
    )

    node = load(rr.terminal("luxury"), lambda x: x)
    node.calculate_layout(text_layout_settings, LayoutContext(width=25, is_outer=True))
    node.render(
        render,
        RenderContext(
            pos=Vec(0, 4),
            reverse=False,
            start_connection_pos=Vec(0, 4),
            end_connection_pos=Vec(27, 4),
        ),
    )

    node = load(rr.non_terminal("🌈gay space communism🌈"), lambda x: x)
    node.calculate_layout(text_layout_settings, LayoutContext(width=25, is_outer=True))
    node.render(
        render,
        RenderContext(
            pos=Vec(0, 7),
            reverse=False,
            start_connection_pos=Vec(0, 4),
            end_connection_pos=Vec(27, 4),
        ),
    )

    # fmt: off
    expected = (
        "                           \n"
        "╴ fully automated ╶────────\n"
        "                           \n"
        "┌────────┐                 \n"
        "┤ luxury ├─────────────────\n"
        "└────────┘                 \n"
        "╔═════════════════════════╗\n"
        "╢ 🌈gay space communism🌈 ╟\n"
        "╚═════════════════════════╝\n"
    )
    # fmt: on
    assert render.to_string() == expected


def test_node_enter(text_layout_settings):
    render = TextRender(27, 7, text_layout_settings)
    node = load(rr.terminal("XXX"), lambda x: x)
    node.calculate_layout(text_layout_settings, LayoutContext(width=25, is_outer=True))
    node.render(
        render,
        RenderContext(
            pos=Vec(0, 3),
            reverse=False,
            start_connection_pos=Vec(0, 3),
            end_connection_pos=Vec(27, 3),
        ),
    )
    # fmt: off
    expected = (
        "                           \n"
        "                           \n"
        "┌─────┐                    \n"
        "┤ XXX ├────────────────────\n"
        "└─────┘                    \n"
        "                           \n"
        "                           \n"
    )
    # fmt: on
    assert render.to_string() == expected

    render = TextRender(27, 7, text_layout_settings)
    node = load(rr.terminal("XXX"), lambda x: x)
    node.calculate_layout(
        text_layout_settings,
        LayoutContext(
            width=25,
            is_outer=True,
            start_connection=ConnectionType.SPLIT,
            end_connection=ConnectionType.SPLIT,
        ),
    )
    node.render(
        render,
        RenderContext(
            pos=Vec(0, 3),
            reverse=False,
            start_connection_pos=Vec(0, 0),
            end_connection_pos=Vec(27, 6),
        ),
    )
    # fmt: off
    expected = (
       "╮                          \n"
       "↓                          \n"
       "│ ┌─────┐                  \n"
       "╰→┤ XXX ├────────────────→╮\n"
       "  └─────┘                 │\n"
       "                          ↓\n"
       "                          ╰\n"
    )
    # fmt: on
    assert render.to_string() == expected

    render = TextRender(27, 7, text_layout_settings)
    node = load(rr.terminal("XXX"), lambda x: x)
    node.calculate_layout(
        text_layout_settings,
        LayoutContext(
            width=25,
            is_outer=True,
            start_connection=ConnectionType.STACK,
            end_connection=ConnectionType.STACK,
        ),
    )
    node.render(
        render,
        RenderContext(
            pos=Vec(0, 3),
            reverse=False,
            start_connection_pos=Vec(1, 0),
            end_connection_pos=Vec(26, 6),
        ),
    )
    # fmt: off
    expected = (
       "╭                          \n"
       "↓                          \n"
       "│ ┌─────┐                  \n"
       "╰→┤ XXX ├────────────────→╮\n"
       "  └─────┘                 │\n"
       "                          ↓\n"
       "                          ╯\n"
       ""
    )
    # fmt: on
    assert render.to_string() == expected
