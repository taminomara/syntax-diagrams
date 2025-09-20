import { type Rendered, type Settings, render } from "../pyodideApi";
import "./Diagram.css";
import styles from "./Diagram.module.css";
import clsx from "clsx";
import { type RefCallback, useEffect, useMemo, useRef, useState } from "react";

export function Diagram({
  code,
  settings,
  continuousRendering,
  setMainElem,
  setDebugElem,
  setDebugData,
}: {
  code: string;
  settings: Settings;
  continuousRendering: boolean;
  setMainElem: RefCallback<SVGSVGElement>;
  setDebugElem: RefCallback<SVGSVGElement>;
  setDebugData: RefCallback<unknown>;
}) {
  const [rendered, setRendered] = useState<Rendered>({});
  const timeout = useRef<NodeJS.Timeout | undefined>(undefined);

  useEffect(() => {
    clearTimeout(timeout.current);
    timeout.current = setTimeout(
      () => {
        timeout.current = undefined;
        render(code, settings).then(setRendered).catch(console.error);
      },
      continuousRendering ? 150 : 0,
    );
  }, [code, settings, continuousRendering]);

  useEffect(
    () => setDebugData(rendered.debug_data),
    [setDebugData, rendered.debug_data],
  );

  const [mainElem, debugElem] = useMemo(() => {
    if (rendered.svg) {
      const mainDiv = document.createElement("div");
      mainDiv.innerHTML = rendered.svg;
      const mainElem = mainDiv.querySelector("svg");

      const debugDiv = document.createElement("div");
      debugDiv.innerHTML = rendered.svg;
      const debugElem = debugDiv.querySelector("svg");

      return [mainElem, debugElem];
    } else {
      return [null, null];
    }
  }, [rendered.svg]);

  const mainElemCurrent = useRef<SVGSVGElement>(null);
  const debugElemCurrent = useRef<SVGSVGElement>(null);

  if (rendered.error) {
    return (
      <div className={styles.Diagram}>
        <h2>Error</h2>
        <pre>{rendered.error}</pre>
      </div>
    );
  } else if (rendered.svg) {
    return (
      <div className={styles.Diagram}>
        <div
          className={clsx(styles.Diagram_Main, "DebugHighlightMain")}
          ref={(div) => {
            if (mainElemCurrent.current === mainElem) {
              return;
            }

            mainElemCurrent.current = mainElem;

            if (div && mainElem) {
              div.replaceChildren(mainElem);
            }
            setMainElem(mainElem);
          }}
        />
        <div
          className={clsx(styles.Diagram_Debug, "DebugHighlightOverlay")}
          ref={(div) => {
            if (debugElemCurrent.current === debugElem) {
              return;
            }

            debugElemCurrent.current = debugElem;

            if (div && debugElem) {
              div.replaceChildren(debugElem);
            }
            setDebugElem(debugElem);
          }}
        />
      </div>
    );
  } else if (rendered.text) {
    return (
      <div className={styles.Diagram}>
        <pre>{rendered.text}</pre>
      </div>
    );
  } else {
    return (
      <div className={styles.Diagram}>
        <p>Preparing Python interpreter...</p>
      </div>
    );
  }
}
