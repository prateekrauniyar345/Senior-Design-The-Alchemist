import React, { useRef, useEffect } from 'react';
import MessageBubble from './MessageBubble';
import { IconBot } from './IconComponents.jsx';
import './ChatWindow.css';

// --- Component: TypingIndicator ---
const TypingIndicator = () => (
  <div className="d-flex justify-content-start my-4">
    <div className="d-flex align-items-start gap-3" style={{ maxWidth: '48rem' }}>
      <div
        className="flex-shrink-0 rounded-circle d-flex align-items-center justify-content-center"
        style={{
          width: '32px',
          height: '32px',
          backgroundColor: '#374151'
        }}
      >
        <IconBot style={{ width: '20px', height: '20px', color: '#60a5fa' }} />
      </div>
      <div className="p-3 rounded" style={{ backgroundColor: '#374151', color: '#e5e7eb' }}>
        <div className="d-flex gap-2">
          <div className="typing-indicator-dot"></div>
          <div className="typing-indicator-dot" style={{ animationDelay: '0.2s' }}></div>
          <div className="typing-indicator-dot" style={{ animationDelay: '0.4s' }}></div>
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
      className="h-100 p-4 p-md-5 chat-window"
      role="log"
      aria-live="polite"
    >
      <div className="mx-auto" style={{ maxWidth: '768px' }}>
        {messages.length === 0 ? (
          <div className="text-center mt-5 empty-chat-subtitle">
            <h1 className="fw-semibold mb-2 empty-chat-title">Smart Agent</h1>
            <p className="fs-6">Start a conversation by typing below.</p>
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