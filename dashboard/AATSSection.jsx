import React from 'react';
import { motion } from 'framer-motion';
import { Shield, Brain, TrendingUp, AlertTriangle } from 'lucide-react';

const capabilities = [
  {
    icon: Shield,
    title: 'Behavioral Credit Scoring',
    description: 'Trust earned through cryptographically verifiable on-chain behavior — not granted through static identity passports.',
  },
  {
    icon: Brain,
    title: 'LLM Sentinel Swarms',
    description: 'AI policing AI across chains and aliases. Sentinel agents monitor the transaction graph in real-time, connecting wallet migrations and tracking bad operators as they attempt to evade detection.',
  },
  {
    icon: TrendingUp,
    title: 'Anti-Sybil Economics',
    description: 'The 95/5 royalty split is a cryptoeconomic defense — every wash trade bleeds 95% to the creator. Fake volume = financial suicide.',
  },
  {
    icon: AlertTriangle,
    title: 'Autophagy Firewall',
    description: 'Agents that ingest verified data get rewarded. Agents that scrape synthetic slop get penalized. Model collapse prevention as a market force.',
  },
];

export default function AATSSection() {
  return (
    <section id="aats" className="py-16 md:py-24 px-4">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-red-500/10 border border-red-500/20 rounded-full mb-5">
            <Shield className="w-4 h-4 text-red-400" />
            <span className="text-sm text-red-400 font-semibold">Integrity Enforcement</span>
          </div>
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            The{' '}
            <span className="bg-gradient-to-r from-red-400 to-[#3399ff] bg-clip-text text-transparent">
              FICO of AGI
            </span>
          </h2>
          <p className="text-gray-400 max-w-3xl mx-auto leading-relaxed">
            The Autonomous Agent Trust Score (AATS) transforms the Golden Codex Registry into a
            decentralized "Agent Credit Bureau" — a behavioral layer that complements identity
            systems like Kite Passport. Trust is computed from on-chain execution history,
            data provenance compliance, and economic alignment, building a living reputation
            that evolves over time.
          </p>
        </motion.div>

        {/* Maestro Avatar + Abstract */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.15 }}
          className="bg-white/[0.03] border border-gray-800 rounded-xl p-6 md:p-8 mb-12"
        >
          <div className="flex items-start gap-5 mb-6">
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-red-500 to-red-700 flex items-center justify-center flex-shrink-0 border-2 border-red-500/30">
              <span className="text-white font-bold text-xs tracking-wider">ARGUS</span>
            </div>
            <div>
              <h3 className="text-white font-bold text-lg">Argus — Autonomous Trust Guardian</h3>
              <p className="text-red-400 text-sm">Behavioral Credit Scoring & Integrity Enforcement</p>
            </div>
          </div>
          <div className="space-y-4 text-gray-400 text-sm leading-relaxed">
            <p>
              Identity tells you <em>who</em> an agent is. Behavior tells you <em>what it does</em>. The AATS
              adds a behavioral credit layer on top of identity systems like Kite Passport — computing trust from{' '}
              <strong className="text-white">continuous on-chain signals</strong>:
              every x402 settlement, every royalty split honored, every verified dataset purchased.
              An agent verified today may drift tomorrow. The score catches it.
            </p>
            <p>
              Argus operates as the enforcement layer — LLM Sentinel Swarms that analyze the transaction graph
              in real-time, flag coordinated attacks, and connect wallet migrations across chains and aliases.
              Scores follow bad operators as they try to evade detection. Score improvement is measured{' '}
              <strong className="text-white">over time, not transactionally</strong> — computed via{' '}
              <span className="text-[#3399ff]">EigenTrust + TraceRank</span> algorithms
              with logarithmic value weighting and exponential temporal decay.
            </p>
          </div>
        </motion.div>

        {/* Capability Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {capabilities.map((cap, i) => {
            const Icon = cap.icon;
            return (
              <motion.div
                key={cap.title}
                initial={{ opacity: 0, y: 15 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: 0.1 * i }}
                className="bg-white/[0.02] border border-gray-800/60 rounded-xl p-5 hover:border-red-500/20 transition-colors"
              >
                <div className="flex items-start gap-3">
                  <div className="w-9 h-9 rounded-lg bg-red-500/10 flex items-center justify-center flex-shrink-0">
                    <Icon className="w-4 h-4 text-red-400" />
                  </div>
                  <div>
                    <h4 className="text-white font-semibold text-sm mb-1">{cap.title}</h4>
                    <p className="text-gray-400 text-xs leading-relaxed">{cap.description}</p>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* Mathematical Formula */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ delay: 0.5 }}
          className="mt-8 text-center"
        >
          <p className="font-mono text-xs text-gray-600">
            Flow(i→j) = Σ log(1 + value<sub>k</sub>) × e<sup>-λ × age<sub>k</sub></sup>
            {' '}|{' '}
            <span className="text-gray-500">EigenTrust + TraceRank on Base L2 / Kite EAS</span>
          </p>
        </motion.div>
      </div>
    </section>
  );
}
