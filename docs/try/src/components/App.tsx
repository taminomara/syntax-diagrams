import "./App.css";
import Diagram from "./Diagram";
import DiagramSettings from "./DiagramSettings";
import Editor from "./Editor";
import { useState } from "react";
import { Panel, PanelGroup, PanelResizeHandle } from "react-resizable-panels";

export default function () {
  const [data, setData] = useState({
    maxWidth: 600,
    reverse: false,
    title: "",
    description: "",
    verticalChoiceSeparationOuter: 9,
    verticalChoiceSeparation: 9,
    verticalSeqSeparationOuter: 18,
    verticalSeqSeparation: 18,
    horizontalSeqSeparation: 10,
    endClass: "COMPLEX",
    arcRadius: 10,
    arcMargin: 5,
    terminalPadding: 10,
    terminalRadius: 10,
    terminalHeight: 22,
    nonTerminalPadding: 10,
    nonTerminalRadius: 0,
    nonTerminalHeight: 22,
    commentPadding: 3,
    commentRadius: 0,
    commentHeight: 22,
    groupVerticalPadding: 10,
    groupHorizontalPadding: 10,
    groupVerticalMargin: 5,
    groupHorizontalMargin: 10,
    groupRadius: 0,
    groupTextHeight: 8,
    groupTextVerticalOffset: 5,
    groupTextHorizontalOffset: 10,
  });

  return (
    <PanelGroup direction="horizontal">
      <Panel defaultSize={40} minSize={20} className="App-Editor">
        <Editor />
      </Panel>
      <PanelResizeHandle className="App-ResizeHandle" />
      <Panel className="App-Main">
        <div className="App-Main-Content">
          <DiagramSettings data={data} setData={setData} />
          <hr />
          <Diagram code="" />
        </div>
      </Panel>
    </PanelGroup>
  );
}
