import neat_railroad_diagrams as rr

default_opts = rr._LayoutSettings(
    horizontal_seq_separation=2,
    vertical_choice_separation=0,
    vertical_seq_separation=2,
    arc_radius=0.5,
    arc_margin=1,
    terminal_padding=2,
    terminal_radius=0,
    terminal_height=2,
    non_terminal_padding=2,
    non_terminal_radius=0,
    non_terminal_height=2,
    comment_padding=2,
    comment_radius=0,
    comment_height=2,
    character_advance=1,
    wide_character_advance=2,
    marker_width=4,
    marker_projected_height=0,
    end_class=rr.EndClass.COMPLEX,
)


def test_line():
    render = rr._TextRender(5, 2, default_opts)
    render.line(1, 0).segment(3)
    render.line(4, 1).segment(-3)
    # fmt: off
    expected = (
        " ─── \n"
        " ─── \n"
    )
    # fmt: on
    assert render.to_string() == expected


def test_line_arrow():
    render = rr._TextRender(5, 8, default_opts)
    render.line(0, 0).segment(5, arrow_begin=True)
    render.line(0, 1, reverse=True).segment(5, arrow_begin=True)
    render.line(0, 2).segment(5, arrow_end=True)
    render.line(0, 3, reverse=True).segment(5, arrow_end=True)
    render.line(5, 4).segment(-5, arrow_begin=True)
    render.line(5, 5, reverse=True).segment(-5, arrow_begin=True)
    render.line(5, 6).segment(-5, arrow_end=True)
    render.line(5, 7, reverse=True).segment(-5, arrow_end=True)
    # fmt: off
    expected = (
        "→────\n"
        "←────\n"
        "────→\n"
        "────←\n"
        "────←\n"
        "────→\n"
        "←────\n"
        "→────\n"
    )
    # fmt: on
    assert render.to_string() == expected


def test_line_bend_reverse():
    render = rr._TextRender(5, 11, default_opts)
    render.line(3, 0).segment(1).bend_reverse(0, "w").segment(-3).bend_reverse(
        0, "e"
    ).segment(1)
    render.line(3, 1).segment(1).bend_reverse(1, "w").segment(-3).bend_reverse(
        -1, "e"
    ).segment(1)
    render.line(3, 4).segment(1).bend_reverse(-1, "w").segment(-3).bend_reverse(
        1, "e"
    ).segment(1)
    render.line(3, 5).segment(1).bend_reverse(2, "w").segment(-3).bend_reverse(
        -2, "e"
    ).segment(1)
    render.line(3, 10).segment(1).bend_reverse(-2, "w").segment(-3).bend_reverse(
        2, "e"
    ).segment(1)
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


def test_line_bend_forward():
    render = rr._TextRender(5, 11, default_opts)
    render.line(0, 0).segment(2).bend_forward(0).segment(2)
    render.line(0, 1).segment(2).bend_forward(1).segment(2)
    render.line(0, 4).segment(2).bend_forward(-1).segment(2)
    render.line(0, 5).segment(2).bend_forward(2).segment(2)
    render.line(0, 10).segment(2).bend_forward(-2).segment(2)
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


def test_node():
    render = rr._TextRender(27, 9, default_opts)

    node = rr.comment("fully automated")._make_node_with_layout_info(25, default_opts)
    node._render(render, 0, 1, False)

    node = rr.terminal("luxury")._make_node_with_layout_info(25, default_opts)
    node._render(render, 0, 4, False)

    node = rr.non_terminal("🌈gay space communism🌈")._make_node_with_layout_info(
        25, default_opts
    )
    node._render(render, 0, 7, False)

    # fmt: off
    expected = (
        "                           \n"
        "╴ fully automated ╶        \n"
        "                           \n"
        "┌────────┐                 \n"
        "┤ luxury ├                 \n"
        "└────────┘                 \n"
        "╔═════════════════════════╗\n"
        "╢ 🌈gay space communism🌈 ╟\n"
        "╚═════════════════════════╝\n"
    )
    # fmt: on
    assert render.to_string() == expected


