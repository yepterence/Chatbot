import React, { useState, useRef } from "react";
import type { Message } from "../interfaces";
import { streamChatResponse } from "../requests";

export default function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", content: "Hello! How can I help you today?" },
  ]);
  const [input, setInput] = useState("");
  const chatEndRef = useRef<HTMLDivElement | null>(null);

  const scrollToBottom = () =>
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMsg: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    scrollToBottom();

    const assistantMsg: Message = { role: "assistant", content: "" };
    setMessages((prev) => [...prev, assistantMsg]);
    scrollToBottom();

    await streamChatResponse([...messages, userMsg], (chunk) => {
      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1].content += chunk;
        return updated;
      });
      scrollToBottom();
    });
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-window">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            <div className={`bubble ${msg.role}`}>{msg.content}</div>
          </div>
        ))}
        <div ref={chatEndRef}></div>
      </div>

      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyPress}
        placeholder="Type a message..."
        rows={2}
      />
      <button onClick={sendMessage}>Send</button>
    </div>
  );
}
