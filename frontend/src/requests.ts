import type { Message } from "./interfaces";

function extractDelta(rawChunk: string): string | null {
  let line = rawChunk.trim();
  if (!line.startsWith("data:")) return null;

  const jsonStr = line.slice(5).trim();
  if (!jsonStr) return null;

  try {
    const data = JSON.parse(jsonStr);
    if (!data.delta) return null;

    let delta = data.delta;

    // recursively unwrap if delta itself is an SSE string
    while (delta.trim().startsWith("data:")) {
      const innerLine = delta.trim().slice(5).trim();
      const innerData = JSON.parse(innerLine);
      delta = innerData.delta ?? "";
    }

    return delta;
  } catch (err) {
    console.error("Failed to parse nested SSE chunk:", jsonStr, err);
    return null;
  }
}

export async function streamChatResponse(
  messages: Message[],
  onChunk: (chunk: string) => void
) {
  const res = await fetch("http://127.0.0.1:8000/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages }),
  });

  let fullText = "";
  let buffer = "";
  const reader = res.body!.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.split("\n\n");
    buffer = parts.pop() ?? "";

    for (const part of parts) {
      const delta = extractDelta(part);
      if (delta !== null) {
        fullText += delta;
        onChunk(delta);
      }
    }
  }
}
