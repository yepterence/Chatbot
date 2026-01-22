// import React from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchChatHistoryList } from "../requests";
import type { ChatHistoryItem } from "../interfaces";
import { useSelectedChatStore } from "../ApplicationStore";

export const ChatHistory = () => {
  const {
    data: chats,
    isLoading,
    isError,
  } = useQuery<ChatHistoryItem[]>({
    queryKey: ["chat-history"],
    queryFn: fetchChatHistoryList,
    retry: false,
    // refetch when window regains focus to show new chats
    refetchOnWindowFocus: true,
  });
  const selectedChatId = useSelectedChatStore((state) => state.id);
  const setSelectedChat = useSelectedChatStore(
    (state) => state.setSelectedChat
  );
  const resetSelectedChat = useSelectedChatStore(
    (state) => state.resetSelectedChat
  );
  const handleNewChat = () => {
    resetSelectedChat();
  };
  if (isLoading) {
    return (
      <nav className="chat-history-sidebar">
        <div className="sidebar-header">
          <h3>Chat History</h3>
          <button onClick={handleNewChat} className="new-chat-btn">
            + New
          </button>
        </div>
        <div className="loading-state">
          <span>Loading chats...</span>
        </div>
      </nav>
    );
  }
  if (isError) return <div>Error Loading History..</div>;

  // Handle Empty state
  const isEmpty = !chats || chats.length === 0;
  return (
    <nav className="chat-history-sidebar">
      <div className="sidebar-header">
        <h3>Chat History</h3>
        <button onClick={handleNewChat} className="new-chat-btn">
          + New
        </button>
      </div>
      {isEmpty ? (
        <div className="empty-state">
          <p className="empty-title">No chats yet</p>
          <p className="empty-subtitle">
            Start a conversation to see your chat history here
          </p>
        </div>
      ) : (
        <div>
          {chats?.map((chat) => (
            <button
              key={chat.id}
              onClick={() => setSelectedChat(chat.id, chat.chat_title)}
              className={`sidebar-item ${
                selectedChatId === chat.id ? "active" : ""
              }`}
              // aria-current={selectedChatId === chat.id ? "page" : undefined}
            >
              <span className="chat-title">{chat.chat_title}</span>
            </button>
          ))}
        </div>
      )}
    </nav>
  );
};
