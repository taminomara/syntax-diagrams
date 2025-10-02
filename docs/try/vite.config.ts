import react from "@vitejs/plugin-react";
import { execSync } from "child_process";
import { mkdirSync, readdirSync, rmSync } from "fs";
import { dirname, join, resolve } from "path";
import { fileURLToPath } from "url";
import { type PluginOption, defineConfig } from "vite";
import { viteStaticCopy } from "vite-plugin-static-copy";

const PYODIDE_EXCLUDE = [
  "!**/*.{md,html}",
  "!**/*.d.ts",
  "!**/*.whl",
  "!**/node_modules",
];

const SRC_DIR = resolve(join(__dirname, "../../"));
const WHEELS_DIR = resolve(join(__dirname, "../../dist"));

function staticCopyPyodide() {
  const pyodideDir = dirname(fileURLToPath(import.meta.resolve("pyodide")));
  return viteStaticCopy({
    targets: [
      {
        src: [join(pyodideDir, "*")].concat(PYODIDE_EXCLUDE),
        dest: "assets",
      },
    ],
    watch: {
      reloadPageOnChange: true,
    },
  });
}

let wheelList: string[] | undefined;

function buildWheels(): PluginOption[] {
  return [
    {
      name: "build-wheels",
      buildStart() {
        this.info(`Clearing ${WHEELS_DIR}`);
        rmSync(WHEELS_DIR, { recursive: true, force: true });
        mkdirSync(WHEELS_DIR, { recursive: true });

        this.info("Building Python wheels");
        execSync("pip wheel -w dist/ .", { cwd: SRC_DIR });
        wheelList = readdirSync(WHEELS_DIR)
          .map((filename) => {
            if (filename.endsWith(".whl")) {
              return filename;
            }
          })
          .filter((filename) => filename !== undefined);
        this.info(`Built ${wheelList.join(", ")}`);
      },
    },
    viteStaticCopy({
      targets: [
        {
          src: join(WHEELS_DIR, "*.whl"),
          dest: "assets/wheels",
        },
      ],
    }),
  ];
}

function resolveWheelList(expectNonEmpty: boolean): PluginOption[] {
  const virtualModuleId = "virtual:wheels.json";
  const resolvedVirtualModuleId = "\0" + virtualModuleId;

  return [
    {
      name: "build-wheels",
      resolveId(id) {
        if (id === virtualModuleId) {
          return resolvedVirtualModuleId;
        }
      },
      load(id) {
        if (id === resolvedVirtualModuleId) {
          if (wheelList === undefined && expectNonEmpty) {
            this.warn(
              "Wheels list was empty during resolution of virtual:wheels.json",
            );
          }
          return JSON.stringify(wheelList ?? []);
        }
      },
    },
  ];
}

function resolveSchema(): PluginOption {
  const virtualModuleId = "virtual:schema.json";
  const resolvedVirtualModuleId = "\0" + virtualModuleId;

  return {
    name: "build-yaml-schema",
    resolveId(id) {
      if (id === virtualModuleId) {
        return resolvedVirtualModuleId;
      }
    },
    load(id) {
      if (id === resolvedVirtualModuleId) {
        this.addWatchFile(join(SRC_DIR, "syntax_diagrams/element.py"));
        return execSync("python syntax_diagrams/element.py", {
          encoding: "utf-8",
          cwd: SRC_DIR,
        });
      }
    },
  };
}

export default defineConfig(({ mode }) => {
  let canonicalUrl = process.env["READTHEDOCS_CANONICAL_URL"] ?? "";
  if (canonicalUrl.endsWith("/")) {
    canonicalUrl = canonicalUrl.slice(0, canonicalUrl.length - 1);
  }
  const version = process.env["READTHEDOCS_VERSION_NAME"] ?? "local";
  const plugins: PluginOption[] = [
    react(),
    staticCopyPyodide(),
    resolveSchema(),
  ];
  const webWorkerPlugins: PluginOption[] = [
    resolveWheelList(mode !== "development"),
  ];
  if (mode !== "development") {
    plugins.push(buildWheels());
  }
  return {
    plugins,
    optimizeDeps: { exclude: ["pyodide"] },
    base: `${canonicalUrl}/try`,
    worker: {
      format: "es",
      plugins() {
        return webWorkerPlugins;
      },
    },
    define: {
      __CANONICAL_URL__: JSON.stringify(canonicalUrl),
      __BUILD_VERSION__: JSON.stringify(version),
    },
    server: {
      proxy: {
        "/api/render": {
          target: "http://127.0.0.1:9011",
          changeOrigin: true,
          rewrite: (path) => path.replace(/^[/]api[/]render[/]?/, "/"),
        },
      },
    },
  };
});
