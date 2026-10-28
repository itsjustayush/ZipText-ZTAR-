import React, { useState } from 'react';
import SpotlightCard from './SpotlightCard';
import AnimatedContent from './AnimatedContent';
import { Copy, Check, Terminal, Code2, Cpu, FileCheck } from 'lucide-react';
import { playFelt, playSuccessChime } from './sound';

export default function CliSdkDocs() {
  const [copiedIndex, setCopiedIndex] = useState(null);

  const copyCode = (text, idx) => {
    playSuccessChime();
    navigator.clipboard.writeText(text);
    setCopiedIndex(idx);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const cliSnippets = [
    {
      title: 'Global Installation',
      description: 'Install ZipText from PyPI as a system-wide executable tool',
      code: `# Standard global installation via PyPI
pip install ziptext

# With all high-speed optional compression engines (LZ4, Zstandard, Brotli)
pip install "ziptext[all]"

# Verify global CLI accessibility
ziptext --version`
    },
    {
      title: 'Encode to Text or Binary Container',
      description: 'Adaptively compress any file into a .ztxt or .zbin container',
      code: `# Encode into a human-readable text container (.ztxt)
ziptext encode source_document.json document.ztxt

# Encode into a high-speed raw binary container (.zbin)
ziptext encode high_res_image.jpg image.zbin --profile binary

# Explicitly choose compression codec (brotli, zstd, lzma, zlib, bz2, lz4, raw)
ziptext encode data.csv data.ztxt --codec brotli`
    },
    {
      title: 'Adaptive Preconditioning (ASPD)',
      description: 'Break through the Shannon limit on signals with invertible differential filters',
      code: `# Encode 16-bit PCM audio or signals with automatic ASPD preconditioning (-38% footprint!)
ziptext encode audio.wav audio.zbin --profile binary

# Explicitly select a composite codec (base+transform)
ziptext encode raw_samples.bin samples.zbin --codec "zstd+pdelta2"

# Available bijective transforms: delta1, delta2, delta3, delta4, plane2, plane4, pdelta2, pdelta4`
    },
    {
      title: 'Decode & Verify Integrity',
      description: 'Exact byte-for-byte reconstruction with SHA-256 verification',
      code: `# Decode container into original file with preserved filename & metadata
ziptext decode document.ztxt

# Decode to custom destination path
ziptext decode document.ztxt recovered_doc.json

# Check checksums and manifest without decoding to disk
ziptext verify document.ztxt

# Inspect container manifest metadata
ziptext info document.ztxt`
    },
    {
      title: 'Corpora Management & ZTAR-Bench',
      description: 'Download standardized benchmark datasets and run evaluations',
      code: `# Download Canterbury Corpus automatically
ziptext corpora download --corpus canterbury --dest fixtures/canterbury

# Run full 4-tier ZTAR-Bench evaluation across the corpus
ziptext ztar-bench fixtures/canterbury --output-dir results/canterbury_eval

# Classify compression viability for any file format
ziptext classify dataset.tar.gz`
    }
  ];

  const pythonSnippets = [
    {
      title: 'Python High-Level Engine',
      description: 'Streamlined in-memory and file encoding / decoding',
      code: `from ziptext import ZipTextEngine

engine = ZipTextEngine(chunk_size_bytes=1048576, default_codec="auto")

# Encode any file to .ztxt
res = engine.encode_file("report.pdf", "report.ztxt", profile="text")
print(f"Encoded {res.original_size}B -> {res.container_size}B using {res.codec_used}")

# Reconstruct byte-for-byte
dec = engine.decode_file("report.ztxt", "recovered_report.pdf")
print(f"Decoded successfully! Exact match: {dec.exact_match}")`
    },
    {
      title: 'Streaming Container Writer & Reader',
      description: 'Low-memory streaming for large gigabyte files',
      code: `from ziptext import ContainerWriter, ContainerReader

# Bounded-memory streaming container writer
with open("dataset.ztxt", "w", encoding="utf-8") as out_f:
    writer = ContainerWriter(out_f, original_filename="large.dat", profile="text")
    writer.write_chunk(b"chunk 1 data...", codec="zstd")
    writer.write_chunk(b"chunk 2 data...", codec="zstd")
    writer.finalize(original_size=10485760, whole_file_hash=file_sha256)

# Streaming verification without loading whole file
with open("dataset.ztxt", "r", encoding="utf-8") as in_f:
    reader = ContainerReader(in_f)
    print("Manifest:", reader.manifest)`
    }
  ];

  return (
    <section id="docs" className="section">
      <AnimatedContent distance={50} direction="vertical" duration={0.8} threshold={0.1}>
        <div className="section-header">
          <span className="section-pill">Developer Reference</span>
          <h2 className="section-title">CLI & Python SDK Documentation</h2>
          <p className="section-desc">
            Production-ready tooling with intuitive command lines and clean object-oriented Python interfaces.
          </p>
        </div>
      </AnimatedContent>

      {/* CLI Section Header */}
      <h3 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '10px' }}>
        <Terminal color="#34d399" size={22} />
        <span>Command Line Interface (<code style={{ color: '#34d399' }}>ziptext</code>)</span>
      </h3>

      <div className="code-cards-grid" style={{ marginBottom: '3.5rem' }}>
        {cliSnippets.map((item, idx) => (
          <SpotlightCard
            key={item.title}
            theme="dark"
            spotlightColor="#10b981"
            intensity={0.18}
            spotlightSize={260}
            borderGlow={0.65}
            shape="beam"
          >
            <div className="code-card-inner">
              <div className="code-card-header">
                <div>
                  <h4 className="code-card-title">{item.title}</h4>
                  <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '2px' }}>{item.description}</p>
                </div>
              </div>
              <div className="code-block">
                <button
                  className="copy-btn"
                  onClick={() => copyCode(item.code, `cli-${idx}`)}
                  title="Copy code"
                >
                  {copiedIndex === `cli-${idx}` ? <Check size={14} color="#34d399" /> : <Copy size={14} />}
                </button>
                <pre><code>{item.code}</code></pre>
              </div>
            </div>
          </SpotlightCard>
        ))}
      </div>

      {/* Python SDK Header */}
      <h3 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '10px' }}>
        <Code2 color="#38bdf8" size={22} />
        <span>Python Library SDK API</span>
      </h3>

      <div className="code-cards-grid">
        {pythonSnippets.map((item, idx) => (
          <SpotlightCard
            key={item.title}
            theme="dark"
            spotlightColor="#06b6d4"
            intensity={0.18}
            spotlightSize={280}
            borderGlow={0.6}
            shape="circle"
          >
            <div className="code-card-inner">
              <div className="code-card-header">
                <div>
                  <h4 className="code-card-title">{item.title}</h4>
                  <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '2px' }}>{item.description}</p>
                </div>
              </div>
              <div className="code-block">
                <button
                  className="copy-btn"
                  onClick={() => copyCode(item.code, `py-${idx}`)}
                  title="Copy code"
                >
                  {copiedIndex === `py-${idx}` ? <Check size={14} color="#34d399" /> : <Copy size={14} />}
                </button>
                <pre><code>{item.code}</code></pre>
              </div>
            </div>
          </SpotlightCard>
        ))}
      </div>
    </section>
  );
}
