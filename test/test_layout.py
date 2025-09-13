# import syntax_diagrams as rr


# def test_seq_layout(text_layout_settings):
#     a = rr.terminal("node A")
#     b = rr.terminal("node B")
#     c = rr.terminal("node C")

#     # Straight line:
#     #
#     #  ┆  ┆                                ┆  ┆
#     #  ┆  ┌────────┐  ┌────────┐  ┌────────┐  ┆
#     #  ┆──┤ node A ├──┤ node B ├──┤ node C ├──┆
#     #  ┆  └────────┘  └────────┘  └────────┘  ┆
#     #  ┆  ┆                                ┆  ┆
#     # ►┆┈┈┆◄┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈►┆┈┈┆◄

#     seq = rr.sequence(a, b, c)._make_node_with_layout_info(100, text_layout_settings)

#     assert seq._width == 34
#     assert seq._height == 0
#     assert seq._up == 1
#     assert seq._down == 1
#     assert seq._margin_l == 2
#     assert seq._margin_r == 2

#     # No breaks:
#     #
#     #  ┆ ┆                        ┆ ┆
#     #  ┆ ┆ ┌────────┐  ┌────────┐ ┆ ┆
#     #  ┆───┤ node A ├──┤ node B ├─┐ ┆
#     #  ┆ ┆ └────────┘  └────────┘ │ ┆
#     #  ┆ ┆                        │ ┆
#     #  ┆ ┌────────────────────────┘ ┆
#     #  ┆ │                        ┆ ┆
#     #  ┆ │ ┌────────┐             ┆ ┆
#     #  ┆ └─┤ node C ├───────────────┆
#     #  ┆ ┆ └────────┘             ┆ ┆
#     #  ┆ ┆                        ┆ ┆
#     # ►┆┈┆◄┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈►┆┈┆◄

#     seq = rr.sequence(a, b, c)._make_node_with_layout_info(30, text_layout_settings)

#     assert seq._width == 26
#     assert seq._height == 6
#     assert seq._up == 1
#     assert seq._down == 1
#     assert seq._margin_l == 1
#     assert seq._margin_r == 1

#     # Soft break after A:
#     #
#     #  ┆ ┆                      ┆  ┆
#     #  ┆ ┆ ┌────────┐           ┆  ┆
#     #  ┆───┤ node A ├─┐         ┆  ┆
#     #  ┆ ┆ └────────┘ │         ┆  ┆
#     #  ┆ ┆            │         ┆  ┆
#     #  ┆ ┌────────────┘         ┆  ┆
#     #  ┆ │                      ┆  ┆
#     #  ┆ │ ┌────────┐  ┌────────┐  ┆
#     #  ┆ └─┤ node B ├──┤ node C ├──┆
#     #  ┆ ┆ └────────┘  └────────┘  ┆
#     #  ┆ ┆                      ┆  ┆
#     # ►┆┈┆◄┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈►┆┈┈┆◄

#     seq = rr.sequence(
#         a, b, c, linebreaks=[rr.LineBreak.SOFT, rr.LineBreak.NO_BREAK]
#     )._make_node_with_layout_info(30, text_layout_settings)

#     assert seq._width == 24
#     assert seq._height == 6
#     assert seq._up == 1
#     assert seq._down == 1
#     assert seq._margin_l == 1
#     assert seq._margin_r == 2

#     # Hard breaks:
#     #
#     #  ┆ ┆            ┆ ┆
#     #  ┆ ┆ ┌────────┐ ┆ ┆
#     #  ┆───┤ node A ├─┐ ┆
#     #  ┆ ┆ └────────┘ │ ┆
#     #  ┆ ┆            │ ┆
#     #  ┆ ┌────────────┘ ┆
#     #  ┆ │            ┆ ┆
#     #  ┆ │ ┌────────┐ ┆ ┆
#     #  ┆ └─┤ node B ├─┐ ┆
#     #  ┆ ┆ └────────┘ │ ┆
#     #  ┆ ┆            │ ┆
#     #  ┆ ┌────────────┘ ┆
#     #  ┆ │            ┆ ┆
#     #  ┆ │ ┌────────┐ ┆ ┆
#     #  ┆ └─┤ node C ├───┆
#     #  ┆ ┆ └────────┘ ┆ ┆
#     #  ┆ ┆            ┆ ┆
#     # ►┆┈┆◄┈┈┈┈┈┈┈┈┈┈►┆┈┆◄

#     seq = rr.sequence(
#         a, b, c, linebreaks=[rr.LineBreak.HARD, rr.LineBreak.HARD]
#     )._make_node_with_layout_info(100, text_layout_settings)

#     assert seq._width == 14
#     assert seq._height == 12
#     assert seq._up == 1
#     assert seq._down == 1
#     assert seq._margin_l == 1
#     assert seq._margin_r == 1

#     # Last node has big margin:
#     #
#     #  ┆    ┆                            ┆ ┆
#     #  ┆    ┆ ┌────────┐      ┌────────┐ ┆ ┆
#     #  ┆──────┤ node A ├──────┤ node B ├─┐ ┆
#     #  ┆    ┆ └────────┘      └────────┘ │ ┆
#     #  ┆    ┆                            │ ┆
#     #  ┆    ┌────────────────────────────┘ ┆
#     #  ┆    │                            ┆ ┆
#     #  ┆    │ ┌────────┐                 ┆ ┆
#     #  ┆    └─┤ node C ├───────────────────┆
#     #  ┆    ┆ └────────┘                 ┆ ┆
#     #  ┆    ┆                            ┆ ┆
#     # ►┆┈┈┈┈┆◄┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈►┆┈┆◄

#     text_layout_settings.horizontal_seq_separation = 6

#     seq = rr.sequence(a, b, c)._make_node_with_layout_info(35, text_layout_settings)

#     assert seq._width == 30
#     assert seq._height == 6
#     assert seq._up == 1
#     assert seq._down == 1
#     assert seq._margin_l == 4
#     assert seq._margin_r == 1
