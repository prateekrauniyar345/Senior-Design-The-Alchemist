import React from "react";
import { Plus, User, Settings, X } from "lucide-react"; // npm install lucide-react
import { Link } from "react-router-dom";
import teamLogo from "../../../../Backend/static/images/the-alchemist.png";

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
      className="flex flex-col h-full bg-[#1c1e26] text-gray-100 w-full max-w-sm"
      aria-label="Sidebar"
      aria-hidden={!isOpen}
    >
      {/* Logo + Toggle */}
      <div className="flex items-center justify-between px-4 py-5 border-b border-gray-700">
        <div className="flex items-center gap-4">
          <img
            src={teamLogo}
            alt="The Alchemist logo"
            className="h-12 w-12 rounded-xl object-cover bg-black/20 p-1"
            loading="lazy"
          />
          <div className="flex flex-col leading-tight">
            <span className="text-base font-semibold uppercase tracking-[0.25em] text-gray-100">
              The Alchemist
            </span>
            <span className="text-sm text-gray-400">AI Research Crew</span>
          </div>
        </div>
        <button
          type="button"
          onClick={() => onToggleSidebar(false)}
          className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-gray-700 text-gray-300 hover:bg-gray-700 hover:text-white transition"
          aria-label="Close sidebar"
        >
          <X size={16} />
        </button>
      </div>

      {/* New Chat */}
      <div className="p-4 border-b border-gray-700">
        <button
          className="flex items-center gap-3 bg-[#2a2c34] hover:bg-[#32343d] text-base font-semibold w-full py-3 px-4 rounded-lg transition"
          onClick={onStartNewChat}
          type="button"
        >
          <Plus size={18} />
          New Chat
        </button>
      </div>

      {/* Chat List */}
      <nav className="flex-1 overflow-y-auto p-4 space-y-1.5">
        {chatList.map((chat) => (
          <button
            key={chat.id}
            className="w-full text-left px-4 py-3 text-base rounded-lg hover:bg-[#2f313b] transition font-medium text-gray-200"
          >
            {chat.title}
          </button>
        ))}
      </nav>

      {/* Bottom buttons */}
      <div className="border-t border-gray-700 p-4 flex items-center justify-between">
        <Link to="#" className="text-sm text-gray-400 hover:text-white font-medium">
          Dashboard
        </Link>
        <div className="flex gap-3">
          <User className="cursor-pointer hover:text-white text-gray-400" size={20} />
          <Settings className="cursor-pointer hover:text-white text-gray-400" size={20} />
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
