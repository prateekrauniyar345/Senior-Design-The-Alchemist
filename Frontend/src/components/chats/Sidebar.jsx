import React, { useState, useEffect } from "react";
import { Plus, User, Settings, X, Menu } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import ProfileModal from "./ProfileModal";
import SettingsModal from "./SettingsModal";
import chatService from "../../services/chatService";
import { useAuth } from "../../contexts/AuthContext";
import "./Sidebar.css";

const Sidebar = ({
  onStartNewChat = () => {},
  onToggleSidebar = () => {},
  isOpen = true,
  currentSessionId = null,
  refreshKey = 0,
  /** When false (e.g. on /chat with no session), do not list past chats—fresh UI only */
  shouldFetchSessions = true,
}) => {
  const { user } = useAuth();
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [sessions, setSessions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  // Fetch sessions only when viewing a specific chat; on plain /chat keep list empty (no auto history)
  useEffect(() => {
    if (!user) {
      setSessions([]);
      setIsLoading(false);
      return;
    }
    if (!shouldFetchSessions) {
      setSessions([]);
      setIsLoading(false);
      return;
    }
    loadSessions();
  }, [user, refreshKey, shouldFetchSessions]);

  const loadSessions = async () => {
    try {
      setIsLoading(true);
      const data = await chatService.getSessions();
      const list = Array.isArray(data)
        ? data
        : data && Array.isArray(data.sessions)
          ? data.sessions
          : [];
      if (data != null && !Array.isArray(data) && !Array.isArray(data?.sessions)) {
        console.warn("[Sidebar] getSessions unexpected shape; using []", data);
      }
      setSessions(list);
    } catch (error) {
      console.error("Failed to load sessions:", error);
      setSessions([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = () => {
    // Delegate to Chat.jsx which handles session creation + navigation
    onStartNewChat();
  };

  const handleSelectChat = (sessionId) => {
    navigate(`/chat/${sessionId}`);
  };

  return (
    <aside
      className={`d-flex flex-column h-100 text-white sidebar`}
      aria-label="Sidebar"
      aria-hidden={!isOpen}
    >
      {isOpen ? (
        <>
          {/* Logo + Toggle */}
          <div className="d-flex align-items-center justify-content-between px-4 py-4 sidebar-header">
            <div className="d-flex align-items-center gap-3">
              <img
                src="/images/the-alchemist.png"
                alt="The Alchemist logo"
                className="rounded object-fit-cover p-1"
                style={{ height: '3rem', width: '3rem', backgroundColor: 'rgba(0,0,0,0.2)' }}
                // loading="lazy"
              />
              <div className="d-flex flex-column" style={{ lineHeight: '1.2' }}>
                <span className="text-uppercase fw-semibold fs-6 sidebar-logo-text">
                  The Alchemist
                </span>
                <span className="">AI Research Crew</span>
              </div>
            </div>
            <button
              type="button"
              onClick={() => onToggleSidebar(false)}
              className="btn btn-outline-secondary d-inline-flex align-items-center justify-content-center rounded p-2 sidebar-toggle-btn"
              aria-label="Close sidebar"
            >
              <X size={16} />
            </button>
          </div>

          {/* New Chat */}
          <div className="p-4 sidebar-header">
            <button
              className="btn w-100 d-flex align-items-center gap-3 fw-semibold py-3 px-4 rounded new-chat-btn text-white rounded-4"
              onClick={handleNewChat}
              type="button"
              disabled={isLoading}
            >
              <Plus size={18} />
              New Chat
            </button>
          </div>

          {/* Chat List */}
          <nav className="flex-fill overflow-auto p-4">
            <div className="d-flex flex-column gap-2">
              {isLoading ? (
                <div className="text-center py-4 text-secondary">
                  <small>Loading chats...</small>
                </div>
              ) : sessions.length > 0 ? (
                sessions.map((session) => (
                  <button
                    key={session.id}
                    onClick={() => handleSelectChat(session.id)}
                    className={`btn w-100 text-start px-4 py-3 rounded fw-medium rounded-4 ${
                      currentSessionId === session.id 
                        ? 'chat-list-btn-active' 
                        : 'chat-list-btn'
                    }`}
                      title={session.title}
                  >
                    <div className="text-truncate" style={{ fontSize: "1.1rem", fontWeight: "500" }}>
                      {session.title}
                    </div>
                    <small className="d-block text-truncate" style={{ color: "white", fontSize: "0.75rem" }}>
                      {new Date(session.created_at).toLocaleDateString()}
                    </small>
                  </button>
                ))
              ) : (
                <div className="text-center py-4 text-secondary">
                  <small>No chats yet. Start a new one!</small>
                </div>
              )}
            </div>
          </nav>

          {/* Bottom buttons */}
          <div className="p-4 d-flex align-items-center justify-content-between sidebar-footer fs-5">
            <Link
              to="/"
              className="text-decoration-none fw-medium small sidebar-footer-link"
            >
              Dashboard
            </Link>
            <div className="d-flex gap-3">
              <button
                onClick={() => setIsProfileOpen(true)}
                className="icon-btn"
                aria-label="Profile"
                title="Profile"
              >
                <User size={20} className="sidebar-footer-icon" />
              </button>
              <button
                onClick={() => setIsSettingsOpen(true)}
                className="icon-btn"
                aria-label="Settings"
                title="Settings"
              >
                <Settings size={20} className="sidebar-footer-icon" />
              </button>
            </div>
          </div>
        </>
      ) : (
        /* Mini Sidebar - Collapsed State */
        <div className="d-flex flex-column align-items-center py-4 gap-4 h-100">
          {/* Menu toggle button */}
          <button
            type="button"
            onClick={() => onToggleSidebar(true)}
            className="btn btn-outline-secondary d-inline-flex align-items-center justify-content-center rounded-4 p-2 sidebar-toggle-btn"
            aria-label="Open sidebar"
            title="Open sidebar"
          >
            <Menu size={20} />
          </button>

          {/* Logo */}
          <button
            type="button"
            onClick={() => onToggleSidebar(true)}
            className="p-0 border-0 bg-transparent"
            aria-label="Open sidebar"
            title="The Alchemist"
          >
            <img
              src="/images/the-alchemist.png"
              alt="The Alchemist logo"
              className="rounded-4 object-fit-cover p-1"
              style={{ 
                height: '2.5rem', 
                width: '2.5rem', 
                backgroundColor: 'rgba(0,0,0,0.2)',
                cursor: 'pointer'
              }}
              loading="lazy"
            />
          </button>

          {/* New Chat button - just icon */}
          <button
            className="btn btn-outline-secondary d-inline-flex align-items-center justify-content-center rounded-4 p-2"
            onClick={handleNewChat}
            type="button"
            aria-label="New chat"
            title="New chat"
            disabled={isLoading}
            style={{ 
              width: '44px', 
              height: '44px',
              backgroundColor: '#2a2c34',
              borderColor: 'transparent'
            }}
          >
            <Plus size={20} />
          </button>
        </div>
      )}

      {/* Modals */}
      <ProfileModal isOpen={isProfileOpen} onClose={() => setIsProfileOpen(false)} />
      <SettingsModal isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} />
    </aside>
  );
};

export default Sidebar;