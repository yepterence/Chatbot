import React, { useState, useRef, useEffect } from "react";
import { fetchChatMessages, streamChatResponse } from "../requests";
import type { Message } from "../interfaces";
import ReactMarkdown from "react-markdown";
import { useSelectedChatStore } from "../ApplicationStore";
import { useQuery } from "@tanstack/react-query";

export const ChatWindow = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  // Get selected chat from Zustand store
  const selectedChatId = useSelectedChatStore((state) => state.id);
  const selectedChatTitle = useSelectedChatStore((state) => state.chat_title);
  const resetSelectedChat = useSelectedChatStore(
    (state) => state.resetSelectedChat
  );
  // Buffer for raw text stream
  const responseBuffer = useRef("");
  const textAreaRef = useRef<HTMLTextAreaElement>(null);
  const { data: historicalMessages, isLoading: isLoadingHistory } = useQuery<
    Message[]
  >({
    queryKey: ["chat-messages", selectedChatId],
    queryFn: () => fetchChatMessages(selectedChatId!),
    // CRITICAL: Only fetch when a chat is selected
    enabled: selectedChatId !== null,
    // Prevent refetching on window focus for chat history
    refetchOnWindowFocus: false,
  });

  useEffect(() => {
    if (historicalMessages && selectedChatId) {
      setMessages(historicalMessages);
    }
  }, [historicalMessages, selectedChatId]);
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
      e.preventDefault();
      await handleSubmit();
    }
  };
  const isEmpty: boolean = messages.length === 0;
  if (isLoadingHistory) {
    return (
      <div className="chat-container">
        <div className="loading-indicator">Loading chat history...</div>
      </div>
    );
  }
  const handleNewChat = () => {
    resetSelectedChat();
    setMessages([]);
    setInput("");
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
        [...messages,{ role: "user", content: userPrompt }],
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
      {/* Header showing current chat or "New Chat" */}
      <div className="chat-header">
        <h2>{selectedChatTitle || "New Chat"}</h2>
        {selectedChatId && (
          <button onClick={handleNewChat} className="new-chat-btn">
            + New Chat
          </button>
        )}
      </div>
      {/* Message display */}
      {messages.map((msg, idx) => (
        <div key={idx} className={`message ${msg.role}`}>
          <ReactMarkdown>{msg.content}</ReactMarkdown>
        </div>
      ))}
      {/* Input */}
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
