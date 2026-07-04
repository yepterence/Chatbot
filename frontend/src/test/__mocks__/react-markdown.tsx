import React from "react";

/** Minimal stand-in for react-markdown: renders children as plain text. */
export default function ReactMarkdown({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