def test_end_class():
    rendered = rr.render_text(
        rr.skip(),
        max_width=60,
        settings=rr.TextRenderSettings(
            end_class=rr.EndClass.SIMPLE,
        ),
    )
    # fmt: off
    expected = (
        "├──────┤\n"
    )
    # fmt: on
    assert rendered == expected

    rendered = rr.render_text(
        rr.skip(),
        max_width=60,
        settings=rr.TextRenderSettings(
            end_class=rr.EndClass.COMPLEX,
        ),
    )
    # fmt: off
    expected = (
        "├┼────┼┤\n"
    )
    # fmt: on
    assert rendered == expected


def test_seq():
    rendered = rr.render_text(
        rr.sequence(
            rr.terminal("A"),
            rr.non_terminal("B"),
        ),
        max_width=60,
    )
    # fmt: off
    expected = (
        "    ┌───┐  ╔═══╗    \n"
        "├┼──┤ A ├──╢ B ╟──┼┤\n"
        "    └───┘  ╚═══╝    \n"
    )
    # fmt: on
    assert rendered == expected

    rendered = rr.render_text(
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
        max_width=60,
    )

    # fmt: off
    expected = (
        "      ┌────┐  ╔══════╗  ┌───┐  ╔══════╗  ┌───┐      \n"
        "├┼────┤ if ├──╢ expr ╟──┤ { ├──╢ body ╟──┤ } ├─╮    \n"
        "      └────┘  ╚══════╝  └───┘  ╚══════╝  └───┘ │    \n"
        "                                               │    \n"
        "    ╭──────────────────────────────────────────╯    \n"
        "    │                                               \n"
        "    │ ┌──────┐  ┌───┐  ╔══════╗  ┌───┐              \n"
        "    ╰─┤ else ├──┤ { ├──╢ body ╟──┤ } ├────────────┼┤\n"
        "      └──────┘  └───┘  ╚══════╝  └───┘              \n"
    )
    # fmt: on
    assert rendered == expected

    rendered = rr.render_text(
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
        max_width=60,
        reverse=True,
    )

    # fmt: off
    expected = (
        "      ┌───┐  ╔══════╗  ┌───┐  ╔══════╗  ┌────┐      \n"
        "    ╭─┤ } ├──╢ body ╟──┤ { ├──╢ expr ╟──┤ if ├────┼┤\n"
        "    │ └───┘  ╚══════╝  └───┘  ╚══════╝  └────┘      \n"
        "    │                                               \n"
        "    ╰──────────────────────────────────────────╮    \n"
        "                                               │    \n"
        "              ┌───┐  ╔══════╗  ┌───┐  ┌──────┐ │    \n"
        "├┼────────────┤ } ├──╢ body ╟──┤ { ├──┤ else ├─╯    \n"
        "              └───┘  ╚══════╝  └───┘  └──────┘      \n"
    )
    # fmt: on
    assert rendered == expected


def test_choice():
    rendered = rr.render_text(rr.optional(rr.terminal("UwU")), max_width=60)
    # fmt: off
    expected = (
        "    ╭→───────→╮    \n"
        "    ↑ ┌─────┐ ↓    \n"
        "├┼──┴→┤ UwU ├→┴──┼┤\n"
        "      └─────┘      \n"
    )
    # fmt: on
    assert rendered == expected

    rendered = rr.render_text(
        rr.choice(
            rr.terminal("1: A *"),
            rr.non_terminal("2: B **"),
            rr.terminal("3: C ***"),
            default=1,
        ),
        max_width=60,
    )

    # fmt: off
    expected = (
        "      ┌────────┐        \n"
        "    ╭→┤ 1: A * ├──→╮    \n"
        "    │ └────────┘   │    \n"
        "    ↑ ╔═════════╗  ↓    \n"
        "├┼──┼→╢ 2: B ** ╟─→┼──┼┤\n"
        "    ↓ ╚═════════╝  ↑    \n"
        "    │ ┌──────────┐ │    \n"
        "    ╰→┤ 3: C *** ├→╯    \n"
        "      └──────────┘      \n"
    )
    # fmt: on
    assert rendered == expected

    rendered = rr.render_text(
        rr.choice(
            rr.terminal("1: A *"),
            rr.non_terminal("2: B **"),
            rr.terminal("3: C ***"),
            default=1,
        ),
        max_width=60,
        reverse=True,
    )

    # fmt: off
    expected = (
        "        ┌────────┐      \n"
        "    ╭←──┤ 1: A * ├←╮    \n"
        "    │   └────────┘ │    \n"
        "    ↓  ╔═════════╗ ↑    \n"
        "├┼──┼←─╢ 2: B ** ╟←┼──┼┤\n"
        "    ↑  ╚═════════╝ ↓    \n"
        "    │ ┌──────────┐ │    \n"
        "    ╰←┤ 3: C *** ├←╯    \n"
        "      └──────────┘      \n"
    )
    # fmt: on
    assert rendered == expected


