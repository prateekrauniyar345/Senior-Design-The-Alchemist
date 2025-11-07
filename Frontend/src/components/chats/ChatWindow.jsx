import React, { useRef, useEffect } from 'react';
import MessageBubble from './MessageBubble';
import { IconBot } from './IconComponents.jsx';

// --- Component: TypingIndicator ---
const TypingIndicator = () => (
  <div className="flex justify-start my-4">
    <div className="flex items-start space-x-3 max-w-xs md:max-w-md lg:max-w-2xl">
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center">
        <IconBot className="w-5 h-5 text-blue-400" />
      </div>
      <div className="bg-gray-700 text-gray-200 p-3 rounded-lg">
        <div className="flex space-x-2">
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
        </div>
      </div>
    </div>
  </div>
);

// --- Component: ChatWindow ---
const ChatWindow = ({ messages, isLoading = false }) => {
  const messagesEndRef = useRef(null);
  const containerRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  return (
    <div 
      ref={containerRef}
      className="h-full p-4 md:p-6 overflow-y-auto bg-[#1c1c1e] text-gray-100" 
      role="log" 
      aria-live="polite"
    >
      <div className="max-w-3xl mx-auto">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-20">
            <h1 className="text-3xl font-semibold mb-2">Smart Agent</h1>
            <p className="text-base">Start a conversation by typing below.</p>
          </div>
        ) : (
          <>
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}
            {isLoading && <TypingIndicator />}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};

export default ChatWindow;
