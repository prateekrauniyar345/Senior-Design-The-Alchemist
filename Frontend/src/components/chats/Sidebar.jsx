import React, { useState } from "react";
import { Plus, User, Settings, X, Menu, Trash2 } from "lucide-react";
import { Link } from "react-router-dom";
import ProfileModal from "./ProfileModal";
import SettingsModal from "./SettingsModal";
import "./Sidebar.css";

const Sidebar = ({
  chats = [],
  currentChatId = null,
  onSelectChat = () => {},
  onDeleteChat = () => {},
  onStartNewChat = () => {},
  onToggleSidebar = () => {},
  isOpen = true,
}) => {
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [hoveredId, setHoveredId] = useState(null);

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
                style={{ height: "3rem", width: "3rem", backgroundColor: "rgba(0,0,0,0.2)" }}
              />
              <div className="d-flex flex-column" style={{ lineHeight: "1.2" }}>
                <span className="text-uppercase fw-semibold fs-6 sidebar-logo-text">
                  The Alchemist
                </span>
                <span>AI Research Crew</span>
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
              onClick={onStartNewChat}
              type="button"
            >
              <Plus size={18} />
              New Chat
            </button>
          </div>

          {/* Chat List */}
          <nav className="flex-fill overflow-auto p-4">
            <div className="d-flex flex-column gap-2">
              {chats.length === 0 ? (
                <div className="text-secondary small">No chats yet</div>
              ) : (
                chats.map((chat) => (
                  <div
                    key={chat.id}
                    className="d-flex align-items-center gap-1 chat-list-item-wrapper"
                    onMouseEnter={() => setHoveredId(chat.id)}
                    onMouseLeave={() => setHoveredId(null)}
                  >
                    <button
                      type="button"
                      className={`btn w-100 text-start px-4 py-3 rounded fw-medium chat-list-btn rounded-4 flex-grow-1 ${
                        currentChatId === chat.id ? "chat-list-btn-active" : ""
                      }`}
                      onClick={() => onSelectChat(chat.id)}
                    >
                      {chat.title || "New conversation"}
                    </button>
                    {hoveredId === chat.id && (
                      <button
                        type="button"
                        className="btn btn-sm p-1 text-danger opacity-75 chat-list-delete-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          if (window.confirm("Delete this chat?")) onDeleteChat(chat.id);
                        }}
                        aria-label="Delete chat"
                      >
                        <Trash2 size={14} />
                      </button>
                    )}
                  </div>
                ))
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
          <button
            type="button"
            onClick={() => onToggleSidebar(true)}
            className="btn btn-outline-secondary d-inline-flex align-items-center justify-content-center rounded-4 p-2 sidebar-toggle-btn"
            aria-label="Open sidebar"
            title="Open sidebar"
          >
            <Menu size={20} />
          </button>

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
                height: "2.5rem",
                width: "2.5rem",
                backgroundColor: "rgba(0,0,0,0.2)",
                cursor: "pointer",
              }}
              loading="lazy"
            />
          </button>

          <button
            className="btn btn-outline-secondary d-inline-flex align-items-center justify-content-center rounded-4 p-2"
            onClick={onStartNewChat}
            type="button"
            aria-label="New chat"
            title="New chat"
            style={{
              width: "44px",
              height: "44px",
              backgroundColor: "#2a2c34",
              borderColor: "transparent",
            }}
          >
            <Plus size={20} />
          </button>
        </div>
      )}

      <ProfileModal isOpen={isProfileOpen} onClose={() => setIsProfileOpen(false)} />
      <SettingsModal isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} />
    </aside>
  );
};

export default Sidebar;
