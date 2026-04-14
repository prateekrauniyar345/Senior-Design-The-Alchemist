// Frontend/src/pages/Chat.jsx
import React, { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Sidebar from "../components/chats/Sidebar";
import ChatWindow from "../components/chats/ChatWindow";
import ChatInput from "../components/chats/ChatInput";
import chatService from "../services/chatService";
import "./Chat.css";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

const createWelcomeMessage = () => ({
  id: `welcome-${Date.now()}`,
  sender: "bot",
  text: "Hello! I’m The Alchemist. Ask me anything about your project, research, or code and I’ll do my best to help.",
  timestamp: new Date().toISOString(),
});

const generateId = (prefix) =>
  `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2)}`;

const mapApiMessage = (msg) => {
  const meta =
    msg.meta_data && typeof msg.meta_data === "object" ? msg.meta_data : {};
  const plotArt = (msg.artifacts || []).find(
    (a) => a.artifact_type === "plot_image"
  );
  let image = null;
  if (plotArt?.file_url) {
    const u = plotArt.file_url;
    image = u.startsWith("http") ? u : `${API_BASE}${u}`;
  }
  return {
    id: msg.id,
    sender: msg.sender === "user" ? "user" : "bot",
    text: msg.content,
    timestamp: msg.created_at,
    chartSpec: meta.chart_spec ?? null,
    sampleData: meta.sample_data ?? null,
    chartData: meta.chart_data ?? null,
    image,
  };
};

const Chat = () => {
  const navigate = useNavigate();
  const { sessionId: routeSessionId } = useParams();
  const [messages, setMessages] = useState([createWelcomeMessage()]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const loadRequestRef = useRef(0);
  const currentRouteSessionRef = useRef(routeSessionId || null);

  useEffect(() => {
    currentRouteSessionRef.current = routeSessionId || null;
  }, [routeSessionId]);

  const refreshSessions = useCallback(async () => {
    try {
      const data = await chatService.getSessions();
      setSessions(Array.isArray(data) ? data : []);
    } catch (e) {
      console.error(e);
      setSessions([]);
    }
  }, []);

  useEffect(() => {
    refreshSessions();
  }, [refreshSessions]);

  const handleStartNewChat = useCallback(async () => {
    try {
      const session = await chatService.createSession("New Chat");
      setSessions((prev) => [
        session,
        ...prev.filter((s) => s.id !== session.id),
      ]);
      setMessages([createWelcomeMessage()]);
      setIsLoading(false);
      setError(null);
      navigate(`/chat/${session.id}`);
    } catch (e) {
      console.error(e);
      setError("Could not create a new chat. Please try again.");
    }
  }, [navigate]);

  const handleSelectSession = useCallback(
    (sessionId) => {
      navigate(`/chat/${sessionId}`);
    },
    [navigate]
  );

  const handleDeleteSession = useCallback(
    async (sessionId) => {
      try {
        await chatService.deleteSession(sessionId);
        setSessions((prev) => prev.filter((s) => s.id !== sessionId));
        if (String(routeSessionId) === String(sessionId)) {
          navigate("/chat");
          setMessages([createWelcomeMessage()]);
        }
      } catch (e) {
        console.error(e);
        setError("Could not delete this chat.");
      }
    },
    [navigate, routeSessionId]
  );

  useEffect(() => {
    const requestId = Date.now() + Math.random();
    loadRequestRef.current = requestId;

    if (!routeSessionId) {
      setMessages([createWelcomeMessage()]);
      return;
    }

    setError(null);
    console.log("[chat.load] begin", { routeSessionId, requestId });

    (async () => {
      try {
        const raw = await chatService.getMessages(routeSessionId);
        const mapped = (raw || []).map(mapApiMessage);
        const isLatest = loadRequestRef.current === requestId;
        const stillOnSameRoute =
          String(currentRouteSessionRef.current) === String(routeSessionId);
        console.log("[chat.load] done", {
          routeSessionId,
          requestId,
          count: mapped.length,
          isLatest,
          stillOnSameRoute,
        });
        if (!isLatest || !stillOnSameRoute) {
          console.log("[chat.load] stale response ignored", { routeSessionId, requestId });
          return;
        }
        setMessages(mapped.length ? mapped : [createWelcomeMessage()]);
      } catch (e) {
        console.error(e);
        setError("Could not load this chat.");
      }
    })();
  }, [routeSessionId]);

  const handleSendMessage = useCallback(
    async (rawMessage) => {
      const text = rawMessage.trim();
      if (!text || isLoading) return;
      let effectiveSessionId = routeSessionId || null;

      // Ensure sends are always attached to a real persisted session.
      if (!effectiveSessionId) {
        const created = await chatService.createSession("New Chat");
        effectiveSessionId = created.id;
        setSessions((prev) => [
          created,
          ...prev.filter((s) => s.id !== created.id),
        ]);
        navigate(`/chat/${created.id}`);
      }
      console.log("[chat.send] ids", {
        routeSessionId,
        activeSessionId: routeSessionId,
        targetSessionId: effectiveSessionId,
      });

      const userMessage = {
        id: generateId("user"),
        sender: "user",
        text,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setError(null);
      setIsLoading(true);

      const shouldUpdateTitle =
        effectiveSessionId &&
        sessions.some(
          (s) => s.id === effectiveSessionId && s.title === "New Chat"
        );

      try {
        const botResponse = await chatService.getLLMResponse(
          text,
          effectiveSessionId || undefined
        );
        console.log("[chat.send] response", {
          targetSessionId: effectiveSessionId,
          success: botResponse?.success,
          hasMessage: Boolean(botResponse?.message),
        });
        const plotPath = botResponse.plot_file_path;
        const image = plotPath
          ? plotPath.startsWith("http")
            ? plotPath
            : `${API_BASE}${plotPath}`
          : null;
        setMessages((prev) => [
          ...prev,
          {
            id: generateId("bot"),
            sender: "bot",
            text: botResponse.message,
            chartSpec: botResponse.chart_spec,
            chartData: botResponse.chart_data,
            sampleData: botResponse.sample_data,
            image,
            timestamp: new Date().toISOString(),
          },
        ]);
        if (shouldUpdateTitle) {
          const readableTitle =
            text.length > 36 ? `${text.slice(0, 33)}...` : text;
          await chatService.updateSession(effectiveSessionId, readableTitle);
          setSessions((prev) =>
            prev.map((s) =>
              s.id === effectiveSessionId ? { ...s, title: readableTitle } : s
            )
          );
        }
      } catch (err) {
        console.error("Failed to fetch assistant response", err);
        setError(
          "The assistant is unavailable right now. Please try again in a moment."
        );
      } finally {
        setIsLoading(false);
      }
    },
    [isLoading, navigate, routeSessionId, sessions]
  );

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
          sessions={sessions}
          activeSessionId={routeSessionId || null}
          onSelectSession={handleSelectSession}
          onDeleteSession={handleDeleteSession}
          onStartNewChat={handleStartNewChat}
          onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
          isOpen={isSidebarOpen}
        />
      </div>

      {isSidebarOpen && (
        <div
          className="w-auto"
          style={{
            width: "1px",
            backgroundColor: "rgba(255, 255, 255, 0.1)",
          }}
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
