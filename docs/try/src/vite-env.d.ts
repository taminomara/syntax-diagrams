/// <reference types="vite/client" />

declare module "virtual:schema.json" {
  import { type JSONSchema } from "monaco-yaml";
  const schema: JSONSchema;
  export default schema;
}

declare module "virtual:wheels.json" {
  const wheels: string[];
  export default wheels;
}

declare const __CANONICAL_URL__: string;
declare const __BUILD_VERSION__: string;
