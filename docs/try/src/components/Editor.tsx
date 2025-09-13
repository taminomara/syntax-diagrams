import schema from "../../gen/schema.json";
import Editor, { type Monaco } from "@monaco-editor/react";
import { type MonacoYaml, configureMonacoYaml } from "monaco-yaml";

let monacoYamlInstance: MonacoYaml | undefined;

const CODE = `---
- optional:
  - "WITH"
  - optional: "RECURSIVE"
  - one_or_more:
    - non_terminal: "common-table-expression"
    repeat: ","
- one_or_more:
  - group:
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
    text: select-core
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

export default function () {
  const beforeMount = (monaco: Monaco) => {
    if (!monacoYamlInstance) {
      monacoYamlInstance = configureMonacoYaml(monaco, {
        hover: true,
        completion: true,
        validate: true,
        format: true,
        enableSchemaRequest: true,
        schemas: [
          {
            fileMatch: ["**/diagram.yaml"],
            schema,
            uri: "https://taminomara.github.io/syntax-diagrams/",
          },
        ],
      });
    }
  };

  const onChange = (value: string | undefined) => {
    try {
      localStorage.setItem("code", value ?? "");
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <Editor
      height="100vh"
      defaultLanguage="yaml"
      defaultValue={localStorage.getItem("code") || CODE}
      theme="vs-dark"
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
        formatOnType: true,
      }}
    />
  );
}
