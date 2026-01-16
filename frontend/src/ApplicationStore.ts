import { create } from "zustand";

interface SelectedChatState {
  id: number | null;
  chat_title: string | null;
  setSelectedChat: (id: number, title: string) => void;
  resetSelectedChat: () => void;
}
export const useSelectedChatStore = create<SelectedChatState>((set) => ({
  id: null,
  chat_title: null,
  setSelectedChat: (id, title) =>
    set({
      id: id,
      chat_title: title,
    }),
  resetSelectedChat: () =>
    set({
      id: null,
      chat_title: null,
    }),
}));
