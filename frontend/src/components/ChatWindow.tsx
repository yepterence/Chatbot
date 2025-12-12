import { useState, useRef } from "react";
import { streamChatResponse } from "../requests";
import type { Message } from "../interfaces";

export const ChatWindow = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  // Buffer for raw text stream
  const responseBuffer = useRef("");
  const textAreaRef = useRef<HTMLTextAreaElement>(null);

  const handleKeyDown = async (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.shiftKey && e.key === "Enter") {
      e.preventDefault();
      const textArea = textAreaRef.current;
      const start = textArea!.selectionStart;
      const end = textArea!.selectionEnd;
      const value = textArea!.value;
      textArea!.value = value.substring(0, start) + "\n" + value.substring(end);
      textArea!.selectionStart = start + 1;
      textArea!.selectionEnd = start + 1;
      textArea!.style.height = "auto";
      textArea!.style.height = textArea?.scrollHeight + "px";
    } else if (e.key === "Enter") {
      await handleSubmit();
    }
  };
  const isEmpty: boolean = messages.length === 0;
  const handleSubmit = async () => {
    if (!input.trim()) return;

    const userPrompt = input;
    setInput("");
    setIsStreaming(true);
    // Add user prompt
    setMessages((prev) => [...prev, { role: "user", content: userPrompt }]);
    // reset buffer
    responseBuffer.current = "";
    try {
      await streamChatResponse(
        [{ role: "user", content: userPrompt }],
        (chunk) => {
          //  Update buffer synchronously
          responseBuffer.current += chunk.content;
          const currentText = responseBuffer.current;
          setMessages((prev) => {
            const newHistory = [...prev];
            const lastMsg = newHistory[newHistory.length - 1];
            if (!lastMsg || lastMsg.role !== "assistant") {
              return [
                ...newHistory,
                { role: "assistant", content: currentText },
              ];
            }
            // Creating new object for last message and replacing content with full buffer
            newHistory[newHistory.length - 1] = {
              ...lastMsg,
              content: currentText,
            };
            return newHistory;
          });
          if (chunk.finished) {
            console.log("Stream concluded");
            setIsStreaming(false);
          }
        }
      );
    } catch (error) {
      console.error("Streaming failed: ", error);
    } finally {
      setIsStreaming(false);
    }
  };
  return (
    <div className={isEmpty ? "chat-container empty" : "chat-container filled"}>
      {messages.map((msg, idx) => (
        <div key={idx} className={`message ${msg.role}`}>
          {msg.content}
        </div>
      ))}

      <div id="input-area" className="input-text-area">
        <textarea
          ref={textAreaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={1}
          style={{ overflow: "hidden" }}
          placeholder="Type your prompt..."
          disabled={isStreaming}
        />
      </div>
    </div>
  );
};
