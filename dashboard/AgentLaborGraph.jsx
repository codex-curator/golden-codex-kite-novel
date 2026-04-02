import React, { useState, useEffect, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Crown, Sunrise, Sparkles, Maximize2, FileCode,
  Archive, Gem, Shield, Globe, Play, RotateCcw,
  CheckCircle, Loader2, Circle, DollarSign, ExternalLink,
  X
} from 'lucide-react';
import { AGENTS, STUDIO_MCP_HUB, PIPELINE_EDGES, generateTxHash, KITE_TESTNET, KITE_CHAIN } from '@/utils/kite/constants';

const ICON_MAP = {
  Crown, Sunrise, Sparkles, Maximize2, FileCode,
  Archive, Gem, Shield, Globe,
};

// Node positions for the pipeline layout (responsive percentages)
// Left 65% is the agent graph, right 35% reserved for settlement ledger
const NODE_POSITIONS = {
  'thalos-prime': { x: 33, y: 8 },
  'aurora':       { x: 10, y: 30 },
  'nova':         { x: 28, y: 48 },
  'flux':         { x: 46, y: 30 },
  'atlas':        { x: 56, y: 48 },
  'archivus':     { x: 18, y: 70 },
  'mintra':       { x: 36, y: 84 },
  'aegis':        { x: 56, y: 70 },
  'studio-mcp-hub': { x: 46, y: 92 },
};

// Pipeline processing order
const PROCESSING_ORDER = ['aurora', 'nova', 'flux', 'atlas', 'archivus', 'mintra', 'aegis'];

function AgentNode({ agent, isActive, isCompleted, isProcessing, onClick, position }) {
  const IconComponent = ICON_MAP[agent.icon] || Circle;
  const isExternal = agent.id === 'studio-mcp-hub';

  return (
    <motion.div
      className="absolute cursor-pointer select-none"
      style={{
        left: `${position.x}%`,
        top: `${position.y}%`,
        transform: 'translate(-50%, -50%)',
        zIndex: isActive ? 20 : 10,
      }}
      onClick={() => onClick(agent)}
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.95 }}
    >
      {/* Pulse ring when processing */}
      {isProcessing && (
        <motion.div
          className="absolute inset-0 rounded-full"
          style={{
            border: `2px solid ${agent.color}`,
            margin: '-8px',
          }}
          animate={{ scale: [1, 1.5, 1], opacity: [0.8, 0, 0.8] }}
          transition={{ duration: 1.5, repeat: Infinity }}
        />
      )}

      {/* Node circle */}
      <motion.div
        className={`relative flex items-center justify-center rounded-full border-2 ${
          isExternal ? 'w-14 h-14 md:w-16 md:h-16' : 'w-16 h-16 md:w-20 md:h-20'
        }`}
        style={{
          borderColor: agent.color,
          backgroundColor: isActive || isCompleted
            ? `${agent.color}20`
            : 'rgba(10, 10, 15, 0.9)',
          boxShadow: isActive
            ? `0 0 20px ${agent.color}40, 0 0 40px ${agent.color}20`
            : isCompleted
            ? `0 0 10px ${agent.color}30`
            : 'none',
        }}
        animate={isProcessing ? { borderColor: [agent.color, '#ffffff', agent.color] } : {}}
        transition={{ duration: 1, repeat: isProcessing ? Infinity : 0 }}
      >
        <IconComponent
          className="w-6 h-6 md:w-8 md:h-8"
          style={{ color: agent.color }}
        />
        {isProcessing && (
          <Loader2 className="absolute -top-1 -right-1 w-4 h-4 text-[#3399ff] animate-spin" />
        )}
        {isCompleted && (
          <CheckCircle className="absolute -top-1 -right-1 w-4 h-4 text-green-400" />
        )}
      </motion.div>

      {/* Label */}
      <div className="text-center mt-1">
        <div className="text-xs md:text-sm font-bold text-white">{agent.name}</div>
        <div className="text-[10px] md:text-xs text-gray-500 hidden md:block">{agent.role}</div>
      </div>
    </motion.div>
  );
}

