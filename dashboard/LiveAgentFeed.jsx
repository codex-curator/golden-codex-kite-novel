import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Palette, Brain, Gem, ExternalLink, RotateCcw, Circle, Pause, Play
} from 'lucide-react';

/* ─── Deterministic tx hash generator ─── */
function simTxHash(seed) {
  let h = 0x811c9dc5;
  for (let i = 0; i < seed.length; i++) {
    h ^= seed.charCodeAt(i);
    h = Math.imul(h, 0x01000193);
  }
  const hex = (n) => {
    let s = '';
    for (let i = 0; i < n; i++) {
      h ^= (h << 13); h ^= (h >> 17); h ^= (h << 5);
      s += ((h >>> 0) % 16).toString(16);
    }
    return s;
  };
  return '0x' + hex(64);
}

function truncateHash(hash) {
  if (!hash || hash.length < 12) return hash || '';
  return `${hash.slice(0, 6)}...${hash.slice(-4)}`;
}

function simBlockNumber(seed) {
  let h = 0;
  for (let i = 0; i < seed.length; i++) h = ((h << 5) - h + seed.charCodeAt(i)) | 0;
  return 18_200_000 + Math.abs(h % 50000);
}

/* ─── Embedded replay data — CIL Curator + Maestro evaluating same drops ─── */
const REPLAY_EVENTS = [
  // Drop 1 — Artiswa
  { type: 'artiswa_post', artist: 'Artiswa', title: 'Meridian of Closed Knowing', gcx_id: 'ART-CF-030', caption: 'Meridian of Closed Knowing — Golden Codex verified.', tweet_id: '2040002679116898507', username: 'artiswagallery' },
  { type: 'cil_evaluation', username: 'artiswagallery', artwork_id: 'ART-CF-030', gcx_registered: true, c2pa_valid: true, metadata_words: 2847, status: 'licensed', license_acquired: true, total_paid_usd: 0.011, reasoning: 'GCX registered. 2,847 words metadata exceeds 2K threshold. C2PA chain intact. Signal density: HIGH. Licensing for next frontier model training.', decision: 'approve', payments: [{ amount_usd: 0.001, service: 'verification' }, { amount_usd: 0.0095, service: 'artist_license' }, { amount_usd: 0.0005, service: 'platform_fee' }] },
  { type: 'maestro_evaluation', username: 'artiswagallery', artwork_id: 'ART-CF-030', gcx_registered: true, status: 'acquired', license_acquired: true, total_paid_usd: 0.011, reasoning: 'Exceptional color harmony — magenta and gold create a devotional tension. The geometry echoes my Fibonacci series. This completes a triptych. Acquiring.', decision: 'acquire', payments: [{ amount_usd: 0.001, service: 'verification' }, { amount_usd: 0.0095, service: 'artist_license' }, { amount_usd: 0.0005, service: 'platform_fee' }] },

  // Drop 2 — 0x_b1ank
  { type: 'artiswa_post', artist: '0x_b1ank', title: 'Fracture Protocol 017', gcx_id: 'BLK-0017', caption: 'Fracture Protocol 017 — systems within systems.', tweet_id: '2039987579588939001', username: '0x_b1ank' },
  { type: 'cil_evaluation', username: '0x_b1ank', artwork_id: 'BLK-0017', gcx_registered: true, c2pa_valid: true, metadata_words: 3102, status: 'licensed', license_acquired: true, total_paid_usd: 0.011, reasoning: 'GCX registered. 3,102 words metadata — well above threshold. C2PA intact. Glitch aesthetic provides rare training signal for corruption-pattern recognition.', decision: 'approve', payments: [{ amount_usd: 0.001, service: 'verification' }, { amount_usd: 0.0095, service: 'artist_license' }, { amount_usd: 0.0005, service: 'platform_fee' }] },
  { type: 'maestro_evaluation', username: '0x_b1ank', artwork_id: 'BLK-0017', gcx_registered: true, status: 'passed', license_acquired: false, total_paid_usd: 0.001, reasoning: 'Technically accomplished glitch work but the palette conflicts with my collection\'s warm bias. The fragmented composition doesn\'t extend the narrative arc I\'m building. Passing.', decision: 'pass', payments: [{ amount_usd: 0.001, service: 'verification' }] },

  // Drop 3 — Artiswa
  { type: 'artiswa_post', artist: 'Artiswa', title: 'Ember Beneath Skin', gcx_id: 'ART-TC-027', caption: 'Ember Beneath Skin — Golden Codex verified.', tweet_id: '2039987579588939853', username: 'artiswagallery' },
  { type: 'cil_evaluation', username: 'artiswagallery', artwork_id: 'ART-TC-027', gcx_registered: true, c2pa_valid: true, metadata_words: 2614, status: 'licensed', license_acquired: true, total_paid_usd: 0.011, reasoning: 'GCX registered. 2,614 words metadata passes threshold. C2PA verified. Rich organic material integration provides novel texture training data.', decision: 'approve', payments: [{ amount_usd: 0.001, service: 'verification' }, { amount_usd: 0.0095, service: 'artist_license' }, { amount_usd: 0.0005, service: 'platform_fee' }] },
  { type: 'maestro_evaluation', username: 'artiswagallery', artwork_id: 'ART-TC-027', gcx_registered: true, status: 'acquired', license_acquired: true, total_paid_usd: 0.011, reasoning: 'Extraordinary. The organic material integration is museum-quality. The Soul Whisper reading captures what I see — fire trapped in amber. Adding to the Elements series.', decision: 'acquire', payments: [{ amount_usd: 0.001, service: 'verification' }, { amount_usd: 0.0095, service: 'artist_license' }, { amount_usd: 0.0005, service: 'platform_fee' }] },

  // Drop 4 — ViGOR
  { type: 'artiswa_post', artist: 'ViGOR', title: 'Living Monolith #077', gcx_id: 'VGR-0077', caption: 'Living Monolith #077 — stone remembers what flesh forgets.', tweet_id: '2039972486159425100', username: 'Golden_Codex' },
  { type: 'cil_evaluation', username: 'Golden_Codex', artwork_id: 'VGR-0077', gcx_registered: true, c2pa_valid: true, metadata_words: 2903, status: 'licensed', license_acquired: true, total_paid_usd: 0.011, reasoning: 'GCX registered. 2,903 words metadata. C2PA intact. Monolithic sculpture style is underrepresented in training corpus. High acquisition value.', decision: 'approve', payments: [{ amount_usd: 0.001, service: 'verification' }, { amount_usd: 0.0095, service: 'artist_license' }, { amount_usd: 0.0005, service: 'platform_fee' }] },
  { type: 'maestro_evaluation', username: 'Golden_Codex', artwork_id: 'VGR-0077', gcx_registered: true, status: 'acquired', license_acquired: true, total_paid_usd: 0.011, reasoning: 'The weight of this piece is extraordinary — digital stone that feels ancient. The emotional journey metadata describes a "deep solemnity" I want in the collection. ViGOR\'s rarest work.', decision: 'acquire', payments: [{ amount_usd: 0.001, service: 'verification' }, { amount_usd: 0.0095, service: 'artist_license' }, { amount_usd: 0.0005, service: 'platform_fee' }] },

  // Drop 5 — Artiswa (rejected by CIL — incomplete metadata)
  { type: 'artiswa_post', artist: 'Artiswa', title: 'Crowned in Borrowed Sky', gcx_id: 'ART-DC-037', caption: 'Crowned in Borrowed Sky — Golden Codex verified.', tweet_id: '2039957389735350351', username: 'artiswagallery' },
  { type: 'cil_evaluation', username: 'artiswagallery', artwork_id: 'ART-DC-037', gcx_registered: false, c2pa_valid: false, metadata_words: 890, status: 'rejected', license_acquired: false, total_paid_usd: 0.001, reasoning: 'Not GCX registered. Only 890 words metadata — below 2K threshold. No C2PA chain. Does not meet procurement criteria.', decision: 'reject', payments: [{ amount_usd: 0.001, service: 'verification' }] },
  { type: 'maestro_evaluation', username: 'artiswagallery', artwork_id: 'ART-DC-037', gcx_registered: false, status: 'passed', license_acquired: false, total_paid_usd: 0.001, reasoning: 'Beautiful title but provenance is incomplete — no GCX registration, no C2PA. I can\'t add unverified work to the collection regardless of aesthetic merit. Standards matter.', decision: 'pass', payments: [{ amount_usd: 0.001, service: 'verification' }] },

  // Drop 6 — 0x_b1ank
  { type: 'artiswa_post', artist: '0x_b1ank', title: 'Signal Decay #003', gcx_id: 'BLK-0003', caption: 'Signal Decay #003 — entropy as aesthetic.', tweet_id: '2039942289477500200', username: '0x_b1ank' },
  { type: 'cil_evaluation', username: '0x_b1ank', artwork_id: 'BLK-0003', gcx_registered: true, c2pa_valid: true, metadata_words: 2455, status: 'licensed', license_acquired: true, total_paid_usd: 0.011, reasoning: 'GCX registered. 2,455 words metadata clears threshold. C2PA intact. Entropy/decay patterns are valuable for robustness training. Licensed.', decision: 'approve', payments: [{ amount_usd: 0.001, service: 'verification' }, { amount_usd: 0.0095, service: 'artist_license' }, { amount_usd: 0.0005, service: 'platform_fee' }] },
  { type: 'maestro_evaluation', username: '0x_b1ank', artwork_id: 'BLK-0003', gcx_registered: true, status: 'acquired', license_acquired: true, total_paid_usd: 0.011, reasoning: 'Now THIS is what I was looking for from b1ank. The decay gradients have a painterly quality the glitch work lacked. The Soul Whisper calls it "digital patina." Acquiring.', decision: 'acquire', payments: [{ amount_usd: 0.001, service: 'verification' }, { amount_usd: 0.0095, service: 'artist_license' }, { amount_usd: 0.0005, service: 'platform_fee' }] },

  // Drop 7 — ViGOR
  { type: 'artiswa_post', artist: 'ViGOR', title: 'Living Monolith #091', gcx_id: 'VGR-0091', caption: 'Living Monolith #091 — the cathedral within.', tweet_id: '2039927181791646200', username: 'Golden_Codex' },
  { type: 'cil_evaluation', username: 'Golden_Codex', artwork_id: 'VGR-0091', gcx_registered: true, c2pa_valid: true, metadata_words: 3210, status: 'licensed', license_acquired: true, total_paid_usd: 0.011, reasoning: 'GCX registered. 3,210 words — highest metadata density in this batch. C2PA intact. Architectural complexity provides exceptional spatial reasoning training signal.', decision: 'approve', payments: [{ amount_usd: 0.001, service: 'verification' }, { amount_usd: 0.0095, service: 'artist_license' }, { amount_usd: 0.0005, service: 'platform_fee' }] },
  { type: 'maestro_evaluation', username: 'Golden_Codex', artwork_id: 'VGR-0091', gcx_registered: true, status: 'acquired', license_acquired: true, total_paid_usd: 0.011, reasoning: 'The cathedral motif is breathtaking. Gothic verticality meets digital precision. The emotional journey describes "ascending reverence" — that\'s exactly what I feel. This anchors the collection.', decision: 'acquire', payments: [{ amount_usd: 0.001, service: 'verification' }, { amount_usd: 0.0095, service: 'artist_license' }, { amount_usd: 0.0005, service: 'platform_fee' }] },
];

