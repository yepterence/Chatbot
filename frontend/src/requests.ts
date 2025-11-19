import type { Message } from "./interfaces";

export async function streamChatResponse(
  messages: Message[],
  onChunk: (chunk: string) => void
) {
  const res = await fetch("http://127.0.0.1:8000/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages }),
  });

  const reader = res.body!.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;

    const chunkStr = decoder.decode(value);
    const lines = chunkStr
      .split("\n")
      .filter((line) => line.startsWith("data:"));

    for (const line of lines) {
      try {
        const jsonData = JSON.parse(line.replace("data: ", ""));
        onChunk(jsonData.delta);
      } catch (err) {
        console.error("Failed to parse chunk:", err);
      }
    }
  }
}
