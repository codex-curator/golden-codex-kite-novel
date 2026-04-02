import React from 'react';
import { motion } from 'framer-motion';
import { Terminal, Github } from 'lucide-react';

const terminalLines = [
  { type: 'comment', text: '# Clone the RAMS Local-Lite repository' },
  { type: 'command', text: '$ git clone https://github.com/codex-curator/rams-cli.git' },
  { type: 'command', text: '$ cd rams-cli' },
  { type: 'blank', text: '' },
  { type: 'comment', text: '# Boot the autonomous agents' },
  { type: 'command', text: '$ npm run start --lite' },
  { type: 'blank', text: '' },
  { type: 'output', text: '[Auth] Authenticating via Kite Agent Passport UID: 0xFE14...063B', color: 'text-blue-400' },
  { type: 'output', text: '[Scan] Monitoring X feed for new creative assets...', color: 'text-gray-400' },
  { type: 'output', text: '[Detect] New artwork found: @artiswagallery posted ARTISWA-0089', color: 'text-yellow-400' },
  { type: 'output', text: '[Verify] Aegis perceptual hash matched. C2PA Soulmark verified.', color: 'text-green-400' },
  { type: 'output', text: '[License] Claude Sonnet evaluated: APPROVED (quality: 0.94, relevance: high)', color: 'text-green-400' },
  { type: 'output', text: '[Settle] x402 payment: $0.95 → artist, $0.05 → platform, $0.02 → verification', color: 'text-purple-400' },
  { type: 'output', text: '[Bundle] 7 receipts batched → Merkle root anchored → 1 tx, 90% gas saved', color: 'text-cyan-400' },
  { type: 'output', text: '[Seal] EAS attestation registered on Kite chain. Clean data ready for ingestion.', color: 'text-cyan-400' },
];

function TerminalLine({ line, index }) {
  if (line.type === 'blank') {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ delay: index * 0.1 }}
        className="h-4"
      />
    );
  }

  let colorClass = 'text-gray-500';
  if (line.type === 'command') colorClass = 'text-green-400';
  if (line.type === 'comment') colorClass = 'text-gray-600';
  if (line.type === 'output') colorClass = line.color || 'text-gray-400';

  return (
    <motion.div
      initial={{ opacity: 0, x: -8 }}
      whileInView={{ opacity: 1, x: 0 }}
      viewport={{ once: true }}
      transition={{ delay: index * 0.1, duration: 0.3 }}
      className={`${colorClass} whitespace-pre-wrap break-all`}
    >
      {line.text}
    </motion.div>
  );
}

export default function CliDemo() {
  return (
    <section className="py-16 md:py-24 px-4">
      <div className="max-w-5xl mx-auto">

        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-10"
        >
          <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-green-500/10 border border-green-500/20 rounded-full mb-5">
            <Terminal className="w-4 h-4 text-green-400" />
            <span className="text-sm text-green-400 font-semibold">Developer Experience</span>
          </div>
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Test It Locally in{' '}
            <span className="bg-gradient-to-r from-green-400 to-[#3399ff] bg-clip-text text-transparent">
              60 Seconds
            </span>
          </h2>
          <p className="text-gray-400 max-w-2xl mx-auto">
            No GCP account needed. No GPU required. Clone, boot, and watch autonomous agents
            authenticate, discover, verify, license, and settle on Kite testnet — from your laptop.
          </p>
        </motion.div>

        {/* Terminal Mockup */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7, delay: 0.2 }}
          className="mb-8"
        >
          <div className="bg-gray-950 border border-gray-700 rounded-xl overflow-hidden shadow-2xl shadow-black/40">
            {/* Title Bar */}
            <div className="flex items-center gap-2 px-4 py-3 bg-gray-900/80 border-b border-gray-800">
              <div className="w-3 h-3 rounded-full bg-red-500" />
              <div className="w-3 h-3 rounded-full bg-yellow-500" />
              <div className="w-3 h-3 rounded-full bg-green-500" />
              <span className="ml-3 text-gray-500 text-xs font-mono">rams-cli — bash</span>
            </div>

            {/* Terminal Content */}
            <div className="p-5 md:p-6 font-mono text-sm leading-relaxed overflow-x-auto">
              {terminalLines.map((line, i) => (
                <TerminalLine key={i} line={line} index={i} />
              ))}
              {/* Blinking cursor */}
              <motion.span
                initial={{ opacity: 0 }}
                whileInView={{ opacity: 1 }}
                viewport={{ once: true }}
                transition={{ delay: terminalLines.length * 0.1 + 0.3 }}
                className="inline-block mt-2"
              >
                <span className="text-green-400">$ </span>
                <motion.span
                  animate={{ opacity: [1, 0] }}
                  transition={{ duration: 0.8, repeat: Infinity, repeatType: 'reverse' }}
                  className="inline-block w-2.5 h-4 bg-green-400 align-middle"
                />
              </motion.span>
            </div>
          </div>
        </motion.div>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ delay: 0.5 }}
          className="flex justify-center"
        >
          <a
            href="https://github.com/codex-curator/golden-codex-kite-novel"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-6 py-3 bg-[#0066cc]/20 border border-[#0066cc]/30 text-[#3399ff] rounded-lg hover:bg-[#0066cc]/30 transition-all text-sm font-medium"
          >
            <Github className="w-4 h-4" />
            View on GitHub — MIT Licensed
          </a>
        </motion.div>

      </div>
    </section>
  );
}
