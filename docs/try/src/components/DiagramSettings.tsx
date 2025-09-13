import "./DiagramSettings.css";
import {
  type ChangeEvent,
  type PropsWithChildren,
  useEffect,
  useState,
} from "react";

export type Settings = {
  maxWidth: number;
  reverse: boolean;
  title: string;
  description: string;
  verticalChoiceSeparationOuter: number;
  verticalChoiceSeparation: number;
  verticalSeqSeparationOuter: number;
  verticalSeqSeparation: number;
  horizontalSeqSeparation: number;
  endClass: string;
  arcRadius: number;
  arcMargin: number;
  terminalPadding: number;
  terminalRadius: number;
  terminalHeight: number;
  nonTerminalPadding: number;
  nonTerminalRadius: number;
  nonTerminalHeight: number;
  commentPadding: number;
  commentRadius: number;
  commentHeight: number;
  groupVerticalPadding: number;
  groupHorizontalPadding: number;
  groupVerticalMargin: number;
  groupHorizontalMargin: number;
  groupRadius: number;
  groupTextHeight: number;
  groupTextVerticalOffset: number;
  groupTextHorizontalOffset: number;
};

export default function ({
  data,
  setData,
}: {
  data: Settings;
  setData: (data: Settings) => void;
}) {
  const updateStr =
    (name: keyof Settings) =>
    (e: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
      setData({ ...data, [name]: e.target.value });
    };
  const updateNum =
    (name: keyof Settings) => (e: ChangeEvent<HTMLInputElement>) => {
      setData({ ...data, [name]: Number(e.target.value) });
    };
  const updateBool =
    (name: keyof Settings) => (e: ChangeEvent<HTMLInputElement>) => {
      setData({ ...data, [name]: Number(e.target.checked) });
    };
  return (
    <>
      <div className="DiagramSettings">
        <div className="DiagramSettings-Group">
          <label htmlFor="DiagramSettings-MaxWidth">Width</label>
          <input
            id="DiagramSettings-MaxWidth"
            value={data.maxWidth}
            onChange={updateNum("maxWidth")}
            type="number"
            min={0}
            step={1}
          />
          <Help>
            Max width after which a sequence will be wrapped. This option is
            used to automatically convert sequences to stacks. Note that this is
            a suggestive option, there is no guarantee that the diagram will fit
            to its <code>Max Width</code>.
          </Help>
        </div>
        <div className="DiagramSettings-Group">
          <label htmlFor="DiagramSettings-Reverse">Reverse</label>
          <input
            id="DiagramSettings-Reverse"
            checked={data.reverse}
            onChange={updateBool("reverse")}
            type="checkbox"
          />
          <Help>If enabled, diagram is rendered right-to-left.</Help>
        </div>
      </div>
      <More>
        <div className="DiagramSettings">
          <div className="DiagramSettings-Group">
            <label htmlFor="DiagramSettings-Title">Title</label>
            <input
              id="DiagramSettings-Title"
              value={data.title}
              onChange={updateStr("title")}
            />
            <Help>
              Title text that will be added to <code>&lt;title&gt;</code>{" "}
              element and <code>aria-label</code> attribute.
            </Help>
          </div>
          <div className="DiagramSettings-Group">
            <label htmlFor="DiagramSettings-Description">Description</label>
            <input
              id="DiagramSettings-Description"
              value={data.description}
              onChange={updateStr("description")}
            />
            <Help>
              Title text that will be added to <code>&lt;desc&gt;</code>{" "}
              element.
            </Help>
          </div>
        </div>
        <h3>Spacing</h3>
        <div className="DiagramSettings">
          <div className="DiagramSettings-Group">
            <label htmlFor="DiagramSettings-VerticalChoiceSeparationOuter">
              Vertical Choice Margin Outer
            </label>
            <input
              id="DiagramSettings-VerticalChoiceSeparationOuter"
              value={data.verticalChoiceSeparationOuter}
              onChange={updateNum("verticalChoiceSeparationOuter")}
              type="number"
              min={0}
              step={1}
            />
            <Help>
              Vertical space between nodes in a <code>choice</code> block, if it
              contains another choice block.
            </Help>
          </div>
          <div className="DiagramSettings-Group">
            <label htmlFor="DiagramSettings-VerticalChoiceSeparation">
              Vertical Choice Margin
            </label>
            <input
              id="DiagramSettings-VerticalChoiceSeparation"
              value={data.verticalChoiceSeparation}
              onChange={updateNum("verticalChoiceSeparation")}
              type="number"
              min={0}
              step={1}
            />
            <Help>
              Vertical space between nodes in a <code>choice</code> block.
            </Help>
          </div>
          <div className="DiagramSettings-Group">
            <label htmlFor="DiagramSettings-VerticalSeqSeparationOuter">
              Vertical Seq Margin Outer
            </label>
            <input
              id="DiagramSettings-VerticalSeqSeparationOuter"
              value={data.verticalSeqSeparationOuter}
              onChange={updateNum("verticalSeqSeparationOuter")}
              type="number"
              min={0}
              step={1}
            />
            <Help>
              Vertical space between nodes in a <code>stack</code> block, if it
              appears outside of any choice block.
            </Help>
          </div>
          <div className="DiagramSettings-Group">
            <label htmlFor="DiagramSettings-VerticalSeqSeparation">
              Vertical Seq Margin
            </label>
            <input
              id="DiagramSettings-VerticalSeqSeparation"
              value={data.verticalSeqSeparation}
              onChange={updateNum("verticalSeqSeparation")}
              type="number"
              min={0}
              step={1}
            />
            <Help>
              Vertical space between nodes in a <code>stack</code> block.
            </Help>
          </div>
          <div className="DiagramSettings-Group">
            <label htmlFor="DiagramSettings-HorizontalSeqSeparation">
              Horizontal Seq Margin
            </label>
            <input
              id="DiagramSettings-HorizontalSeqSeparation"
              value={data.horizontalSeqSeparation}
              onChange={updateNum("horizontalSeqSeparation")}
              type="number"
              min={0}
              step={1}
            />
            <Help>Horizontal space between adjacent nodes.</Help>
          </div>
        </div>
        <h3>Style</h3>
        <div className="DiagramSettings">
          <div className="DiagramSettings-Group">
            <label htmlFor="DiagramSettings-EndClass">End Class</label>
            <select
              id="DiagramSettings-EndClass"
              value={data.endClass}
              onChange={updateStr("endClass")}
            >
              <option value="COMPLEX">Complex</option>
              <option value="SIMPLE">Simple</option>
            </select>
            <Help>Controls how diagram start and end look like.</Help>
          </div>
          <div className="DiagramSettings-Group">
            <label htmlFor="DiagramSettings-ArcRadius">Arc Radius</label>
            <input
              id="DiagramSettings-ArcRadius"
              value={data.arcRadius}
              onChange={updateNum("arcRadius")}
              type="number"
              min={0}
              step={1}
            />
            <Help>Arc radius of railroads. 10px by default.</Help>
          </div>
          <div className="DiagramSettings-Group">
            <label htmlFor="DiagramSettings-ArcMargin">Arc Margin</label>
            <input
              id="DiagramSettings-ArcMargin"
              value={data.arcMargin}
              onChange={updateNum("arcMargin")}
              type="number"
              min={0}
              step={1}
            />
            <Help>Margin around arcs.</Help>
          </div>
        </div>
        <h3>Nodes</h3>
        <div className="DiagramSettings">
          <div className="DiagramSettings-Group">
            <label htmlFor="DiagramSettings-TerminalPadding">
              Terminal Padding
            </label>
            <input
              id="DiagramSettings-TerminalPadding"
              value={data.terminalPadding}
              onChange={updateNum("terminalPadding")}
              type="number"
              min={0}
              step={1}
            />
            <Help>Horizontal padding around text in terminal nodes.</Help>
          </div>
          <div className="DiagramSettings-Group">
            <label htmlFor="DiagramSettings-TerminalRadius">
              Terminal Radius
            </label>
            <input
              id="DiagramSettings-TerminalRadius"
              value={data.terminalRadius}
              onChange={updateNum("terminalRadius")}
              type="number"
              min={0}
              step={1}
            />
            <Help>Border radius in terminal nodes.</Help>
          </div>
          <div className="DiagramSettings-Group">
            <label htmlFor="DiagramSettings-TerminalHeight">
              Terminal Height
            </label>
            <input
              id="DiagramSettings-TerminalHeight"
              value={data.terminalHeight}
              onChange={updateNum("terminalHeight")}
              type="number"
              min={0}
              step={1}
            />
            <Help>Height of a terminal node.</Help>
          </div>
          <div className="DiagramSettings-Group">
            <label htmlFor="DiagramSettings-NonTerminalPadding">
              Non Terminal Padding
            </label>
            <input
              id="DiagramSettings-NonTerminalPadding"
              value={data.nonTerminalPadding}
              onChange={updateNum("nonTerminalPadding")}
              type="number"
              min={0}
              step={1}
            />
            <Help>Horizontal padding around text in non-terminal nodes.</Help>
          </div>
          <div className="DiagramSettings-Group">
            <label htmlFor="DiagramSettings-NonTerminalRadius">
              Non Terminal Radius
            </label>
            <input
              id="DiagramSettings-NonTerminalRadius"
              value={data.nonTerminalRadius}
              onChange={updateNum("nonTerminalRadius")}
              type="number"
              min={0}
              step={1}
            />
            <Help>Border radius in non-terminal nodes.</Help>
          </div>
          <div className="DiagramSettings-Group">
            <label htmlFor="DiagramSettings-NonTerminalHeight">
              Non Terminal Height
            </label>
            <input
              id="DiagramSettings-NonTerminalHeight"
              value={data.nonTerminalHeight}
              onChange={updateNum("nonTerminalHeight")}
              type="number"
              min={0}
              step={1}
            />
            <Help>Height of a non-terminal node.</Help>
          </div>
          <div className="DiagramSettings-Group">
            <label htmlFor="DiagramSettings-CommentPadding">
              Comment Padding
            </label>
            <input
              id="DiagramSettings-CommentPadding"
              value={data.commentPadding}
              onChange={updateNum("commentPadding")}
              type="number"
              min={0}
              step={1}
            />
            <Help>Horizontal padding around text in comment nodes.</Help>
          </div>
          <div className="DiagramSettings-Group">
            <label htmlFor="DiagramSettings-CommentRadius">
              Comment Radius
            </label>
            <input
              id="DiagramSettings-CommentRadius"
              value={data.commentRadius}
              onChange={updateNum("commentRadius")}
              type="number"
              min={0}
              step={1}
            />
            <Help>Border radius in comment nodes.</Help>
          </div>
          <div className="DiagramSettings-Group">
            <label htmlFor="DiagramSettings-CommentHeight">
              Comment Height
            </label>
            <input
              id="DiagramSettings-CommentHeight"
              value={data.commentHeight}
              onChange={updateNum("commentHeight")}
              type="number"
              min={0}
              step={1}
            />
            <Help>Height of a comment node.</Help>
          </div>
        </div>
        <h3>Groups</h3>
        <div className="DiagramSettings">
          <div className="DiagramSettings-Group">
            <label htmlFor="DiagramSettings-GroupVerticalPadding">
              Group Vertical Padding
            </label>
            <input
              id="DiagramSettings-GroupVerticalPadding"
              value={data.groupVerticalPadding}
              onChange={updateNum("groupVerticalPadding")}
              type="number"
              min={0}
              step={1}
            />
            <Help>Vertical padding inside of group elements.</Help>
          </div>
          <div className="DiagramSettings-Group">
            <label htmlFor="DiagramSettings-GroupHorizontalPadding">
              Group Horizontal Padding
            </label>
            <input
              id="DiagramSettings-GroupHorizontalPadding"
              value={data.groupHorizontalPadding}
              onChange={updateNum("groupHorizontalPadding")}
              type="number"
              min={0}
              step={1}
            />
            <Help>Horizontal padding inside of group elements.</Help>
          </div>
          <div className="DiagramSettings-Group">
            <label htmlFor="DiagramSettings-GroupVerticalMargin">
              Group Vertical Margin
            </label>
            <input
              id="DiagramSettings-GroupVerticalMargin"
              value={data.groupVerticalMargin}
              onChange={updateNum("groupVerticalMargin")}
              type="number"
              min={0}
              step={1}
            />
            <Help>Vertical margin outside of group elements.</Help>
          </div>
          <div className="DiagramSettings-Group">
            <label htmlFor="DiagramSettings-GroupHorizontalMargin">
              Group Horizontal Margin
            </label>
            <input
              id="DiagramSettings-GroupHorizontalMargin"
              value={data.groupHorizontalMargin}
              onChange={updateNum("groupHorizontalMargin")}
              type="number"
              min={0}
              step={1}
            />
            <Help>Horizontal margin outside of group elements.</Help>
          </div>
          <div className="DiagramSettings-Group">
            <label htmlFor="DiagramSettings-GroupRadius">Group Radius</label>
            <input
              id="DiagramSettings-GroupRadius"
              value={data.groupRadius}
              onChange={updateNum("groupRadius")}
              type="number"
              min={0}
              step={1}
            />
            <Help>Border radius in groups.</Help>
          </div>
          <div className="DiagramSettings-Group">
            <label htmlFor="DiagramSettings-GroupTextHeight">
              Group Text Height
            </label>
            <input
              id="DiagramSettings-GroupTextHeight"
              value={data.groupTextHeight}
              onChange={updateNum("groupTextHeight")}
              type="number"
              min={0}
              step={1}
            />
            <Help>
              Height of the group text, added to the top vertical margin.
            </Help>
          </div>
          <div className="DiagramSettings-Group">
            <label htmlFor="DiagramSettings-GroupTextVerticalOffset">
              Group Text Vertical Offset
            </label>
            <input
              id="DiagramSettings-GroupTextVerticalOffset"
              value={data.groupTextVerticalOffset}
              onChange={updateNum("groupTextVerticalOffset")}
              type="number"
              min={0}
              step={1}
            />
            <Help>Offset from group rectangle to its heading.</Help>
          </div>
          <div className="DiagramSettings-Group">
            <label htmlFor="DiagramSettings-GroupTextHorizontalOffset">
              Group Text Horizontal Offset
            </label>
            <input
              id="DiagramSettings-GroupTextHorizontalOffset"
              value={data.groupTextHorizontalOffset}
              onChange={updateNum("groupTextHorizontalOffset")}
              type="number"
              min={0}
              step={1}
            />
            <Help>Offset from group rectangle to its heading.</Help>
          </div>
        </div>
      </More>
    </>
  );
}

