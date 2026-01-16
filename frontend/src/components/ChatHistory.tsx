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
  });
  const setSelectedChat = useSelectedChatStore(
    (state) => state.setSelectedChat
  );

  if (isLoading) return <div>Loading History..</div>;
  if (isError) return <div>Error Loading History..</div>;
  return (
    <nav>
      <div>
        <h3>ChatHistory</h3>
      </div>
      <div>
        {chats?.map((chat) => (
          <button
            key={chat.id}
            onClick={() => setSelectedChat(chat.id, chat.chat_title)}
            // className={`sidebar-item ${
            //   selectedChatId === chat.id ? "active" : ""
            // }`}
          >
            <span>{chat.chat_title}</span>
          </button>
        ))}
      </div>
    </nav>
  );
};
