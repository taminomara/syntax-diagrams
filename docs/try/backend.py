from __future__ import annotations
import typing as _t

from flask import Flask, request, Response

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
        data = request.get_json()
        try:
            diagram = data["diagram"]
            rawSettings = data["settings"]
            if rawSettings["render"] == "svg":
                settings = syntax_diagrams.SvgRenderSettings(
                    max_width=rawSettings["svgMaxWidth"],
                    reverse=rawSettings["reverse"],
                    title=rawSettings["svgTitle"],
                    description=rawSettings["svgDescription"],
                    vertical_choice_separation_outer=rawSettings[
                        "svgVerticalChoiceSeparationOuter"
                    ],
                    vertical_choice_separation=rawSettings[
                        "svgVerticalChoiceSeparation"
                    ],
                    vertical_seq_separation_outer=rawSettings[
                        "svgVerticalSeqSeparationOuter"
                    ],
                    vertical_seq_separation=rawSettings["svgVerticalSeqSeparation"],
                    horizontal_seq_separation=rawSettings["svgHorizontalSeqSeparation"],
                    end_class=syntax_diagrams.EndClass(rawSettings["endClass"]),
                    arc_radius=rawSettings["svgArcRadius"],
                    arc_margin=rawSettings["svgArcMargin"],
                    terminal_padding=rawSettings["svgTerminalPadding"],
                    terminal_radius=rawSettings["svgTerminalRadius"],
                    terminal_height=rawSettings["svgTerminalHeight"],
                    non_terminal_padding=rawSettings["svgNonTerminalPadding"],
                    non_terminal_radius=rawSettings["svgNonTerminalRadius"],
                    non_terminal_height=rawSettings["svgNonTerminalHeight"],
                    comment_padding=rawSettings["svgCommentPadding"],
                    comment_radius=rawSettings["svgCommentRadius"],
                    comment_height=rawSettings["svgCommentHeight"],
                    group_vertical_padding=rawSettings["svgGroupVerticalPadding"],
                    group_horizontal_padding=rawSettings["svgGroupHorizontalPadding"],
                    group_vertical_margin=rawSettings["svgGroupVerticalMargin"],
                    group_horizontal_margin=rawSettings["svgGroupHorizontalMargin"],
                    group_radius=rawSettings["svgGroupRadius"],
                    group_text_height=rawSettings["svgGroupTextHeight"],
                    group_text_vertical_offset=rawSettings[
                        "svgGroupTextVerticalOffset"
                    ],
                    group_text_horizontal_offset=rawSettings[
                        "svgGroupTextHorizontalOffset"
                    ],
                    css_style=None,
                    css_class="syntax-diagram",
                )
            else:
                settings = syntax_diagrams.TextRenderSettings(
                    max_width=rawSettings["textMaxWidth"],
                    reverse=rawSettings["reverse"],
                    vertical_choice_separation_outer=rawSettings[
                        "textVerticalChoiceSeparationOuter"
                    ],
                    vertical_choice_separation=rawSettings[
                        "textVerticalChoiceSeparation"
                    ],
                    vertical_seq_separation_outer=rawSettings[
                        "textVerticalSeqSeparationOuter"
                    ],
                    vertical_seq_separation=rawSettings["textVerticalSeqSeparation"],
                    horizontal_seq_separation=rawSettings[
                        "textHorizontalSeqSeparation"
                    ],
                    end_class=syntax_diagrams.EndClass(rawSettings["endClass"]),
                    group_vertical_padding=rawSettings["textGroupVerticalPadding"],
                    group_horizontal_padding=rawSettings["textGroupHorizontalPadding"],
                    group_vertical_margin=rawSettings["textGroupVerticalMargin"],
                    group_horizontal_margin=rawSettings["textGroupHorizontalMargin"],
                    group_text_height=rawSettings["textGroupTextHeight"],
                    group_text_vertical_offset=rawSettings[
                        "textGroupTextVerticalOffset"
                    ],
                    group_text_horizontal_offset=rawSettings[
                        "textGroupTextHorizontalOffset"
                    ],
                )
        except KeyError as e:
            return f"Unknown key {e}", 400

        try:
            if rawSettings["render"] == "svg":
                rendered = syntax_diagrams.render_svg(
                    diagram,
                    settings=_t.cast(syntax_diagrams.SvgRenderSettings, settings),
                    _dump_debug_data=True,
                )
            else:
                rendered = syntax_diagrams.render_text(
                    diagram,
                    settings=_t.cast(syntax_diagrams.TextRenderSettings, settings),
                )
        except syntax_diagrams.LoadingError as e:
            return str(e), 400

        return Response(rendered, mimetype="image/svg+xml")

    return START_PAGE


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=9011)
