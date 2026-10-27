import React, { useState } from 'react';
import AnimatedContent from './AnimatedContent';
import { INCIDENT_REGISTER } from '../data/benchmarkData';
import { ShieldAlert, Bug, CheckCircle2, ChevronRight, FileCode2 } from 'lucide-react';
import { playFelt } from './sound';

export default function IncidentRegister() {
  const [selectedIncident, setSelectedIncident] = useState(INCIDENT_REGISTER[0]);

  const handleSelect = (item) => {
    playFelt(1.1);
    setSelectedIncident(item);
  };

  return (
    <section id="incidents" className="section">
      <AnimatedContent distance={50} direction="vertical" duration={0.8} threshold={0.1}>
        <div className="section-header">
          <span className="section-pill" style={{ color: '#f87171', borderColor: 'rgba(239, 68, 68, 0.3)', background: 'rgba(239, 68, 68, 0.1)' }}>
            Engineering Rigor
          </span>
          <h2 className="section-title">Incident & Error Log Register</h2>
          <p className="section-desc">
            Complete transparency into real test anomalies, root-cause forensics, regression unit tests, and structural fixes.
          </p>
        </div>
      </AnimatedContent>

      <div 
        style={{
          display: 'grid',
          gridTemplateColumns: 'minmax(300px, 1fr) 2fr',
          gap: '24px',
          background: 'var(--bg-card)',
          border: '1px solid var(--border-color)',
          borderRadius: 'var(--radius-xl)',
          padding: '24px',
          boxShadow: '0 20px 40px rgba(0, 0, 0, 0.4)'
        }}
      >
        {/* Incident List */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {INCIDENT_REGISTER.map((item) => (
            <div
              key={item.id}
              onClick={() => handleSelect(item)}
              style={{
                padding: '12px 16px',
                borderRadius: 'var(--radius-md)',
                background: selectedIncident.id === item.id ? 'rgba(16, 185, 129, 0.15)' : 'rgba(255, 255, 255, 0.03)',
                border: `1px solid ${selectedIncident.id === item.id ? 'var(--emerald-primary)' : 'var(--border-color)'}`,
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span 
                  style={{ 
                    fontFamily: 'var(--font-mono)', 
                    fontSize: '0.78rem', 
                    fontWeight: 700, 
                    color: selectedIncident.id === item.id ? 'var(--emerald-light)' : 'var(--text-muted)' 
                  }}
                >
                  {item.id}
                </span>
                <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                  {item.title}
                </span>
              </div>
              <ChevronRight size={16} color={selectedIncident.id === item.id ? '#34d399' : '#64748b'} />
            </div>
          ))}
        </div>

        {/* Selected Incident Detail */}
        <div 
          style={{
            background: 'rgba(0, 0, 0, 0.45)',
            border: '1px solid var(--border-color)',
            borderRadius: 'var(--radius-md)',
            padding: '24px',
            display: 'flex',
            flexDirection: 'column',
            gap: '16px'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.88rem', fontWeight: 700, color: '#34d399' }}>
              INCIDENT FORENSIC DOSSIER • {selectedIncident.id}
            </span>
            <span 
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                padding: '4px 10px',
                borderRadius: '9999px',
                background: 'rgba(16, 185, 129, 0.15)',
                color: '#34d399',
                fontSize: '0.75rem',
                fontWeight: 600
              }}
            >
              <CheckCircle2 size={12} />
              {selectedIncident.status}
            </span>
          </div>

          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#f8fafc' }}>
            {selectedIncident.title}
          </h3>

          <div>
            <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 700, letterSpacing: '0.05em' }}>
              Reported Symptom
            </span>
            <div style={{ marginTop: '4px', background: 'rgba(239, 68, 68, 0.08)', border: '1px solid rgba(239, 68, 68, 0.2)', padding: '10px 14px', borderRadius: '8px', fontFamily: 'var(--font-mono)', fontSize: '0.82rem', color: '#fca5a5' }}>
              {selectedIncident.symptom}
            </div>
          </div>

          <div>
            <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 700, letterSpacing: '0.05em' }}>
              Root Cause Analysis
            </span>
            <p style={{ marginTop: '4px', fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              {selectedIncident.rootCause}
            </p>
          </div>

          <div>
            <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 700, letterSpacing: '0.05em' }}>
              Architectural Fix & Test Verification
            </span>
            <div style={{ marginTop: '4px', background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.25)', padding: '12px 14px', borderRadius: '8px', fontSize: '0.88rem', color: '#6ee7b7', lineHeight: 1.5 }}>
              {selectedIncident.fix}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
