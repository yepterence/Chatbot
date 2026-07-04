import { render, screen, fireEvent, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ChatWindow } from "./ChatWindow";
import { useSelectedChatStore } from "../ApplicationStore";
import * as requests from "../requests";

jest.mock("../requests");

const mockedRequests = requests as jest.Mocked<typeof requests>;

type Chunk = { content: string; finished: boolean };

/** Builds a streamChatResponse mock that synchronously replays the given chunks to onChunk. */
function makeStreamMock(chunks: Chunk[]) {
  return jest.fn(async (_messages: unknown, onChunk: (chunk: Chunk) => void) => {
    for (const chunk of chunks) {
      onChunk(chunk);
    }
  });
}

/**
 * Types text and submits via Enter, using a raw keydown (rather than letting
 * userEvent simulate the browser's real default action) because the plain
 * "Enter" branch of handleKeyDown never calls preventDefault(), which would
 * otherwise leave a literal newline in the textarea as an unrelated artifact.
 */
async function submitMessage(
  user: ReturnType<typeof userEvent.setup>,
  textarea: HTMLElement,
  text: string
) {
  await user.type(textarea, text);
  await act(async () => {
    fireEvent.keyDown(textarea, { key: "Enter" });
    await Promise.resolve();
  });
}

function renderChatWindow() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <ChatWindow />
    </QueryClientProvider>
  );
}

beforeEach(() => {
  useSelectedChatStore.setState({ id: null, chat_title: null });
});

describe("ChatWindow", () => {
  it("renders an empty state with no messages initially", () => {
    const { container } = renderChatWindow();
    expect(screen.getByPlaceholderText("Type your prompt...")).toBeInTheDocument();
    expect(container.querySelectorAll(".message")).toHaveLength(0);
  });

  it("adds the user message immediately and streams the assistant reply", async () => {
    mockedRequests.streamChatResponse.mockImplementation(
      makeStreamMock([
        { content: "Hi", finished: false },
        { content: " there", finished: true },
      ])
    );
    const user = userEvent.setup();
    renderChatWindow();

    await submitMessage(user, screen.getByPlaceholderText("Type your prompt..."), "Hello");

    expect(await screen.findByText("Hello")).toBeInTheDocument();
    expect(await screen.findByText("Hi there")).toBeInTheDocument();
    expect(mockedRequests.streamChatResponse).toHaveBeenCalledTimes(1);
  });

  it("keeps the full conversation visible in the same window across multiple turns", async () => {
    mockedRequests.streamChatResponse
      .mockImplementationOnce(makeStreamMock([{ content: "First answer", finished: true }]))
      .mockImplementationOnce(makeStreamMock([{ content: "Second answer", finished: true }]));

    const user = userEvent.setup();
    renderChatWindow();
    const textarea = screen.getByPlaceholderText("Type your prompt...");

    // Turn 1
    await submitMessage(user, textarea, "First question");
    expect(await screen.findByText("First answer")).toBeInTheDocument();

    // Turn 2, submitted in the same mounted ChatWindow instance (no unmount/reset in between)
    await submitMessage(user, textarea, "Second question");
    expect(await screen.findByText("Second answer")).toBeInTheDocument();

    // Both turns must still be rendered together in the same chat window.
    expect(screen.getByText("First question")).toBeInTheDocument();
    expect(screen.getByText("First answer")).toBeInTheDocument();
    expect(screen.getByText("Second question")).toBeInTheDocument();
    expect(screen.getByText("Second answer")).toBeInTheDocument();
    expect(mockedRequests.streamChatResponse).toHaveBeenCalledTimes(2);
  });

  it("stays within the currently selected chat context across multiple turns (does not start a new chat)", async () => {
    // Simulate continuing an existing, already-persisted conversation loaded
    // from the sidebar -- this is the one scenario where the frontend
    // currently has a concrete "active chat" identity that could be lost.
    useSelectedChatStore.setState({ id: 42, chat_title: "Existing chat" });
    mockedRequests.fetchChatMessages.mockResolvedValue([
      { role: "user", content: "Old question" },
      { role: "assistant", content: "Old answer" },
    ]);
    const resetSelectedChatSpy = jest.fn(useSelectedChatStore.getState().resetSelectedChat);
    useSelectedChatStore.setState({ resetSelectedChat: resetSelectedChatSpy });

    mockedRequests.streamChatResponse
      .mockImplementationOnce(makeStreamMock([{ content: "First follow-up answer", finished: true }]))
      .mockImplementationOnce(makeStreamMock([{ content: "Second follow-up answer", finished: true }]));

    const user = userEvent.setup();
    renderChatWindow();
    expect(await screen.findByText("Old question")).toBeInTheDocument();

    const textarea = screen.getByPlaceholderText("Type your prompt...");
    await submitMessage(user, textarea, "Follow-up question one");
    expect(await screen.findByText("First follow-up answer")).toBeInTheDocument();

    await submitMessage(user, textarea, "Follow-up question two");
    expect(await screen.findByText("Second follow-up answer")).toBeInTheDocument();

    // The active chat's identity must stay exactly what it was: no implicit
    // "new chat" transition should happen just because the user kept talking.
    expect(useSelectedChatStore.getState().id).toBe(42);
    expect(useSelectedChatStore.getState().chat_title).toBe("Existing chat");
    expect(resetSelectedChatSpy).not.toHaveBeenCalled();

    // NOTE: this only guards conversations that were already associated with
    // a chat id (e.g. reopened from history). For a *brand-new* conversation
    // (selectedChatId starts null), there is currently no mechanism at all
    // for the frontend to learn the id the backend persists after turn 1 --
    // streamChatResponse exposes no return value or response header, so
    // setSelectedChat() can never be called for a fresh chat. That gap,
    // combined with the backend always creating a new ChatHistory row per
    // turn (see test_persist_chat_does_not_reuse_existing_session_across_turns
    // in test/test_llm_client.py), is what allows a single multi-turn
    // conversation to be silently split into multiple saved chats.
  });

  it("sends the full conversation history, not just the latest turn, on later requests", async () => {
    mockedRequests.streamChatResponse
      .mockImplementationOnce(makeStreamMock([{ content: "First answer", finished: true }]))
      .mockImplementationOnce(makeStreamMock([{ content: "Second answer", finished: true }]));

    const user = userEvent.setup();
    renderChatWindow();
    const textarea = screen.getByPlaceholderText("Type your prompt...");

    await submitMessage(user, textarea, "First question");
    await screen.findByText("First answer");

    await submitMessage(user, textarea, "Second question");
    await screen.findByText("Second answer");

    const secondCallMessages = mockedRequests.streamChatResponse.mock.calls[1][0];
    expect(secondCallMessages).toEqual([
      { role: "user", content: "First question" },
      { role: "assistant", content: "First answer" },
      { role: "user", content: "Second question" },
    ]);
  });

  it("clears messages and resets the selected chat when starting a new chat", async () => {
    useSelectedChatStore.setState({ id: 42, chat_title: "Existing chat" });
    mockedRequests.fetchChatMessages.mockResolvedValue([
      { role: "user", content: "Old question" },
      { role: "assistant", content: "Old answer" },
    ]);

    renderChatWindow();
    expect(await screen.findByText("Old question")).toBeInTheDocument();

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: /new chat/i }));

    expect(screen.queryByText("Old question")).not.toBeInTheDocument();
    expect(useSelectedChatStore.getState().id).toBeNull();
  });
});
