import React, { useCallback, useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Sidebar from "../components/chats/Sidebar";
import ChatWindow from "../components/chats/ChatWindow";
import ChatInput from "../components/chats/ChatInput";
import { IconMenu } from "../components/chats/IconComponents.jsx";
import chatService from "../services/chatService";
import { useAuth } from "../contexts/AuthContext";
import "./Chat.css";

const createWelcomeMessage = () => ({
  id: `welcome-${Date.now()}`,
  sender: "bot",
  text: "Hello! I'm The Alchemist. Ask me anything about your project, research, or code and I'll do my best to help.",
  timestamp: new Date().toISOString(),
});

const generateId = (prefix) =>
  `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2)}`;

/** Convert a DB message record to the shape the ChatWindow expects. */
const dbMessageToLocal = (msg) => ({
  id: msg.id,
  sender: msg.sender,
  text: msg.content,
  image: msg.meta_data?.plot || null,
  chart_spec: msg.meta_data?.chart_spec || null,
  timestamp: msg.created_at,
});

const Chat = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [messages, setMessages] = useState([createWelcomeMessage()]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  // Used to tell Sidebar to re-fetch its session list
  const [sidebarRefreshKey, setSidebarRefreshKey] = useState(0);

  // Track whether this is the first user message in the session (for title update)
  const isFirstMessageRef = useRef(true);

  // Load messages from DB when sessionId changes
  useEffect(() => {
    if (sessionId) {
      loadSessionMessages(sessionId);
    } else {
      setMessages([createWelcomeMessage()]);
      isFirstMessageRef.current = true;
    }
  }, [sessionId]);

  const loadSessionMessages = async (sid) => {
    try {
      setIsLoading(true);
      const dbMessages = await chatService.getMessages(sid);
      if (dbMessages.length === 0) {
        setMessages([createWelcomeMessage()]);
        isFirstMessageRef.current = true;
      } else {
        setMessages(dbMessages.map(dbMessageToLocal));
        isFirstMessageRef.current = false;
      }
    } catch (err) {
      console.error("Failed to load session messages:", err);
      setMessages([createWelcomeMessage()]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartNewChat = useCallback(async () => {
    if (!user) {
      // Not logged in — just clear local state
      setMessages([createWelcomeMessage()]);
      setError(null);
      isFirstMessageRef.current = true;
      navigate("/chat");
      return;
    }
    try {
      const newSession = await chatService.createSession("New Chat");
      setSidebarRefreshKey((k) => k + 1);
      navigate(`/chat/${newSession.id}`);
    } catch (err) {
      console.error("Failed to create session:", err);
      setMessages([createWelcomeMessage()]);
      setError(null);
      navigate("/chat");
    }
  }, [user, navigate]);

  const handleSendMessage = useCallback(
    async (rawMessage) => {
      const text = rawMessage.trim();
      if (!text || isLoading) return;

      // --- Resolve active session ---
      let activeSessionId = sessionId || null;

      if (!activeSessionId && user) {
        // First message with no session yet — create one
        try {
          const newSession = await chatService.createSession("New Chat");
          activeSessionId = newSession.id;
          setSidebarRefreshKey((k) => k + 1);
          // Update URL without triggering a full re-render / message reload
          navigate(`/chat/${activeSessionId}`, { replace: true });
        } catch (err) {
          console.error("Failed to create session:", err);
          // Continue without session — messages won't be persisted
        }
      }

      // --- Optimistically add user message ---
      const userMessage = {
        id: generateId("user"),
        sender: "user",
        text,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMessage]);
      setError(null);
      setIsLoading(true);

      // --- Update session title on first user message ---
      if (isFirstMessageRef.current && activeSessionId && user) {
        isFirstMessageRef.current = false;
        const title = text.length > 50 ? `${text.slice(0, 47)}...` : text;
        chatService.updateSession(activeSessionId, title).catch(() => {});
        setSidebarRefreshKey((k) => k + 1);
      }

      try {
        const botResponse = await chatService.getLLMResponse(text, activeSessionId);
        setMessages((prev) => [
          ...prev,
          {
            id: generateId("bot"),
            sender: "bot",
            text: botResponse.message,
            image: botResponse.plot_file_path || null,
            chart_spec: botResponse.chart_spec || null,
            timestamp: new Date().toISOString(),
          },
        ]);
      } catch (err) {
        console.error("Failed to fetch assistant response", err);
        setError("The assistant is unavailable right now. Please try again in a moment.");
      } finally {
        setIsLoading(false);
      }
    },
    [sessionId, isLoading, user, navigate]
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
        style={{ width: isSidebarOpen ? "280px" : "80px", flexShrink: 0, transition: "width 0.3s ease" }}
      >
        <Sidebar
          onStartNewChat={handleStartNewChat}
          onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
          isOpen={isSidebarOpen}
          currentSessionId={sessionId || null}
          refreshKey={sidebarRefreshKey}
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
              />
            </div>
          </div>
        )}

        <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} />
      </section>
    </div>
  );
};

export default Chat;
