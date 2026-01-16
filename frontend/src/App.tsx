import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ChatWindow } from "./components/ChatWindow";
import { ChatHistory } from "./components/ChatHistory";
const queryClient = new QueryClient();
export default function App() {
  return (
    <div>
      <h1 className="chat-title">Simple Chat</h1>
      <QueryClientProvider client={queryClient}>
        <ChatHistory />
        <ChatWindow />
      </QueryClientProvider>
    </div>
  );
}
