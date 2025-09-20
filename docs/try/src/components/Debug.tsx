import styles from "./Debug.module.css";
import clsx from "clsx";
import { useLayoutEffect, useMemo, useRef, useState } from "react";
import { Panel, PanelGroup, PanelResizeHandle } from "react-resizable-panels";

export function Debug({
  main,
  debug,
  debugData,
}: {
  main: SVGSVGElement | null;
  debug: SVGSVGElement | null;
  debugData: unknown;
}) {
  if (main === null || debug === null) {
    return (
      <div className={styles.Debug}>
        <div className={styles.Debug_TreePane}>
          Debug view is not available.
        </div>
      </div>
    );
  } else {
    return <DebugImpl main={main} debug={debug} rawDebugData={debugData} />;
  }
}

function DebugImpl({
  main,
  debug,
  rawDebugData,
}: {
  main: SVGSVGElement;
  debug: SVGSVGElement;
  rawDebugData: unknown;
}) {
  const [debugData, debugDataById] = useMemo(() => {
    return prepareDebugData(rawDebugData);
  }, [rawDebugData]);

  const [selected, setSelected] = useState({ id: "", needScroll: false });
  const [hovered, setHovered] = useState("");

  useLayoutEffect(() => {
    const elems: Element[] = [];
    for (const svg of [main, debug]) {
      let elem;
      if (hovered) {
        elem = svg.querySelector(`g[data-dbg-id="${hovered}"]`);
      } else if (selected.id) {
        elem = svg.querySelector(`g[data-dbg-id="${selected.id}"]`);
      }
      if (elem) {
        elem.classList.add("DebugHighlight");
        elems.push(elem);
      }
    }
    return () => {
      elems.forEach((elem) => elem.classList.remove("DebugHighlight"));
    };
  }, [selected, hovered, main, debug]);

  useLayoutEffect(() => {
    if (selected.id && selected.needScroll) {
      const elem = main.querySelector(`g[data-dbg-id="${selected.id}"]`);
      if (elem) {
        elem.scrollIntoView({ behavior: "smooth" });
      }
    }
  }, [selected, main]);

  return (
    <PanelGroup direction="vertical" className={styles.Debug}>
      <Panel defaultSize={70} minSize={20} className={styles.Debug_TreePane}>
        {debugData.map((data) => (
          <DebugItem
            data={data}
            key={data.id}
            selected={selected}
            setSelected={setSelected}
            setHovered={setHovered}
          />
        ))}
      </Panel>
      <PanelResizeHandle className="ResizeHandle ResizeHandle__Horizontal" />
      <Panel minSize={20} className={styles.Debug_DetailsPane}>
        {selected.id ? (
          <ItemInfo
            data={debugDataById[selected.id]?.data}
            setHovered={setHovered}
            setSelected={setSelected}
          />
        ) : (
          <span>Select an item to view its debug data.</span>
        )}
      </Panel>
    </PanelGroup>
  );
}

type DebugItemData = {
  id: string;
  index: number;
  name: string;
  children: DebugItemData[];
  data: Record<string, unknown>;
};

function prepareDebugData(
  data: unknown,
): [DebugItemData[], Record<string, DebugItemData>] {
  const result: DebugItemData[] = [];
  const itemsById: Record<string, DebugItemData> = {};

  if (typeof data !== "object") {
    return [result, itemsById];
  }

  for (const id in data) {
    const datum = (
      data as Record<
        string,
        {
          id: string;
          index: number;
          name: string;
          parent?: string;
          data: Record<string, unknown>;
        }
      >
    )[id];

    const item: DebugItemData = {
      id,
      index: datum["index"],
      name: datum["name"],
      children: itemsById[id]?.children ?? [],
      data: datum["data"],
    };

    itemsById[id] = item;

    const parentId = datum["parent"];
    if (parentId) {
      let parent = itemsById[parentId];
      if (!parent) {
        parent = itemsById[parentId] = {
          id: parentId,
          index: 0,
          name: "??",
          children: [],
          data: {},
        };
      }
      parent.children.push(item);
    } else {
      result.push(item);
    }
  }

  sortDebugData(result);

  return [result, itemsById];
}

function sortDebugData(data: DebugItemData[]) {
  data.sort((a, b) => a.index - b.index);
  for (const item of data) {
    sortDebugData(item.children);
  }
}

