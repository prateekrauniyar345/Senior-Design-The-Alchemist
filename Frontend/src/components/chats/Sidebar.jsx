import React from "react";
import { Plus, User, Settings, X, Menu } from "lucide-react";
import { Link } from "react-router-dom";
import "./Sidebar.css";

const Sidebar = ({
  onStartNewChat = () => {},
  onToggleSidebar = () => {},
  isOpen = true,
}) => {
  const chatList = [
    { id: 1, title: "Project brainstorm" },
    { id: 2, title: "Math help session" },
    { id: 3, title: "Code review notes" },
  ];

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
              {chatList.map((chat) => (
                <button
                  key={chat.id}
                  className="btn w-100 text-start px-4 py-3 rounded fw-medium chat-list-btn rounded-4"
                >
                  {chat.title}
                </button>
              ))}
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
              <User
                size={20}
                className="sidebar-footer-icon"
              />
              <Settings
                size={20}
                className="sidebar-footer-icon"
              />
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
            onClick={onStartNewChat}
            type="button"
            aria-label="New chat"
            title="New chat"
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
    </aside>
  );
};

export default Sidebar;