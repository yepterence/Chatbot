import { useState, useEffect, useRef } from "react";
import { streamChatResponse } from "../requests";
import type { Message } from "../interfaces";

export const ChatWindow = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  // Buffer for raw text stream
  const responseBuffer = useRef("");
  // Handle mounting/unmounting of component
  const isMounted = useRef(true);

  useEffect(() => {
    return () => {
      isMounted.current = false;
    };
  }, []);

  const handleKeyDown = async (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      await handleSubmit();
    }
  };
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
    <div className="chat-container">
      {messages.map((msg, idx) => (
        <div key={idx} className={`message ${msg.role}`}>
          {msg.content}
        </div>
      ))}

      <div className="input-area">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isStreaming}
        />
        <button onClick={handleSubmit} disabled={isStreaming}>
          {isStreaming ? "..." : "Send"}
        </button>
      </div>
    </div>
  );
};
