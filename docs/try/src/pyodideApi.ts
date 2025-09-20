import { type Message, type Response } from "./pyodideApiTypes";
import PyodideWorker from "./pyodideWorker?worker";
import yaml from "yaml";

export type Settings = {
  render: "svg" | "text";

  reverse: boolean;
  endClass: string;

  svgMaxWidth: number;
  svgTitle: string;
  svgDescription: string;
  svgVerticalChoiceSeparationOuter: number;
  svgVerticalChoiceSeparation: number;
  svgVerticalSeqSeparationOuter: number;
  svgVerticalSeqSeparation: number;
  svgHorizontalSeqSeparation: number;
  svgArrowStyle:
    | "NONE"
    | "TRIANGLE"
    | "STEALTH"
    | "BARB"
    | "HARPOON"
    | "HARPOON_UP";
  svgArrowLength: number;
  svgArrowCrossLength: number;
  svgArcRadius: number;
  svgArcMargin: number;
  svgTerminalHorizontalPadding: number;
  svgTerminalVerticalPadding: number;
  svgTerminalRadius: number;
  svgNonTerminalHorizontalPadding: number;
  svgNonTerminalVerticalPadding: number;
  svgNonTerminalRadius: number;
  svgCommentHorizontalPadding: number;
  svgCommentVerticalPadding: number;
  svgCommentRadius: number;
  svgGroupVerticalPadding: number;
  svgGroupHorizontalPadding: number;
  svgGroupVerticalMargin: number;
  svgGroupHorizontalMargin: number;
  svgGroupRadius: number;
  svgGroupTextVerticalOffset: number;
  svgGroupTextHorizontalOffset: number;

  textMaxWidth: number;
  textVerticalChoiceSeparationOuter: number;
  textVerticalChoiceSeparation: number;
  textVerticalSeqSeparationOuter: number;
  textVerticalSeqSeparation: number;
  textHorizontalSeqSeparation: number;
  textGroupVerticalPadding: number;
  textGroupHorizontalPadding: number;
  textGroupVerticalMargin: number;
  textGroupHorizontalMargin: number;
  textGroupTextVerticalOffset: number;
  textGroupTextHorizontalOffset: number;
};

export type Rendered = {
  svg?: string;
  text?: string;
  error?: string;
  debug_data?: unknown;
};

type InProgress = Record<
  number,
  {
    promise: Promise<string>;
    resolve: (result: string) => void;
    reject: (error: string) => void;
  }
>;

type WorkerState = {
  worker: Worker;
  inProgress: InProgress;
  lastId: number;
};

const CODE = `
from pyodide.ffi import JsNull

import syntax_diagrams


def convert_nulls(o):
    if isinstance(o, JsNull):
        return None
    elif isinstance(o, list):
        return [convert_nulls(k) for k in o]
    elif isinstance(o, dict):
        return {convert_nulls(k): convert_nulls(v) for k, v in o.items()}
    else:
        return o


if settings["render"] == "svg":
    rendered = syntax_diagrams.render_svg(
        convert_nulls(diagram),
        settings=syntax_diagrams.SvgRenderSettings(
            max_width=settings["svgMaxWidth"],
            reverse=settings["reverse"],
            title=settings["svgTitle"],
            description=settings["svgDescription"],
            vertical_choice_separation_outer=settings["svgVerticalChoiceSeparationOuter"],
            vertical_choice_separation=settings["svgVerticalChoiceSeparation"],
            vertical_seq_separation_outer=settings["svgVerticalSeqSeparationOuter"],
            vertical_seq_separation=settings["svgVerticalSeqSeparation"],
            horizontal_seq_separation=settings["svgHorizontalSeqSeparation"],
            end_class=syntax_diagrams.EndClass(settings["endClass"]),
            arc_radius=settings["svgArcRadius"],
            arc_margin=settings["svgArcMargin"],
            arrow_style=syntax_diagrams.ArrowStyle(settings["svgArrowStyle"]),
            arrow_length=settings["svgArrowLength"],
            arrow_cross_length=settings["svgArrowCrossLength"],
            terminal_horizontal_padding=settings["svgTerminalHorizontalPadding"],
            terminal_vertical_padding=settings["svgTerminalVerticalPadding"],
            terminal_radius=settings["svgTerminalRadius"],
            non_terminal_horizontal_padding=settings["svgNonTerminalHorizontalPadding"],
            non_terminal_vertical_padding=settings["svgNonTerminalVerticalPadding"],
            non_terminal_radius=settings["svgNonTerminalRadius"],
            comment_horizontal_padding=settings["svgCommentHorizontalPadding"],
            comment_vertical_padding=settings["svgCommentVerticalPadding"],
            comment_radius=settings["svgCommentRadius"],
            group_vertical_padding=settings["svgGroupVerticalPadding"],
            group_horizontal_padding=settings["svgGroupHorizontalPadding"],
            group_vertical_margin=settings["svgGroupVerticalMargin"],
            group_horizontal_margin=settings["svgGroupHorizontalMargin"],
            group_radius=settings["svgGroupRadius"],
            group_text_vertical_offset=settings["svgGroupTextVerticalOffset"],
            group_text_horizontal_offset=settings["svgGroupTextHorizontalOffset"],
            css_style=None,
            css_class="syntax-diagram",
        ),
        _dump_debug_data=True,
    )
else:
    rendered = syntax_diagrams.render_text(
        convert_nulls(diagram),
        settings=syntax_diagrams.TextRenderSettings(
            max_width=settings["textMaxWidth"],
            reverse=settings["reverse"],
            vertical_choice_separation_outer=settings["textVerticalChoiceSeparationOuter"],
            vertical_choice_separation=settings["textVerticalChoiceSeparation"],
            vertical_seq_separation_outer=settings["textVerticalSeqSeparationOuter"],
            vertical_seq_separation=settings["textVerticalSeqSeparation"],
            horizontal_seq_separation=settings["textHorizontalSeqSeparation"],
            end_class=syntax_diagrams.EndClass(settings["endClass"]),
            group_vertical_padding=settings["textGroupVerticalPadding"],
            group_horizontal_padding=settings["textGroupHorizontalPadding"],
            group_vertical_margin=settings["textGroupVerticalMargin"],
            group_horizontal_margin=settings["textGroupHorizontalMargin"],
            group_text_vertical_offset=settings["textGroupTextVerticalOffset"],
            group_text_horizontal_offset=settings["textGroupTextHorizontalOffset"],
        ),
        _dump_debug_data=True,
    )

rendered
`;