function DebugItem({
  data,
  selected,
  setSelected,
  setHovered,
}: {
  data: DebugItemData;
  selected: { id: string; needScroll: boolean };
  setSelected: (selected: { id: string; needScroll: boolean }) => void;
  setHovered: (hovered: string) => void;
}) {
  const ref = useRef<HTMLDivElement>(null);

  const isSelected = data.id === selected.id;

  useLayoutEffect(() => {
    if (ref.current && isSelected && selected.needScroll) {
      ref.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [isSelected, selected.needScroll]);

  const [seen, setSeen] = useState(true);

  const nameSplit = /^([^"]*)(".*")$/.exec(data.name);
  let name;
  if (nameSplit) {
    name = (
      <>
        <span className={styles.Debug_NodeName}>{nameSplit[1]}</span>
        <span className={styles.Debug_NodeText}>{nameSplit[2]}</span>
      </>
    );
  } else {
    name = <span className={styles.Debug_NodeName}>{data.name}</span>;
  }

  return (
    <div className={styles.Debug_Item} ref={ref}>
      <div
        className={clsx(
          styles.Debug_Node,
          selected.id === data.id ? styles.Debug_Node__Selected : null,
          data.children.length === 0
            ? styles.Debug_Node__Empty
            : seen
              ? styles.Debug_Node__Active
              : styles.Debug_Node__Hidden,
        )}
        onClick={() => {
          if (selected.id === data.id) {
            setSelected({ id: "", needScroll: false });
          } else {
            setSelected({ id: data.id, needScroll: false });
          }
        }}
        onMouseEnter={() => {
          setHovered(data.id);
        }}
        onMouseLeave={() => {
          setHovered("");
        }}
      >
        <span
          className={clsx(
            styles.Debug_NodeToggle,
            data.children.length === 0
              ? styles.Debug_NodeToggle__Empty
              : seen
                ? styles.Debug_NodeToggle__Active
                : styles.Debug_NodeToggle__Hidden,
          )}
          onClick={(event) => {
            event.stopPropagation();
            setSeen(!seen);
          }}
        />
        {name}
      </div>
      <ul
        className={clsx(
          styles.Debug_ItemList,
          data.children.length === 0
            ? styles.Debug_ItemList__Empty
            : seen
              ? styles.Debug_ItemList__Active
              : styles.Debug_ItemList__Hidden,
        )}
      >
        {data.children.map((child) => (
          <DebugItem
            data={child}
            key={child.id}
            selected={selected}
            setSelected={setSelected}
            setHovered={setHovered}
          />
        ))}
      </ul>
    </div>
  );
}

function ItemInfo({
  data,
  setHovered,
  setSelected,
}: {
  data?: Record<string, unknown>;
  setHovered: (hovered: string) => void;
  setSelected: (selected: { id: string; needScroll: boolean }) => void;
}) {
  if (!data) {
    return (
      <div className={styles.Debug_ItemInfo}>
        This element was not rendered (probably due to optimization of
        optionals).
      </div>
    );
  }
  let order: string[];
  if ("$order" in data) {
    order = data.$order as string[];
  } else {
    order = Object.keys(data);
  }
  return (
    <div className={styles.Debug_ItemInfo}>
      <ul className={styles.Debug_ItemInfoList}>
        {order.map((key, i) => {
          return (
            <ul key={i} className={styles.Debug_ItemInfoElement}>
              <div className={styles.Debug_ItemInfoElementName}>
                <div className={styles.Debug_ItemInfoElementNameBg}>{key}</div>
              </div>
              <div
                className={clsx(
                  styles.Debug_ItemInfoElementValue,
                  styles.Debug_ItemInfoElementValue__Short,
                )}
              >
                <ItemInfoValue
                  value={data[key]}
                  setHovered={setHovered}
                  setSelected={setSelected}
                />
              </div>
            </ul>
          );
        })}
      </ul>
    </div>
  );
}

function ItemInfoValue({
  value,
  setHovered,
  setSelected,
}: {
  value: unknown;
  setHovered: (hovered: string) => void;
  setSelected: (selected: { id: string; needScroll: boolean }) => void;
}) {
  if (value === null) {
    return <span className={styles.Debug_ValueNone}>None</span>;
  } else if (typeof value == "boolean") {
    return (
      <span className={styles.Debug_ValueBool}>{value ? "True" : "False"}</span>
    );
  } else if (typeof value == "number") {
    return <span className={styles.Debug_ValueNumber}>{String(value)}</span>;
  } else if (typeof value == "string") {
    return (
      <span className={styles.Debug_ValueString}>{JSON.stringify(value)}</span>
    );
  } else if (value instanceof Array) {
    return (
      <span className={styles.Debug_ValueList}>
        {value.map((item, i) => {
          return (
            <span key={i} className={styles.Debug_ValueListItem}>
              <ItemInfoValue
                value={item as unknown}
                setHovered={setHovered}
                setSelected={setSelected}
              />
            </span>
          );
        })}
      </span>
    );
  } else if (typeof value == "object") {
    if ("$elem" in value) {
      return (
        <span
          className={styles.Debug_ValueNode}
          onMouseEnter={() => {
            if ("$id" in value && typeof value.$id === "string") {
              setHovered(value.$id);
            }
          }}
          onMouseLeave={() => {
            setHovered("");
          }}
          onClick={() => {
            if ("$id" in value && typeof value.$id === "string") {
              setSelected({ id: value.$id, needScroll: true });
            }
          }}
        >
          {String(value.$elem)}
        </span>
      );
    } else {
      let order: string[];
      if ("$order" in value) {
        order = value.$order as string[];
      } else {
        order = Object.keys(value);
      }

      return (
        <span className={styles.Debug_ValueDict}>
          {order.map((key, i) => {
            return (
              <span key={i} className={styles.Debug_ValueDictItem}>
                <span className={styles.Debug_ValueDictKey}>{key}</span>
                <span className={styles.Debug_ValueDictValue}>
                  <ItemInfoValue
                    value={(value as Record<string, unknown>)[key]}
                    setHovered={setHovered}
                    setSelected={setSelected}
                  />
                </span>
              </span>
            );
          })}
        </span>
      );
    }
  } else {
    <span className={styles.Debug_ValueUnknown}>{JSON.stringify(value)}</span>;
  }
}
