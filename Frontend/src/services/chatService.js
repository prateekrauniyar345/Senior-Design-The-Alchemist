// src/services/chatService.js
import apiClient from "../api/apiClient";

/**
 * Chat service for handling LLM API interactions and chat history
 * Uses axios apiClient for consistent error handling and token refresh
 */
const chatService = {
  /**
   * Get response from the backend agent.
   * @param {string} userMessage - The user's message.
   * @param {string} sessionId - Optional session ID for message persistence
   * @returns {Promise<object>} The full response object from the backend agent.
   */
  async getLLMResponse(userMessage, sessionId = null) {
    try {
      const payload = { query: userMessage };
      if (sessionId) payload.session_id = sessionId;

      const response = await apiClient.post("/api/agent/chat", payload);
      return response.data;
    } catch (error) {
      console.error('Error in getLLMResponse:', error.message);
      throw error;
    }
  },

  // ========== SESSION MANAGEMENT ==========

  /**
   * Get all chat sessions for the current user
   * @returns {Promise<Array>} Array of session objects
   */
  async getSessions() {
    try {
      const response = await apiClient.get("/api/sessions");
      return response.data;
    } catch (error) {
      console.error('Error in getSessions:', error.message);
      throw error;
    }
  },

  /**
   * Create a new chat session
   * @param {string} title - Title for the new session
   * @returns {Promise<object>} The created session object
   */
  async createSession(title = "New Chat") {
    try {
      const response = await apiClient.post("/api/sessions", { title });
      return response.data;
    } catch (error) {
      console.error('Error in createSession:', error.message);
      throw error;
    }
  },

  /**
   * Update session title
   * @param {string} sessionId - The session ID
   * @param {string} title - New title for the session
   * @returns {Promise<object>} The updated session object
   */
  async updateSession(sessionId, title) {
    try {
      const response = await apiClient.put(`/api/sessions/${sessionId}`, { title });
      return response.data;
    } catch (error) {
      console.error('Error in updateSession:', error.message);
      throw error;
    }
  },

  /**
   * Delete a chat session
   * @param {string} sessionId - The session ID to delete
   * @returns {Promise<object>} Confirmation message
   */
  async deleteSession(sessionId) {
    try {
      const response = await apiClient.delete(`/api/sessions/${sessionId}`);
      return response.data;
    } catch (error) {
      console.error('Error in deleteSession:', error.message);
      throw error;
    }
  },

  // ========== MESSAGE MANAGEMENT ==========

  /**
   * Get all messages in a session
   * @param {string} sessionId - The session ID
   * @returns {Promise<Array>} Array of message objects
   */
  async getMessages(sessionId) {
    try {
      const response = await apiClient.get(`/api/sessions/${sessionId}/messages`);
      return response.data;
    } catch (error) {
      console.error('Error in getMessages:', error.message);
      throw error;
    }
  },

  /**
   * Save a message to a session
   * @param {string} sessionId - The session ID
   * @param {string} content - Message content
   * @param {string} sender - "user" or "bot"
   * @param {string} outputType - Type of output (text, plot, chart, etc.)
   * @param {object} metadata - Additional metadata (plot URLs, chart specs, etc.)
   * @returns {Promise<object>} The saved message object
   */
  async saveMessage(sessionId, content, sender, outputType = "text", metadata = null) {
    try {
      const response = await apiClient.post(
        `/api/sessions/${sessionId}/messages`,
        {
          content,
          sender,
          output_type: outputType,
          meta_data: metadata,
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error in saveMessage:', error.message);
      throw error;
    }
  },
};

export default chatService;