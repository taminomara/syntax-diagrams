from __future__ import annotations

import traceback
import typing as _t

from flask import Flask, Response, request

import syntax_diagrams

app = Flask(__name__)

START_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Syntax Diagram Debug Viewer Backend</title>
</head>
<body>
    <h1>Syntax Diagram Debug Viewer Backend</h1>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            return render_diagram()
        except Exception:
            return dict(error=traceback.format_exc()), 500

    return START_PAGE


def render_diagram():
    data = request.get_json()
    try:
        diagram = data["diagram"]
        rawSettings = data["settings"]
        if rawSettings["render"] == "svg":
            # fmt: off
            settings = syntax_diagrams.SvgRenderSettings(
                max_width=rawSettings["svgMaxWidth"],
                reverse=rawSettings["reverse"],
                title=rawSettings["svgTitle"],
                description=rawSettings["svgDescription"],
                vertical_choice_separation_outer=rawSettings["svgVerticalChoiceSeparationOuter"],
                vertical_choice_separation=rawSettings["svgVerticalChoiceSeparation"],
                vertical_seq_separation_outer=rawSettings["svgVerticalSeqSeparationOuter"],
                vertical_seq_separation=rawSettings["svgVerticalSeqSeparation"],
                horizontal_seq_separation=rawSettings["svgHorizontalSeqSeparation"],
                end_class=syntax_diagrams.EndClass(rawSettings["endClass"]),
                arc_radius=rawSettings["svgArcRadius"],
                arc_margin=rawSettings["svgArcMargin"],
                arrow_style=syntax_diagrams.ArrowStyle(rawSettings["svgArrowStyle"]),
                arrow_length=rawSettings["svgArrowLength"],
                arrow_cross_length=rawSettings["svgArrowCrossLength"],
                terminal_horizontal_padding=rawSettings["svgTerminalHorizontalPadding"],
                terminal_vertical_padding=rawSettings["svgTerminalVerticalPadding"],
                terminal_radius=rawSettings["svgTerminalRadius"],
                non_terminal_horizontal_padding=rawSettings["svgNonTerminalHorizontalPadding"],
                non_terminal_vertical_padding=rawSettings["svgNonTerminalVerticalPadding"],
                non_terminal_radius=rawSettings["svgNonTerminalRadius"],
                comment_horizontal_padding=rawSettings["svgCommentHorizontalPadding"],
                comment_vertical_padding=rawSettings["svgCommentVerticalPadding"],
                comment_radius=rawSettings["svgCommentRadius"],
                group_vertical_padding=rawSettings["svgGroupVerticalPadding"],
                group_horizontal_padding=rawSettings["svgGroupHorizontalPadding"],
                group_vertical_margin=rawSettings["svgGroupVerticalMargin"],
                group_horizontal_margin=rawSettings["svgGroupHorizontalMargin"],
                group_radius=rawSettings["svgGroupRadius"],
                group_text_vertical_offset=rawSettings["svgGroupTextVerticalOffset"],
                group_text_horizontal_offset=rawSettings["svgGroupTextHorizontalOffset"],
                css_style=None,
                css_class="syntax-diagram",
            )
            # fmt: on
        else:
            # fmt: off
            settings = syntax_diagrams.TextRenderSettings(
                max_width=rawSettings["textMaxWidth"],
                reverse=rawSettings["reverse"],
                vertical_choice_separation_outer=rawSettings["textVerticalChoiceSeparationOuter"],
                vertical_choice_separation=rawSettings["textVerticalChoiceSeparation"],
                vertical_seq_separation_outer=rawSettings["textVerticalSeqSeparationOuter"],
                vertical_seq_separation=rawSettings["textVerticalSeqSeparation"],
                horizontal_seq_separation=rawSettings["textHorizontalSeqSeparation"],
                end_class=syntax_diagrams.EndClass(rawSettings["endClass"]),
                group_vertical_padding=rawSettings["textGroupVerticalPadding"],
                group_horizontal_padding=rawSettings["textGroupHorizontalPadding"],
                group_vertical_margin=rawSettings["textGroupVerticalMargin"],
                group_horizontal_margin=rawSettings["textGroupHorizontalMargin"],
                group_text_vertical_offset=rawSettings["textGroupTextVerticalOffset"],
                group_text_horizontal_offset=rawSettings["textGroupTextHorizontalOffset"],
            )
            # fmt: on
    except KeyError as e:
        return f"Unknown key {e}", 400

    try:
        if rawSettings["render"] == "svg":
            rendered = syntax_diagrams.render_svg(
                diagram,
                settings=_t.cast(syntax_diagrams.SvgRenderSettings, settings),
                _dump_debug_data=True,  # type: ignore
            )
        else:
            rendered = syntax_diagrams.render_text(
                diagram,
                settings=_t.cast(syntax_diagrams.TextRenderSettings, settings),
                _dump_debug_data=True,  # type: ignore
            )
    except syntax_diagrams.LoadingError as e:
        return str(e), 400

    return Response(rendered, content_type="application/json")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=9011)
