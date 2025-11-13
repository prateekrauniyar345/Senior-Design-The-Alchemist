import React from 'react';
import { IconUser} from './IconComponents.jsx';

// --- Component: MessageBubble ---
const MessageBubble = React.memo(({ message }) => {
  const { sender, text, timestamp } = message;
  const isUser = sender === 'user';

  return (
    <div className={`d-flex ${isUser ? 'justify-content-end' : 'justify-content-start'} mb-4`}>
      <div
        className={`d-flex align-items-start gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
        style={{ maxWidth: '48rem' }}
      >
        {/* Avatar */}
        <div 
          className="flex-shrink-0 rounded-circle d-flex align-items-center justify-content-center"
          style={{ 
            width: '32px', 
            height: '32px', 
            backgroundColor: '#161618' 
          }}
          aria-hidden="true"
        >
          {isUser ? (
            <IconUser style={{ width: '20px', height: '20px', color: '#d1d5db' }} />
          ) : (
            <img
              src="/images/the-alchemist.png"
              alt="The Alchemist logo"
              className="rounded object-fit-cover p-1"
              style={{ height: '3rem', width: '3rem' }}
              loading="lazy"
            />
          )}
        </div>
        
        {/* Message Content */}
        <div className={`d-flex flex-column ${isUser ? 'align-items-end' : 'align-items-start'}`}>
          <div
            className="p-3 rounded"
            style={{
              color: isUser ? '#ffffff' : '#e5e7eb',
              borderBottomRightRadius: isUser ? '0.125rem' : undefined,
              borderBottomLeftRadius: !isUser ? '0.125rem' : undefined
            }}
          >
            <p className="mb-0" style={{ 
              fontSize: '14px', 
              lineHeight: '1.625', 
              whiteSpace: 'pre-wrap', 
              wordBreak: 'break-word' 
            }}>
              {text}
            </p>
          </div>
          
          {/* Timestamp */}
          {timestamp && (
            <span 
              className={`mt-1 px-1 ${isUser ? 'text-end' : 'text-start'}`}
              style={{ fontSize: '0.75rem', color: '#6b7280' }}
            >
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