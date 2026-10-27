import React from 'react';
import LetterGlitch from './LetterGlitch';
import { playGlitchTick } from './sound';

export default function GlitchSection() {
  return (
    <section className="section" style={{ paddingTop: '2rem', paddingBottom: '2rem' }}>
      <div 
        style={{
          position: 'relative',
          width: '100%',
          height: '380px',
          borderRadius: 'var(--radius-xl)',
          overflow: 'hidden',
          border: '1px solid var(--border-color)',
          background: 'rgba(9, 10, 15, 0.85)'
        }}
        onPointerMove={() => {
          if (Math.random() < 0.08) playGlitchTick();
        }}
      >
        {/* React Bits <LetterGlitch /> component */}
        <LetterGlitch
          glitchColors={['#ffffff', '#10b981', '#34d399', '#06b6d4']}
          baseColor="#064e3b"
          glitchAmount={0.45}
          speed={0.9}
          flow={0.6}
          clickEffect="tear"
          interactive={true}
          cursorRadius={150}
          fontSize={15}
        />

        {/* Centered glass badge over the glitch canvas */}
        <div 
          style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            pointerEvents: 'none',
            background: 'radial-gradient(circle at 50% 50%, rgba(9, 10, 15, 0.6) 0%, rgba(9, 10, 15, 0.9) 80%)'
          }}
        >
          <div 
            style={{
              padding: '12px 28px',
              borderRadius: '9999px',
              background: 'rgba(16, 185, 129, 0.12)',
              border: '1px solid rgba(16, 185, 129, 0.35)',
              backdropFilter: 'blur(16px)',
              color: '#34d399',
              fontFamily: 'var(--font-mono)',
              fontSize: '0.9rem',
              fontWeight: 600,
              boxShadow: '0 0 30px rgba(16, 185, 129, 0.25)',
              textAlign: 'center'
            }}
          >
            INTERACTIVE STREAMING PAYLOAD MATRIX • MOVE CURSOR TO DECODE
          </div>
          <p style={{ marginTop: '10px', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Click anywhere on the grid to generate quantum burst tears
          </p>
        </div>
      </div>
    </section>
  );
}
