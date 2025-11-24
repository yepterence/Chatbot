import { useState } from "react";
import { streamChatResponse } from "../requests";
import type { Message } from "../interfaces";

export const ChatWindow = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const handleKeyDown = async (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      await handleSubmit();
    }
  };
  const handleSubmit = async () => {
    if (!input.trim()) return;
    const userMsg: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsStreaming(true);

    try {
      let assistantInitialized = false;

      await streamChatResponse([{ role: "user", content: input }], (chunk) => {
        setMessages((prev) => {
          const newHistory = [...prev];
          if (!assistantInitialized) {
            newHistory.push({ role: "assistant", content: "" });
            assistantInitialized = true;
          }
          const lastMsg = newHistory[newHistory.length - 1];
          lastMsg.content += chunk.content;
          return newHistory;
        });

        if (chunk.finished) {
          console.log("Stream concluded");
          setIsStreaming(false);
        }
      });
    } catch (error) {
      console.error("Streaming failed: ", error);
    }
  };
  return (
    <>
      {messages.map((msg, idx) => (
        <div key={idx} className={msg.role}>
          {msg.content}
        </div>
      ))}
      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
      />
      <button onClick={handleSubmit} disabled={isStreaming}>
        Send
      </button>
    </>
  );
};
