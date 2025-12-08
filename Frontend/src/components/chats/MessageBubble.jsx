import React, { useState } from 'react';
import { IconUser } from './IconComponents.jsx';
import { Download, Mail, FileImage, FileText } from 'lucide-react';

// --- Component: MessageBubble ---
const MessageBubble = React.memo(({ message }) => {
  const { sender, text, timestamp, image } = message;
  const isUser = sender === 'user';
  const [showEmailModal, setShowEmailModal] = useState(false);
  const [emailAddress, setEmailAddress] = useState('');
  const [emailStatus, setEmailStatus] = useState('');
  const [isDownloading, setIsDownloading] = useState(false);

  // Extract filename from image URL
  const getFileName = () => {
    if (!image) return null;
    const urlParts = image.split('/');
    return urlParts[urlParts.length - 1];
  };

  const fileName = getFileName();
  const isHtmlFile = fileName?.endsWith('.html');

  // Download plot in specified format
  const handleDownload = async (format) => {
    if (!fileName) return;
    
    setIsDownloading(true);
    try {
      const response = await fetch(`/api/plots/download/${fileName}?format=${format}`);
      
      if (!response.ok) {
        throw new Error('Download failed');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = format === 'pdf' ? fileName.replace(/\.(png|html)$/, '.pdf') : fileName;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Download error:', error);
      alert('Failed to download file');
    } finally {
      setIsDownloading(false);
    }
  };

  // Send plot via email
  const handleEmail = async () => {
    if (!fileName || !emailAddress) return;

    try {
      const response = await fetch('/api/plots/email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          file_name: fileName,
          recipient_email: emailAddress,
          subject: 'Your Mineral Data Visualization',
          message: 'Please find attached your requested mineral data visualization from The Alchemist platform.'
        })
      });

      const data = await response.json();
      
      if (data.success) {
        setEmailStatus('success');
        setTimeout(() => {
          setShowEmailModal(false);
          setEmailAddress('');
          setEmailStatus('');
        }, 2000);
      } else {
        setEmailStatus('error');
      }
    } catch (error) {
      console.error('Email error:', error);
      setEmailStatus('error');
    }
  };

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
                {isHtmlFile ? (
                  <iframe
                    src={image}
                    title="Interactive Heatmap"
                    style={{
                      width: '100%',
                      height: '500px',
                      borderRadius: '8px',
                      border: '1px solid #4b5563'
                    }}
                  />
                ) : (
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
                )}
                
                {/* Download and Email Buttons */}
                <div className="mt-3 d-flex gap-2 flex-wrap">
                  <button
                    onClick={() => handleDownload(isHtmlFile ? 'html' : 'png')}
                    disabled={isDownloading}
                    className="btn btn-sm btn-outline-light d-flex align-items-center gap-1"
                    style={{
                      fontSize: '0.875rem',
                      padding: '0.375rem 0.75rem',
                      borderRadius: '6px'
                    }}
                  >
                    <FileImage size={16} />
                    {isDownloading ? 'Downloading...' : `Download ${isHtmlFile ? 'HTML' : 'PNG'}`}
                  </button>
                  
                  {!isHtmlFile && (
                    <button
                      onClick={() => handleDownload('pdf')}
                      disabled={isDownloading}
                      className="btn btn-sm btn-outline-light d-flex align-items-center gap-1"
                      style={{
                        fontSize: '0.875rem',
                        padding: '0.375rem 0.75rem',
                        borderRadius: '6px'
                      }}
                    >
                      <FileText size={16} />
                      {isDownloading ? 'Converting...' : 'Download PDF'}
                    </button>
                  )}
                  
                  <button
                    onClick={() => setShowEmailModal(true)}
                    className="btn btn-sm btn-outline-light d-flex align-items-center gap-1"
                    style={{
                      fontSize: '0.875rem',
                      padding: '0.375rem 0.75rem',
                      borderRadius: '6px'
                    }}
                  >
                    <Mail size={16} />
                    Email
                  </button>
                </div>
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

      {/* Email Modal */}
      {showEmailModal && (
        <div 
          className="modal show d-block" 
          style={{ backgroundColor: 'rgba(0, 0, 0, 0.7)' }}
          onClick={() => setShowEmailModal(false)}
        >
          <div className="modal-dialog modal-dialog-centered" onClick={(e) => e.stopPropagation()}>
            <div className="modal-content" style={{ backgroundColor: '#2a2c34', color: '#fff' }}>
              <div className="modal-header" style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.1)' }}>
                <h5 className="modal-title">Email Visualization</h5>
                <button 
                  type="button" 
                  className="btn-close btn-close-white" 
                  onClick={() => setShowEmailModal(false)}
                ></button>
              </div>
              <div className="modal-body">
                <div className="mb-3">
                  <label htmlFor="emailInput" className="form-label">Recipient Email</label>
                  <input
                    id="emailInput"
                    type="email"
                    className="form-control"
                    value={emailAddress}
                    onChange={(e) => setEmailAddress(e.target.value)}
                    placeholder="Enter email address"
                    style={{
                      backgroundColor: '#1c1c1e',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      color: '#fff'
                    }}
                  />
                </div>
                {emailStatus === 'success' && (
                  <div className="alert alert-success">Email sent successfully!</div>
                )}
                {emailStatus === 'error' && (
                  <div className="alert alert-danger">Failed to send email. Please try again.</div>
                )}
              </div>
              <div className="modal-footer" style={{ borderTop: '1px solid rgba(255, 255, 255, 0.1)' }}>
                <button 
                  type="button" 
                  className="btn btn-secondary" 
                  onClick={() => setShowEmailModal(false)}
                >
                  Cancel
                </button>
                <button 
                  type="button" 
                  className="btn btn-primary" 
                  onClick={handleEmail}
                  disabled={!emailAddress || emailStatus === 'success'}
                >
                  Send Email
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
});

MessageBubble.displayName = 'MessageBubble';

export default MessageBubble;