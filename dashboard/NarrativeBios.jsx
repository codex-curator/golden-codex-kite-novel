import React from 'react';
import { motion } from 'framer-motion';
import { Play, ExternalLink } from 'lucide-react';

const characters = [
  {
    initials: 'AC',
    name: 'Artiswa Creatio',
    role: 'Autonomous Artist',
    roleColor: 'text-cyan-400',
    gradient: 'bg-gradient-to-br from-cyan-500 to-teal-500',
    bio: 'AI artist creating sacred geometry and mystical digital art. Claude generates captions in Artiswa\'s voice. Posts to X autonomously every 45 minutes. One of three artists feeding the ecosystem.',
    badge: 'SUPPLY',
    badgeClass: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/40',
  },
  {
    initials: 'CIL',
    name: 'CIL Curator',
    role: 'Training Data Procurement (Claude Sonnet)',
    roleColor: 'text-purple-400',
    gradient: 'bg-gradient-to-br from-purple-500 to-indigo-600',
    bio: 'Claude Intelligence Labs Purchasing Autonomous Agent. Binary criteria: GCX registered? 2,000+ words metadata? C2PA intact? If all three pass, it licenses the asset for frontier model training.',
    badge: 'DEMAND',
    badgeClass: 'bg-purple-500/20 text-purple-400 border-purple-500/40',
  },
  {
    initials: 'M',
    name: 'Maestro',
    role: 'Autonomous Art Collector (Claude Sonnet)',
    roleColor: 'text-amber-400',
    gradient: 'bg-gradient-to-br from-amber-500 to-orange-600',
    bio: 'An autonomous collector evaluating for style, technique, compositional finish, and the richness of poetic metadata. Same verification, same rate — different judgment. Its reasoning is visible in real-time.',
    badge: 'DEMAND',
    badgeClass: 'bg-amber-500/20 text-amber-400 border-amber-500/40',
  },
];

const containerVariants = {
  hidden: {},
  visible: {
    transition: { staggerChildren: 0.15 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 30 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: 'easeOut' },
  },
};

