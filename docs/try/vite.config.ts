import react from "@vitejs/plugin-react";
import { dirname, join } from "path";
import { fileURLToPath } from "url";
import { defineConfig } from "vite";
import { viteStaticCopy } from "vite-plugin-static-copy";

const PYODIDE_EXCLUDE = [
  "!**/*.{md,html}",
  "!**/*.d.ts",
  "!**/*.whl",
  "!**/node_modules",
];

export function viteStaticCopyPyodide() {
  const pyodideDir = dirname(fileURLToPath(import.meta.resolve("pyodide")));
  return viteStaticCopy({
    targets: [
      {
        src: [join(pyodideDir, "*")].concat(PYODIDE_EXCLUDE),
        dest: "assets",
      },
    ],
  });
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), viteStaticCopyPyodide()],
  optimizeDeps: { exclude: ["pyodide"] },
});
