import React from 'react';
import { ExternalLink, Terminal, Shield, Cloud } from 'lucide-react';
import { playFelt } from './sound';

export default function Footer() {
  return (
    <footer className="footer">
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-secondary)' }}>
        <Cloud size={16} color="#38bdf8" />
        <span>Optimized for Cloudflare Pages Static Hosting • Python package distributed via PyPI</span>
      </div>

      <div className="footer-links">
        <a href="#simulator" onClick={() => playFelt(0.9)}>Simulator</a>
        <a href="#features" onClick={() => playFelt(0.9)}>Features</a>
        <a href="#benchmarks" onClick={() => playFelt(0.9)}>Benchmarks</a>
        <a href="#docs" onClick={() => playFelt(0.9)}>Docs</a>
        <a href="https://github.com/itsjustayush/ZipText-ZTAR-" target="_blank" rel="noreferrer" onClick={() => playFelt(1.1)}>
          GitHub <ExternalLink size={12} style={{ display: 'inline', marginLeft: '2px' }} />
        </a>
        <a href="https://pypi.org/project/ziptext/" target="_blank" rel="noreferrer" onClick={() => playFelt(1.1)}>
          PyPI <ExternalLink size={12} style={{ display: 'inline', marginLeft: '2px' }} />
        </a>
      </div>

      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '8px' }}>
        ZipText (ZTAR) • Lossless Adaptive Textual & Binary Container Framework • Open Source MIT License
      </div>
    </footer>
  );
}
