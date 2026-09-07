import React, { useState } from 'react';

const nav = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  padding: '16px 0',
  marginBottom: '16px',
  borderBottom: '0.5px solid var(--border)',
};

const logoBox = {
  width: '16px', height: '16px', borderRadius: '3px',
  background: 'linear-gradient(135deg, var(--cyan), var(--purple))',
  marginRight: '8px', flexShrink: 0,
};

const logoText = {
  fontFamily: 'Syne, sans-serif', fontWeight: 700,
  fontSize: '19px', letterSpacing: '0.05em', display: 'flex', alignItems: 'center',
};

const rightContainer = {
  display: 'flex',
  alignItems: 'center',
  gap: '12px'
};

const statusPill = {
  display: 'flex', alignItems: 'center', gap: '6px',
  background: 'var(--s1)', border: '0.5px solid var(--border)',
  padding: '6px 12px', borderRadius: '999px',
};

const dot = {
  width: '8px', height: '8px', borderRadius: '50%',
  background: 'var(--green)',
  animation: 'pulse 2s infinite',
};

const statusText = {
  color: 'var(--green)', fontSize: '10px',
  fontFamily: 'JetBrains Mono, monospace',
  letterSpacing: '0.1em', textTransform: 'uppercase',
};

const extBtn = {
  background: 'transparent',
  border: '1px solid var(--cyan)',
  color: 'var(--cyan)',
  padding: '6px 12px',
  borderRadius: '999px',
  fontSize: '11px',
  fontFamily: 'JetBrains Mono, monospace',
  cursor: 'pointer',
  display: 'flex',
  alignItems: 'center',
  gap: '6px',
  transition: 'all 0.2s',
  textTransform: 'uppercase'
};

const modalOverlay = {
  position: 'fixed',
  top: 0, left: 0, right: 0, bottom: 0,
  background: 'rgba(0,0,0,0.8)',
  backdropFilter: 'blur(5px)',
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  zIndex: 9999
};

const modalContent = {
  background: 'var(--bg)',
  border: '1px solid var(--border)',
  borderRadius: '12px',
  padding: '24px',
  width: '90%',
  maxWidth: '550px',
  color: 'var(--text)',
  position: 'relative'
};

const closeBtn = {
  position: 'absolute',
  top: '16px', right: '16px',
  background: 'transparent',
  border: 'none',
  color: 'var(--subtext)',
  cursor: 'pointer',
  fontSize: '18px'
};

const TopNav = () => {
  const [showModal, setShowModal] = useState(false);

  return (
    <>
      <div style={nav}>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <div style={logoBox} />
          <div style={logoText}>
            AEGIS<span style={{ color: 'var(--cyan)' }}>.</span>AI
          </div>
        </div>
        <div style={rightContainer}>
          <button 
            style={extBtn}
            onClick={() => setShowModal(true)}
            onMouseOver={(e) => { e.target.style.background = 'var(--cyan)'; e.target.style.color = '#000'; }}
            onMouseOut={(e) => { e.target.style.background = 'transparent'; e.target.style.color = 'var(--cyan)'; }}
          >
            🧩 Install Extension
          </button>
          <div style={statusPill}>
            <div style={dot} />
            <span style={statusText}>System Online</span>
          </div>
        </div>
      </div>

      {showModal && (
        <div style={modalOverlay} onClick={() => setShowModal(false)}>
          <div style={modalContent} onClick={e => e.stopPropagation()}>
            <button style={closeBtn} onClick={() => setShowModal(false)}>✕</button>
            
            <h2 style={{ fontFamily: 'Syne, sans-serif', color: 'var(--cyan)', marginTop: 0, marginBottom: '20px' }}>
              Install AEGIS.AI Extension
            </h2>
            
            <div style={{ fontFamily: 'Inter, sans-serif', fontSize: '14px', lineHeight: '1.6', color: 'var(--subtext)' }}>
              <p>The AEGIS extension allows you to scan emails, links, and text directly on any website (like Gmail or WhatsApp) without leaving the page.</p>
              
              <div style={{ margin: '20px 0', textAlign: 'center' }}>
                <a 
                  href="/aegis-extension.zip" 
                  download
                  style={{
                    display: 'inline-block',
                    background: 'var(--cyan)', color: '#000',
                    padding: '10px 24px', borderRadius: '6px',
                    textDecoration: 'none', fontWeight: 'bold',
                    fontFamily: 'JetBrains Mono, monospace',
                    boxShadow: '0 4px 12px rgba(0, 212, 255, 0.3)'
                  }}
                >
                  📥 Download Extension File (.zip)
                </a>
              </div>

              <h3 style={{ color: 'var(--text)', fontSize: '15px', marginTop: '20px' }}>Installation Steps:</h3>
              <ol style={{ paddingLeft: '20px' }}>
                <li style={{ marginBottom: '8px' }}>Download the zip file using the button above and <strong>extract/unzip it</strong> to a folder.</li>
                <li style={{ marginBottom: '8px' }}>Open a new tab in Chrome and go to <code style={{ color: 'var(--cyan)', background: 'var(--s1)', padding: '2px 6px', borderRadius: '4px' }}>chrome://extensions/</code></li>
                <li style={{ marginBottom: '8px' }}>Turn on <strong>"Developer mode"</strong> in the top right corner.</li>
                <li style={{ marginBottom: '8px' }}>Click <strong>"Load unpacked"</strong> in the top left and select the folder you just extracted.</li>
              </ol>

              <h3 style={{ color: 'var(--text)', fontSize: '15px', marginTop: '20px' }}>How it Works:</h3>
              <ul style={{ paddingLeft: '20px' }}>
                <li style={{ marginBottom: '8px' }}>Go to any website and highlight a suspicious sentence, email, or link.</li>
                <li style={{ marginBottom: '8px' }}><strong>Right-click</strong> the highlighted text and select <strong>"Scan with AEGIS.AI"</strong>.</li>
                <li style={{ marginBottom: '8px' }}>Our AI models will analyze the text instantly and attach a secure threat rating badge right next to the text on your screen!</li>
              </ul>
            </div>
            
            <button 
              onClick={() => setShowModal(false)}
              style={{
                width: '100%', padding: '12px', marginTop: '24px',
                background: 'rgba(0, 212, 255, 0.1)', color: 'var(--cyan)',
                border: '1px solid var(--cyan)', borderRadius: '6px',
                cursor: 'pointer', fontFamily: 'JetBrains Mono, monospace',
                fontWeight: 'bold'
              }}
            >
              Done
            </button>
          </div>
        </div>
      )}
    </>
  );
};

export default TopNav;