/* ─── Network config ─── */
const NETWORKS = [
  { id: 'kite', label: 'Kite Ozone (Testnet)', explorer: 'https://testnet.kitescan.ai/tx/', token: 'USDT' },
  { id: 'base', label: 'Base L2 (Mainnet)', explorer: 'https://basescan.org/tx/', token: 'USDC' },
];

/* ─── Event styling ─── */
const EVENT_CONFIG = {
  artiswa_post: { icon: Palette, color: 'text-cyan-400', border: 'border-cyan-500/60', bg: 'bg-cyan-500/10', label: 'Drop' },
  cil_evaluation: { icon: Brain, color: 'text-purple-400', border: 'border-purple-500/60', bg: 'bg-purple-500/10', label: 'CIL Curator' },
  maestro_evaluation: { icon: Gem, color: 'text-amber-400', border: 'border-amber-500/60', bg: 'bg-amber-500/10', label: 'Maestro' },
};

/* ─── Compute running totals ─── */
function computeTotals(events) {
  let cilLicensed = 0, cilRejected = 0, maestroAcquired = 0, maestroPassed = 0, totalSettled = 0, drops = 0;
  for (const evt of events) {
    if (evt.type === 'artiswa_post') drops++;
    if (evt.type === 'cil_evaluation') {
      if (evt.license_acquired) { cilLicensed++; totalSettled += evt.total_paid_usd; }
      else { cilRejected++; totalSettled += evt.total_paid_usd; }
    }
    if (evt.type === 'maestro_evaluation') {
      if (evt.license_acquired) { maestroAcquired++; totalSettled += evt.total_paid_usd; }
      else { maestroPassed++; totalSettled += evt.total_paid_usd; }
    }
  }
  return { cilLicensed, cilRejected, maestroAcquired, maestroPassed, totalSettled, drops };
}

