import React from 'react';
import { motion } from 'framer-motion';
import { ExternalLink, Github, BookOpen } from 'lucide-react';

export default function PitchSection() {
  return (
    <section className="py-20 md:py-28 px-4">
      <div className="max-w-5xl mx-auto">

        {/* Headline */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-14"
        >
          <p className="text-[#3399ff] text-sm font-semibold tracking-widest uppercase mb-4">
            Evaluate the Source
          </p>
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-6 leading-tight max-w-4xl mx-auto">
            The Agentic Economy Needs Clean Data.{' '}
            <span className="bg-gradient-to-r from-[#0066cc] to-[#3399ff] bg-clip-text text-transparent">
              We Are the Automated Clearing House.
            </span>
          </h2>
          <p className="text-gray-400 text-base md:text-lg max-w-3xl mx-auto leading-relaxed">
            A production-deployed compliance firewall with 8 autonomous agents, 500K+ verified assets,
            and a three-model intelligence stack — settling every operation on Kite chain.
            The company that aligns with Metavolve Labs is going to win the AI war.
          </p>
        </motion.div>

        {/* CTA Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-16"
        >
          <a
            href="https://github.com/codex-curator/golden-codex-kite-novel"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-center gap-2 px-5 py-3.5 bg-[#0066cc] hover:bg-[#0055aa] rounded-lg text-white font-medium transition-all text-sm"
          >
            <Github className="w-4 h-4" />
            GitHub Repo
          </a>
          <a
            href="https://docs.gokite.ai"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-center gap-2 px-5 py-3.5 bg-transparent border border-gray-600 hover:border-gray-400 rounded-lg text-gray-300 hover:text-white font-medium transition-all text-sm"
          >
            <BookOpen className="w-4 h-4" />
            Kite Documentation
          </a>
          <a
            href="https://golden-codex.com"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-center gap-2 px-5 py-3.5 bg-transparent border border-gray-600 hover:border-gray-400 rounded-lg text-gray-300 hover:text-white font-medium transition-all text-sm"
          >
            <ExternalLink className="w-4 h-4" />
            Live Platform
          </a>
        </motion.div>

        {/* Footer */}
        <div className="pt-10 border-t border-gray-800 text-center">
          <p className="text-gray-500 text-sm mb-1">
            Metavolve Labs, Inc. | San Francisco, California
          </p>
          <p className="text-gray-600 text-sm italic mb-6">
            "Synthetic Data is not the problem. Synthetic Garbage is."
          </p>
          <div className="flex items-center justify-center gap-5 text-xs text-gray-600">
            <a href="https://github.com/codex-curator" target="_blank" rel="noopener noreferrer" className="hover:text-gray-400 transition-colors">GitHub</a>
            <span className="text-gray-800">|</span>
            <a href="https://studiomcphub.com" target="_blank" rel="noopener noreferrer" className="hover:text-gray-400 transition-colors">StudioMCPHub</a>
            <span className="text-gray-800">|</span>
            <a href="https://huggingface.co/datasets/Metavolve-Labs/alexandria-aeternum-genesis" target="_blank" rel="noopener noreferrer" className="hover:text-gray-400 transition-colors">HuggingFace</a>
            <span className="text-gray-800">|</span>
            <a href="https://www.encode.club" target="_blank" rel="noopener noreferrer" className="hover:text-gray-400 transition-colors">Encode Club</a>
          </div>
        </div>

      </div>
    </section>
  );
}
