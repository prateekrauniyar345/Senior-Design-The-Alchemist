// Frontend/src/pages/Chat.jsx
import React, { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Sidebar from "../components/chats/Sidebar";
import ChatWindow from "../components/chats/ChatWindow";
import ChatInput from "../components/chats/ChatInput";
import chatService from "../services/chatService";
import "./Chat.css";

const WELCOME_MESSAGE_TEXT =
  "Hello! I’m The Alchemist. Ask me anything about your project, research, or code and I’ll do my best to help.";

const createWelcomeMessage = () => ({
  id: `welcome-${Date.now()}`,
  sender: "bot",
  text: WELCOME_MESSAGE_TEXT,
  timestamp: new Date().toISOString(),
});

const generateId = (prefix) =>
  `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2)}`;

const mapApiMessagesToUi = (rows) =>
  (rows || []).map((m) => {
    const meta =
      m.meta_data && typeof m.meta_data === "object" ? m.meta_data : {};
    let sender = m.sender;
    if (sender === "assistant" || sender === "agent") sender = "bot";
    return {
      id: String(m.id),
      sender,
      text: m.content,
      timestamp: m.created_at,
      chartSpec: meta.chart_spec ?? null,
      chartData: meta.chart_data ?? null,
      sampleData: meta.sample_data ?? null,
      image: meta.image ?? meta.plot_file_path ?? null,
    };
  });

const Chat = () => {
  const navigate = useNavigate();
  const { sessionId: routeSessionId } = useParams();

  const [messages, setMessages] = useState([createWelcomeMessage()]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [conversationTitle, setConversationTitle] = useState("New conversation");
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [sessions, setSessions] = useState([]);
  const [pendingSessionId, setPendingSessionId] = useState(null);

  const effectiveSessionId = routeSessionId ?? pendingSessionId;

  const refreshSessions = useCallback(async () => {
    try {
      const list = await chatService.getSessions();
      setSessions(Array.isArray(list) ? list : []);
    } catch (err) {
      console.error("Failed to load chat sessions", err);
      setSessions([]);
    }
  }, []);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const list = await chatService.getSessions();
        if (cancelled) return;
        setSessions(Array.isArray(list) ? list : []);

        if (!routeSessionId) {
          setMessages([createWelcomeMessage()]);
          setConversationTitle("New conversation");
          return;
        }

        const msgs = await chatService.getMessages(routeSessionId);
        if (cancelled) return;
        setMessages(mapApiMessagesToUi(msgs));
        const s = list.find((x) => String(x.id) === String(routeSessionId));
        setConversationTitle(s?.title ?? "Chat");
      } catch (err) {
        console.error("Failed to load chat", err);
        if (!cancelled) {
          setError("Could not load this conversation.");
          setMessages([createWelcomeMessage()]);
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [routeSessionId]);

  const handleStartNewChat = useCallback(() => {
    navigate("/chat", { replace: true });
    setPendingSessionId(null);
    setMessages([createWelcomeMessage()]);
    setIsLoading(false);
    setError(null);
    setConversationTitle("New conversation");
  }, [navigate]);

  const handleSelectChat = useCallback(
    (sessionId) => {
      navigate(`/chat/${sessionId}`, { replace: false });
    },
    [navigate]
  );

  const handleSendMessage = useCallback(
    async (rawMessage) => {
      const text = rawMessage.trim();
      if (!text || isLoading) return;

      let sessionId = routeSessionId ?? pendingSessionId;

      if (!sessionId) {
        try {
          const session = await chatService.createSession("New conversation");
          sessionId = session.id;
          setPendingSessionId(sessionId);
          await chatService.saveMessage(
            sessionId,
            WELCOME_MESSAGE_TEXT,
            "bot",
            "text",
            null
          );
          await refreshSessions();
        } catch (err) {
          console.error("Failed to create chat session", err);
          setError("Could not start a saved chat. Please sign in and try again.");
          return;
        }
      }

      const userMessage = {
        id: generateId("user"),
        sender: "user",
        text,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setError(null);
      setIsLoading(true);

      const wasNewConversation = conversationTitle === "New conversation";
      const readableTitle =
        text.length > 36 ? `${text.slice(0, 33)}...` : text;
      if (wasNewConversation) {
        setConversationTitle(readableTitle);
      }

      try {
        const botResponse = await chatService.getLLMResponse(text, sessionId);
        setMessages((prev) => [
          ...prev,
          {
            id: generateId("bot"),
            sender: "bot",
            text: botResponse.message,
            chartSpec: botResponse.chart_spec,
            chartData: botResponse.chart_data,
            sampleData: botResponse.sample_data,
            image: botResponse.plot_file_path ?? null,
            timestamp: new Date().toISOString(),
          },
        ]);

        if (
          !routeSessionId ||
          String(routeSessionId) !== String(sessionId)
        ) {
          navigate(`/chat/${sessionId}`, { replace: true });
        }
        setPendingSessionId(null);

        try {
          if (wasNewConversation) {
            await chatService.updateSession(sessionId, readableTitle);
          }
          await refreshSessions();
        } catch (e) {
          console.warn("Session title refresh failed", e);
        }
      } catch (err) {
        console.error("Failed to fetch assistant response", err);
        setError(
          "The assistant is unavailable right now. Please try again in a moment."
        );
        if (sessionId) {
          try {
            const synced = await chatService.getMessages(sessionId);
            setMessages(mapApiMessagesToUi(synced));
          } catch (_) {
            /* keep optimistic UI if sync fails */
          }
        }
      } finally {
        setIsLoading(false);
      }
    },
    [
      conversationTitle,
      isLoading,
      navigate,
      pendingSessionId,
      refreshSessions,
      routeSessionId,
    ]
  );

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
          sessions={sessions}
          activeSessionId={effectiveSessionId}
          onSelectChat={handleSelectChat}
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