function PaymentParticle({ from, to, amount, color, onComplete }) {
  const fromPos = NODE_POSITIONS[from];
  const toPos = NODE_POSITIONS[to];
  if (!fromPos || !toPos) return null;

  return (
    <motion.div
      className="absolute z-30 pointer-events-none"
      initial={{
        left: `${fromPos.x}%`,
        top: `${fromPos.y}%`,
        opacity: 0,
        scale: 0,
      }}
      animate={{
        left: `${toPos.x}%`,
        top: `${toPos.y}%`,
        opacity: [0, 1, 1, 0],
        scale: [0, 1, 1, 0.5],
      }}
      transition={{ duration: 1.2, ease: 'easeInOut' }}
      onAnimationComplete={onComplete}
      style={{ transform: 'translate(-50%, -50%)' }}
    >
      <div
        className="flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-mono font-bold whitespace-nowrap"
        style={{
          backgroundColor: `${color}30`,
          border: `1px solid ${color}`,
          color: color,
        }}
      >
        <DollarSign className="w-3 h-3" />
        {amount}
      </div>
    </motion.div>
  );
}

function ConnectionLine({ from, to, isActive, color }) {
  const fromPos = NODE_POSITIONS[from];
  const toPos = NODE_POSITIONS[to];
  if (!fromPos || !toPos) return null;

  return (
    <line
      x1={`${fromPos.x}%`}
      y1={`${fromPos.y}%`}
      x2={`${toPos.x}%`}
      y2={`${toPos.y}%`}
      stroke={isActive ? color : '#333'}
      strokeWidth={isActive ? 2 : 1}
      strokeDasharray={isActive ? 'none' : '4 4'}
      opacity={isActive ? 0.8 : 0.3}
    />
  );
}

function AgentDetailPanel({ agent, onClose }) {
  if (!agent) return null;

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      className="absolute right-4 top-4 w-72 bg-black/90 border border-gray-700 rounded-lg p-4 z-40 backdrop-blur-sm"
    >
      <button onClick={onClose} className="absolute top-2 right-2 text-gray-500 hover:text-white">
        <X className="w-4 h-4" />
      </button>
      <div className="flex items-center gap-3 mb-3">
        <div
          className="w-10 h-10 rounded-full flex items-center justify-center border"
          style={{ borderColor: agent.color, backgroundColor: `${agent.color}20` }}
        >
          {React.createElement(ICON_MAP[agent.icon] || Circle, {
            className: 'w-5 h-5',
            style: { color: agent.color },
          })}
        </div>
        <div>
          <div className="font-bold text-white">{agent.name}</div>
          <div className="text-xs text-gray-400">{agent.role}</div>
        </div>
      </div>
      <p className="text-xs text-gray-300 mb-3">{agent.description}</p>
      <div className="space-y-1.5 text-xs">
        {agent.passportId && (
          <div className="flex justify-between">
            <span className="text-gray-500">Kite Passport</span>
            <span className="font-mono text-gray-300">{agent.passportId}</span>
          </div>
        )}
        {agent.paymentScheme && (
          <div className="flex justify-between">
            <span className="text-gray-500">Payment Scheme</span>
            <span className="text-[#3399ff]">{agent.paymentScheme}</span>
          </div>
        )}
        {agent.cost !== null && agent.cost !== undefined && (
          <div className="flex justify-between">
            <span className="text-gray-500">Cost per Job</span>
            <span className="text-green-400">${agent.cost.toFixed(3)} USDC</span>
          </div>
        )}
      </div>
    </motion.div>
  );
}

