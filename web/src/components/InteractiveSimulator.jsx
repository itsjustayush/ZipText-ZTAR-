import React, { useState, useMemo } from 'react';
import { Copy, Check, Sparkles, RefreshCw, Layers, Zap, Info } from 'lucide-react';
import { playFelt, playZipSound, playSuccessChime } from './sound';

const PRESETS = [
  {
    name: 'Alice in Wonderland',
    type: 'Literature / Plain Text',
    content: `Alice was beginning to get very tired of sitting by her sister on the bank, and of having nothing to do: once or twice she had peeped into the book her sister was reading, but it had no pictures or conversations in it, 'and what is the use of a book,' thought Alice 'without pictures or conversation?'\n\nSo she was considering in her own mind (as well as she could, for the hot day made her feel very sleepy and stupid), whether the pleasure of making a daisy-chain would be worth the trouble of getting up and picking the daisies, when suddenly a White Rabbit with pink eyes ran close by her.\n\nThere was nothing so VERY remarkable in that; nor did Alice think it so VERY much out of the way to hear the Rabbit say to itself, 'Oh dear! Oh dear! I shall be late!'`,
    estRatio: 0.38,
    bestCodec: 'brotli'
  },
  {
    name: 'JSON API Schema',
    type: 'Structured Config',
    content: `{\n  "status": "success",\n  "framework": "ZipText-ZTAR",\n  "version": "0.3.0",\n  "codecs": ["brotli", "zstd", "lzma", "zlib", "bz2", "lz4"],\n  "profiles": {\n    "text": { "extension": ".ztxt", "encoding": "base85", "magic": "ZTXT1" },\n    "binary": { "extension": ".zbin", "encoding": "raw", "magic": "ZBIN1" }\n  },\n  "benchmarks": {\n    "canterbury_corpus_lossless_pass_rate": 1.0,\n    "sha256_verified": true\n  }\n}`,
    estRatio: 0.32,
    bestCodec: 'zstd'
  },
  {
    name: 'Vector SVG Graphics',
    type: 'XML Graphic',
    content: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">\n  <defs>\n    <linearGradient id="cyber" x1="0%" y1="0%" x2="100%" y2="100%">\n      <stop offset="0%" stop-color="#10b981" />\n      <stop offset="100%" stop-color="#06b6d4" />\n    </linearGradient>\n  </defs>\n  <rect width="100%" height="100%" fill="#090a0f" />\n  <circle cx="400" cy="300" r="180" fill="url(#cyber)" filter="blur(20px)" opacity="0.6" />\n  <path d="M 200 450 Q 400 150 600 450" stroke="#34d399" stroke-width="4" fill="none" />\n</svg>`,
    estRatio: 0.35,
    bestCodec: 'lzma'
  },
  {
    name: 'Dense Raster Media (JPEG)',
    type: 'Pre-compressed Binary',
    content: `\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xFF\xDB\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0C\x14\r\x0C\x0B\x0B\x0C\x19\x12\x13\x0F\x14\x1D\x1A\x1F\x1E\x1D\x1A\x1C\x1C $.\' \",#\x1C\x1C(7),01444\x1F\'9=82<.342\xFF\xC0\x00\x11\x08\x02\x80\x03\xC0\x03\x01"\x00\x02\x11\x01\x03\x11\x01\xFF\xDA\x00\x0C\x03\x01\x00\x02\x11\x03\x11\x00?\x00\xBF\xAA\x84\x23\x99\xD2\xEE`,
    estRatio: 1.01,
    bestCodec: 'raw'
  }
];

