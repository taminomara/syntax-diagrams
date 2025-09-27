import dataclasses

import pytest
import yaml

import syntax_diagrams as rr


def check_svg(
    diagram,
    reverse,
    regression,
    text_regression,
    svg_render_settings,
    text_render_settings,
):
    rendered = rr.render_svg(
        diagram,
        max_width=400,
        reverse=reverse,
        settings=svg_render_settings,
    )
    regression(rendered)


def check_svg_arc_margin(
    diagram,
    reverse,
    regression,
    text_regression,
    svg_render_settings,
    text_render_settings,
):
    svg_render_settings = dataclasses.replace(
        svg_render_settings,
        arc_radius=0,
        arc_margin=50,
        horizontal_seq_separation=0,
    )
    check_svg(
        diagram,
        reverse,
        regression,
        text_regression,
        svg_render_settings,
        text_render_settings,
    )


def check_svg_arc_radius(
    diagram,
    reverse,
    regression,
    text_regression,
    svg_render_settings,
    text_render_settings,
):
    svg_render_settings = dataclasses.replace(
        svg_render_settings,
        arc_radius=50,
        arc_margin=0,
        horizontal_seq_separation=0,
    )
    check_svg(
        diagram,
        reverse,
        regression,
        text_regression,
        svg_render_settings,
        text_render_settings,
    )


def check_svg_sep(
    diagram,
    reverse,
    regression,
    text_regression,
    svg_render_settings,
    text_render_settings,
):
    svg_render_settings = dataclasses.replace(
        svg_render_settings,
        arc_radius=0,
        arc_margin=0,
        horizontal_seq_separation=50,
    )
    check_svg(
        diagram,
        reverse,
        regression,
        text_regression,
        svg_render_settings,
        text_render_settings,
    )


def check_text(
    diagram,
    reverse,
    regression,
    text_regression,
    svg_render_settings,
    text_render_settings,
):
    rendered = rr.render_text(
        diagram,
        max_width=80,
        reverse=reverse,
        settings=text_render_settings,
    )
    text_regression(rendered)


_STACK = rr.stack(rr.terminal("A"), rr.terminal("B"))