function More(props: PropsWithChildren) {
  const [seen, setSeen] = useState(false);

  const messageClassName = seen
    ? "DiagramSettings-More-Message--Active"
    : "DiagramSettings-More-Message--Hidden";

  return (
    <div className="DiagramSettings-More">
      <a
        className="DiagramSettings-More-Toggle"
        title="Show more settings"
        onClick={() => {
          setSeen(!seen);
        }}
      >
        {seen ? "▼" : "▶"} More settings
      </a>
      <div className={`DiagramSettings-More-Message ${messageClassName}`}>
        {props.children}
      </div>
    </div>
  );
}

function Help(props: PropsWithChildren) {
  const [seenTarget, setSeenTarget] = useState(false);
  const [seen, setSeen] = useState(false);

  useEffect(() => {
    if (seen == seenTarget) {
      return;
    }
    if (seenTarget) {
      setSeen(true);
    } else {
      const handler = setTimeout(() => setSeen(false), 500);
      return () => clearTimeout(handler);
    }
  }, [seen, seenTarget]);

  const messageClassName = seen
    ? "DiagramSettings-Help-Message--Active"
    : "DiagramSettings-Help-Message--Hidden";

  return (
    <div className="DiagramSettings-Help">
      <a
        className="DiagramSettings-Help-Toggle"
        title="Show help"
        onClick={() => {
          setSeenTarget(!seen);
          setSeen(!seen);
        }}
        onMouseLeave={() => {
          setSeenTarget(false);
        }}
      >
        ?
      </a>
      <div
        className={`DiagramSettings-Help-Message ${messageClassName}`}
        onMouseEnter={() => {
          setSeenTarget(true);
        }}
        onMouseLeave={() => {
          setSeenTarget(false);
        }}
      >
        {props.children}
      </div>
    </div>
  );
}