function makeWorker(): WorkerState {
  const inProgress: InProgress = {};

  const worker = new PyodideWorker();
  worker.addEventListener("message", (event: MessageEvent<Response>) => {
    const id = event.data.id;
    if (id === undefined || inProgress[id] === undefined) {
      return;
    }

    const { resolve, reject } = inProgress[id];

    if (event.data.result !== undefined) {
      resolve(event.data.result);
    } else {
      reject(event.data.error ?? "Unknown error");
    }
  });
  worker.addEventListener("error", (error) => {
    console.error(error);
  });
  worker.addEventListener("messageerror", (error) => {
    console.error(error);
  });
  return { worker, inProgress, lastId: 1 };
}

export let render: (data: string, settings: Settings) => Promise<Rendered>;

if (import.meta.env.DEV) {
  render = async function (
    data: string,
    settings: Settings,
  ): Promise<Rendered> {
    let diagram;
    try {
      diagram = yaml.parse(data) as unknown;
    } catch (error) {
      return { error: `Failed to parse YAML: ${String(error)}` };
    }

    const response = await fetch("/api/render", {
      method: "POST",
      body: JSON.stringify({ diagram, settings }),
      headers: { "Content-Type": "application/json" },
    });

    if (!response.ok) {
      const error =
        response.headers.get("Content-Type") === "application/json"
          ? ((await response.json()) as { error: string }).error
          : await response.text();
      return {
        error: `Failed to render diagram: error ${response.status}\n\n${error}`,
      };
    }

    const { rendered, debug_data } = (await response.json()) as {
      rendered: string;
      debug_data: string;
    };
    switch (settings.render) {
      case "svg":
        return { svg: rendered, debug_data };
      case "text":
        return { text: rendered, debug_data };
    }
  };
} else {
  const state = makeWorker();
  render = async function (
    data: string,
    settings: Settings,
  ): Promise<Rendered> {
    let diagram;
    try {
      diagram = yaml.parse(data) as unknown;
    } catch (error) {
      return { error: `Failed to parse YAML: ${String(error)}` };
    }

    const id = state.lastId++;

    let resolve, reject;
    const promise = new Promise<string>((resolve_, reject_) => {
      resolve = resolve_;
      reject = reject_;
    });

    if (resolve === undefined || reject === undefined) {
      throw new Error("unreachable");
    }

    state.inProgress[id] = { promise, resolve, reject };

    state.worker.postMessage({
      id,
      script: CODE,
      context: { diagram, settings },
    } satisfies Message);

    let rendered: string;
    let debug_data: unknown;
    try {
      const result = JSON.parse(await promise) as {
        rendered: string;
        debug_data: string;
      };
      rendered = result.rendered;
      debug_data = result.debug_data;
    } catch (error) {
      return { error: `Failed to render diagram: ${String(error)}` };
    }

    switch (settings.render) {
      case "svg":
        return { svg: rendered, debug_data };
      case "text":
        return { text: rendered, debug_data };
    }
  };
}