def test_one_or_more():
    rendered = rr.render_text(
        rr.one_or_more(
            rr.terminal("UwU"),
        ),
        max_width=60,
    )

    # fmt: off
    expected = (
        "      ┌─────┐      \n"
        "├┼──┬→┤ UwU ├→┬──┼┤\n"
        "    ↑ └─────┘ ↓    \n"
        "    ╰←───────←╯    \n"
    )
    # fmt: on
    assert rendered == expected

    rendered = rr.render_text(
        rr.one_or_more(
            rr.terminal("UwU"),
            repeat=rr.terminal("R"),
        ),
        max_width=60,
    )

    # fmt: off
    expected = (
        "      ┌─────┐      \n"
        "├┼──┬→┤ UwU ├→┬──┼┤\n"
        "    ↑ └─────┘ ↓    \n"
        "    │  ┌───┐  │    \n"
        "    ╰←─┤ R ├─←╯    \n"
        "       └───┘       \n"
    )
    # fmt: on
    assert rendered == expected

    rendered = rr.render_text(
        rr.one_or_more(rr.terminal("UwU"), repeat=rr.optional(rr.terminal("OwO"))),
        max_width=60,
    )
    # fmt: off
    expected = (
        "      ┌─────┐      \n"
        "├┼──┬→┤ UwU ├→┬──┼┤\n"
        "    ↑ └─────┘ ↓    \n"
        "    ├←───────←┤    \n"
        "    │ ┌─────┐ │    \n"
        "    ╰←┤ OwO ├←╯    \n"
        "      └─────┘      \n"
    )
    # fmt: on
    assert rendered == expected

    rendered = rr.render_text(
        rr.one_or_more(rr.terminal("UwU"), repeat=rr.one_or_more(rr.terminal("B"))),
        max_width=60,
    )
    # fmt: off
    expected = (
        "       ┌─────┐       \n"
        "├┼──┬→─┤ UwU ├─→┬──┼┤\n"
        "    ↑  └─────┘  ↓    \n"
        "    │   ┌───┐   │    \n"
        "    ╰←┬←┤ B ├←┬←╯    \n"
        "      ↓ └───┘ ↑      \n"
        "      ╰→─────→╯      \n"
    )
    # fmt: on
    assert rendered == expected

    rendered = rr.render_text(
        rr.one_or_more(
            rr.terminal("UwU"),
            repeat=rr.one_or_more(
                rr.terminal("B"),
                repeat=rr.one_or_more(
                    rr.terminal("C"),
                ),
            ),
        ),
        max_width=60,
    )
    # fmt: off
    expected = (
        "         ┌─────┐         \n"
        "├┼──┬→───┤ UwU ├───→┬──┼┤\n"
        "    ↑    └─────┘    ↓    \n"
        "    │     ┌───┐     │    \n"
        "    ╰←┬←──┤ B ├──←┬←╯    \n"
        "      ↓   └───┘   ↑      \n"
        "      │   ┌───┐   │      \n"
        "      ╰→┬→┤ C ├→┬→╯      \n"
        "        ↑ └───┘ ↓        \n"
        "        ╰←─────←╯        \n"
    )
    # fmt: on
    assert rendered == expected