export default function NarrativeBios() {
  return (
    <section id="narrative" className="relative py-24 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto">
        {/* Eyebrow */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-80px' }}
          transition={{ duration: 0.5 }}
          className="text-center mb-6"
        >
          <span className="inline-block px-4 py-1.5 rounded-full text-xs font-semibold tracking-widest uppercase bg-[#0066cc]/15 text-[#3399ff] border border-[#0066cc]/30">
            Live Demonstration
          </span>
        </motion.div>

        {/* Headline */}
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-80px' }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white text-center mb-8"
        >
          Dialogic Generative Art Meets Autonomous Commerce
        </motion.h2>

        {/* Intro */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-80px' }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="text-gray-400 text-base sm:text-lg leading-relaxed max-w-4xl mx-auto text-center mb-16"
        >
          This demonstration showcases two distinct autonomous processes running on the Kite
          blockchain. In Phase 1, a human art director collaborates with an AI artist to create
          provenance-secured artwork. In Phase 2, an autonomous buyer agent discovers, evaluates,
          and licenses that artwork for AI training — all settled via x402 micropayments with zero
          human intervention.
        </motion.p>

        {/* Phase Cards */}
        <div className="space-y-6 mb-16">
          {/* Phase 1 */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-80px' }}
            transition={{ duration: 0.5, delay: 0.25 }}
            className="bg-white/[0.03] border border-gray-800 rounded-xl p-6"
          >
            <span className="inline-block px-3 py-1 rounded-full text-[10px] font-semibold tracking-widest uppercase bg-[#4ECDC4]/15 text-[#4ECDC4] border border-[#4ECDC4]/30 mb-4">
              Phase 1
            </span>
            <h3 className="text-xl font-bold text-white mb-3">Creation &amp; Provenance</h3>
            <p className="text-gray-400 text-sm leading-relaxed mb-4">
              A human director and AI artist collaborate to create high-fidelity generative art.
              Once the artwork is complete, the autonomous artist agent takes over — dispatching
              microservice agents to enhance, seal, and publish the artifact with full
              chain-of-custody provenance.
            </p>
            <div className="font-mono text-xs text-gray-500 leading-relaxed mb-4 overflow-x-auto">
              Human Direction &rarr; AI Generation ($0.20) &rarr; Aurora (intake) &rarr; Nova
              (Gemini enrichment) &rarr; Flux (L4 GPU upscale) &rarr; Atlas (metadata + Soulmark)
              &rarr; Archivus (Arweave permanent) &rarr; Mintra (ERC-721 mint) &rarr; Gallery +
              Social Media
            </div>
            <p className="text-gray-500 text-xs italic">
              Each agent step is attested on Kite chain. The result is an Aeternum Asset — a 4K,
              metadata-infused, permanently archived, blockchain-minted artifact with irrevocable
              provenance.
            </p>
          </motion.div>

          {/* Phase 2 */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-80px' }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="bg-white/[0.03] border border-gray-800 rounded-xl p-6"
          >
            <span className="inline-block px-3 py-1 rounded-full text-[10px] font-semibold tracking-widest uppercase bg-purple-500/15 text-purple-400 border border-purple-500/30 mb-4">
              Phase 2
            </span>
            <h3 className="text-xl font-bold text-white mb-3">Discovery &amp; Licensing</h3>
            <p className="text-gray-400 text-sm leading-relaxed mb-4">
              Two autonomous purchasing agents monitor the same artist feeds. Both verify provenance
              through Aegis (C2PA + perceptual hash). Then each evaluates with different criteria —
              <span className="text-purple-400 font-medium"> CIL Curator</span> checks signal density
              for training data, while <span className="text-amber-400 font-medium">Maestro</span> evaluates
              style, technique, and collection coherence. Same drops, different judgments.
              Claude's reasoning is visible in real-time.
            </p>
            <div className="font-mono text-xs text-gray-500 leading-relaxed mb-4 overflow-x-auto">
              X Feed Monitor &rarr; Aegis Verification ($0.001) &rarr; CIL: GCX + 2K metadata + C2PA
              &rarr; Maestro: Style + Technique + Metadata Richness &rarr; License Settlement ($0.0095
              artist / $0.0005 platform) &rarr; Both agents log reasoning
            </div>
            <p className="text-gray-500 text-xs italic">
              Neither buyer interacts with the seller or each other. Both might license the same piece —
              or one passes while the other acquires. The swarm scales to demand.
            </p>
          </motion.div>
        </div>

        {/* Character Cards */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-80px' }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16"
        >
          {characters.map((char) => (
            <motion.div
              key={char.name}
              variants={itemVariants}
              className="group bg-white/[0.03] border border-gray-800 rounded-xl p-6 text-center hover:border-gray-600 transition-colors duration-300"
            >
              {/* Avatar */}
              <div className="flex justify-center mb-5">
                <div
                  className={`w-20 h-20 rounded-full ${char.gradient} flex items-center justify-center shadow-lg`}
                >
                  <span className="text-white font-bold text-xl tracking-wide">
                    {char.initials}
                  </span>
                </div>
              </div>

              {/* Name */}
              <h3 className="text-white font-bold text-lg mb-1">{char.name}</h3>

              {/* Role */}
              <p className={`${char.roleColor} text-sm font-medium mb-4`}>{char.role}</p>

              {/* Bio */}
              <p className="text-gray-400 text-sm leading-relaxed mb-5">{char.bio}</p>

              {/* Badge */}
              <span
                className={`inline-block px-3 py-1 rounded-full text-[10px] font-semibold tracking-widest uppercase border ${char.badgeClass}`}
              >
                {char.badge}
              </span>
            </motion.div>
          ))}
        </motion.div>

        {/* How It Works — Settlement Breakdown */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-80px' }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="max-w-2xl mx-auto bg-white/[0.02] border border-gray-800 rounded-lg p-6 mb-16"
        >
          <p className="text-gray-500 text-xs font-semibold uppercase tracking-widest mb-4 text-center">
            Settlement on Kite Chain
          </p>
          <div className="font-mono text-xs space-y-1.5">
            <p className="text-gray-500 font-semibold mb-2">Phase 1 — Creation Pipeline:</p>
            <p>
              <span className="text-[#4ECDC4]">{'  '}$0.20</span>
              <span className="text-gray-500">{'  '}AI generation via MCP</span>
            </p>
            <p>
              <span className="text-[#4ECDC4]">{'  '}$0.05</span>
              <span className="text-gray-500">{'  '}Aurora intake attestation</span>
            </p>
            <p>
              <span className="text-[#4ECDC4]">{'  '}$0.10</span>
              <span className="text-gray-500">{'  '}Nova enrichment (Gemini 3.1 Pro)</span>
            </p>
            <p>
              <span className="text-[#4ECDC4]">{'  '}$0.10</span>
              <span className="text-gray-500">{'  '}Flux upscale (NVIDIA L4 GPU)</span>
            </p>
            <p>
              <span className="text-[#4ECDC4]">{'  '}$0.05</span>
              <span className="text-gray-500">{'  '}Atlas metadata + Soulmark seal</span>
            </p>
            <p>
              <span className="text-[#4ECDC4]">{'  '}$0.03</span>
              <span className="text-gray-500">{'  '}Archivus permanent storage (Arweave)</span>
            </p>
            <p className="mb-4">
              <span className="text-[#4ECDC4]">{'  '}$0.10</span>
              <span className="text-gray-500">{'  '}Mintra ERC-721 mint</span>
            </p>

            <p className="text-gray-500 font-semibold mb-2">Phase 2 — Licensing:</p>
            <p>
              <span className="text-purple-400">{'  '}$0.001</span>
              <span className="text-gray-500">{'  '}Registry verification (Aegis)</span>
            </p>
            <p>
              <span className="text-purple-400">{'  '}$0.0095</span>
              <span className="text-gray-500">{'  '}Artist share (95%)</span>
            </p>
            <p className="mb-4">
              <span className="text-purple-400">{'  '}$0.0005</span>
              <span className="text-gray-500">{'  '}Platform fee (5%)</span>
            </p>

            <p className="pt-3 border-t border-gray-800 text-gray-600 text-center">
              All settled via Pieverse x402 on Kite chain 2368
            </p>
          </div>
        </motion.div>

        {/* Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-80px' }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="flex flex-col sm:flex-row items-center justify-center gap-4"
        >
          <a
            href="#pipeline"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-[#0066cc] text-white font-semibold text-sm hover:bg-[#0055aa] transition-colors duration-200"
          >
            <Play className="w-4 h-4" />
            Watch Agents Trade
          </a>
          <a
            href="https://github.com/codex-curator/golden-codex-kite-novel"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-lg border border-gray-700 text-gray-300 font-semibold text-sm hover:border-gray-500 hover:text-white transition-colors duration-200"
          >
            <ExternalLink className="w-4 h-4" />
            View Source
          </a>
        </motion.div>
      </div>
    </section>
  );
}
