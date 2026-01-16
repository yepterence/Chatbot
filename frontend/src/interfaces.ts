export interface Message {
  role: "user" | "assistant";
  content: string;
}

export interface ChatHistoryItem {
  id: number;
  chat_title: string;
}
