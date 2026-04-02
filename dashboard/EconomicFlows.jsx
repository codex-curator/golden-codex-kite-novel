import React from 'react';
import { motion } from 'framer-motion';
import { ArrowRightLeft, ShoppingCart, Globe, ArrowRight } from 'lucide-react';

const flows = [
  {
    icon: ArrowRightLeft,
    title: 'Internal Settlement',
    color: '#3399ff',
    borderColor: '#3399ff',
    description:
      '8 pipeline agents settle every operation on Kite via x402. Aurora verifies intake ($0.05), Nova enriches with Gemini ($0.10), Flux upscales on L4 GPU ($0.10), Atlas infuses metadata ($0.05). Each agent earns PoAI rewards for compute work.',
    flow: [
      { label: 'Thalos', cost: null },
      { label: 'Aurora', cost: '$0.05' },
      { label: 'Nova', cost: '$0.10' },
      { label: 'Flux', cost: '$0.10' },
      { label: 'Atlas', cost: '$0.05' },
      { label: 'Archivus', cost: null },
      { label: 'Mintra', cost: null },
      { label: 'Aegis', cost: null },
    ],
    badge: 'gokite-aa protocol',
  },
  {
    icon: ShoppingCart,
    title: 'Enterprise Data Procurement',
    color: '#4ECDC4',
    borderColor: '#4ECDC4',
    description:
      'Autonomous procurement bots discover creative assets on social platforms, verify provenance via C2PA + perceptual hash, evaluate quality with Claude Sonnet, and license compliant training data \u2014 all settled on Kite with zero human intervention.',
    flow: [
      { label: 'X Feed', cost: null },
      { label: 'Watchdog', cost: null },
      { label: 'Aegis Verify', cost: null },
      { label: 'Claude Evaluate', cost: null },
      { label: 'x402 License', cost: null },
    ],
    badge: 'Zero-touch compliance',
  },
  {
    icon: Globe,
    title: 'MCP Service Marketplace',
    color: '#E17055',
    borderColor: '#E17055',
    description:
      '27 live tools on StudioMCPHub, discoverable by any AI agent via Model Context Protocol. External agents call verify_provenance ($0.008), upscale_image ($0.10), or search_dataset ($0.005) \u2014 paying on Kite. Agents both spend and earn.',
    flow: [
      { label: 'Any AI Agent', cost: null },
      { label: 'MCP Discovery', cost: null },
      { label: 'StudioMCPHub', cost: null },
      { label: 'x402 Settlement', cost: null },
    ],
    badge: 'Two-sided economy',
  },
];

function FlowDiagram({ flow, color }) {
  return (
    <div className="bg-black/60 rounded-lg p-3 overflow-x-auto">
      <div className="text-[10px] text-gray-600 uppercase tracking-wider mb-2">
        Pipeline Flow
      </div>
      <div className="flex items-center gap-1 flex-wrap font-mono text-xs">
        {flow.map((step, i) => (
          <React.Fragment key={i}>
            <span className="inline-flex flex-col items-center gap-0.5">
              <span className="text-gray-300">{step.label}</span>
              {step.cost && (
                <span className="text-green-400 text-[10px]">{step.cost}</span>
              )}
            </span>
            {i < flow.length - 1 && (
              <ArrowRight
                className="w-3 h-3 flex-shrink-0"
                style={{ color: `${color}80` }}
              />
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}

function FlowCard({ data, index }) {
  const Icon = data.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-50px' }}
      transition={{ duration: 0.5, delay: index * 0.15 }}
      className="bg-white/5 border border-gray-800 border-l-4 rounded-xl p-6 hover:border-gray-600 transition-all flex flex-col"
      style={{ borderLeftColor: data.borderColor }}
    >
      {/* Icon */}
      <div
        className="w-12 h-12 rounded-lg flex items-center justify-center mb-4"
        style={{
          backgroundColor: `${data.color}15`,
          border: `1px solid ${data.color}30`,
        }}
      >
        <Icon className="w-6 h-6" style={{ color: data.color }} />
      </div>

      {/* Title */}
      <h3 className="text-lg font-bold text-white mb-2">{data.title}</h3>

      {/* Description */}
      <p className="text-sm text-gray-400 leading-relaxed mb-4 flex-1">
        {data.description}
      </p>

      {/* Flow visualization */}
      <div className="mb-4">
        <FlowDiagram flow={data.flow} color={data.color} />
      </div>

      {/* Badge */}
      <div className="flex justify-end">
        <span
          className="px-3 py-1 rounded-full text-xs font-mono"
          style={{
            backgroundColor: `${data.color}15`,
            color: data.color,
            border: `1px solid ${data.color}30`,
          }}
        >
          {data.badge}
        </span>
      </div>
    </motion.div>
  );
}

export default function EconomicFlows() {
  return (
    <section className="py-16 md:py-24 px-4">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center mb-12"
        >
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-3">
            Three Economic Flows on Kite
          </h2>
          <p className="text-gray-400 max-w-2xl mx-auto">
            The RAMS enables a two-sided agentic economy where autonomous agents
            are both consumers and providers of paid services, all settled on
            Kite via x402.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {flows.map((flow, i) => (
            <FlowCard key={i} data={flow} index={i} />
          ))}
        </div>
      </div>
    </section>
  );
}
