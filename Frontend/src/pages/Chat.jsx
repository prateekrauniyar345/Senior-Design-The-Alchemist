import React, { useCallback, useState } from "react";
import Sidebar from "../components/chats/Sidebar";
import ChatWindow from "../components/chats/ChatWindow";
import ChatInput from "../components/chats/ChatInput";
import { IconMenu } from "../components/chats/IconComponents.jsx";
import chatService from "../services/chatService";
import "./Chat.css";

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
            text: botResponse.message,
            image: botResponse.plot_file_path, // Add the image path to the message object
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
    <div className="d-flex vh-100 chat-container">
      <div
        className="sidebar-container"
        style={{ width: isSidebarOpen ? '280px' : '80px', flexShrink: 0, transition: 'width 0.3s ease' }}
      >
        <Sidebar
          onStartNewChat={handleStartNewChat}
          onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
          isOpen={isSidebarOpen}
        />
      </div>

      {isSidebarOpen && <div className="w-auto" style={{width: "1px", backgroundColor: "rgba(255, 255, 255, 0.1)"}} aria-hidden="true" />}

      <section className="d-flex flex-column flex-grow-1 chat-main">
        <div className="flex-grow-1 chat-window-wrapper">
          <ChatWindow messages={messages} isLoading={isLoading} />
        </div>

        {error && (
          <div className="px-4 pt-2">
            <div className="alert alert-danger error-banner d-flex justify-content-between align-items-center">
              <span>{error}</span>
              <button
                type="button"
                onClick={() => setError(null)}
                className="btn-close"
                aria-label="Dismiss"
              ></button>
            </div>
          </div>
        )}

        <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} />
      </section>
    </div>
  );
};

export default Chat;
