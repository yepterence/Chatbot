import React from "react";
import ChatWindow from "./components/ChatWindow";

export default function App() {
  return (
    <div
      style={{
        maxWidth: "600px",
        margin: "2rem auto",
        fontFamily: "sans-serif",
      }}
    >
      <h1>Simple Chat</h1>
      <ChatWindow />
    </div>
  );
}
