import type { Theme } from "./App";
import { type Monaco, Editor as MonacoEditor } from "@monaco-editor/react";
import { configureMonacoYaml } from "monaco-yaml";
import { useEffect, useState } from "react";
import schema from "virtual:schema.json";

const CODE = `---
- optional:
  - "WITH"
  - optional: "RECURSIVE"
  - one_or_more:
    - non_terminal: "common-table-expression"
    repeat: ","
- one_or_more:
  - text: select-core
    group:
    - choice:
      - stack:
        -
          - "SELECT"
          - choice:
            -
            - "DISTINCT"
            - "ALL"
          - one_or_more:
            - non_terminal: "result-column"
            repeat: ","
        -
          - optional:
            - "FROM"
            - choice:
              - one_or_more:
                - non_terminal: "table-or-subquery"
                repeat: ","
              - non_terminal: "join-clause"
        -
          - optional:
            - "WHERE"
            - non_terminal: "expr"
        -
          - optional:
            - "GROUP"
            - "BY"
            - one_or_more:
              - non_terminal: "expr"
              repeat: ","
          - optional:
            - "HAVING"
            - non_terminal: "expr"
        -
          - optional:
            - "WINDOW"
            - one_or_more:
              - non_terminal: "window-name"
              - "AS"
              - non_terminal: "window-defn"
              repeat: ","
            skip: true
            skip_bottom: true
      -
        - "VALUES"
        - one_or_more:
          - "("
          - one_or_more:
              non_terminal: "expr"
            repeat: ","
          - ")"
          repeat: ","
  repeat:
    non_terminal: "compound-operator"
- optional:
  - "ORDER"
  - "BY"
  - one_or_more:
    - non_terminal: "ordering-term"
    repeat: ","
- optional:
  - barrier:
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
  skip: true
  skip_bottom: true
`;

export function Editor({
  setCode,
  theme,
}: {
  setCode?: (code: string | undefined) => void;
  theme: Theme;
}) {
  const [monaco, setMonaco] = useState<Monaco | null>(null);
  const defaultValue = localStorage.getItem("code") || CODE;

  const beforeMount = (monaco: Monaco) => {
    setMonaco(monaco);

    if (setCode) {
      setCode(defaultValue);
    }
    monaco.editor.setTheme(theme === "light" ? "vs" : "vs-dark");

    configureMonacoYaml(monaco, {
      hover: true,
      completion: true,
      validate: true,
      format: true,
      enableSchemaRequest: true,
      schemas: [
        {
          fileMatch: ["**/diagram.yaml"],
          schema,
          uri: import.meta.resolve("virtual:schema.json"),
        },
      ],
    });
  };

  useEffect(() => {
    if (monaco) {
      monaco.editor.setTheme(theme === "light" ? "vs" : "vs-dark");
    }
  }, [monaco, theme]);

  const onChange = (value: string | undefined) => {
    if (setCode) {
      setCode(value ?? "");
    }
    try {
      localStorage.setItem("code", value ?? "");
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <MonacoEditor
      height="100%"
      defaultLanguage="yaml"
      defaultValue={defaultValue}
      theme={theme === "light" ? "vs" : "vs-dark"}
      path="diagram.yaml"
      beforeMount={beforeMount}
      onChange={onChange}
      options={{
        tabSize: 2,
        minimap: {
          enabled: false,
        },
        scrollbar: {
          horizontalScrollbarSize: 8,
          verticalScrollbarSize: 8,
        },
        automaticLayout: true,
        quickSuggestions: {
          other: true,
          comments: false,
          strings: true,
        },
      }}
    />
  );
}
