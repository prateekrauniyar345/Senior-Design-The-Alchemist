import React from 'react';
import { IconUser } from './IconComponents.jsx';

// --- Component: MessageBubble ---
const MessageBubble = React.memo(({ message }) => {
  const { sender, text, timestamp, image } = message;
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
            backgroundColor: isUser ? '#374151' : 'transparent'
          }}
          aria-hidden="true"
        >
          {isUser ? (
            <IconUser style={{ width: '20px', height: '20px', color: '#d1d5db' }} />
          ) : (
            <img
              src="/images/the-alchemist.png"
              alt="The Alchemist logo"
              style={{ width: '32px', height: '32px' }}
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
            {/* Text */}
            {text && (
              <p className="mb-0" style={{ 
                fontSize: '14px', 
                lineHeight: '1.625', 
                whiteSpace: 'pre-wrap', 
                wordBreak: 'break-word' 
              }}>
                {text}
              </p>
            )}

            {/* Image (Plot) */}
            {image && (
              <div className="mt-2">
                <img
                  src={image}
                  alt="Generated plot"
                  style={{
                    maxWidth: '100%',
                    height: 'auto',
                    borderRadius: '8px',
                    border: '1px solid #4b5563'
                  }}
                />
              </div>
            )}
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