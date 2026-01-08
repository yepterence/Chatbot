import type { Message } from "./interfaces";
export async function fetchChatHistoryList() {
  const url = "http://127.0.0.1:8000/chat/chat_history";
  try {
    const res = await fetch(url);
    return res.json();
  } catch (error) {
    console.error("Failed to fetch chat history", error);
    throw error;
  }
}
export async function fetchChatMessages(chatId: Number) {
  const url = `http://127.0.0.1:8000/chat/${chatId}`;
  try {
    const res = await fetch(url);
    if (!res.ok) {
      throw new Error(`Error ${res.status}: Could not find chat messages.`);
    }
    return await res.json();
  } catch (error) {
    console.error("Failed to fetch chat messages:", error);
    throw error;
  }
}
export async function streamChatResponse(
  messages: Message[],
  onChunk: (chunk: { content: string; finished: boolean }) => void
) {
  const res = await fetch("http://127.0.0.1:8000/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages }),
  });

  if (!res.ok) {
    throw new Error("Network response is not ok");
  }

  if (!res.body) throw new Error("Response has no body");
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed.startsWith("data:")) continue;

      const jsonStr = trimmed.slice(5).trim();
      try {
        const data = JSON.parse(jsonStr);
        onChunk({
          content: data.content ?? "",
          finished: data.finished ?? false,
        });
      } catch (e) {
        console.error("Failed to parse SSE chunk:", jsonStr, e);
      }
    }
  }
}
