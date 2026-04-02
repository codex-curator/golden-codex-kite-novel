import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, Star } from 'lucide-react';

const requiredCriteria = [
  {
    title: 'Web App & CLI Tool',
    description: 'golden-codex.com live + Local Lite CLI for instant testing',
  },
  {
    title: 'Agent Authenticates Itself',
    description: 'Every agent uses a native Kite Passport before interacting with APIs',
  },
  {
    title: 'Executes Autonomously',
    description: 'Zero human clicks. Cloud Scheduler triggers. Agents decide independently.',
  },
  {
    title: 'On-Chain Settlement',
    description: 'x402 micropayments via Pieverse facilitator on Kite chain',
  },
  {
    title: 'Deployed Live in Production',
    description: 'GCP Cloud Run \u2014 186 Terraform-managed resources, L4 GPUs',
  },
  {
    title: 'GitHub Repo with Clear README',
    description: 'MIT licensed, docker-compose reproducible, full documentation',
  },
];

const bonusCriteria = [
  {
    title: 'Multi-Agent Coordination',
    description: '8-agent swarm passes structured tasks sequentially with provenance tracking',
  },
  {
    title: 'Scoped Permissions & Revocation',
    description: 'SPACE framework: ephemeral session keys, $10/day rate limits, autonomous financial revocation',
  },
  {
    title: 'Gas Abstraction',
    description: 'Integrated gokite-aa SDK \u2014 thousands of x402 micro-transactions with zero manual wallet clicks',
  },
];

const containerVariants = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: 0.12,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, x: -16 },
  visible: {
    opacity: 1,
    x: 0,
    transition: { duration: 0.4, ease: 'easeOut' },
  },
};

export default function RubricAlignment() {
  return (
    <section className="py-16 md:py-24 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center mb-14"
        >
          <p className="text-sm text-[#3399ff] uppercase tracking-wider font-medium mb-3">
            Engineered for Kite
          </p>
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            We Checked Every Box.{' '}
            <span className="bg-gradient-to-r from-[#FBBF24] to-[#F59E0B] bg-clip-text text-transparent">
              Including All Three Bonuses.
            </span>
          </h2>
          <p className="text-gray-400 max-w-2xl mx-auto text-sm md:text-base leading-relaxed">
            Agents on Golden Codex both spend and earn on the Kite L1. We didn't build
            a wrapper &mdash; we built a two-sided machine economy.
          </p>
        </motion.div>

        {/* Two-column grid */}
        <div className="grid md:grid-cols-2 gap-8">
          {/* Required Criteria */}
          <div>
            <motion.div
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              className="mb-5"
            >
              <span className="text-xs uppercase tracking-wider text-gray-500 font-semibold">
                Required Criteria &mdash; 6 / 6
              </span>
            </motion.div>

            <motion.ul
              className="space-y-4"
              variants={containerVariants}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: '-40px' }}
            >
              {requiredCriteria.map((item) => (
                <motion.li
                  key={item.title}
                  variants={itemVariants}
                  className="flex items-start gap-3 bg-white/[0.02] border border-gray-800/60 rounded-lg p-4 hover:border-green-400/20 transition-colors"
                >
                  <CheckCircle className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="text-white font-semibold text-sm">{item.title}</p>
                    <p className="text-gray-400 text-xs mt-0.5 leading-relaxed">
                      {item.description}
                    </p>
                  </div>
                </motion.li>
              ))}
            </motion.ul>
          </div>

          {/* Bonus Criteria */}
          <div>
            <motion.div
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              className="mb-5"
            >
              <span className="text-xs uppercase tracking-wider text-[#FBBF24]/70 font-semibold">
                Bonus Criteria &mdash; 3 / 3
              </span>
            </motion.div>

            <motion.ul
              className="space-y-4"
              variants={containerVariants}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: '-40px' }}
            >
              {bonusCriteria.map((item) => (
                <motion.li
                  key={item.title}
                  variants={itemVariants}
                  className="flex items-start gap-3 bg-[#FBBF24]/[0.03] border border-[#FBBF24]/20 rounded-lg p-4 hover:border-[#FBBF24]/40 transition-colors"
                >
                  <Star className="w-5 h-5 text-[#FBBF24] mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="text-white font-semibold text-sm">{item.title}</p>
                    <p className="text-gray-400 text-xs mt-0.5 leading-relaxed">
                      {item.description}
                    </p>
                  </div>
                </motion.li>
              ))}
            </motion.ul>

            {/* Summary badge */}
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.6, duration: 0.4 }}
              className="mt-6 bg-gradient-to-r from-[#FBBF24]/10 to-green-400/10 border border-[#FBBF24]/20 rounded-lg p-4 text-center"
            >
              <p className="text-white font-bold text-lg">
                9 / 9{' '}
                <span className="text-gray-400 font-normal text-sm">criteria met</span>
              </p>
              <p className="text-gray-500 text-xs mt-1">
                Perfect score. Every required + every bonus.
              </p>
            </motion.div>
          </div>
        </div>
      </div>
    </section>
  );
}
