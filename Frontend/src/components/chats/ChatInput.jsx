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
    <div className="w-full p-4 md:p-6 bg-[#343541] border-t border-gray-700">
      <div className="max-w-3xl mx-auto flex items-end gap-3">
        <textarea
          ref={textareaRef}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Send a message..."
          rows="1"
          disabled={disabled}
          aria-label="Chat message input"
          className="
            flex-1 p-3
            bg-[#40414f] text-gray-100 placeholder-gray-500
            rounded-lg resize-none
            border border-gray-600
            focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
            disabled:opacity-50 disabled:cursor-not-allowed
            text-sm leading-6
          "
          style={{ 
            minHeight: '44px',
            maxHeight: '160px'
          }}
        />
        <button
          onClick={handleSubmit}
          disabled={!inputValue.trim() || disabled}
          aria-label="Send message"
          className="
            flex-shrink-0
            p-3 bg-blue-600 rounded-lg
            text-white
            disabled:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed
            hover:bg-blue-700 active:bg-blue-800
            transition-colors duration-150
            flex items-center justify-center
          "
          style={{ 
            minWidth: '44px',
            minHeight: '44px'
          }}
        >
          <IconSend className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
};

export default ChatInput;
