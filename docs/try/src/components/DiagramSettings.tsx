import type { Settings } from "../pyodideApi";
import styles from "./DiagramSettings.module.css";
import clsx from "clsx";
import {
  type ChangeEvent,
  type PropsWithChildren,
  useEffect,
  useState,
} from "react";

export function DiagramSettings({
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

  if (data.render === "svg")
    return (
      <div className={styles.DiagramSettings}>
        <div className={styles.DiagramSettings_Group}>
          <div className={styles.DiagramSettings_Item}>
            <label htmlFor="DiagramSettings_Render">Rendering engine</label>
            <select
              id="DiagramSettings_Render"
              className={styles.DiagramSettings_Input}
              value={data.render}
              onChange={updateStr("render")}
            >
              <option value="svg">SVG</option>
              <option value="text">Text</option>
            </select>
            <Help>Controls which rendering engine is used.</Help>
          </div>
        </div>
        <h3>Basic settings</h3>
        <div className={styles.DiagramSettings_Group}>
          <div className={styles.DiagramSettings_Item}>
            <label htmlFor="DiagramSettings_MaxWidth">Width</label>
            <input
              id="DiagramSettings_MaxWidth"
              className={styles.DiagramSettings_Input}
              value={data.svgMaxWidth}
              onChange={updateNum("svgMaxWidth")}
              type="number"
              min={0}
              step={1}
            />
            <Help>
              Max width after which a sequence will be wrapped. This option is
              used to automatically convert sequences to stacks. Note that this
              is a suggestive option, there is no guarantee that the diagram
              will fit to its <code>Max Width</code>.
            </Help>
          </div>
          <div className={styles.DiagramSettings_Group}>
            <div className={styles.DiagramSettings_Item}>
              <label htmlFor="DiagramSettings_EndClass">End Class</label>
              <select
                id="DiagramSettings_EndClass"
                className={styles.DiagramSettings_Input}
                value={data.endClass}
                onChange={updateStr("endClass")}
              >
                <option value="COMPLEX">Complex</option>
                <option value="SIMPLE">Simple</option>
              </select>
              <Help>Controls how diagram start and end look like.</Help>
            </div>
          </div>
          <div className={styles.DiagramSettings_Item}>
            <label htmlFor="DiagramSettings_Reverse">Reverse</label>
            <input
              id="DiagramSettings_Reverse"
              className={styles.DiagramSettings_Checkbox}
              checked={data.reverse}
              onChange={updateBool("reverse")}
              type="checkbox"
            />
            <Help>If enabled, diagram is rendered right-to-left.</Help>
          </div>
        </div>
        <More>
          <h3>Title</h3>
          <div className={styles.DiagramSettings_Group}>
            <div className={styles.DiagramSettings_Item}>
              <label htmlFor="DiagramSettings_Title">Title</label>
              <input
                id="DiagramSettings_Title"
                className={styles.DiagramSettings_Input}
                value={data.svgTitle}
                onChange={updateStr("svgTitle")}
              />
              <Help>
                Title text that will be added to <code>&lt;title&gt;</code>{" "}
                element and <code>aria-label</code> attribute.
              </Help>
            </div>
            <div className={styles.DiagramSettings_Item}>
              <label htmlFor="DiagramSettings_Description">Description</label>
              <input
                id="DiagramSettings_Description"
                className={styles.DiagramSettings_Input}
                value={data.svgDescription}
                onChange={updateStr("svgDescription")}
              />
              <Help>
                Title text that will be added to <code>&lt;desc&gt;</code>{" "}
                element.
              </Help>
            </div>
          </div>
          <h3>Spacing</h3>
          <div className={styles.DiagramSettings_Group}>
            <div className={styles.DiagramSettings_Item}>
              <label htmlFor="DiagramSettings_VerticalChoiceSeparationOuter">
                Vertical Choice Margin Outer
              </label>
              <input
                id="DiagramSettings_VerticalChoiceSeparationOuter"
                className={styles.DiagramSettings_Input}
                value={data.svgVerticalChoiceSeparationOuter}
                onChange={updateNum("svgVerticalChoiceSeparationOuter")}
                type="number"
                min={0}
                step={1}
              />
              <Help>
                Vertical space between nodes in a <code>choice</code> block, if
                it contains another choice block.
              </Help>
            </div>
            <div className={styles.DiagramSettings_Item}>
              <label htmlFor="DiagramSettings_VerticalChoiceSeparation">
                Vertical Choice Margin
              </label>
              <input
                id="DiagramSettings_VerticalChoiceSeparation"
                className={styles.DiagramSettings_Input}
                value={data.svgVerticalChoiceSeparation}
                onChange={updateNum("svgVerticalChoiceSeparation")}
                type="number"
                min={0}
                step={1}
              />
              <Help>
                Vertical space between nodes in a <code>choice</code> block.
              </Help>
            </div>
            <div className={styles.DiagramSettings_Item}>
              <label htmlFor="DiagramSettings_VerticalSeqSeparationOuter">
                Vertical Seq Margin Outer
              </label>
              <input
                id="DiagramSettings_VerticalSeqSeparationOuter"
                className={styles.DiagramSettings_Input}
                value={data.svgVerticalSeqSeparationOuter}
                onChange={updateNum("svgVerticalSeqSeparationOuter")}
                type="number"
                min={0}
                step={1}
              />
              <Help>
                Vertical space between nodes in a <code>stack</code> block, if
                it appears outside of any choice block.
              </Help>
            </div>
            <div className={styles.DiagramSettings_Item}>
              <label htmlFor="DiagramSettings_VerticalSeqSeparation">
                Vertical Seq Margin
              </label>
              <input
                id="DiagramSettings_VerticalSeqSeparation"
                className={styles.DiagramSettings_Input}
                value={data.svgVerticalSeqSeparation}
                onChange={updateNum("svgVerticalSeqSeparation")}
                type="number"
                min={0}
                step={1}
              />
              <Help>
                Vertical space between nodes in a <code>stack</code> block.
              </Help>
            </div>
            <div className={styles.DiagramSettings_Item}>
              <label htmlFor="DiagramSettings_HorizontalSeqSeparation">
                Horizontal Seq Margin
              </label>
              <input
                id="DiagramSettings_HorizontalSeqSeparation"
                className={styles.DiagramSettings_Input}
                value={data.svgHorizontalSeqSeparation}
                onChange={updateNum("svgHorizontalSeqSeparation")}
                type="number"
                min={0}
                step={1}
              />
              <Help>Horizontal space between adjacent nodes.</Help>
            </div>
          </div>
          <h3>Style</h3>

          <div className={styles.DiagramSettings_Group}>
            <div className={styles.DiagramSettings_Item}>
              <label htmlFor="DiagramSettings_ArrowStyle">Arrow Style</label>
              <select
                id="DiagramSettings_ArrowStyle"
                className={styles.DiagramSettings_Input}
                value={data.svgArrowStyle}
                onChange={updateStr("svgArrowStyle")}
              >
                <option value="NONE">None</option>
                <option value="TRIANGLE">Triangle</option>
                <option value="STEALTH">Stealth</option>
                <option value="BARB">Barb</option>
                <option value="HARPOON">Harpoon</option>
                <option value="HARPOON_UP">Harpoon Up</option>
              </select>
              <Help>Controls which rendering engine is used.</Help>
            </div>
            <div className={styles.DiagramSettings_Item}>
              <label htmlFor="DiagramSettings_ArrowLength">Arrow Length</label>
              <input
                id="DiagramSettings_ArrowLength"
                className={styles.DiagramSettings_Input}
                value={data.svgArrowLength}
                onChange={updateNum("svgArrowLength")}
                type="number"
                min={0}
                step={1}
              />
              <Help>Length of an arrow along its line.</Help>
            </div>
            <div className={styles.DiagramSettings_Item}>
              <label htmlFor="DiagramSettings_ArrowCrossLength">
                Arrow Cross Length
              </label>
              <input
                id="DiagramSettings_ArrowCrossLength"
                className={styles.DiagramSettings_Input}
                value={data.svgArrowCrossLength}
                onChange={updateNum("svgArrowCrossLength")}
                type="number"
                min={0}
                step={1}
              />
              <Help>Length of an arrow across its line.</Help>
            </div>
            <div className={styles.DiagramSettings_Item}>
              <label htmlFor="DiagramSettings_ArcRadius">Arc Radius</label>
              <input
                id="DiagramSettings_ArcRadius"
                className={styles.DiagramSettings_Input}
                value={data.svgArcRadius}
                onChange={updateNum("svgArcRadius")}
                type="number"
                min={0}
                step={1}
              />
              <Help>Arc radius of railroads. 10px by default.</Help>
            </div>
            <div className={styles.DiagramSettings_Item}>
              <label htmlFor="DiagramSettings_ArcMargin">Arc Margin</label>
              <input
                id="DiagramSettings_ArcMargin"
                className={styles.DiagramSettings_Input}
                value={data.svgArcMargin}
                onChange={updateNum("svgArcMargin")}
                type="number"
                min={0}
                step={1}
              />
              <Help>Margin around arcs.</Help>
            </div>
          </div>
          <h3>Nodes</h3>
          <div className={styles.DiagramSettings_Group}>
            <div className={styles.DiagramSettings_Item}>
              <label htmlFor="DiagramSettings_TerminalHorizontalPadding">
                Terminal Horizontal Padding
              </label>
              <input
                id="DiagramSettings_TerminalHorizontalPadding"
                className={styles.DiagramSettings_Input}
                value={data.svgTerminalHorizontalPadding}
                onChange={updateNum("svgTerminalHorizontalPadding")}
                type="number"
                min={0}
                step={1}
              />
              <Help>Horizontal padding around text in terminal nodes.</Help>
            </div>
            <div className={styles.DiagramSettings_Item}>
              <label htmlFor="DiagramSettings_TerminalVerticalPadding">
                Terminal Vertical Padding
              </label>
              <input
                id="DiagramSettings_TerminalVerticalPadding"
                className={styles.DiagramSettings_Input}
                value={data.svgTerminalVerticalPadding}
                onChange={updateNum("svgTerminalVerticalPadding")}
                type="number"
                min={0}
                step={1}
              />
              <Help>Vertical padding around text in terminal nodes.</Help>
            </div>
            <div className={styles.DiagramSettings_Item}>
              <label htmlFor="DiagramSettings_TerminalRadius">
                Terminal Radius
              </label>
              <input
                id="DiagramSettings_TerminalRadius"
                className={styles.DiagramSettings_Input}
                value={data.svgTerminalRadius}
                onChange={updateNum("svgTerminalRadius")}
                type="number"
                min={0}
                step={1}
              />
              <Help>Border radius in terminal nodes.</Help>
            </div>
            <div className={styles.DiagramSettings_Item}>
              <label htmlFor="DiagramSettings_NonTerminalHorizontalPadding">
                Non Terminal Horizontal Padding
              </label>
              <input
                id="DiagramSettings_NonTerminalHorizontalPadding"
                className={styles.DiagramSettings_Input}
                value={data.svgNonTerminalHorizontalPadding}
                onChange={updateNum("svgNonTerminalHorizontalPadding")}
                type="number"
                min={0}
                step={1}
              />
              <Help>Horizontal padding around text in non-terminal nodes.</Help>
            </div>
            <div className={styles.DiagramSettings_Item}>
              <label htmlFor="DiagramSettings_NonTerminalVerticalPadding">
                Non Terminal Vertical Padding
              </label>
              <input
                id="DiagramSettings_NonTerminalVerticalPadding"
                className={styles.DiagramSettings_Input}
                value={data.svgNonTerminalVerticalPadding}
                onChange={updateNum("svgNonTerminalVerticalPadding")}
                type="number"
                min={0}
                step={1}
              />
              <Help>Vertical padding around text in non-terminal nodes.</Help>
            </div>
            <div className={styles.DiagramSettings_Item}>
              <label htmlFor="DiagramSettings_NonTerminalRadius">
                Non Terminal Radius
              </label>
              <input
                id="DiagramSettings_NonTerminalRadius"
                className={styles.DiagramSettings_Input}
                value={data.svgNonTerminalRadius}
                onChange={updateNum("svgNonTerminalRadius")}
                type="number"
                min={0}
                step={1}
              />
              <Help>Border radius in non-terminal nodes.</Help>
            </div>
            <div className={styles.DiagramSettings_Item}>
              <label htmlFor="DiagramSettings_CommentHorizontalPadding">
                Comment Horizontal Padding
              </label>
              <input
                id="DiagramSettings_CommentHorizontalPadding"
                className={styles.DiagramSettings_Input}
                value={data.svgCommentHorizontalPadding}
                onChange={updateNum("svgCommentHorizontalPadding")}
                type="number"
                min={0}
                step={1}
              />
              <Help>Horizontal padding around text in comment nodes.</Help>
            </div>
            <div className={styles.DiagramSettings_Item}>
              <label htmlFor="DiagramSettings_CommentVerticalPadding">
                Comment Vertical Padding
              </label>
              <input
                id="DiagramSettings_CommentVerticalPadding"
                className={styles.DiagramSettings_Input}
                value={data.svgCommentVerticalPadding}
                onChange={updateNum("svgCommentVerticalPadding")}
                type="number"
                min={0}
                step={1}
              />
              <Help>Vertical padding around text in comment nodes.</Help>
            </div>
            <div className={styles.DiagramSettings_Item}>
              <label htmlFor="DiagramSettings_CommentRadius">
                Comment Radius
              </label>
              <input
                id="DiagramSettings_CommentRadius"
                className={styles.DiagramSettings_Input}
                value={data.svgCommentRadius}
                onChange={updateNum("svgCommentRadius")}
                type="number"
                min={0}
                step={1}
              />
              <Help>Border radius in comment nodes.</Help>
            </div>
          </div>
          <h3>Groups</h3>
          <div className={styles.DiagramSettings_Group}>
            <div className={styles.DiagramSettings_Item}>
              <label htmlFor="DiagramSettings_GroupVerticalPadding">
                Group Vertical Padding
              </label>
              <input
                id="DiagramSettings_GroupVerticalPadding"
                className={styles.DiagramSettings_Input}
                value={data.svgGroupVerticalPadding}
                onChange={updateNum("svgGroupVerticalPadding")}
                type="number"
                min={0}
                step={1}
              />
              <Help>Vertical padding inside of group elements.</Help>
            </div>
            <div className={styles.DiagramSettings_Item}>
              <label htmlFor="DiagramSettings_GroupHorizontalPadding">
                Group Horizontal Padding
              </label>
              <input
                id="DiagramSettings_GroupHorizontalPadding"
                className={styles.DiagramSettings_Input}
                value={data.svgGroupHorizontalPadding}
                onChange={updateNum("svgGroupHorizontalPadding")}
                type="number"
                min={0}
                step={1}
              />
              <Help>Horizontal padding inside of group elements.</Help>
            </div>
            <div className={styles.DiagramSettings_Item}>
              <label htmlFor="DiagramSettings_GroupVerticalMargin">
                Group Vertical Margin
              </label>
              <input
                id="DiagramSettings_GroupVerticalMargin"
                className={styles.DiagramSettings_Input}
                value={data.svgGroupVerticalMargin}
                onChange={updateNum("svgGroupVerticalMargin")}
                type="number"
                min={0}
                step={1}
              />
              <Help>Vertical margin outside of group elements.</Help>
            </div>
            <div className={styles.DiagramSettings_Item}>
              <label htmlFor="DiagramSettings_GroupHorizontalMargin">
                Group Horizontal Margin
              </label>
              <input
                id="DiagramSettings_GroupHorizontalMargin"
                className={styles.DiagramSettings_Input}
                value={data.svgGroupHorizontalMargin}
                onChange={updateNum("svgGroupHorizontalMargin")}
                type="number"
                min={0}
                step={1}
              />
              <Help>Horizontal margin outside of group elements.</Help>
            </div>
            <div className={styles.DiagramSettings_Item}>
              <label htmlFor="DiagramSettings_GroupRadius">Group Radius</label>
              <input
                id="DiagramSettings_GroupRadius"
                className={styles.DiagramSettings_Input}
                value={data.svgGroupRadius}
                onChange={updateNum("svgGroupRadius")}
                type="number"
                min={0}
                step={1}
              />
              <Help>Border radius in groups.</Help>
            </div>
            <div className={styles.DiagramSettings_Item}>
              <label htmlFor="DiagramSettings_GroupTextVerticalOffset">
                Group Text Vertical Offset
              </label>
              <input
                id="DiagramSettings_GroupTextVerticalOffset"
                className={styles.DiagramSettings_Input}
                value={data.svgGroupTextVerticalOffset}
                onChange={updateNum("svgGroupTextVerticalOffset")}
                type="number"
                min={0}
                step={1}
              />
              <Help>Offset from group rectangle to its heading.</Help>
            </div>
            <div className={styles.DiagramSettings_Item}>
              <label htmlFor="DiagramSettings_GroupTextHorizontalOffset">
                Group Text Horizontal Offset
              </label>
              <input
                id="DiagramSettings_GroupTextHorizontalOffset"
                className={styles.DiagramSettings_Input}
                value={data.svgGroupTextHorizontalOffset}
                onChange={updateNum("svgGroupTextHorizontalOffset")}
                type="number"
                min={0}
                step={1}
              />
              <Help>Offset from group rectangle to its heading.</Help>
            </div>
          </div>
        </More>
      </div>
    );
  else
    return (
      <div className={styles.DiagramSettings}>
        <div className={styles.DiagramSettings_Group}>
          <div className={styles.DiagramSettings_Item}>
            <label htmlFor="DiagramSettings_Render">Rendering engine</label>
            <select
              id="DiagramSettings_Render"
              className={styles.DiagramSettings_Input}
              value={data.render}
              onChange={updateStr("render")}
            >
              <option value="svg">SVG</option>
              <option value="text">Text</option>
            </select>
            <Help>Controls which rendering engine is used.</Help>
          </div>
        </div>
        <h3>Basic settings</h3>
        <div className={styles.DiagramSettings_Group}>
          <div className={styles.DiagramSettings_Item}>
            <label htmlFor="DiagramSettings_MaxWidth">Width</label>
            <input
              id="DiagramSettings_MaxWidth"
              className={styles.DiagramSettings_Input}
              value={data.textMaxWidth}
              onChange={updateNum("textMaxWidth")}
              type="number"
              min={0}
              step={1}
            />
            <Help>
              Max width after which a sequence will be wrapped. This option is
              used to automatically convert sequences to stacks. Note that this
              is a suggestive option, there is no guarantee that the diagram
              will fit to its <code>Max Width</code>.
            </Help>
          </div>
          <div className={styles.DiagramSettings_Group}>
            <div className={styles.DiagramSettings_Item}>
              <label htmlFor="DiagramSettings_EndClass">End Class</label>
              <select
                id="DiagramSettings_EndClass"
                className={styles.DiagramSettings_Input}
                value={data.endClass}
                onChange={updateStr("endClass")}
              >
                <option value="COMPLEX">Complex</option>
                <option value="SIMPLE">Simple</option>
              </select>
              <Help>Controls how diagram start and end look like.</Help>
            </div>
          </div>
          <div className={styles.DiagramSettings_Item}>
            <label htmlFor="DiagramSettings_Reverse">Reverse</label>
            <input
              id="DiagramSettings_Reverse"
              className={styles.DiagramSettings_Checkbox}
              checked={data.reverse}
              onChange={updateBool("reverse")}
              type="checkbox"
            />
            <Help>If enabled, diagram is rendered right-to-left.</Help>
          </div>
        </div>
        <More>
          <h3>Spacing</h3>
          <div className={styles.DiagramSettings_Group}>
            <div className={styles.DiagramSettings_Item}>
              <label htmlFor="DiagramSettings_VerticalChoiceSeparationOuter">
                Vertical Choice Margin Outer
              </label>
              <input
                id="DiagramSettings_VerticalChoiceSeparationOuter"
                className={styles.DiagramSettings_Input}
                value={data.textVerticalChoiceSeparationOuter}
                onChange={updateNum("textVerticalChoiceSeparationOuter")}
                type="number"
                min={1}
                step={1}
              />
              <Help>
                Vertical space between nodes in a <code>choice</code> block, if
                it contains another choice block.
              </Help>
            </div>
            <div className={styles.DiagramSettings_Item}>
              <label htmlFor="DiagramSettings_VerticalChoiceSeparation">
                Vertical Choice Margin
              </label>
              <input
                id="DiagramSettings_VerticalChoiceSeparation"
                className={styles.DiagramSettings_Input}
                value={data.textVerticalChoiceSeparation}
                onChange={updateNum("textVerticalChoiceSeparation")}
                type="number"
                min={1}
                step={1}
              />
              <Help>
                Vertical space between nodes in a <code>choice</code> block.
              </Help>
            </div>
            <div className={styles.DiagramSettings_Item}>
              <label htmlFor="DiagramSettings_VerticalSeqSeparationOuter">
                Vertical Seq Margin Outer
              </label>
              <input
                id="DiagramSettings_VerticalSeqSeparationOuter"
                className={styles.DiagramSettings_Input}
                value={data.textVerticalSeqSeparationOuter}
                onChange={updateNum("textVerticalSeqSeparationOuter")}
                type="number"
                min={1}
                step={1}
              />
              <Help>
                Vertical space between nodes in a <code>stack</code> block, if
                it appears outside of any choice block.
              </Help>
            </div>
            <div className={styles.DiagramSettings_Item}>
              <label htmlFor="DiagramSettings_VerticalSeqSeparation">
                Vertical Seq Margin
              </label>
              <input
                id="DiagramSettings_VerticalSeqSeparation"
                className={styles.DiagramSettings_Input}
                value={data.textVerticalSeqSeparation}
                onChange={updateNum("textVerticalSeqSeparation")}
                type="number"
                min={1}
                step={1}
              />
              <Help>
                Vertical space between nodes in a <code>stack</code> block.
              </Help>
            </div>
            <div className={styles.DiagramSettings_Item}>
              <label htmlFor="DiagramSettings_HorizontalSeqSeparation">
                Horizontal Seq Margin
              </label>
              <input
                id="DiagramSettings_HorizontalSeqSeparation"
                className={styles.DiagramSettings_Input}
                value={data.textHorizontalSeqSeparation}
                onChange={updateNum("textHorizontalSeqSeparation")}
                type="number"
                min={1}
                step={1}
              />
              <Help>Horizontal space between adjacent nodes.</Help>
            </div>
          </div>
          <h3>Groups</h3>
          <div className={styles.DiagramSettings_Group}>
            <div className={styles.DiagramSettings_Item}>
              <label htmlFor="DiagramSettings_GroupVerticalPadding">
                Group Vertical Padding
              </label>
              <input
                id="DiagramSettings_GroupVerticalPadding"
                className={styles.DiagramSettings_Input}
                value={data.textGroupVerticalPadding}
                onChange={updateNum("textGroupVerticalPadding")}
                type="number"
                min={0}
                step={1}
              />
              <Help>Vertical padding inside of group elements.</Help>
            </div>
            <div className={styles.DiagramSettings_Item}>
              <label htmlFor="DiagramSettings_GroupHorizontalPadding">
                Group Horizontal Padding
              </label>
              <input
                id="DiagramSettings_GroupHorizontalPadding"
                className={styles.DiagramSettings_Input}
                value={data.textGroupHorizontalPadding}
                onChange={updateNum("textGroupHorizontalPadding")}
                type="number"
                min={0}
                step={1}
              />
              <Help>Horizontal padding inside of group elements.</Help>
            </div>
            <div className={styles.DiagramSettings_Item}>
              <label htmlFor="DiagramSettings_GroupVerticalMargin">
                Group Vertical Margin
              </label>
              <input
                id="DiagramSettings_GroupVerticalMargin"
                className={styles.DiagramSettings_Input}
                value={data.textGroupVerticalMargin}
                onChange={updateNum("textGroupVerticalMargin")}
                type="number"
                min={0}
                step={1}
              />
              <Help>Vertical margin outside of group elements.</Help>
            </div>
            <div className={styles.DiagramSettings_Item}>
              <label htmlFor="DiagramSettings_GroupHorizontalMargin">
                Group Horizontal Margin
              </label>
              <input
                id="DiagramSettings_GroupHorizontalMargin"
                className={styles.DiagramSettings_Input}
                value={data.textGroupHorizontalMargin}
                onChange={updateNum("textGroupHorizontalMargin")}
                type="number"
                min={0}
                step={1}
              />
              <Help>Horizontal margin outside of group elements.</Help>
            </div>
            <div className={styles.DiagramSettings_Item}>
              <label htmlFor="DiagramSettings_GroupTextVerticalOffset">
                Group Text Vertical Offset
              </label>
              <input
                id="DiagramSettings_GroupTextVerticalOffset"
                className={styles.DiagramSettings_Input}
                value={data.textGroupTextVerticalOffset}
                onChange={updateNum("textGroupTextVerticalOffset")}
                type="number"
                min={-1}
                step={1}
              />
              <Help>Offset from group rectangle to its heading.</Help>
            </div>
            <div className={styles.DiagramSettings_Item}>
              <label htmlFor="DiagramSettings_GroupTextHorizontalOffset">
                Group Text Horizontal Offset
              </label>
              <input
                id="DiagramSettings_GroupTextHorizontalOffset"
                className={styles.DiagramSettings_Input}
                value={data.textGroupTextHorizontalOffset}
                onChange={updateNum("textGroupTextHorizontalOffset")}
                type="number"
                min={0}
                step={1}
              />
              <Help>Offset from group rectangle to its heading.</Help>
            </div>
          </div>
        </More>
      </div>
    );
}

function More(props: PropsWithChildren) {
  const [seen, setSeen] = useState(false);

  return (
    <div className={styles.DiagramSettings_More}>
      <a
        className={clsx(
          styles.DiagramSettings_MoreToggle,
          seen
            ? styles.DiagramSettings_MoreToggle__Active
            : styles.DiagramSettings_MoreToggle__Hidden,
        )}
        title="Show more settings"
        onClick={() => {
          setSeen(!seen);
        }}
      >
        More settings
      </a>
      <div
        className={clsx(
          styles.DiagramSettings_MoreContent,
          seen
            ? styles.DiagramSettings_MoreContent__Active
            : styles.DiagramSettings_MoreContent__Hidden,
        )}
      >
        {props.children}
      </div>
    </div>
  );
}

function Help(props: PropsWithChildren) {
  const [seenTarget, setSeenTarget] = useState(false);
  const [seen, setSeen] = useState(false);

  useEffect(() => {
    if (seen === seenTarget) {
      return;
    }
    if (seenTarget) {
      setSeen(true);
    } else {
      const handler = setTimeout(() => setSeen(false), 500);
      return () => clearTimeout(handler);
    }
  }, [seen, seenTarget]);

  return (
    <div className={styles.DiagramSettings_Help}>
      <a
        className={clsx(styles.DiagramSettings_HelpToggle, "button")}
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
        className={clsx(
          styles.DiagramSettings_HelpMessage,
          seen
            ? styles.DiagramSettings_HelpMessage__Active
            : styles.DiagramSettings_HelpMessage__Hidden,
        )}
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
