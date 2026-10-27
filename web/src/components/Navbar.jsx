import React, { useState } from 'react';
import { Volume2, VolumeX, Copy, Check, ExternalLink, Terminal } from 'lucide-react';
import { playFelt, isAudioMuted, toggleAudioMute } from './sound';

export default function Navbar() {
  const [copied, setCopied] = useState(false);
  const [muted, setMuted] = useState(isAudioMuted());

  const handleCopyPip = () => {
    playFelt(1.2);
    navigator.clipboard.writeText('pip install ziptext');
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleToggleSound = () => {
    const next = toggleAudioMute();
    setMuted(next);
    if (!next) playFelt(1.0);
  };

  const handleNavClick = () => {
    playFelt(0.9);
  };

  return (
    <nav className="navbar">
      <div className="nav-brand">
        <div className="brand-icon">Z</div>
        <span>ZipText <span style={{ color: 'var(--emerald-light)', fontSize: '0.8rem', fontWeight: 600 }}>ZTAR</span></span>
      </div>

      <div className="nav-links">
        <a href="#simulator" className="nav-link" onClick={handleNavClick}>Simulator</a>
        <a href="#features" className="nav-link" onClick={handleNavClick}>Features</a>
        <a href="#benchmarks" className="nav-link" onClick={handleNavClick}>Benchmarks</a>
        <a href="#docs" className="nav-link" onClick={handleNavClick}>CLI & SDK</a>
        <a href="#incidents" className="nav-link" onClick={handleNavClick}>Error Register</a>
      </div>

      <div className="nav-actions">
        <button 
          className="sound-toggle-btn" 
          onClick={handleToggleSound} 
          title={muted ? "Unmute Audio (React Bits Sound Lab)" : "Mute Audio (React Bits Sound Lab)"}
          aria-label="Toggle Sound"
        >
          {muted ? <VolumeX size={18} /> : <Volume2 size={18} />}
        </button>

        <div className="pip-chip" onClick={handleCopyPip} title="Click to copy PyPI command">
          <Terminal size={14} />
          <span>pip install ziptext</span>
          {copied ? <Check size={14} color="#34d399" /> : <Copy size={14} />}
        </div>

        <a 
          href="https://github.com/itsjustayush/ZipText-ZTAR-" 
          target="_blank" 
          rel="noreferrer" 
          className="btn-secondary"
          style={{ padding: '8px 16px', fontSize: '0.85rem' }}
          onClick={() => playFelt(1.1)}
        >
          <span>GitHub</span>
          <ExternalLink size={13} />
        </a>
      </div>
    </nav>
  );
}
