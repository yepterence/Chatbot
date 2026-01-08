// import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchChatHistoryList } from "../requests";
import type { ChatHistoryItem, ChatHistoryProps } from "../interfaces";
// This component will display all the chat titles in a menu bar
// On app load up, it will query the chat  history table and retrieve all the listed chat titles.
// When a new chat is created, and the user engages with a prompt, upon completing the first response, a new chat title will be added and the state of the chat history menu will be refreshed/updated.
// When a chat title is selected, the entire chat history will load up for that specific title and then the chat history will be available on the chatwindow

export const ChatHistory: React.FC<ChatHistoryProps> = ({
  onSelectChat,
  selectedChatId,
}) => {
  const {
    data: chats,
    isLoading,
    isError,
  } = useQuery<ChatHistoryItem[]>({
    queryKey: ["chat-history"],
    queryFn: fetchChatHistoryList,
  });
  if (isLoading)
    return <div className="p-4 text-gray-500">Loading History..</div>;
  if (isError)
    return <div className="p-4 text-red-500">Error Loading History..</div>;
  return (
    <nav>
      <div>
        <h3>ChatHistory</h3>;
      </div>
      <div>
        {chats?.map((chat) => (
          <button
            key={chat.id}
            onClick={() => onSelectChat(chat.id)}
            className={`sidebar-item ${
              selectedChatId === chat.id ? "active" : ""
            }`}
          >
            <span>{chat.chat_title}</span>
          </button>
        ))}
      </div>
    </nav>
  );
};