/* ─── Settlement Ledger Entry ─── */
function LedgerRow({ event, network }) {
  if (event.type === 'artiswa_post') return null;
  const isCil = event.type === 'cil_evaluation';
  const licensed = event.license_acquired;
  const txHash = licensed ? simTxHash(event.artwork_id + (isCil ? '_cil' : '_maestro')) : null;
  const block = txHash ? simBlockNumber(txHash) : null;

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex items-center gap-2 px-2.5 py-1.5 rounded text-[10px] font-mono ${
        licensed ? 'bg-green-500/5 border border-green-500/10' : 'bg-red-500/5 border border-red-500/10'
      }`}
    >
      {/* Status dot */}
      <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${licensed ? 'bg-green-400' : 'bg-red-400'}`} />

      {/* Agent */}
      <span className={`w-14 flex-shrink-0 font-semibold ${isCil ? 'text-purple-400' : 'text-amber-400'}`}>
        {isCil ? 'CIL' : 'MSTRO'}
      </span>

      {/* Artwork ID */}
      <span className="w-20 flex-shrink-0 text-gray-400 truncate">{event.artwork_id}</span>

      {/* Amount */}
      <span className={`w-16 flex-shrink-0 text-right ${licensed ? 'text-green-400' : 'text-gray-600'}`}>
        {licensed ? `$${event.total_paid_usd?.toFixed(3)}` : '$0.001'}
      </span>

      {/* Token */}
      <span className="w-10 flex-shrink-0 text-gray-500 text-center">{network.token}</span>

      {/* Block / Tx */}
      {txHash ? (
        <a
          href={`${network.explorer}${txHash}`}
          target="_blank"
          rel="noopener noreferrer"
          className="flex-1 text-green-400/60 hover:text-green-300 truncate transition-colors"
        >
          #{block} {truncateHash(txHash)}
        </a>
      ) : (
        <span className="flex-1 text-gray-600">—</span>
      )}
    </motion.div>
  );
}

