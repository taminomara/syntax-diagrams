import yamlWorker from "./yaml.worker.js?worker";
import { loader } from "@monaco-editor/react";
import * as monaco from "monaco-editor";
import editorWorker from "monaco-editor/esm/vs/editor/editor.worker?worker";

// @ts-expect-error no typings
self.MonacoEnvironment = {
  getWorker(_: unknown, label: string) {
    switch (label) {
      case "editorWorkerService":
        return new editorWorker();
      case "yaml":
        return new yamlWorker();
      default:
        throw new Error(`Unknown label ${label}`);
    }
  },
};

loader.config({ monaco });
