// src/services/chatService.js

/**
 * Chat service for handling LLM API interactions
 */
const chatService = {
    /**
 * Get response from the backend agent.
 * @param {string} userMessage - The user's message.
 * @returns {Promise<object>} The full response object from the backend agent, including message and plot_file_path.
 */
async getLLMResponse(userMessage) {
  try {
    const response = await fetch('/api/agent/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query: userMessage }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'An unknown error occurred.' }));
      throw new Error(errorData.detail || `HTTP error! Status: ${response.status}`);
    }

    const data = await response.json();
    return data;

  } catch (error) {
    console.error('Error in getLLMResponse:', error);
    throw error; // Re-throw to be handled by the component
  }
},
  
/**
 * Optional: Stream response from LLM API
 * @param {string} userMessage - The user's message
 * @param {Function} onChunk - Callback for each chunk of data
 * @returns {Promise<void>}
 */
async streamLLMResponse(userMessage, onChunk) {
  try {
      // TODO: Implement streaming API call
      // Example with fetch streaming:
      // const response = await fetch('YOUR_STREAMING_ENDPOINT', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ message: userMessage })
      // });
      
      // const reader = response.body.getReader();
      // const decoder = new TextDecoder();
      
      // while (true) {
      //   const { done, value } = await reader.read();
      //   if (done) break;
      //   const chunk = decoder.decode(value);
      //   onChunk(chunk);
      // }
      
      // Simulated streaming for now
      const fullResponse = `Streamed response to: "${userMessage}"`;
      for (let i = 0; i < fullResponse.length; i++) {
        await new Promise(resolve => setTimeout(resolve, 50));
        onChunk(fullResponse.slice(0, i + 1));
      }
    } catch (error) {
        console.error('Error in streamLLMResponse:', error);
        throw error;
      }
    }
  };
  
  export default chatService;