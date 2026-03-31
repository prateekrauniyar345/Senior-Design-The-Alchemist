import React, { useCallback, useEffect, useMemo, useState } from "react";
import Sidebar from "../components/chats/Sidebar";
import ChatWindow from "../components/chats/ChatWindow";
import ChatInput from "../components/chats/ChatInput";
import chatService from "../services/chatService";
import "./Chat.css";

const createWelcomeMessage = () => ({
  id: `welcome-${Date.now()}`,
  sender: "bot",
  text: "Hello! I’m The Alchemist. Ask me anything about your project, research, or code and I’ll do my best to help.",
  timestamp: new Date().toISOString(),
  isWelcome: true,
});

const generateId = (prefix) =>
  `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2)}`;

const normalizeDbMessage = (message) => {
  const role = message.sender || message.role;
  const sender = role === "assistant" ? "bot" : role === "user" ? "user" : "bot";
  const image =
    message?.image ||
    message?.metadata?.plot_file_path ||
    message?.metadata?.image ||
    message?.plot_file_path ||
    (message?.output_type === "plot" ? message?.meta_data : null) ||
    null;
  return {
    id: message.id || generateId("msg"),
    sender,
    text: message.content || "",
    image,
    timestamp: message.created_at || new Date().toISOString(),
  };
};

const Chat = () => {
  const [messages, setMessages] = useState([createWelcomeMessage()]);
  const [chats, setChats] = useState([]);
  const [currentChatId, setCurrentChatId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [error, setError] = useState(null);

  const currentChatTitle = useMemo(() => {
    const active = chats.find((chat) => chat.id === currentChatId);
    return active?.title || "New conversation";
  }, [chats, currentChatId]);

  const loadChats = useCallback(async () => {
    try {
      const data = await chatService.listChats();
      setChats(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Failed to load chats:", err);
    }
  }, []);

  useEffect(() => {
    loadChats();
  }, [loadChats]);

  const handleStartNewChat = useCallback(async () => {
    try {
      setError(null);
      setIsLoading(true);

      const newChat = await chatService.createChat("New chat");
      setCurrentChatId(newChat.id);
      setMessages([createWelcomeMessage()]);

      await loadChats();
    } catch (err) {
      console.error("Failed to create chat:", err);
      setError("Could not start a new chat right now.");
    } finally {
      setIsLoading(false);
    }
  }, [loadChats]);

  const handleSelectChat = useCallback(async (chatId) => {
    try {
      setError(null);
      setIsLoading(true);

      const fullChat = await chatService.getChat(chatId);
      const dbMessages = Array.isArray(fullChat?.messages)
        ? fullChat.messages.map(normalizeDbMessage)
        : [];

      setCurrentChatId(chatId);
      setMessages(dbMessages.length ? dbMessages : [createWelcomeMessage()]);
    } catch (err) {
      console.error("Failed to load chat:", err);
      setError("Could not load this conversation.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleDeleteChat = useCallback(
    async (chatId) => {
      try {
        setError(null);
        await chatService.deleteChat(chatId);

        const wasActive = currentChatId === chatId;

        await loadChats();

        if (wasActive) {
          setCurrentChatId(null);
          setMessages([createWelcomeMessage()]);
        }
      } catch (err) {
        console.error("Failed to delete chat:", err);
        setError("Could not delete this conversation.");
      }
    },
    [currentChatId, loadChats]
  );

  const handleSendMessage = useCallback(
    async (rawMessage) => {
      const text = rawMessage.trim();
      if (!text || isLoading) return;

      const optimisticUserMessage = {
        id: generateId("user"),
        sender: "user",
        text,
        timestamp: new Date().toISOString(),
      };

      setError(null);
      setMessages((prev) => {
        const withoutWelcome =
          prev.length === 1 && prev[0]?.isWelcome ? [] : prev;
        return [...withoutWelcome, optimisticUserMessage];
      });
      setIsLoading(true);

      let activeChatId = currentChatId;

      try {
        if (!activeChatId) {
          const newChat = await chatService.createChat("New chat");
          activeChatId = newChat.id;
          setCurrentChatId(activeChatId);
        }

        await chatService.createMessage(activeChatId, {
          role: "user",
          content: text,
          metadata: {},
        });

        const botResponse = await chatService.getLLMResponse(text);

        const assistantText =
          botResponse?.message ||
          botResponse?.answer ||
          botResponse?.response ||
          "No response received.";

        const assistantMetadata = {
          ...(botResponse?.metadata || {}),
          ...(botResponse?.plot_file_path
            ? { plot_file_path: botResponse.plot_file_path }
            : {}),
        };

        const savedAssistantMessage = await chatService.createMessage(activeChatId, {
          role: "assistant",
          content: assistantText,
          metadata: assistantMetadata,
        });

        const normalizedAssistant = normalizeDbMessage(savedAssistantMessage);

        setMessages((prev) => [...prev, normalizedAssistant]);
        await loadChats();
      } catch (err) {
        console.error("Failed to fetch assistant response", err);
        setError(
          "The assistant is unavailable right now. Please try again in a moment."
        );
      } finally {
        setIsLoading(false);
      }
    },
    [currentChatId, isLoading, loadChats]
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
        style={{
          width: isSidebarOpen ? "280px" : "80px",
          flexShrink: 0,
          transition: "width 0.3s ease",
        }}
      >
        <Sidebar
          onStartNewChat={handleStartNewChat}
          onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
          isOpen={isSidebarOpen}
          chats={chats}
          currentChatId={currentChatId}
          onSelectChat={handleSelectChat}
          onDeleteChat={handleDeleteChat}
        />
      </div>

      {isSidebarOpen && (
        <div
          className="w-auto"
          style={{ width: "1px", backgroundColor: "rgba(255, 255, 255, 0.1)" }}
          aria-hidden="true"
        />
      )}

      <section className="d-flex flex-column flex-grow-1 chat-main">
        <div className="px-4 pt-3 pb-2 border-bottom border-secondary-subtle">
          <div className="small text-secondary">{statusLine}</div>
          <div className="fw-semibold text-light">{currentChatTitle}</div>
        </div>

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