import type { Settings } from "../pyodideApi";
import styles from "./App.module.css";
import { Debug } from "./Debug";
import { Diagram } from "./Diagram";
import { DiagramSettings } from "./DiagramSettings";
import { Editor } from "./Editor";
import clsx from "clsx";
import deepEqual from "deep-equal";
import { useEffect, useLayoutEffect, useState } from "react";
import { Panel, PanelGroup, PanelResizeHandle } from "react-resizable-panels";
import { Tab, TabList, TabPanel, Tabs } from "react-tabs";

export type Theme = "light" | "dark";
type ThemeSelector = "light" | "dark" | "auto";

function nextTheme(theme: ThemeSelector): ThemeSelector {
  switch (theme) {
    case "light":
      return "dark";
    case "dark":
      return "auto";
    case "auto":
      return "light";
  }
}

const prefersDark = window.matchMedia("(prefers-color-scheme: dark)");

const defaultSettings: Settings = {
  render: "svg",

  reverse: false,
  endClass: "COMPLEX",

  svgMaxWidth: 600,
  svgTitle: "",
  svgDescription: "",
  svgVerticalChoiceSeparationOuter: 9,
  svgVerticalChoiceSeparation: 9,
  svgVerticalSeqSeparationOuter: 18,
  svgVerticalSeqSeparation: 18,
  svgHorizontalSeqSeparation: 10,
  svgArrowStyle: "NONE",
  svgArrowLength: 10,
  svgArrowCrossLength: 4,
  svgArcRadius: 10,
  svgArcMargin: 5,
  svgTerminalHorizontalPadding: 10,
  svgTerminalVerticalPadding: 3,
  svgTerminalRadius: 10,
  svgNonTerminalHorizontalPadding: 10,
  svgNonTerminalVerticalPadding: 3,
  svgNonTerminalRadius: 0,
  svgCommentHorizontalPadding: 3,
  svgCommentVerticalPadding: 3,
  svgCommentRadius: 0,
  svgGroupVerticalPadding: 10,
  svgGroupHorizontalPadding: 10,
  svgGroupVerticalMargin: 5,
  svgGroupHorizontalMargin: 10,
  svgGroupRadius: 0,
  svgGroupTextVerticalOffset: 0,
  svgGroupTextHorizontalOffset: 10,

  textMaxWidth: 80,
  textVerticalChoiceSeparationOuter: 1,
  textVerticalChoiceSeparation: 1,
  textVerticalSeqSeparationOuter: 1,
  textVerticalSeqSeparation: 1,
  textHorizontalSeqSeparation: 2,
  textGroupVerticalPadding: 1,
  textGroupHorizontalPadding: 2,
  textGroupVerticalMargin: 0,
  textGroupHorizontalMargin: 2,
  textGroupTextVerticalOffset: -1,
  textGroupTextHorizontalOffset: 2,
};

