import React, { useCallback, useState } from "react";
import Sidebar from "../components/chats/Sidebar";
import ChatWindow from "../components/chats/ChatWindow";
import ChatInput from "../components/chats/ChatInput";
import { IconMenu } from "../components/chats/IconComponents.jsx";
import chatService from "../services/chatService";

const createWelcomeMessage = () => ({
  id: `welcome-${Date.now()}`,
  sender: "bot",
  text: "Hello! I’m The Alchemist. Ask me anything about your project, research, or code and I’ll do my best to help.",
  timestamp: new Date().toISOString(),
});

const generateId = (prefix) =>
  `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2)}`;

const Chat = () => {
  const [messages, setMessages] = useState([createWelcomeMessage()]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [conversationNumber, setConversationNumber] = useState(1);
  const [conversationTitle, setConversationTitle] = useState("New conversation");
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  const handleStartNewChat = useCallback(() => {
    setMessages([createWelcomeMessage()]);
    setIsLoading(false);
    setError(null);
    setConversationNumber((prev) => prev + 1);
    setConversationTitle("New conversation");
  }, []);

  const handleSendMessage = useCallback(
    async (rawMessage) => {
      const text = rawMessage.trim();
      if (!text || isLoading) return;

      const userMessage = {
        id: generateId("user"),
        sender: "user",
        text,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setError(null);
      setIsLoading(true);

      if (conversationTitle === "New conversation") {
        const readableTitle =
          text.length > 36 ? `${text.slice(0, 33)}...` : text;
        setConversationTitle(readableTitle);
      }

      try {
        const botResponse = await chatService.getLLMResponse(text);
        setMessages((prev) => [
          ...prev,
          {
            id: generateId("bot"),
            sender: "bot",
            text: botResponse,
            timestamp: new Date().toISOString(),
          },
        ]);
      } catch (err) {
        console.error("Failed to fetch assistant response", err);
        setError(
          "The assistant is unavailable right now. Please try again in a moment."
        );
      } finally {
        setIsLoading(false);
      }
    },
    [conversationTitle, isLoading]
  );

  const statusLine = (() => {
    if (error) return "We hit a snag. Feel free to retry.";
    if (isLoading) return "Assistant is thinking...";
    return "Ask about Minerals.";
  })();

  return (
    <div className="flex flex-1 min-h-0 w-full bg-[#202123] text-gray-200">
      <div
        className={`relative h-full flex-shrink-0 overflow-hidden transition-[width] duration-300 ${
          isSidebarOpen ? "w-80" : "w-0"
        }`}
      >
        <div
          className={`absolute inset-0 transform transition-transform duration-300 ${
            isSidebarOpen ? "translate-x-0" : "-translate-x-full"
          }`}
        >
          <Sidebar
            onStartNewChat={handleStartNewChat}
            onToggleSidebar={() => setIsSidebarOpen(false)}
            isOpen={isSidebarOpen}
          />
        </div>
      </div>

      {isSidebarOpen && <div className="w-[1px] bg-gray-800/80" aria-hidden="true" />}

      <section className="flex flex-col flex-1 min-h-0 bg-[#1c1c1e]">
        <header className="border-b border-gray-800/70 px-4 sm:px-6 py-4">
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              {!isSidebarOpen && (
                <button
                  type="button"
                  onClick={() => setIsSidebarOpen(true)}
                  className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-gray-700 text-gray-300 hover:bg-gray-700 hover:text-white transition"
                  aria-label="Show sidebar"
                >
                  <IconMenu className="h-4 w-4" />
                </button>
              )}
              <p className="text-lg font-semibold text-white">
                {conversationTitle || `Conversation ${conversationNumber}`}
              </p>
            </div>
          </div>
          <p className="text-sm text-gray-400 mt-1">{statusLine}</p>
        </header>

        <div className="flex-1 min-h-0">
          <ChatWindow messages={messages} isLoading={isLoading} />
        </div>

        {error && (
          <div className="px-6 pt-2">
            <div className="max-w-3xl mx-auto w-full rounded-lg border border-red-500/40 bg-red-500/10 text-sm text-red-200 px-4 py-2 flex items-center justify-between gap-4">
              <span>{error}</span>
              <button
                type="button"
                onClick={() => setError(null)}
                className="text-xs font-medium underline-offset-2 hover:underline"
              >
                Dismiss
              </button>
            </div>
          </div>
        )}

        <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} />
      </section>
    </div>
  );
};

export default Chat;