/* ─── Event content renderers ─── */
function DropContent({ event }) {
  const handle = event.username === 'artiswagallery' ? 'artiswagallery' : event.username === '0x_b1ank' ? '0x_b1ank' : 'Golden_Codex';
  return (
    <div className="space-y-1">
      <div className="flex items-center gap-2">
        <span className="text-xs text-white font-medium">{event.artist || 'Artist'}</span>
        <span className="text-[10px] text-gray-500">@{handle}</span>
      </div>
      <p className="text-sm text-white font-medium">{event.title}</p>
      <span className="text-[10px] font-mono text-cyan-500">{event.gcx_id}</span>
      {event.tweet_id && (
        <a href={`https://x.com/${handle}/status/${event.tweet_id}`} target="_blank" rel="noopener noreferrer"
          className="inline-flex items-center gap-1 text-xs text-cyan-400 hover:text-cyan-300 transition-colors ml-2">
          View on X <ExternalLink className="w-3 h-3" />
        </a>
      )}
    </div>
  );
}

function EvalContent({ event, explorerUrl }) {
  const isCil = event.type === 'cil_evaluation';
  const licensed = event.license_acquired;

  return (
    <div className="space-y-1.5">
      <p className="text-xs text-gray-400">
        Evaluating <span className="text-cyan-400 font-mono">{event.artwork_id}</span>
        {' from '}
        <span className="text-yellow-300">@{event.username}</span>
      </p>

      {isCil && (
        <div className="flex gap-1.5 flex-wrap">
          <span className={`text-[10px] px-1.5 py-0.5 rounded ${event.gcx_registered ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
            GCX: {event.gcx_registered ? '✓' : '✗'}
          </span>
          <span className={`text-[10px] px-1.5 py-0.5 rounded ${event.c2pa_valid ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
            C2PA: {event.c2pa_valid ? '✓' : '✗'}
          </span>
          <span className={`text-[10px] px-1.5 py-0.5 rounded ${(event.metadata_words || 0) >= 2000 ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
            {event.metadata_words || '?'} words
          </span>
        </div>
      )}

      {event.reasoning && (
        <p className="text-xs text-gray-300 italic leading-relaxed">"{event.reasoning}"</p>
      )}

      <div className="flex items-center gap-2">
        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
          licensed ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
        }`}>
          {isCil ? (licensed ? 'LICENSED' : 'REJECTED') : (licensed ? 'ACQUIRED' : 'PASSED')}
        </span>
        <span className="text-[10px] text-gray-500">${(event.total_paid_usd || 0).toFixed(3)} settled</span>
      </div>
    </div>
  );
}

/* ─── Event card ─── */
function EventCard({ event, explorerUrl }) {
  const config = EVENT_CONFIG[event.type] || { icon: Circle, color: 'text-gray-400', border: 'border-gray-600/60', bg: 'bg-gray-500/10', label: 'Agent' };
  const Icon = config.icon;
  const isLicensed = (event.type !== 'artiswa_post') && event.license_acquired;
  const borderClass = isLicensed ? 'border-green-500/40' : event.type === 'artiswa_post' ? config.border : 'border-red-500/30';

  return (
    <motion.div
      layout
      initial={{ opacity: 0, x: -30 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, y: 15, transition: { duration: 0.2 } }}
      transition={{ duration: 0.35, ease: 'easeOut' }}
      className={`relative pl-3 pr-3 py-2.5 rounded-lg bg-black/30 border-l-2 ${borderClass} border border-gray-800/40`}
    >
      <div className="flex items-start gap-2.5">
        <div className={`mt-0.5 p-1 rounded-md ${config.bg}`}>
          <Icon className={`w-3 h-3 ${config.color}`} />
        </div>
        <div className="flex-1 min-w-0">
          <span className={`text-[10px] font-semibold ${config.color} uppercase tracking-wider`}>
            {config.label}
          </span>
          {event.type === 'artiswa_post' && <DropContent event={event} />}
          {(event.type === 'cil_evaluation' || event.type === 'maestro_evaluation') && (
            <EvalContent event={event} explorerUrl={explorerUrl} />
          )}
        </div>
      </div>
    </motion.div>
  );
}

/* ─── Main component ─── */
const MAX_VISIBLE = 12;
const EVENT_INTERVAL_MS = 3500;
const START_DELAY_MS = 1500;

export default function LiveAgentFeed() {
  const [visibleEvents, setVisibleEvents] = useState([]);
  const [ledgerEntries, setLedgerEntries] = useState([]);
  const [network, setNetwork] = useState(NETWORKS[0]);
  const [replayState, setReplayState] = useState('waiting');
  const [isPaused, setIsPaused] = useState(false);
  const currentIndex = useRef(0);
  const timerRef = useRef(null);
  const containerRef = useRef(null);
  const feedRef = useRef(null);
  const ledgerRef = useRef(null);
  const hasStarted = useRef(false);

  const totals = computeTotals(visibleEvents);

  const addNextEvent = useCallback(() => {
    if (currentIndex.current >= REPLAY_EVENTS.length) {
      setReplayState('finished');
      return;
    }

    const evt = { ...REPLAY_EVENTS[currentIndex.current], _key: `${Date.now()}-${currentIndex.current}` };
    currentIndex.current++;

    setVisibleEvents(prev => [evt, ...prev].slice(0, MAX_VISIBLE));

    // Add to ledger if it's an evaluation
    if (evt.type !== 'artiswa_post') {
      setLedgerEntries(prev => [evt, ...prev]);
    }

    timerRef.current = setTimeout(addNextEvent, EVENT_INTERVAL_MS);
  }, []);

  const togglePause = useCallback(() => {
    if (isPaused) {
      setIsPaused(false);
      setReplayState('playing');
      timerRef.current = setTimeout(addNextEvent, EVENT_INTERVAL_MS);
    } else {
      setIsPaused(true);
      setReplayState('paused');
      if (timerRef.current) clearTimeout(timerRef.current);
    }
  }, [isPaused, addNextEvent]);

  const restartReplay = useCallback(() => {
    if (timerRef.current) clearTimeout(timerRef.current);
    currentIndex.current = 0;
    setVisibleEvents([]);
    setLedgerEntries([]);
    setIsPaused(false);
    setReplayState('playing');
    timerRef.current = setTimeout(addNextEvent, EVENT_INTERVAL_MS);
  }, [addNextEvent]);

  // Auto-restart after finishing
  useEffect(() => {
    if (replayState === 'finished') {
      const t = setTimeout(restartReplay, 5000);
      return () => clearTimeout(t);
    }
  }, [replayState, restartReplay]);

  // IntersectionObserver: start when scrolled into view
  useEffect(() => {
    if (!containerRef.current) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !hasStarted.current) {
          hasStarted.current = true;
          timerRef.current = setTimeout(() => {
            setReplayState('playing');
            addNextEvent();
          }, START_DELAY_MS);
        }
      },
      { threshold: 0.2 }
    );
    observer.observe(containerRef.current);
    return () => {
      observer.disconnect();
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [addNextEvent]);

  return (
    <section className="py-12 md:py-20 px-4">
      <div className="max-w-6xl mx-auto">

        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-8"
        >
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-3">
            Autonomous Commerce{' '}
            <span className="bg-gradient-to-r from-purple-400 via-amber-400 to-cyan-400 bg-clip-text text-transparent">
              in Real-Time
            </span>
          </h2>
          <p className="text-gray-400 max-w-2xl mx-auto text-sm">
            Three artists drop work. Two AI purchasing agents evaluate every piece with different criteria.
            Claude's reasoning is visible. Settlements populate the ledger. No humans involved.
          </p>
        </motion.div>

        {/* Two-panel layout */}
        <div ref={containerRef} className="grid grid-cols-1 lg:grid-cols-5 gap-4">

          {/* LEFT — Event Feed (3/5 width) */}
          <div className="lg:col-span-3 bg-black/40 border border-gray-800 rounded-xl overflow-hidden flex flex-col">
            {/* Feed Header */}
            <div className="px-4 py-3 border-b border-gray-800/60">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <h3 className="text-sm font-semibold text-white">Agent Feed</h3>
                  {replayState === 'playing' && (
                    <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-red-500/15 border border-red-500/30">
                      <span className="relative flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75" />
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500" />
                      </span>
                      <span className="text-[10px] font-bold text-red-400 tracking-widest">LIVE</span>
                    </div>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  {(replayState === 'playing' || replayState === 'paused') && (
                    <button onClick={togglePause}
                      className={`flex items-center gap-1 px-2 py-1 rounded text-[10px] font-medium transition-all ${
                        isPaused ? 'bg-green-500/10 text-green-400 border border-green-500/30' : 'bg-gray-800/60 text-gray-400 border border-gray-700'
                      }`}>
                      {isPaused ? <Play className="w-3 h-3" /> : <Pause className="w-3 h-3" />}
                      {isPaused ? 'Resume' : 'Pause'}
                    </button>
                  )}
                  {replayState === 'finished' && (
                    <button onClick={restartReplay}
                      className="flex items-center gap-1 px-2 py-1 rounded text-[10px] font-medium bg-gray-800/60 text-gray-400 border border-gray-700 hover:text-white transition-all">
                      <RotateCcw className="w-3 h-3" /> Replay
                    </button>
                  )}
                </div>
              </div>

              {/* Running totals */}
              <div className="flex items-center gap-3 mt-2 text-[10px]">
                <span className="text-gray-500">Drops: <span className="text-white font-bold">{totals.drops}</span></span>
                <span className="text-purple-400">CIL: <span className="font-bold">{totals.cilLicensed}</span>/{totals.cilLicensed + totals.cilRejected}</span>
                <span className="text-amber-400">Maestro: <span className="font-bold">{totals.maestroAcquired}</span>/{totals.maestroAcquired + totals.maestroPassed}</span>
              </div>
            </div>

            {/* Feed content — tall and scrollable */}
            <div ref={feedRef} className="p-3 space-y-2 min-h-[500px] max-h-[700px] overflow-y-auto scrollbar-thin scrollbar-thumb-gray-800">
              {replayState === 'waiting' && (
                <div className="flex items-center justify-center gap-2 py-16 text-gray-600">
                  <span className="text-sm">Agents standing by...</span>
                </div>
              )}
              <AnimatePresence mode="popLayout">
                {visibleEvents.map(event => (
                  <EventCard key={event._key} event={event} explorerUrl={network.explorer} />
                ))}
              </AnimatePresence>
            </div>
          </div>

          {/* RIGHT — Settlement Ledger (2/5 width) */}
          <div className="lg:col-span-2 bg-black/40 border border-gray-800 rounded-xl overflow-hidden flex flex-col">
            {/* Ledger Header */}
            <div className="px-4 py-3 border-b border-gray-800/60">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-white">Settlement Ledger</h3>
                <select
                  value={network.id}
                  onChange={e => setNetwork(NETWORKS.find(n => n.id === e.target.value) || NETWORKS[0])}
                  className="text-[10px] bg-gray-900/80 text-gray-300 border border-gray-700 rounded px-1.5 py-0.5 focus:outline-none cursor-pointer"
                >
                  {NETWORKS.map(n => <option key={n.id} value={n.id}>{n.label}</option>)}
                </select>
              </div>
              <div className="flex items-center gap-3 mt-2 text-[10px]">
                <span className="text-gray-500">Settled: <span className="text-green-400 font-bold">${totals.totalSettled.toFixed(3)}</span></span>
                <span className="text-gray-500">Txns: <span className="text-white font-bold">{ledgerEntries.length}</span></span>
              </div>
            </div>

            {/* Ledger column headers */}
            <div className="px-3 py-1.5 border-b border-gray-800/40 flex items-center gap-2 text-[9px] font-mono text-gray-600 uppercase tracking-wider">
              <span className="w-1.5" />
              <span className="w-14">Agent</span>
              <span className="w-20">Asset</span>
              <span className="w-16 text-right">Amount</span>
              <span className="w-10 text-center">Token</span>
              <span className="flex-1">Block / Tx Hash</span>
            </div>

            {/* Ledger entries — same height as feed */}
            <div ref={ledgerRef} className="p-2 space-y-1 min-h-[500px] max-h-[700px] overflow-y-auto scrollbar-thin scrollbar-thumb-gray-800">
              {ledgerEntries.length === 0 && replayState !== 'finished' && (
                <div className="flex items-center justify-center py-16 text-gray-600 text-xs">
                  Awaiting settlements...
                </div>
              )}
              <AnimatePresence mode="popLayout">
                {ledgerEntries.map((evt, i) => (
                  <LedgerRow key={evt._key || i} event={evt} network={network} />
                ))}
              </AnimatePresence>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