export function App() {
  const [theme, setTheme] = useState<ThemeSelector>(
    (localStorage.getItem("theme") as ThemeSelector) ?? "auto",
  );
  const [browserTheme, setBrowserTheme] = useState<Theme>(
    prefersDark.matches ? "dark" : "light",
  );

  useEffect(() => {
    localStorage.setItem("theme", theme);
  }, [theme]);
  useEffect(() => {
    const listener = () => {
      setBrowserTheme(prefersDark.matches ? "dark" : "light");
    };
    prefersDark.addEventListener("change", listener);
    return () => prefersDark.removeEventListener("change", listener);
  }, []);

  const effectiveTheme = theme === "auto" ? browserTheme : theme;
  useLayoutEffect(() => {
    document.body.dataset.theme = effectiveTheme;
  }, [effectiveTheme]);

  const [continuousRendering, setContinuousRendering] = useState(true);

  const [code, setCode] = useState<string | undefined>(undefined);
  const [targetCode, setTargetCode] = useState<string | undefined>();

  const [settings, setSettings] = useState(defaultSettings);
  const [targetSettings, setTargetSettings] = useState(defaultSettings);

  const [debugData, setDebugData] = useState<unknown>(null);
  const [mainElem, setMainElem] = useState<SVGSVGElement | null>(null);
  const [debugElem, setDebugElem] = useState<SVGSVGElement | null>(null);

  return (
    <PanelGroup className={styles.App} direction="horizontal">
      <Panel defaultSize={40} minSize={20} className={styles.App_SidePane}>
        <Tabs className={styles.App_Tabs} forceRenderTabPanel={true}>
          <TabList className={styles.App_TabList}>
            <Tab
              className={styles.App_Tab}
              selectedClassName={styles.App_Tab__Active}
            >
              Editor
            </Tab>
            <Tab
              className={styles.App_Tab}
              selectedClassName={styles.App_Tab__Active}
            >
              Settings
            </Tab>
            <Tab
              className={styles.App_Tab}
              selectedClassName={styles.App_Tab__Active}
            >
              Debug
            </Tab>
            <div className={clsx(styles.App_Tab, styles.App_Tab__Spacer)} />
            <a
              className={clsx(styles.App_Tab, styles.App_Tab__Link)}
              href={__CANONICAL_URL__ || "/"}
            >
              Docs
            </a>
            <a
              className={clsx(styles.App_Tab, styles.App_Tab__Link)}
              href="https://github.com/taminomara/syntax-diagrams/"
            >
              Repo
            </a>
            {__BUILD_VERSION__ !== "stable" ? <div className={clsx(styles.App_Tab, styles.App_Tab__Version)}>
              Version: {__BUILD_VERSION__}
            </div> : null}
            <button
              className={clsx(styles.App_Tab, styles.App_Tab__Icon)}
              onClick={() => {
                setTheme(nextTheme(theme));
              }}
            >
              <span className="Hidden">Toggle Theme</span>
              <svg aria-hidden="true" focusable="false">
                {theme === "dark" ? (
                  <use href="#svg-moon"></use>
                ) : theme === "light" ? (
                  <use href="#svg-sun"></use>
                ) : browserTheme == "light" ? (
                  <use href="#svg-sun-with-moon"></use>
                ) : (
                  <use href="#svg-moon-with-sun"></use>
                )}
              </svg>
            </button>
          </TabList>

          <TabPanel
            className={clsx(styles.App_TabPanel, styles.App_TabPanel__NoScroll)}
            selectedClassName={styles.App_TabPanel__Active}
          >
            <Editor
              setCode={(newCode) => {
                setCode(newCode);
                if (continuousRendering || code === undefined) {
                  setTargetCode(newCode);
                  setTargetSettings(settings);
                }
              }}
              theme={effectiveTheme}
            />
          </TabPanel>
          <TabPanel
            className={styles.App_TabPanel}
            selectedClassName={styles.App_TabPanel__Active}
          >
            <DiagramSettings
              data={settings}
              setData={(settings) => {
                setSettings(settings);
                if (continuousRendering) {
                  setTargetCode(code);
                  setTargetSettings(settings);
                }
              }}
            />
          </TabPanel>
          <TabPanel
            className={clsx(styles.App_TabPanel, styles.App_TabPanel__NoScroll)}
            selectedClassName={styles.App_TabPanel__Active}
          >
            <Debug main={mainElem} debug={debugElem} debugData={debugData} />
          </TabPanel>
        </Tabs>

        <div className={styles.App_RunPanel}>
          <div className={styles.App_RunPanelInputGroup}>
            <label htmlFor="App_ContinuousRenderingButton">
              Continuous rendering
            </label>
            <input
              id="App_ContinuousRenderingButton"
              type="checkbox"
              checked={continuousRendering}
              onChange={(event) => {
                setContinuousRendering(event.target.checked);
                if (event.target.checked) {
                  setTargetCode(code);
                  setTargetSettings(settings);
                }
              }}
            ></input>
          </div>
          <button
            onClick={() => {
              setTargetCode(code);
              setTargetSettings(settings);
            }}
            className={clsx(
              targetCode !== code || !deepEqual(settings, targetSettings)
                ? "accent"
                : null,
            )}
          >
            Render
          </button>
        </div>
      </Panel>
      <PanelResizeHandle className="ResizeHandle ResizeHandle__Vertical" />
      <Panel minSize={20} className={styles.App_MainPane}>
        <div className={styles.App_MainPaneContent}>
          <Diagram
            code={targetCode ?? ""}
            settings={targetSettings}
            continuousRendering={continuousRendering}
            setMainElem={setMainElem}
            setDebugElem={setDebugElem}
            setDebugData={setDebugData}
          />
        </div>
      </Panel>
    </PanelGroup>
  );
}
