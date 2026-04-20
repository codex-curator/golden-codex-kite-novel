import React, { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { ChevronDown, Play, Network, Zap } from 'lucide-react';

// Animated network background canvas
function NetworkBackground() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animationId;
    let nodes = [];

    function resize() {
      canvas.width = canvas.offsetWidth * window.devicePixelRatio;
      canvas.height = canvas.offsetHeight * window.devicePixelRatio;
      ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    }

    function initNodes() {
      nodes = [];
      const count = Math.min(40, Math.floor((canvas.offsetWidth * canvas.offsetHeight) / 15000));
      for (let i = 0; i < count; i++) {
        nodes.push({
          x: Math.random() * canvas.offsetWidth,
          y: Math.random() * canvas.offsetHeight,
          vx: (Math.random() - 0.5) * 0.4,
          vy: (Math.random() - 0.5) * 0.4,
          radius: Math.random() * 2 + 1,
          color: ['#0066cc', '#4ECDC4', '#FF6B6B', '#45B7D1', '#74B9FF'][Math.floor(Math.random() * 5)],
        });
      }
    }

    function draw() {
      const w = canvas.offsetWidth;
      const h = canvas.offsetHeight;
      ctx.clearRect(0, 0, w, h);

      // Update + draw nodes
      nodes.forEach(node => {
        node.x += node.vx;
        node.y += node.vy;
        if (node.x < 0 || node.x > w) node.vx *= -1;
        if (node.y < 0 || node.y > h) node.vy *= -1;

        ctx.beginPath();
        ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
        ctx.fillStyle = node.color;
        ctx.globalAlpha = 0.6;
        ctx.fill();
      });

      // Draw connections
      ctx.globalAlpha = 0.08;
      ctx.strokeStyle = '#0066cc';
      ctx.lineWidth = 1;
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const dx = nodes[i].x - nodes[j].x;
          const dy = nodes[i].y - nodes[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 150) {
            ctx.globalAlpha = 0.08 * (1 - dist / 150);
            ctx.beginPath();
            ctx.moveTo(nodes[i].x, nodes[i].y);
            ctx.lineTo(nodes[j].x, nodes[j].y);
            ctx.stroke();
          }
        }
      }
      ctx.globalAlpha = 1;
      animationId = requestAnimationFrame(draw);
    }

    resize();
    initNodes();
    draw();

    window.addEventListener('resize', () => { resize(); initNodes(); });
    return () => {
      cancelAnimationFrame(animationId);
      window.removeEventListener('resize', resize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 w-full h-full"
      style={{ opacity: 0.5 }}
    />
  );
}

export default function HeroSection({ onLaunchDemo }) {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      <NetworkBackground />

      {/* Gradient overlays */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-[#0a0a1e]" />
      <div className="absolute inset-0 bg-gradient-to-r from-[#0a0a1e]/50 via-transparent to-[#0a0a1e]/50" />

      <div className="relative z-10 text-center px-4 max-w-4xl mx-auto">
        {/* Eyebrow pills */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="flex items-center justify-center gap-4 mb-8"
        >
          <div className="flex items-center gap-2 px-4 py-2 bg-[#0066cc]/10 border border-[#0066cc]/20 rounded-full">
            <Zap className="w-4 h-4 text-[#3399ff]" />
            <span className="text-sm text-[#3399ff] font-semibold">Kite AI Global Hackathon 2026</span>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 rounded-full">
            <Network className="w-4 h-4 text-white/60" />
            <span className="text-sm text-white/60 font-semibold">Agentic Commerce + Novel</span>
          </div>
        </motion.div>

        {/* Headline */}
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="text-4xl md:text-6xl font-bold mb-6 leading-tight"
        >
          <span className="text-white">The </span>
          <span className="bg-gradient-to-r from-[#0066cc] via-[#3399ff] to-[#0066cc] bg-clip-text text-transparent">
            Zero-Trust Compliance Firewall
          </span>
          <span className="text-white"> for the $4.5 Trillion Agent Economy.</span>
        </motion.h1>

        {/* Sub-headline */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="text-xl text-gray-400 mb-6"
        >
          Synthetic data isn't the problem. Synthetic garbage is.
        </motion.p>

        {/* Body */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.5 }}
          className="text-base text-gray-500 mb-4 max-w-2xl mx-auto"
        >
          Frontier AI models are starving for high-signal data, but enterprise ingestion is
          paralyzed by copyright liability. Golden Codex RAMS (Recursive Agent Market Swarm) is a scalable
          autonomous procurement swarm — AI agents that discover, cryptographically verify, and legally license
          high-signal data, settling instantly via Kite x402 micropayments.
        </motion.p>

        {/* Secondary body */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          className="text-sm text-gray-600 italic mb-10 max-w-2xl mx-auto"
        >
          Zero human intervention. Zero legal liability. Clean data at the speed of compute.
        </motion.p>

        {/* CTA buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.7 }}
          className="flex flex-col sm:flex-row items-center justify-center gap-4"
        >
          <button
            onClick={onLaunchDemo}
            className="group flex items-center gap-2 px-8 py-3.5 bg-gradient-to-r from-[#0066cc] to-[#0052a3] text-white font-bold rounded-lg hover:from-[#3399ff] hover:to-[#0066cc] transition-all shadow-lg shadow-[#0066cc]/25"
          >
            <Play className="w-5 h-5" />
            Watch Agents Trade
            <ChevronDown className="w-4 h-4 group-hover:translate-y-0.5 transition-transform" />
          </button>
          <a
            href="https://github.com/codex-curator/golden-codex-kite-novel"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-6 py-3.5 border border-gray-700 text-gray-300 rounded-lg hover:border-gray-500 hover:text-white transition-all"
          >
            View Source
          </a>
        </motion.div>


      </div>

      {/* Scroll indicator */}
      <motion.div
        className="absolute bottom-8 left-1/2 -translate-x-1/2"
        animate={{ y: [0, 8, 0] }}
        transition={{ duration: 2, repeat: Infinity }}
      >
        <ChevronDown className="w-6 h-6 text-gray-600" />
      </motion.div>
    </section>
  );
}