export default function AgentLaborGraph() {
  const [isRunning, setIsRunning] = useState(false);
  const [currentStep, setCurrentStep] = useState(-1);
  const [completedSteps, setCompletedSteps] = useState(new Set());
  const [activePayments, setActivePayments] = useState([]);
  const [txHashes, setTxHashes] = useState({});
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [easAttestation, setEasAttestation] = useState(null);
  const [artworkId, setArtworkId] = useState(null);
  const paymentIdRef = useRef(0);

  const allAgents = [...AGENTS, { ...STUDIO_MCP_HUB, paymentScheme: null, cost: null, passportId: null }];

  const resetDemo = useCallback(() => {
    setIsRunning(false);
    setCurrentStep(-1);
    setCompletedSteps(new Set());
    setActivePayments([]);
    setTxHashes({});
    setEasAttestation(null);
    setArtworkId(null);
    setSelectedAgent(null);
  }, []);

  const runDemo = useCallback(() => {
    resetDemo();
    setIsRunning(true);
    setArtworkId(`GCX${String(Math.floor(Math.random() * 9999) + 1).padStart(5, '0')}`);

    // Process each agent in sequence with delays
    PROCESSING_ORDER.forEach((agentId, index) => {
      const agent = AGENTS.find(a => a.id === agentId);
      const delay = (index + 1) * 2200;

      // Start processing
      setTimeout(() => {
        setCurrentStep(index);

        // Fire payment particle from Thalos
        if (agent?.cost) {
          const pid = ++paymentIdRef.current;
          setActivePayments(prev => [...prev, {
            id: pid,
            from: 'thalos-prime',
            to: agentId,
            amount: agent.cost.toFixed(agent.cost < 0.01 ? 3 : 2),
            color: agent.color,
          }]);
        }
      }, delay);

      // Complete processing
      setTimeout(() => {
        setCompletedSteps(prev => new Set([...prev, agentId]));
        setTxHashes(prev => ({ ...prev, [agentId]: generateTxHash() }));

        // EAS attestation when Atlas completes
        if (agentId === 'atlas') {
          setEasAttestation(`0x${generateTxHash().slice(2, 66)}`);
        }

        // MCP discovery after Flux
        if (agentId === 'flux') {
          const pid = ++paymentIdRef.current;
          setActivePayments(prev => [...prev, {
            id: pid,
            from: 'thalos-prime',
            to: 'studio-mcp-hub',
            amount: 'MCP',
            color: STUDIO_MCP_HUB.color,
          }]);
        }
      }, delay + 1500);
    });

    // End demo
    setTimeout(() => {
      setIsRunning(false);
      setCurrentStep(PROCESSING_ORDER.length);
    }, (PROCESSING_ORDER.length + 1) * 2200 + 1500);
  }, [resetDemo]);

  const removePayment = useCallback((id) => {
    setActivePayments(prev => prev.filter(p => p.id !== id));
  }, []);

  const isComplete = currentStep >= PROCESSING_ORDER.length;

  return (
    <section className="relative py-16 md:py-24 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Section Header */}
        <div className="text-center mb-8">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-2">
            Autonomous Data Procurement Pipeline
          </h2>
          <p className="text-gray-400 max-w-2xl mx-auto">
            8 autonomous agents discover, verify, enrich, and license data — settling every operation via x402 micropayments on Kite chain. Zero human intervention.
          </p>
        </div>

        {/* Controls */}
        <div className="flex items-center justify-center gap-4 mb-6">
          <button
            onClick={runDemo}
            disabled={isRunning}
            className="flex items-center gap-2 px-6 py-2.5 rounded-lg font-semibold text-sm transition-all disabled:opacity-50 disabled:cursor-not-allowed bg-[#0066cc]/20 text-[#3399ff] border border-[#0066cc]/30 hover:bg-[#0066cc]/30"
          >
            <Play className="w-4 h-4" />
            {isComplete ? 'Run Again' : 'Launch Pipeline'}
          </button>
          {(isRunning || isComplete) && (
            <button
              onClick={resetDemo}
              className="flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm text-gray-400 border border-gray-700 hover:border-gray-500 transition-all"
            >
              <RotateCcw className="w-4 h-4" />
              Reset
            </button>
          )}
          {artworkId && (
            <span className="text-xs font-mono text-gray-500">
              Artwork: <span className="text-[#3399ff]">{artworkId}</span>
            </span>
          )}
        </div>

        {/* The Graph */}
        <div className="relative w-full aspect-[16/10] md:aspect-[16/9] bg-black/40 border border-gray-800 rounded-xl overflow-hidden">
          {/* Testnet badge */}
          <div className="absolute top-3 left-3 z-30 flex items-center gap-1.5 px-2 py-1 bg-[#0066cc]/10 border border-[#0066cc]/20 rounded text-[10px] text-[#3399ff] font-mono">
            <Circle className="w-2 h-2 fill-current" />
            Kite Ozone Testnet Simulation
          </div>

          {/* Connection lines (SVG layer) */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ zIndex: 1 }}>
            {PIPELINE_EDGES.map((edge) => (
              <ConnectionLine
                key={`${edge.from}-${edge.to}`}
                from={edge.from}
                to={edge.to}
                isActive={completedSteps.has(edge.from) || completedSteps.has(edge.to)}
                color={allAgents.find(a => a.id === edge.to)?.color || '#555'}
              />
            ))}
          </svg>

          {/* Agent nodes */}
          {allAgents.map((agent) => {
            const pos = NODE_POSITIONS[agent.id];
            if (!pos) return null;
            const pipelineIdx = PROCESSING_ORDER.indexOf(agent.id);
            return (
              <AgentNode
                key={agent.id}
                agent={agent}
                position={pos}
                isActive={
                  agent.id === 'thalos-prime'
                    ? isRunning || isComplete
                    : pipelineIdx === currentStep
                }
                isCompleted={
                  agent.id === 'thalos-prime' ? isComplete : completedSteps.has(agent.id)
                }
                isProcessing={pipelineIdx === currentStep && isRunning}
                onClick={setSelectedAgent}
              />
            );
          })}

          {/* Payment particles */}
          <AnimatePresence>
            {activePayments.map((payment) => (
              <PaymentParticle
                key={payment.id}
                {...payment}
                onComplete={() => removePayment(payment.id)}
              />
            ))}
          </AnimatePresence>

          {/* Settlement Ledger — right panel inside the graph */}
          <div className="absolute right-3 top-12 bottom-3 w-[30%] z-20 flex flex-col">
            <div className="bg-black/80 border border-gray-800 rounded-lg p-3 backdrop-blur-sm flex-1 overflow-hidden flex flex-col">
              <h3 className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <DollarSign className="w-3 h-3 text-green-400" />
                x402 Settlement Ledger
              </h3>
              {Object.keys(txHashes).length === 0 ? (
                <div className="flex-1 flex items-center justify-center">
                  <span className="text-[10px] text-gray-600 italic">Launch pipeline to see settlements...</span>
                </div>
              ) : (
                <div className="space-y-1.5 overflow-y-auto flex-1">
                  {Object.entries(txHashes).map(([agentId, hash]) => {
                    const agent = AGENTS.find(a => a.id === agentId);
                    if (!agent) return null;
                    return (
                      <motion.div
                        key={agentId}
                        initial={{ opacity: 0, x: 10 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="flex items-center gap-2 text-[10px] font-mono"
                      >
                        <span style={{ color: agent.color }} className="w-14 text-right font-bold truncate">
                          {agent.name}
                        </span>
                        <span className="text-green-400 w-10 flex-shrink-0">
                          ${agent.cost?.toFixed(3) || '0.000'}
                        </span>
                        <span className="text-gray-600 truncate flex-1 hidden md:inline">
                          {hash.slice(0, 14)}...
                        </span>
                        <a
                          href={`${KITE_TESTNET.explorerUrl}/tx/${hash}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-400 hover:text-blue-300 flex-shrink-0"
                        >
                          <ExternalLink className="w-2.5 h-2.5" />
                        </a>
                      </motion.div>
                    );
                  })}
                </div>
              )}
              {easAttestation && (
                <div className="mt-2 pt-2 border-t border-gray-800 flex items-center gap-1.5 text-[10px]">
                  <Shield className="w-3 h-3 text-[#3399ff]" />
                  <span className="text-gray-400">EAS:</span>
                  <span className="font-mono text-[#3399ff] truncate">{easAttestation.slice(0, 18)}...</span>
                </div>
              )}
              {isComplete && (
                <div className="mt-2 pt-2 border-t border-gray-800 text-center">
                  <span className="text-[10px] text-green-400 font-bold">
                    Total: $0.438 USDC via gokite-aa
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Agent detail panel */}
          <AnimatePresence>
            {selectedAgent && (
              <AgentDetailPanel
                agent={selectedAgent}
                onClose={() => setSelectedAgent(null)}
              />
            )}
          </AnimatePresence>
        </div>
      </div>
    </section>
  );
}
