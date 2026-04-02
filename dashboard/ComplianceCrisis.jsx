import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, ShieldAlert, Zap } from 'lucide-react';

const stats = [
  {
    icon: TrendingUp,
    value: '$4.5T',
    label: 'Projected Agent Economy by 2030',
  },
  {
    icon: ShieldAlert,
    value: '89%',
    label: 'Of enterprises cite data provenance as top AI risk',
  },
  {
    icon: Zap,
    value: '$0.44',
    label: 'Average cost to verify + license one asset',
  },
];

export default function ComplianceCrisis() {
  return (
    <section className="py-16 md:py-24 px-4">
      <div className="max-w-5xl mx-auto">
        {/* Section header */}
        <motion.p
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-sm uppercase tracking-widest text-gray-500 text-center mb-4"
        >
          The 2026 Enterprise Bottleneck
        </motion.p>

        {/* Headline */}
        <motion.h2
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="text-3xl md:text-4xl font-bold text-white text-center mb-10 leading-tight"
        >
          AI is Autonomous. Enterprise Legal Teams Are Not.
        </motion.h2>

        {/* Image */}
        <motion.div
          initial={{ opacity: 0, scale: 0.97 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7, delay: 0.15 }}
          className="max-w-4xl mx-auto mb-3"
        >
          <img
            src="/site_images/kite-end-of-wild-west.png"
            alt="The End of the Wild West — legacy scraped datasets face mounting regulatory challenges"
            className="w-full rounded-xl border border-red-900/30"
          />
        </motion.div>
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="text-gray-500 text-xs md:text-sm text-center mb-12 italic"
        >
          Legacy scraped datasets face mounting regulatory and legal challenges.
        </motion.p>

        {/* Body paragraphs */}
        <div className="max-w-3xl mx-auto space-y-6 mb-12">
          <motion.p
            initial={{ opacity: 0, y: 14 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="text-gray-400 text-sm md:text-base leading-relaxed"
          >
            The transition to agentic AI has hit a wall: <strong className="text-white">Data Provenance</strong>.
            Following landmark 2025 rulings, scraping unverified datasets carries multi-billion-dollar
            class-action exposure. LAION-5B. Common Crawl. The shadow libraries that trained a generation
            of models are now legal liabilities.
          </motion.p>

          <motion.p
            initial={{ opacity: 0, y: 14 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="text-gray-400 text-sm md:text-base leading-relaxed"
          >
            To defend your algorithms, you must prove a high mathematical probability that your models
            do not contain infringing materials. But requiring human lawyers to authorize every agentic
            data transaction kills the autonomy that makes agents valuable.
          </motion.p>
        </div>

        {/* Solution callout */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.35 }}
          className="max-w-3xl mx-auto border-l-4 border-[#3399ff] bg-[#0066cc]/5 p-4 rounded mb-14"
        >
          <p className="text-gray-300 text-sm md:text-base leading-relaxed">
            <strong className="text-white">The Solution: Compliance-as-Code.</strong>{' '}
            We turn legal clearance into a sub-second, gasless API call. Your agents don't just
            ingest a file — they ingest an immutable C2PA Soulmark and a permanent x402 receipt
            of consent.
          </p>
        </motion.div>

        {/* Stat cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
          {stats.map((stat, i) => (
            <motion.div
              key={stat.value}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: 0.4 + i * 0.1 }}
              className="bg-white/[0.03] border border-gray-800 rounded-xl p-6 text-center hover:border-[#0066cc]/40 transition-colors"
            >
              <stat.icon className="w-6 h-6 text-[#3399ff] mx-auto mb-3" />
              <p className="text-3xl md:text-4xl font-bold text-white mb-2">{stat.value}</p>
              <p className="text-gray-400 text-xs md:text-sm leading-snug">{stat.label}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
