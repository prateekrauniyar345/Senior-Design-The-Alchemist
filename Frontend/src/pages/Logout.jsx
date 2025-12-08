import React from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircle } from 'lucide-react';
import '../components/auth/auth.css';

export default function Logout() {
  const navigate = useNavigate();

  return (
    <div className="auth-container">
      <div className="auth-card">
        {/* Success Icon */}
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <CheckCircle 
            size={64} 
            style={{ 
              color: '#10b981',
              strokeWidth: 2
            }} 
          />
        </div>

        {/* Heading */}
        <h1 className="auth-heading" style={{ textAlign: 'center' }}>
          Logged Out Successfully
        </h1>

        {/* Message */}
        <p style={{ 
          textAlign: 'center', 
          color: '#9ca3af', 
          fontSize: '1rem',
          marginBottom: '2rem',
          lineHeight: '1.5'
        }}>
          You have been successfully logged out of your account.
          <br />
          Your session has been cleared for security.
        </p>

        {/* Action Buttons */}
        <div style={{ 
          display: 'flex', 
          flexDirection: 'column', 
          gap: '1rem',
          marginTop: '2rem'
        }}>
          <button
            onClick={() => navigate('/signin')}
            className="auth-button"
            style={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: '#fff',
              border: 'none',
              padding: '0.875rem 1.5rem',
              borderRadius: '8px',
              fontSize: '1rem',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.2s',
            }}
            onMouseOver={(e) => e.target.style.transform = 'translateY(-2px)'}
            onMouseOut={(e) => e.target.style.transform = 'translateY(0)'}
          >
            Sign In Again
          </button>

          <button
            onClick={() => navigate('/')}
            style={{
              background: 'transparent',
              color: '#9ca3af',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              padding: '0.875rem 1.5rem',
              borderRadius: '8px',
              fontSize: '1rem',
              fontWeight: '500',
              cursor: 'pointer',
              transition: 'all 0.2s',
            }}
            onMouseOver={(e) => {
              e.target.style.borderColor = 'rgba(255, 255, 255, 0.3)';
              e.target.style.color = '#fff';
            }}
            onMouseOut={(e) => {
              e.target.style.borderColor = 'rgba(255, 255, 255, 0.1)';
              e.target.style.color = '#9ca3af';
            }}
          >
            Go to Dashboard
          </button>
        </div>

        {/* Footer Note */}
        <p style={{
          textAlign: 'center',
          color: '#6b7280',
          fontSize: '0.875rem',
          marginTop: '2rem'
        }}>
          Need help? Contact support at{' '}
          <a 
            href="mailto:support@thealchemist.com" 
            style={{ 
              color: '#667eea',
              textDecoration: 'none'
            }}
          >
            support@thealchemist.com
          </a>
        </p>
      </div>
    </div>
  );
}
