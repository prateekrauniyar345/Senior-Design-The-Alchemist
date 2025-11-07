import React from 'react';
import { IconUser, IconBot } from './IconComponents.jsx';

// --- Component: MessageBubble ---
const MessageBubble = React.memo(({ message }) => {
  const { sender, text, timestamp } = message;
  const isUser = sender === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`
          flex items-start gap-3
          max-w-xs md:max-w-md lg:max-w-2xl
          ${isUser ? 'flex-row-reverse' : 'flex-row'}
        `}
      >
        {/* Avatar */}
        <div 
          className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center"
          aria-hidden="true"
        >
          {isUser ? (
            <IconUser className="w-5 h-5 text-gray-300" />
          ) : (
            <IconBot className="w-5 h-5 text-blue-400" />
          )}
        </div>
        
        {/* Message Content */}
        <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
          <div
            className={`
              p-3 rounded-lg
              ${isUser 
                ? 'bg-blue-600 text-white rounded-br-sm' 
                : 'bg-gray-700 text-gray-200 rounded-bl-sm'
              }
            `}
          >
            <p className="text-sm leading-relaxed whitespace-pre-wrap break-words">
              {text}
            </p>
          </div>
          
          {/* Timestamp */}
          {timestamp && (
            <span className={`text-xs text-gray-500 mt-1 px-1 ${isUser ? 'text-right' : 'text-left'}`}>
              {new Date(timestamp).toLocaleTimeString([], { 
                hour: '2-digit', 
                minute: '2-digit' 
              })}
            </span>
          )}
        </div>
      </div>
    </div>
  );
});

MessageBubble.displayName = 'MessageBubble';

export default MessageBubble;