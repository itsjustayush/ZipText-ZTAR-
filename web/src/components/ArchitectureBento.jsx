import React from 'react';
import MagicBento from './MagicBento';

export default function ArchitectureBento() {
  return (
    <section id="features" className="section">
      <div className="section-header">
        <span className="section-pill">Core Engineering</span>
        <h2 className="section-title">Architecture & System Capabilities</h2>
        <p className="section-desc">
          Engineered for bounded-memory throughput, cryptographic chunk validation, and dual-profile distribution across web and systems programming.
        </p>
      </div>

      <MagicBento
        columns={4}
        rowHeight={220}
        gap={14}
        radius={20}
        theme="dark"
        glowColor="#10b981"
        enableBorderGlow={true}
        enableSpotlight={true}
        spotlightRadius={280}
        enableStars={true}
        particleCount={20}
        enableTilt={true}
        enableMagnetism={true}
        clickEffect={true}
      />
    </section>
  );
}