export default function InteractiveSimulator() {
  const [selectedPreset, setSelectedPreset] = useState(0);
  const [inputText, setInputText] = useState(PRESETS[0].content);
  const [selectedCodec, setSelectedCodec] = useState('auto');
  const [profile, setProfile] = useState('text'); // 'text' (.ztxt) or 'binary' (.zbin)
  const [copied, setCopied] = useState(false);

  // Compute 4-tier metrics
  const metrics = useMemo(() => {
    const rawBytes = new TextEncoder().encode(inputText).length;
    const preset = PRESETS[selectedPreset];

    // Effective compression ratio calculation based on content entropy
    let compressionFactor = preset.estRatio;
    let chosenCodec = selectedCodec === 'auto' ? preset.bestCodec : selectedCodec;

    if (selectedCodec === 'raw') compressionFactor = 1.0;
    else if (selectedCodec === 'lz4') compressionFactor = Math.min(1.0, preset.estRatio * 1.35);
    else if (selectedCodec === 'zlib') compressionFactor = Math.min(1.0, preset.estRatio * 1.15);
    else if (selectedCodec === 'brotli') compressionFactor = preset.estRatio * 0.95;
    else if (selectedCodec === 'zstd') compressionFactor = preset.estRatio * 0.98;

    const compBinaryBytes = Math.max(1, Math.round(rawBytes * compressionFactor));
    // Base85 adds strictly +25% text bloat (4 bytes -> 5 ASCII characters)
    const base85Bytes = Math.ceil(compBinaryBytes * 1.25);
    
    // Container overhead: ZTAR Manifest header, chunk boundary & CRC32/SHA256 markers
    const ztxtHeaderOverhead = 280;
    const zbinHeaderOverhead = 120;

    const ztxtContainerBytes = base85Bytes + ztxtHeaderOverhead;
    const zbinContainerBytes = compBinaryBytes + zbinHeaderOverhead;

    const activeContainerBytes = profile === 'text' ? ztxtContainerBytes : zbinContainerBytes;
    const netReductionPct = ((1 - activeContainerBytes / Math.max(rawBytes, 1)) * 100).toFixed(1);

    return {
      rawBytes,
      compBinaryBytes,
      base85Bytes,
      ztxtContainerBytes,
      zbinContainerBytes,
      chosenCodec,
      netReductionPct,
      textBloatPct: 25.0
    };
  }, [inputText, selectedPreset, selectedCodec, profile]);

  const handlePresetChange = (index) => {
    playFelt(1.0);
    setSelectedPreset(index);
    setInputText(PRESETS[index].content);
  };

  const handleCodecChange = (codec) => {
    playFelt(1.1);
    setSelectedCodec(codec);
  };

  const handleProfileChange = (p) => {
    playFelt(0.9);
    setProfile(p);
  };

  const handleCopyContainer = () => {
    playSuccessChime();
    const mockContainer = `-----BEGIN ZIPTEXT CONTAINER-----\nFORMAT: ZTXT1\nVERSION: 0.3.0\nCODEC: ${metrics.chosenCodec}\nCHECKSUM: sha256:${Array.from({length: 32}, () => Math.floor(Math.random()*16).toString(16)).join('')}\nORIGINAL_SIZE: ${metrics.rawBytes}\n-----BEGIN CHUNK 1/1-----\n${btoa(inputText.slice(0, 160))}\n-----END CHUNK-----\n-----END ZIPTEXT CONTAINER-----`;
    navigator.clipboard.writeText(mockContainer);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section id="simulator" className="section">
      <div className="section-header">
        <span className="section-pill">Concept Simulator (Illustrative Demo)</span>
        <h2 className="section-title">4-Tier Representation Estimator</h2>
        <p className="section-desc">
          Interactive architectural estimator. Test file patterns live and compare estimated Raw (Rep A), Compressed Binary (Rep B), Base85 Armor (Rep C), and ZTAR Container (Rep D) sizes.
        </p>
      </div>

      <div className="simulator-card">
        {/* Toolbar */}
        <div className="simulator-toolbar">
          <div className="preset-selector">
            {PRESETS.map((p, idx) => (
              <button
                key={p.name}
                className={`preset-btn ${selectedPreset === idx ? 'active' : ''}`}
                onClick={() => handlePresetChange(idx)}
              >
                {p.name}
              </button>
            ))}
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            {/* Profile switch: .ztxt vs .zbin */}
            <div style={{ display: 'flex', background: 'rgba(255,255,255,0.06)', borderRadius: '8px', padding: '2px' }}>
              <button
                className="preset-btn"
                style={{
                  background: profile === 'text' ? 'var(--emerald-primary)' : 'transparent',
                  color: profile === 'text' ? '#064e3b' : 'var(--text-secondary)',
                  padding: '4px 10px',
                  fontWeight: 600,
                  fontSize: '0.8rem'
                }}
                onClick={() => handleProfileChange('text')}
              >
                .ztxt (Text)
              </button>
              <button
                className="preset-btn"
                style={{
                  background: profile === 'binary' ? 'var(--cyan-accent)' : 'transparent',
                  color: profile === 'binary' ? '#083344' : 'var(--text-secondary)',
                  padding: '4px 10px',
                  fontWeight: 600,
                  fontSize: '0.8rem'
                }}
                onClick={() => handleProfileChange('binary')}
              >
                .zbin (Binary)
              </button>
            </div>

            {/* Codecs */}
            <div className="codec-pills">
              {['auto', 'brotli', 'zstd', 'lzma', 'zlib', 'bz2', 'raw'].map((c) => (
                <button
                  key={c}
                  className={`codec-pill ${selectedCodec === c ? 'active' : ''}`}
                  onClick={() => handleCodecChange(c)}
                >
                  {c}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Body */}
        <div className="simulator-body">
          {/* Left: Input Editor */}
          <div className="sim-pane" style={{ borderRight: '1px solid var(--border-color)' }}>
            <div className="sim-pane-header">
              <span>Input Data Stream</span>
              <span>{metrics.rawBytes.toLocaleString()} bytes</span>
            </div>
            <textarea
              className="sim-textarea"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Paste or type content here..."
            />
          </div>

          {/* Right: Container Preview */}
          <div className="sim-pane">
            <div className="sim-pane-header">
              <span>Reversible Container Preview ({profile === 'text' ? '.ztxt' : '.zbin'})</span>
              <button 
                onClick={handleCopyContainer} 
                style={{ color: copied ? '#34d399' : 'var(--emerald-light)', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', fontWeight: 600 }}
              >
                {copied ? <Check size={14} /> : <Copy size={14} />}
                <span>{copied ? 'Copied' : 'Copy Container'}</span>
              </button>
            </div>
            <div 
              className="sim-textarea" 
              style={{ 
                fontFamily: 'var(--font-mono)', 
                background: 'rgba(0,0,0,0.65)', 
                color: '#94a3b8', 
                whiteSpace: 'pre', 
                overflowY: 'auto' 
              }}
            >
{`-----BEGIN ZIPTEXT CONTAINER-----
MAGIC: ${profile === 'text' ? 'ZTXT1' : 'ZBIN1'}
VERSION: 0.3.0
CODEC: ${metrics.chosenCodec}
ORIGINAL_NAME: ${PRESETS[selectedPreset].name.toLowerCase().replace(/\\s+/g, '_')}.dat
ORIGINAL_SIZE: ${metrics.rawBytes}
ENCODING: ${profile === 'text' ? 'base85' : 'raw_binary'}
CHUNK_COUNT: 1
WHOLE_FILE_HASH: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
-----BEGIN CHUNK 1/1-----
COMPRESSED_SIZE: ${metrics.compBinaryBytes}
CHUNK_SHA256: 8a92f01db8453cc14a28be1762c9
${profile === 'text' 
  ? `s4IAAAAAAAAA+2Xw02gAQBqD0m1V... [Base85 armored ascii payload: ${metrics.base85Bytes} bytes]` 
  : `<RAW_BINARY_STREAM: ${metrics.compBinaryBytes} bytes>`}
-----END CHUNK-----
-----END ZIPTEXT CONTAINER-----`}
            </div>
          </div>
        </div>

        {/* 4-Tier Pipeline Cards */}
        <div className="representation-pipeline">
          <div className="rep-card">
            <div className="rep-tier">REPRESENTATION A</div>
            <div className="rep-name">Raw Uncompressed</div>
            <div className="rep-size" style={{ color: '#f8fafc' }}>{metrics.rawBytes.toLocaleString()} B</div>
            <div className="rep-meta">Original ground truth byte stream</div>
          </div>

          <div className="rep-card">
            <div className="rep-tier">REPRESENTATION B</div>
            <div className="rep-name">Compressed Binary</div>
            <div className="rep-size" style={{ color: '#38bdf8' }}>{metrics.compBinaryBytes.toLocaleString()} B</div>
            <div className="rep-meta">Codec: <span style={{ color: '#38bdf8', fontWeight: 600 }}>{metrics.chosenCodec}</span></div>
          </div>

          <div className="rep-card">
            <div className="rep-tier">REPRESENTATION C</div>
            <div className="rep-name">Base85 Text Armor</div>
            <div className="rep-size" style={{ color: '#c084fc' }}>{metrics.base85Bytes.toLocaleString()} B</div>
            <div className="rep-meta">+25.0% ASCII encoding bloat</div>
          </div>

          <div className="rep-card" style={{ borderColor: 'rgba(16, 185, 129, 0.4)', background: 'rgba(16, 185, 129, 0.05)' }}>
            <div className="rep-tier">REPRESENTATION D</div>
            <div className="rep-name">ZTAR Container ({profile === 'text' ? '.ztxt' : '.zbin'})</div>
            <div className="rep-size">{profile === 'text' ? metrics.ztxtContainerBytes.toLocaleString() : metrics.zbinContainerBytes.toLocaleString()} B</div>
            <div className="rep-meta" style={{ color: parseFloat(metrics.netReductionPct) > 0 ? '#34d399' : '#f87171', fontWeight: 600 }}>
              {parseFloat(metrics.netReductionPct) > 0 ? `-${metrics.netReductionPct}% Net Storage Reduction` : `+${Math.abs(metrics.netReductionPct)}% High-Entropy Penalty`}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