@pytest.mark.parametrize(
    "check",
    [
        check_svg,
        # check_svg_arc_margin,
        # check_svg_arc_radius,
        # check_svg_sep,
        check_text,
    ],
    ids=[
        "svg",
        # "svg_arc_margin",
        # "svg_arc_radius",
        # "svg_sep",
        "txt",
    ],
)
@pytest.mark.parametrize(
    "reverse",
    [
        False,
        True,
    ],
    ids=[
        "ltr",
        "rtl",
    ],
)
@pytest.mark.parametrize(
    "diagram",
    [
        # Nodes
        pytest.param(
            rr.skip(),
            id="skip",
        ),
        pytest.param(
            rr.terminal("A"),
            id="terminal",
        ),
        pytest.param(
            rr.non_terminal("A"),
            id="non_terminal",
        ),
        pytest.param(
            rr.comment("A"),
            id="comment",
        ),
        pytest.param(
            rr.terminal("A\nB C\nD"),
            id="terminal_multiline",
        ),
        # Sequences
        pytest.param(
            rr.sequence(
                rr.skip(),
            ),
            id="sequence-empty",
        ),
        pytest.param(
            rr.sequence(
                rr.terminal("A"),
            ),
            id="sequence-1",
        ),
        pytest.param(
            rr.sequence(
                rr.terminal("A"),
                rr.non_terminal("B C D"),
                rr.terminal("E"),
            ),
            id="sequence-3",
        ),
        pytest.param(
            rr.stack(
                rr.terminal("A"),
                rr.non_terminal("B C D"),
                rr.terminal("E"),
            ),
            id="stack",
        ),
        pytest.param(
            rr.no_break(
                rr.terminal("A"),
                rr.non_terminal("B C D"),
                rr.terminal("E"),
            ),
            id="no_break-short",
        ),
        pytest.param(
            rr.no_break(
                rr.terminal("A very very long terminal"),
                rr.terminal("A very very long terminal"),
            ),
            id="no_break-long",
        ),
        pytest.param(
            rr.sequence(
                rr.terminal("Long terminal"),
                rr.terminal("A"),
                rr.terminal("B"),
                rr.terminal("C"),
                rr.terminal("Long terminal"),
                # rr.terminal("A very very long terminal"),
                # rr.terminal("A very very long terminal"),
                # rr.terminal("A very very long terminal"),
            ),
            id="sequence-break",
        ),
        pytest.param(
            rr.sequence(
                rr.terminal("Long terminal"),
                rr.terminal("A"),
                rr.terminal("B"),
                rr.terminal("C"),
                rr.terminal("Long terminal"),
                linebreaks=[
                    "DEFAULT",
                    "DEFAULT",
                    "SOFT",
                    "DEFAULT",
                ],
            ),
            id="sequence-soft-break",
        ),
        pytest.param(
            rr.sequence(
                rr.terminal("XX"),
                rr.choice(
                    rr.terminal("A"),
                    rr.terminal("B"),
                    rr.terminal("C"),
                    default=1,
                ),
                rr.terminal("YY"),
            ),
            id="sequence-up-down",
        ),
        pytest.param(
            rr.stack(
                rr.choice(
                    rr.terminal("A"),
                    rr.terminal("B"),
                    rr.terminal("C"),
                    default=1,
                ),
                rr.terminal("XX"),
                rr.terminal("YY"),
            ),
            id="stack-up-down-0",
        ),
        pytest.param(
            rr.stack(
                rr.terminal("XX"),
                rr.choice(
                    rr.terminal("A"),
                    rr.terminal("B"),
                    rr.terminal("C"),
                    default=1,
                ),
                rr.terminal("YY"),
            ),
            id="stack-up-down-1",
        ),
        pytest.param(
            rr.stack(
                rr.terminal("XX"),
                rr.terminal("YY"),
                rr.choice(
                    rr.terminal("A"),
                    rr.terminal("B"),
                    rr.terminal("C"),
                    default=1,
                ),
            ),
            id="stack-up-down-2",
        ),
        # Optionals
        pytest.param(
            rr.optional(
                rr.skip(),
            ),
            id="optional-empty",
        ),
        pytest.param(
            rr.optional(
                rr.terminal("A"),
            ),
            id="optional",
        ),
        pytest.param(
            rr.optional(
                rr.terminal("A"),
                skip=True,
            ),
            id="optional-skip",
        ),
        pytest.param(
            rr.optional(
                rr.terminal("A"),
                skip_bottom=True,
            ),
            id="optional-bottom",
        ),
        pytest.param(
            rr.optional(
                rr.terminal("A"),
                skip=True,
                skip_bottom=True,
            ),
            id="optional-bottom-skip",
        ),
        # Choices
        pytest.param(
            rr.choice(
                rr.skip(),
            ),
            id="choice-empty",
        ),
        pytest.param(
            rr.choice(
                rr.terminal("A"),
            ),
            id="choice-1",
        ),
        pytest.param(
            rr.choice(
                rr.terminal("A"),
                rr.terminal("B"),
                rr.terminal("C"),
            ),
            id="choice-3",
        ),
        pytest.param(
            rr.choice(
                rr.terminal("A"),
                rr.terminal("B"),
                rr.terminal("C"),
                default=1,
            ),
            id="choice-3-default-1",
        ),
        pytest.param(
            rr.choice(
                rr.terminal("A"),
                rr.terminal("B"),
                rr.terminal("C"),
                default=2,
            ),
            id="choice-3-default-2",
        ),
        pytest.param(
            rr.choice(
                rr.skip(),
                rr.terminal("A"),
                rr.skip(),
                rr.terminal("B"),
            ),
            id="choice-several-skips",
        ),
        pytest.param(
            rr.choice(
                rr.skip(),
                rr.terminal("A"),
                rr.skip(),
                rr.terminal("B"),
                default=2,
            ),
            id="choice-several-skips-default",
        ),
        pytest.param(
            rr.choice(
                rr.sequence(
                    rr.terminal("A"),
                    rr.choice(
                        rr.terminal("A"),
                        rr.terminal("B"),
                        rr.terminal("C"),
                        default=1,
                    ),
                    rr.terminal("B"),
                ),
                rr.terminal("XX"),
                rr.terminal("YY"),
            ),
            id="choice-up-down-0",
        ),
        pytest.param(
            rr.choice(
                rr.terminal("XX"),
                rr.sequence(
                    rr.terminal("A"),
                    rr.choice(
                        rr.terminal("A"),
                        rr.terminal("B"),
                        rr.terminal("C"),
                        default=1,
                    ),
                    rr.terminal("B"),
                ),
                rr.terminal("YY"),
            ),
            id="choice-up-down-1",
        ),
        pytest.param(
            rr.choice(
                rr.terminal("XX"),
                rr.terminal("YY"),
                rr.sequence(
                    rr.terminal("A"),
                    rr.choice(
                        rr.terminal("A"),
                        rr.terminal("B"),
                        rr.terminal("C"),
                        default=1,
                    ),
                    rr.terminal("B"),
                ),
                default=1,
            ),
            id="choice-up-down-2",
        ),
        pytest.param(
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
            id="choice-up-down-complex",
        ),
        pytest.param(
            rr.choice(
                rr.sequence(
                    rr.choice(
                        rr.terminal("A"),
                        rr.terminal("B"),
                    ),
                    rr.terminal("X"),
                ),
                rr.sequence(
                    rr.terminal("XXX"),
                    rr.choice(
                        rr.terminal("A"),
                        rr.terminal("B"),
                        default=1,
                    ),
                ),
            ),
            id="choice-tucking",
        ),
        # One or more
        pytest.param(
            rr.one_or_more(
                rr.skip(),
            ),
            id="one_or_more-empty",
        ),
        pytest.param(
            rr.one_or_more(rr.skip(), repeat=rr.terminal("A")),
            id="one_or_more-non-empty-repeat",
        ),
        pytest.param(
            rr.one_or_more(
                rr.terminal("A"),
            ),
            id="one_or_more-1",
        ),
        pytest.param(
            rr.one_or_more(
                rr.terminal("A"),
                repeat=rr.terminal("B"),
            ),
            id="one_or_more-1-repeat",
        ),
        pytest.param(
            rr.one_or_more(
                rr.sequence(
                    rr.terminal("A"),
                    rr.terminal("B"),
                    rr.terminal("C"),
                ),
            ),
            id="one_or_more-3",
        ),
        pytest.param(
            rr.one_or_more(
                rr.sequence(
                    rr.terminal("A"),
                    rr.optional(rr.terminal("B")),
                    rr.terminal("C"),
                ),
                repeat=rr.sequence(
                    rr.terminal("D"),
                    rr.optional(rr.terminal("E")),
                    rr.terminal("F"),
                ),
            ),
            id="one_or_more-3-repeat",
        ),
        pytest.param(
            rr.one_or_more(
                rr.non_terminal("arg"),
                repeat=rr.choice(
                    rr.terminal(","),
                    rr.terminal(";"),
                ),
            ),
            id="one_or_more-repeat-choice",
        ),
        pytest.param(
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
                ),
            ),
            id="one_or_more-repeat-one_or_more",
        ),
        pytest.param(
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
            id="one_or_more-up-down",
        ),
        pytest.param(
            rr.stack(
                rr.terminal("X"),
                rr.one_or_more(
                    rr.terminal("A"),
                    repeat=rr.stack(rr.terminal("B")),
                ),
                rr.terminal("Y"),
            ),
            id="one_or_more-stack-integration",
        ),
        # Zero or more
        pytest.param(
            rr.zero_or_more(
                rr.skip(),
            ),
            id="zero_or_more-empty",
        ),
        pytest.param(
            rr.zero_or_more(rr.skip(), repeat=rr.terminal("A")),
            id="zero_or_more-non-empty-repeat",
        ),
        pytest.param(
            rr.zero_or_more(
                rr.terminal("A"),
            ),
            id="zero_or_more-1",
        ),
        pytest.param(
            rr.zero_or_more(
                rr.terminal("A"),
                repeat=rr.terminal("B"),
            ),
            id="zero_or_more-1-repeat",
        ),
        pytest.param(
            rr.zero_or_more(
                rr.sequence(
                    rr.terminal("A"),
                    rr.terminal("B"),
                    rr.terminal("C"),
                ),
            ),
            id="zero_or_more-3",
        ),
        pytest.param(
            rr.zero_or_more(
                rr.sequence(
                    rr.terminal("A"),
                    rr.optional(rr.terminal("B")),
                    rr.terminal("C"),
                ),
                repeat=rr.sequence(
                    rr.terminal("D"),
                    rr.optional(rr.terminal("E")),
                    rr.terminal("F"),
                ),
            ),
            id="zero_or_more-3-repeat",
        ),
        pytest.param(
            rr.zero_or_more(
                rr.non_terminal("arg"),
                repeat=rr.choice(
                    rr.terminal(","),
                    rr.terminal(";"),
                ),
            ),
            id="zero_or_more-repeat-choice",
        ),
        pytest.param(
            rr.zero_or_more(
                rr.non_terminal("arg"),
                repeat=rr.sequence(
                    rr.zero_or_more(
                        rr.non_terminal("arg"),
                        repeat=rr.choice(
                            rr.terminal(","),
                            rr.terminal(";"),
                        ),
                    ),
                ),
            ),
            id="zero_or_more-repeat-zero_or_more",
        ),
        pytest.param(
            rr.zero_or_more(
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
            id="zero_or_more-up-down",
        ),
        pytest.param(
            rr.stack(
                rr.terminal("X"),
                rr.zero_or_more(
                    rr.terminal("A"),
                    repeat=rr.stack(rr.terminal("B")),
                ),
                rr.terminal("Y"),
            ),
            id="zero_or_more-stack-integration",
        ),
        # Optimizations
        pytest.param(
            rr.sequence(
                rr.optional(
                    rr.sequence(
                        rr.optional(rr.terminal("A")),
                        rr.terminal("B"),
                    )
                ),
                rr.terminal("C"),
            ),
            id="optional-opt-start-top",
        ),
        pytest.param(
            rr.sequence(
                rr.optional(
                    rr.sequence(
                        rr.optional(rr.terminal("A"), skip_bottom=True),
                        rr.terminal("B"),
                    ),
                    skip_bottom=True,
                ),
                rr.terminal("C"),
            ),
            id="optional-opt-start-bottom",
        ),
        pytest.param(
            rr.sequence(
                rr.terminal("A"),
                rr.optional(
                    rr.sequence(
                        rr.terminal("B"),
                        rr.optional(rr.terminal("C")),
                    )
                ),
            ),
            id="optional-opt-end-top",
        ),
        pytest.param(
            rr.sequence(
                rr.terminal("A"),
                rr.optional(
                    rr.sequence(
                        rr.terminal("B"),
                        rr.optional(rr.terminal("C"), skip_bottom=True),
                    ),
                    skip_bottom=True,
                ),
            ),
            id="optional-opt-end-bottom",
        ),
        pytest.param(
            rr.choice(
                rr.sequence(
                    rr.optional(rr.terminal("A")),
                    rr.terminal("B"),
                ),
                rr.skip(),
                rr.sequence(
                    rr.optional(rr.terminal("C")),
                    rr.terminal("D"),
                ),
                default=1,
            ),
            id="optional-opt-mid-start",
        ),
        pytest.param(
            rr.choice(
                rr.sequence(
                    rr.terminal("A"),
                    rr.optional(rr.terminal("B")),
                ),
                rr.skip(),
                rr.sequence(
                    rr.terminal("C"),
                    rr.optional(rr.terminal("D")),
                ),
                default=1,
            ),
            id="optional-opt-mid-end",
        ),
        pytest.param(
            rr.choice(
                rr.sequence(
                    rr.optional(rr.terminal("A")),
                    rr.terminal("B"),
                ),
                rr.skip(),
                rr.sequence(
                    rr.terminal("C"),
                    rr.optional(rr.terminal("D")),
                ),
                default=1,
            ),
            id="optional-opt-mid-mixed",
        ),
        pytest.param(
            rr.choice(
                rr.sequence(
                    rr.optional(rr.terminal("A")),
                    rr.optional(rr.terminal("B")),
                ),
                rr.terminal("X"),
                rr.skip(),
            ),
            id="optional-opt-mid-blocked",
        ),
        pytest.param(
            rr.optional(
                rr.sequence(
                    rr.optional(rr.terminal("A")),
                    rr.optional(rr.terminal("B")),
                ),
            ),
            id="optional-opt-opt",
        ),
        pytest.param(
            rr.stack(
                rr.choice(
                    rr.terminal("A"),
                    rr.sequence(
                        rr.terminal("B"),
                        rr.choice(
                            rr.terminal("C"),
                            rr.skip(),
                            rr.terminal("D"),
                        ),
                    ),
                ),
                rr.terminal("E"),
            ),
            id="optional-opt-complex",
        ),
        pytest.param(
            yaml.safe_load(
                r"""
                    - optional:
                      - "WITH"
                      - optional: "RECURSIVE"
                      - one_or_more:
                        - non_terminal: "common-table-expression"
                        repeat: ","
                    - one_or_more:
                      - group:
                        - choice:
                          -
                            - "SELECT"
                            - choice:
                              -
                              - "DISTINCT"
                              - "ALL"
                            - one_or_more:
                              - non_terminal: "result-column"
                              repeat: ","
                            - optional:
                              - "FROM"
                              - choice:
                                - one_or_more:
                                  - non_terminal: "table-or-subquery"
                                  repeat: ","
                                - non_terminal: "join-clause"
                            - optional:
                              - "WHERE"
                              - non_terminal: "expr"
                            - optional:
                              - "GROUP"
                              - "BY"
                              - one_or_more:
                                - non_terminal: "expr"
                                repeat: ","
                            - optional:
                              - "HAVING"
                              - non_terminal: "expr"
                            - optional:
                              - "WINDOW"
                              - one_or_more:
                                - non_terminal: "window-name"
                                - "AS"
                                - non_terminal: "window-defn"
                                repeat: ","
                          -
                            - "VALUES"
                            - one_or_more:
                              - "("
                              - one_or_more:
                                  non_terminal: "expr"
                                repeat: ","
                              - ")"
                              repeat: ","
                        text: select-core
                      repeat:
                        non_terminal: "compound-operator"
                    - optional:
                      - "ORDER"
                      - "BY"
                      - one_or_more:
                        - non_terminal: "ordering-term"
                        repeat: ","
                    - optional:
                      - "LIMIT"
                      - non_terminal: "expr"
                      - choice:
                        -
                        -
                          - "OFFSET"
                          - non_terminal: "expr"
                        -
                          - ","
                          - non_terminal: "expr"
            """
            ),
            id="complex",
        ),
        pytest.param(
            rr.sequence(
                rr.terminal("A"),
                rr.group(
                    rr.choice(
                        rr.terminal("X"),
                        rr.stack(
                            rr.terminal("B"),
                            rr.terminal("C"),
                        ),
                        rr.terminal("Y"),
                        default=1,
                    )
                ),
                rr.terminal("D"),
            ),
            id="group-no-title",
        ),
        pytest.param(
            rr.sequence(
                rr.terminal("A"),
                rr.group(
                    rr.choice(
                        rr.terminal("X"),
                        rr.stack(
                            rr.terminal("B"),
                            rr.terminal("C"),
                        ),
                        rr.terminal("Y"),
                        default=1,
                    ),
                    text="Group",
                ),
                rr.terminal("D"),
            ),
            id="group-title",
        ),
        pytest.param(
            rr.sequence(
                rr.terminal("A"),
                rr.group(
                    rr.terminal("B"),
                    text="Long group title",
                ),
                rr.terminal("C"),
            ),
            id="group-long-title",
        ),
        pytest.param(
            rr.sequence(
                rr.terminal("A"),
                rr.group(
                    rr.terminal("B"),
                    text="Long\ngroup\ntitle",
                ),
                rr.terminal("C"),
            ),
            id="group-multiline-title",
        ),
    ],
)
def test_render(
    check,
    diagram,
    reverse,
    regression,
    text_regression,
    svg_render_settings,
    text_render_settings,
):
    check(
        diagram,
        reverse,
        regression,
        text_regression,
        svg_render_settings,
        text_render_settings,
    )
