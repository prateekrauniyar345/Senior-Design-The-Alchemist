import React, { useState, useRef, useEffect } from 'react';
import { IconSend } from './IconComponents.jsx';

// --- Component: ChatInput ---
const ChatInput = ({ onSendMessage, disabled = false }) => {
  const [inputValue, setInputValue] = useState('');
  const textareaRef = useRef(null);

  useEffect(() => {
    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      const scrollHeight = textareaRef.current.scrollHeight;
      textareaRef.current.style.height = `${Math.min(scrollHeight, 160)}px`;
    }
  }, [inputValue]);

  const handleSubmit = (e) => {
    if (e) e.preventDefault();
    if (inputValue.trim() && !disabled) {
      onSendMessage(inputValue.trim());
      setInputValue('');
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div 
      className="w-100 p-4 p-md-5" 
    >
      <div className="mx-auto d-flex align-items-end gap-3" style={{ maxWidth: '768px' }}>
        <textarea
          ref={textareaRef}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Send a message..."
          rows="1"
          disabled={disabled}
          aria-label="Chat message input"
          className="flex-fill p-3 rounded border text-white"
          style={{ 
            resize: 'none',
            minHeight: '44px',
            maxHeight: '160px',
            fontSize: '0.875rem',
            lineHeight: '1.5rem'
          }}
        />
        <button
          onClick={handleSubmit}
          disabled={!inputValue.trim() || disabled}
          aria-label="Send message"
          className="btn btn-primary d-flex align-items-center justify-content-center flex-shrink-0"
          style={{ 
            minWidth: '44px',
            minHeight: '44px',
            backgroundColor: disabled || !inputValue.trim() ? '#6c757d' : '#0d6efd',
            borderColor: disabled || !inputValue.trim() ? '#6c757d' : '#0d6efd',
            opacity: disabled || !inputValue.trim() ? 0.5 : 1,
            cursor: disabled || !inputValue.trim() ? 'not-allowed' : 'pointer'
          }}
        >
          <IconSend style={{ width: '20px', height: '20px' }} />
        </button>
      </div>
    </div>
  );
};

export default ChatInput;