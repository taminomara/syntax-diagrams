import { type Message, type Response } from "./pyodideApiTypes";
import { loadPyodide } from "pyodide";
import type { PyProxy } from "pyodide/ffi";
import wheels from "virtual:wheels.json";

async function load() {
  return loadPyodide({
    packages: wheels.map(
      (wheel: string) => `${__CANONICAL_URL__}/try/assets/wheels/${wheel}`,
    ),
  });
}

console.info("Loading Pyodide...");
const pyodideReadyPromise = load();
pyodideReadyPromise
  .then(() => console.info("Pyodide loaded"))
  .catch(console.error);

self.onmessage = async (event: MessageEvent<Message>) => {
  const pyodide = await pyodideReadyPromise;
  const { id, script, context } = event.data;
  const globals = pyodide.toPy(context) as PyProxy;
  try {
    const result = pyodide.runPython(script, { globals }) as string;
    self.postMessage({ result, id } satisfies Response);
  } catch (error) {
    self.postMessage({ error: String(error), id } satisfies Response);
  }
};
