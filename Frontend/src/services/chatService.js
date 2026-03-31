// src/services/chatService.js

const API_BASE = import.meta.env.VITE_API_URL || "";

async function parseResponse(response) {
  const contentType = response.headers.get("content-type") || "";

  let data;
  if (contentType.includes("application/json")) {
    data = await response.json();
  } else {
    data = await response.text();
  }

  if (!response.ok) {
    const message =
      typeof data === "string"
        ? data
        : data?.detail || data?.message || "An unknown error occurred.";
    throw new Error(message);
  }

  return data;
}

const chatService = {
  async getLLMResponse(userMessage) {
    const response = await fetch(`${API_BASE}/api/agent/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
      body: JSON.stringify({ query: userMessage }),
    });

    return parseResponse(response);
  },

  async createSession(title = "New conversation") {
    const response = await fetch(`${API_BASE}/api/chat/sessions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ title }),
    });
    return parseResponse(response);
  },

  async listSessions() {
    const response = await fetch(`${API_BASE}/api/chat/sessions`, {
      method: "GET",
      credentials: "include",
    });
    return parseResponse(response);
  },

  async getSession(sessionId) {
    const response = await fetch(`${API_BASE}/api/chat/sessions/${sessionId}`, {
      method: "GET",
      credentials: "include",
    });
    return parseResponse(response);
  },

  async createMessage(sessionId, payload) {
    const response = await fetch(
      `${API_BASE}/api/chat/sessions/${sessionId}/messages`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(payload),
      }
    );
    return parseResponse(response);
  },

  async renameSession(sessionId, title) {
    const response = await fetch(`${API_BASE}/api/chat/sessions/${sessionId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ title }),
    });
    return parseResponse(response);
  },

  async deleteSession(sessionId) {
    const response = await fetch(`${API_BASE}/api/chat/sessions/${sessionId}`, {
      method: "DELETE",
      credentials: "include",
    });
    return parseResponse(response);
  },

  createChat(title) {
    return this.createSession(title);
  },
  listChats() {
    return this.listSessions();
  },
  getChat(id) {
    return this.getSession(id);
  },
  renameChat(id, title) {
    return this.renameSession(id, title);
  },
  deleteChat(id) {
    return this.deleteSession(id);
  },
};

export default chatService;