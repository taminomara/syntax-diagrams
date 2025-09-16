export type Message = {
  id: number;
  script: string;
  context: Record<string, unknown>;
};

export type Response =
  | { id: number; result: string; error?: undefined }
  | { id: number; result?: undefined; error: string };
