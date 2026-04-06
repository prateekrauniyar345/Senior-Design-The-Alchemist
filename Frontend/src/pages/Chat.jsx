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

  /** Latest route param — read after awaits so stale loads never overwrite the active chat */
  const routeSessionIdRef = useRef(sessionId);
  routeSessionIdRef.current = sessionId ?? null;

  const [messages, setMessages] = useState(() =>
    sessionId ? [] : [createWelcomeMessage()]
  );
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  // Used to tell Sidebar to re-fetch its session list
  const [sidebarRefreshKey, setSidebarRefreshKey] = useState(0);

  // Track whether this is the first user message in the session (for title update)
  const isFirstMessageRef = useRef(true);
  // After first-message session creation we navigate before getLLMResponse persists rows;
  // skip the fetch that would replace optimistic messages with an empty list.
  const suppressSessionFetchRef = useRef(null);
  /** Bumped when the sessionId effect starts a fetch — stale completions must not clear isLoading */
  const sessionFetchGenRef = useRef(0);

  useEffect(() => {
    console.log("[Chat DEBUG] Chat component MOUNT");
    return () => console.log("[Chat DEBUG] Chat component UNMOUNT");
  }, []);

  // Load messages from DB when sessionId changes
  useEffect(() => {
    console.log("[Chat DEBUG] sessionId effect fired (route vs ref)", {
      sessionId: sessionId ?? null,
      routeRef: routeSessionIdRef.current,
      suppress: suppressSessionFetchRef.current,
    });
    if (!sessionId) {
      suppressSessionFetchRef.current = null;
      console.log("[Chat DEBUG] sessionId effect: no id → welcome only");
      setMessages([createWelcomeMessage()]);
      isFirstMessageRef.current = true;
      setIsLoading(false);
      return;
    }
    if (
      suppressSessionFetchRef.current !== null &&
      String(suppressSessionFetchRef.current) === String(sessionId)
    ) {
      console.log("[Chat DEBUG] sessionId effect: SKIP fetch (first-send suppress)", String(sessionId));
      return;
    }
    sessionFetchGenRef.current += 1;
    const fetchGen = sessionFetchGenRef.current;
    console.log("[Chat DEBUG] sessionId effect: loadSessionMessages", String(sessionId), "gen=", fetchGen);
    loadSessionMessages(sessionId, { manageLoading: true, allowEmptyWipe: true, fetchGen });
  }, [sessionId]);

  const loadSessionMessages = async (
    sid,
    { manageLoading = true, allowEmptyWipe = true, fetchGen } = {}
  ) => {
    console.log("[Chat DEBUG] loadSessionMessages START", {
      sid: String(sid),
      manageLoading,
      allowEmptyWipe,
      fetchGen: fetchGen ?? null,
    });
    try {
      if (manageLoading) setIsLoading(true);
      const dbMessages = await chatService.getMessages(sid);
      const rows = Array.isArray(dbMessages) ? dbMessages : [];
      console.log("[Chat DEBUG] loadSessionMessages fetched count", rows.length, {
        sid: String(sid),
        routeNow: routeSessionIdRef.current,
      });

      if (String(routeSessionIdRef.current) !== String(sid)) {
        console.log("[Chat DEBUG] loadSessionMessages STALE — skip setMessages", {
          requested: String(sid),
          routeNow: String(routeSessionIdRef.current),
        });
        return;
      }

      if (rows.length === 0) {
        if (!allowEmptyWipe) {
          console.log(
            "[Chat DEBUG] loadSessionMessages: empty result, skip wipe (allowEmptyWipe=false)"
          );
          return;
        }
        console.log("[Chat DEBUG] loadSessionMessages: empty → welcome only");
        setMessages([createWelcomeMessage()]);
        isFirstMessageRef.current = true;
      } else {
        console.log("[Chat DEBUG] loadSessionMessages: setMessages from DB", rows.length, "rows");
        setMessages(rows.map(dbMessageToLocal));
        isFirstMessageRef.current = false;
      }
    } catch (err) {
      console.error("[Chat DEBUG] loadSessionMessages ERROR", err);
      if (String(routeSessionIdRef.current) !== String(sid)) {
        console.log("[Chat DEBUG] loadSessionMessages ERROR ignored (stale)", String(sid));
        return;
      }
      if (allowEmptyWipe) {
        console.log("[Chat DEBUG] loadSessionMessages: error → welcome only");
        setMessages([createWelcomeMessage()]);
      }
    } finally {
      if (manageLoading) {
        const superseded = fetchGen !== undefined && fetchGen !== sessionFetchGenRef.current;
        if (!superseded) {
          setIsLoading(false);
        } else {
          console.log("[Chat DEBUG] loadSessionMessages END — isLoading unchanged (superseded gen)", {
            fetchGen,
            currentGen: sessionFetchGenRef.current,
          });
        }
      }
      console.log("[Chat DEBUG] loadSessionMessages END", {
        sid: String(sid),
        routeNow: routeSessionIdRef.current,
      });
    }
  };

  const handleStartNewChat = useCallback(async () => {
    setMessages([createWelcomeMessage()]);
    setError(null);
    isFirstMessageRef.current = true;
    setSidebarRefreshKey((k) => k + 1);
    navigate("/chat");
  }, [navigate]);

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
          console.log("[Chat DEBUG] createSession result", { id: activeSessionId });
          setSidebarRefreshKey((k) => k + 1);
          suppressSessionFetchRef.current = activeSessionId;
          console.log("[Chat DEBUG] navigate", { to: `/chat/${activeSessionId}`, replace: true });
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
      setMessages((prev) => {
        const next = [...prev, userMessage];
        console.log("[Chat DEBUG] setMessages optimistic USER", {
          prevLen: prev.length,
          nextLen: next.length,
        });
        return next;
      });
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
        console.log("[Chat DEBUG] getLLMResponse START", {
          activeSessionId,
          hasUser: !!user,
        });
        const botResponse = await chatService.getLLMResponse(text, activeSessionId);
        console.log("[Chat DEBUG] getLLMResponse END");
        const failed = botResponse.success === false;
        const replyText = failed
          ? `Agent workflow failed${botResponse.error ? `: ${botResponse.error}` : ""}`
          : botResponse.message;
        setMessages((prev) => {
          const next = [
            ...prev,
            {
              id: generateId("bot"),
              sender: "bot",
              text: replyText,
              image: failed ? null : botResponse.plot_file_path || null,
              chart_spec: failed ? null : botResponse.chart_spec || null,
              timestamp: new Date().toISOString(),
            },
          ];
          console.log("[Chat DEBUG] setMessages after BOT", { prevLen: prev.length, nextLen: next.length });
          return next;
        });
        if (activeSessionId && user) {
          try {
            await loadSessionMessages(activeSessionId, {
              manageLoading: false,
              allowEmptyWipe: false,
            });
          } catch (_) {
            /* keep optimistic state */
          }
        }
      } catch (err) {
        console.error("[Chat DEBUG] getLLMResponse FAILED", err);
        console.error("Failed to fetch assistant response", err);
        setError("The assistant is unavailable right now. Please try again in a moment.");
      } finally {
        console.log("[Chat DEBUG] first-send finally: clear suppress, isLoading false");
        suppressSessionFetchRef.current = null;
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
          shouldFetchSessions={Boolean(sessionId)}
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
