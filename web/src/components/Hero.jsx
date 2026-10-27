import React from 'react';
import GradientWaves from './GradientWaves';
import TechText from './TechText';
import { ArrowRight, BookOpen, Cpu, ShieldCheck } from 'lucide-react';
import { playFelt, playZipSound } from './sound';

export default function Hero() {
  return (
    <section className="hero-section">
      {/* React Bits <GradientWaves /> WebGL 2 component background */}
      <div className="hero-waves-background">
        <GradientWaves
          horizonColor="#052e16"
          waveColor="#10b981"
          crestColor="#d1fae5"
          speed={0.35}
          amplitude={2.6}
          relief={1}
          lightAngle={170}
          mouseInteraction
          swellOnClick
          waveScale={0.7}
          swell={38}
          turbulence={24}
          fogDepth={12}
        />
      </div>

      <div className="hero-overlay-scrim" />

      <div className="hero-content">
        <div className="hero-badge">
          <span className="hero-badge-dot" />
          <span>ZipText v0.2.0 • ZTAR Core Framework • Lossless ASCII & Binary Containers</span>
        </div>

        {/* React Bits <TechText /> interactive vector wordmark with physics */}
        <div className="tech-text-container">
          <TechText
            text="ZIPTEXT"
            fontWeight={800}
            fontSize={140}
            color="#f8fafc"
            accentColor="#10b981"
            reveal="letter"
            dashLength={4}
            dashGap={2}
            specks={16}
            intro="assemble"
            introDuration={1.8}
            clickKick={true}
            draggable={true}
            bounce={0.4}
            guides={true}
          />
        </div>

        <p className="hero-tagline">
          Represent any file as a compact, reversible textual (<code style={{ color: '#34d399' }}>.ztxt</code>) or binary (<code style={{ color: '#38bdf8' }}>.zbin</code>) container. Bounded-memory streaming, adaptive compression algorithms, and byte-for-byte SHA-256 verification.
        </p>

        <div className="hero-buttons">
          <a 
            href="#simulator" 
            className="btn-primary"
            onClick={() => { playZipSound(); }}
          >
            <span>Interactive Simulator</span>
            <ArrowRight size={18} />
          </a>

          <a 
            href="#benchmarks" 
            className="btn-secondary"
            onClick={() => { playFelt(1.0); }}
          >
            <Cpu size={18} color="#34d399" />
            <span>Canterbury Benchmarks</span>
          </a>

          <a 
            href="#docs" 
            className="btn-secondary"
            onClick={() => { playFelt(0.9); }}
          >
            <BookOpen size={18} />
            <span>CLI & SDK Quickstart</span>
          </a>
        </div>
      </div>
    </section>
  );
}
