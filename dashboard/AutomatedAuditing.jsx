import React from 'react';
import { motion } from 'framer-motion';
import { Image, Video, FileText, Database } from 'lucide-react';

const dataTypes = [
  {
    icon: Image,
    title: 'Digital Art & Photography',
    description: '500K+ assets verified. C2PA + perceptual hash at 100K+ scale.',
  },
  {
    icon: Video,
    title: 'Video & Animation',
    description: 'Frame-level provenance verification. VEO 2 animated narrative support.',
  },
  {
    icon: FileText,
    title: 'Documents & Manuals',
    description: 'Cryptographic sealing for RAG pipelines and enterprise IP.',
  },
  {
    icon: Database,
    title: 'Training Datasets',
    description: 'Autonomous micro-licensing for compliant model training at scale.',
  },
];

const stats = [
  { value: '3 AI Models', label: 'Claude + Gemini + GPT-4o intelligence stack' },
  { value: '27 MCP Tools', label: 'Live at StudioMCPHub.com \u2014 discoverable by any agent' },
  { value: '186 Resources', label: 'Terraform-managed GCP production infrastructure' },
];

export default function AutomatedAuditing() {
  return (
    <section className="py-16 md:py-24 px-4 bg-[#0a0a1e]">
      <div className="max-w-6xl mx-auto">
        {/* Eyebrow */}
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-sm text-[#4ECDC4] uppercase tracking-wider text-center mb-4"
        >
          The Omnivore Data Refinery
        </motion.p>

        {/* Headline */}
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="text-3xl md:text-4xl font-bold text-white text-center mb-6"
        >
          Art Was the Stress Test.{' '}
          <span className="bg-gradient-to-r from-[#0066cc] to-[#3399ff] bg-clip-text text-transparent">
            Enterprise Data Is the Destination.
          </span>
        </motion.h2>

        {/* Subheadline */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="text-gray-400 text-center max-w-3xl mx-auto mb-12 leading-relaxed"
        >
          We built this infrastructure on digital art because high-dimensional perceptual
          hashing is the hardest computational provenance problem to solve. We solved it.
          Now, our format-agnostic metadata factory processes the high-signal, real-world
          data your frontier models need to scale.
        </motion.p>

        {/* NEST Image */}
        <motion.div
          initial={{ opacity: 0, scale: 0.97 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="max-w-4xl mx-auto mb-4"
        >
          <img
            src="/site_images/kite-automated-auditing.png"
            alt="NEST automated auditing dashboard showing AI agents filtering synthetic data"
            className="w-full rounded-xl border border-[#4ECDC4]/20"
          />
        </motion.div>
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.5 }}
          className="text-gray-500 text-sm text-center max-w-3xl mx-auto mb-16"
        >
          NEST-powered AI agents filter synthetic data in real-time, matching against
          Persistent Provenance Pointers.
        </motion.p>

        {/* Data-type Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 mb-16">
          {dataTypes.map((item, i) => {
            const Icon = item.icon;
            return (
              <motion.div
                key={item.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: 0.1 * i }}
                className="bg-white/[0.03] border border-gray-800 rounded-xl p-5 hover:border-[#4ECDC4]/30 transition-colors"
              >
                <div className="w-10 h-10 rounded-lg bg-[#4ECDC4]/10 flex items-center justify-center mb-3">
                  <Icon className="w-5 h-5 text-[#4ECDC4]" />
                </div>
                <h3 className="text-white font-semibold text-sm mb-2">{item.title}</h3>
                <p className="text-gray-400 text-xs leading-relaxed">{item.description}</p>
              </motion.div>
            );
          })}
        </div>

        {/* Key Differentiator Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto"
        >
          {stats.map((stat, i) => (
            <motion.div
              key={stat.value}
              initial={{ opacity: 0, y: 15 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: 0.15 * i }}
              className="text-center p-6 bg-white/[0.02] border border-gray-800/60 rounded-xl"
            >
              <p className="text-2xl md:text-3xl font-bold bg-gradient-to-r from-[#4ECDC4] to-[#3399ff] bg-clip-text text-transparent mb-2">
                {stat.value}
              </p>
              <p className="text-gray-400 text-sm">{stat.label}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
