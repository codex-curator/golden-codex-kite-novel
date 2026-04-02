import React, { useState, useEffect, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Eye, Image, Shield, DollarSign, CheckCircle, XCircle,
  Loader2, AlertCircle, ExternalLink, Play, RefreshCw,
  Twitter, FileCode, Download, Scale, CreditCard, Upload,
  Clock, ArrowRight
} from 'lucide-react';
import { KITE_TESTNET, KITE_CHAIN } from '@/utils/kite/constants';

const WATCHDOG_URL = 'https://watchdog-agent-172867820131.us-west1.run.app';
// Fallback for local dev / before deployment
const FALLBACK_URL = '';

const STEP_ICONS = {
  image_download: Download,
  verification_fee: CreditCard,
  aegis_payment: CreditCard,
  aegis_verification: Shield,
  content_preview: Image,
  claude_evaluation: Scale,
  license_evaluation: Scale,
  artist_payment: DollarSign,
  platform_fee: CreditCard,
};

const STEP_COLORS = {
  in_progress: 'text-[#3399ff]',
  complete: 'text-green-400',
  failed: 'text-red-400',
  skipped: 'text-gray-500',
  settled: 'text-green-400',
  simulated: 'text-blue-400',
};

// ---------------------------------------------------------------------------
// Step Animation Component
// ---------------------------------------------------------------------------

function PipelineStep({ step, index, isLatest }) {
  const Icon = STEP_ICONS[step.name] || FileCode;
  const colorClass = STEP_COLORS[step.status] || 'text-gray-400';
  const isActive = step.status === 'in_progress';

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.15, duration: 0.3 }}
      className={`flex items-start gap-3 py-2 px-3 rounded-lg ${
        isLatest ? 'bg-white/5' : ''
      }`}
    >
      <div className="flex-shrink-0 mt-0.5">
        {isActive ? (
          <Loader2 className={`w-4 h-4 ${colorClass} animate-spin`} />
        ) : step.status === 'complete' || step.status === 'settled' ? (
          <CheckCircle className={`w-4 h-4 ${colorClass}`} />
        ) : step.status === 'failed' ? (
          <XCircle className={`w-4 h-4 ${colorClass}`} />
        ) : (
          <Icon className={`w-4 h-4 ${colorClass}`} />
        )}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className={`text-sm font-medium ${colorClass}`}>
            {formatStepName(step.name)}
          </span>
          <span className="text-[10px] text-gray-600 font-mono">
            {step.timestamp ? new Date(step.timestamp).toLocaleTimeString() : ''}
          </span>
        </div>
        {step.details && Object.keys(step.details).length > 0 && (
          <div className="mt-1 space-y-0.5">
            {Object.entries(step.details).map(([key, val]) => {
              if (val === null || val === undefined) return null;
              return (
                <div key={key} className="text-xs text-gray-500 flex items-center gap-1">
                  <span className="text-gray-600">{formatKey(key)}:</span>
                  <span className={
                    key === 'tx_hash' ? 'font-mono text-blue-400 truncate' :
                    key === 'amount' ? 'text-green-400 font-semibold' :
                    typeof val === 'boolean' ? (val ? 'text-green-400' : 'text-red-400') :
                    'text-gray-400'
                  }>
                    {typeof val === 'boolean' ? (val ? 'TRUE' : 'FALSE') : String(val)}
                  </span>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </motion.div>
  );
}

// ---------------------------------------------------------------------------
// Single Event Card (right panel)
// ---------------------------------------------------------------------------

function EventCard({ event, isExpanded, onToggle }) {
  const isComplete = event.status === 'complete';
  const isProcessing = !isComplete && event.status !== 'failed';
  const hasLicense = event.license_acquired;

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-black/60 border rounded-lg overflow-hidden transition-colors ${
        isProcessing ? 'border-[#0066cc]/30' :
        hasLicense ? 'border-green-500/30' :
        'border-gray-800'
      }`}
    >
      {/* Header */}
      <button
        onClick={onToggle}
        className="w-full flex items-center gap-3 p-3 hover:bg-white/5 transition-colors text-left"
      >
        {/* Status indicator */}
        <div className={`w-2 h-2 rounded-full flex-shrink-0 ${
          isProcessing ? 'bg-[#3399ff] animate-pulse' :
          isComplete && hasLicense ? 'bg-green-400' :
          isComplete ? 'bg-gray-500' :
          'bg-red-400'
        }`} />

        {/* Image thumbnail */}
        {event.image_url && event.image_url !== 'local://upload' && (
          <img
            src={event.image_url}
            alt=""
            className="w-10 h-10 rounded object-cover flex-shrink-0"
            onError={(e) => { e.target.style.display = 'none'; }}
          />
        )}

        {/* Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold text-white truncate">
              @{event.username}
            </span>
            {hasLicense && (
              <span className="px-1.5 py-0.5 bg-green-500/10 text-green-400 text-[10px] rounded font-semibold">
                LICENSED
              </span>
            )}
          </div>
          <div className="text-xs text-gray-500 truncate">{event.tweet_text}</div>
        </div>

        {/* Payment total */}
        {event.total_paid_usd > 0 && (
          <div className="text-right flex-shrink-0">
            <div className="text-sm font-mono text-green-400">
              ${event.total_paid_usd?.toFixed(3)}
            </div>
            <div className="text-[10px] text-gray-600">settled</div>
          </div>
        )}
      </button>

      {/* Expanded: Pipeline steps */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-3 pb-3 border-t border-gray-800/50">
              {/* Verification results */}
              {event.verification && (
                <div className="mt-3 grid grid-cols-2 gap-2">
                  <VerifyBadge
                    label="C2PA"
                    value={event.verification.c2pa_valid}
                  />
                  <VerifyBadge
                    label="GCX Registered"
                    value={event.verification.gcx_registered}
                  />
                </div>
              )}

              {/* Pipeline steps */}
              <div className="mt-3 space-y-1">
                {(event.steps || []).map((step, i) => (
                  <PipelineStep
                    key={`${step.name}-${i}`}
                    step={step}
                    index={i}
                    isLatest={i === (event.steps || []).length - 1}
                  />
                ))}
              </div>

              {/* Payment details */}
              {event.payments && event.payments.length > 0 && (
                <div className="mt-3 pt-2 border-t border-gray-800/50">
                  <div className="text-[10px] text-gray-600 uppercase tracking-wider mb-1">
                    x402 Settlements
                  </div>
                  {event.payments.map((p, i) => (
                    <div key={i} className="flex items-center justify-between text-xs py-1">
                      <span className="text-gray-400">{p.service}</span>
                      <div className="flex items-center gap-2">
                        <span className="text-green-400 font-mono">${p.amount_usd?.toFixed(3)}</span>
                        <span className={`px-1 py-0.5 rounded text-[10px] ${
                          p.status === 'settled' ? 'bg-green-500/10 text-green-400' :
                          p.status === 'simulated' ? 'bg-blue-500/10 text-blue-400' :
                          'bg-red-500/10 text-red-400'
                        }`}>
                          {p.status}
                        </span>
                        {p.tx_hash && (
                          <a
                            href={`${KITE_TESTNET.explorerUrl}/tx/${p.tx_hash}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-400 hover:text-blue-300"
                          >
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Artwork ID if found */}
              {event.verification?.artwork_id && (
                <div className="mt-2 text-xs text-[#3399ff] font-mono">
                  Artwork: {event.verification.artwork_id}
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

function VerifyBadge({ label, value }) {
  return (
    <div className={`flex items-center gap-1.5 px-2 py-1.5 rounded ${
      value ? 'bg-green-500/10 border border-green-500/20' : 'bg-red-500/10 border border-red-500/20'
    }`}>
      {value ? (
        <CheckCircle className="w-3.5 h-3.5 text-green-400" />
      ) : (
        <XCircle className="w-3.5 h-3.5 text-red-400" />
      )}
      <span className={`text-xs font-semibold ${value ? 'text-green-400' : 'text-red-400'}`}>
        {label}
      </span>
    </div>
  );
}

// ---------------------------------------------------------------------------
// X Feed Panel (left side)
// ---------------------------------------------------------------------------

function XFeedPanel({ events }) {
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 mb-4">
        <Twitter className="w-5 h-5 text-blue-400" />
        <h3 className="text-sm font-semibold text-white uppercase tracking-wider">
          Artist Image Drops
        </h3>
      </div>

      {events.length === 0 ? (
        <div className="text-center py-12 text-gray-600">
          <Eye className="w-8 h-8 mx-auto mb-2 opacity-50" />
          <p className="text-sm">Watching for new drops...</p>
          <p className="text-xs mt-1">@artiswagallery · @0x_b1ank · @Golden_Codex</p>
        </div>
      ) : (
        <div className="space-y-3">
          {events.map((event) => (
            <motion.div
              key={event.job_id}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-gray-900/50 border border-gray-800 rounded-lg p-3"
            >
              {/* Tweet header */}
              <div className="flex items-center gap-2 mb-2">
                <div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center">
                  <Twitter className="w-4 h-4 text-blue-400" />
                </div>
                <div>
                  <div className="text-sm font-semibold text-white">
                    {event.artist_display_name || event.username}
                  </div>
                  <div className="text-xs text-gray-500">@{event.username}</div>
                </div>
                <div className="ml-auto text-[10px] text-gray-600">
                  {event.detected_at ? new Date(event.detected_at).toLocaleTimeString() : ''}
                </div>
              </div>

              {/* Tweet text */}
              <p className="text-sm text-gray-300 mb-2">{event.tweet_text}</p>

              {/* Image */}
              {event.image_url && event.image_url !== 'local://upload' && (
                <div className="relative rounded-lg overflow-hidden mb-2">
                  <img
                    src={event.image_url}
                    alt=""
                    className="w-full aspect-video object-cover"
                    onError={(e) => {
                      e.target.src = '';
                      e.target.className = 'hidden';
                    }}
                  />
                  {/* Scanning overlay when processing */}
                  {event.status !== 'complete' && event.status !== 'failed' && (
                    <motion.div
                      className="absolute inset-0 bg-gradient-to-b from-[#0066cc]/10 to-transparent"
                      animate={{ opacity: [0.3, 0.6, 0.3] }}
                      transition={{ duration: 1.5, repeat: Infinity }}
                    >
                      <motion.div
                        className="absolute left-0 right-0 h-0.5 bg-[#3399ff]/50"
                        animate={{ top: ['0%', '100%', '0%'] }}
                        transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                      />
                    </motion.div>
                  )}
                </div>
              )}

              {/* Quick status */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1">
                  {event.status === 'complete' ? (
                    <CheckCircle className="w-3.5 h-3.5 text-green-400" />
                  ) : event.status === 'failed' ? (
                    <XCircle className="w-3.5 h-3.5 text-red-400" />
                  ) : (
                    <Loader2 className="w-3.5 h-3.5 text-[#3399ff] animate-spin" />
                  )}
                  <span className={`text-xs ${
                    event.status === 'complete' ? 'text-green-400' :
                    event.status === 'failed' ? 'text-red-400' :
                    'text-[#3399ff]'
                  }`}>
                    {event.status === 'complete'
                      ? (event.license_acquired ? 'Licensed & Paid' : 'Verified — Not Licensed')
                      : formatStepName(event.status)}
                  </span>
                </div>
                {event.total_paid_usd > 0 && (
                  <span className="text-xs font-mono text-green-400">
                    ${event.total_paid_usd?.toFixed(3)} settled
                  </span>
                )}
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main Dashboard Component
// ---------------------------------------------------------------------------

export default function WatchdogDashboard() {
  const [events, setEvents] = useState([]);
  const [expandedEvent, setExpandedEvent] = useState(null);
  const [isPolling, setIsPolling] = useState(false);
  const [stats, setStats] = useState(null);
  const [demoMode, setDemoMode] = useState(false);
  const fileInputRef = useRef(null);

  // Fetch events from watchdog agent
  const fetchEvents = useCallback(async () => {
    try {
      const resp = await fetch(`${WATCHDOG_URL}/events?limit=20`);
      if (resp.ok) {
        const data = await resp.json();
        setEvents(data.events || []);
      }
    } catch {
      // Watchdog not deployed yet — use demo data
    }
  }, []);

  // Fetch stats
  const fetchStats = useCallback(async () => {
    try {
      const resp = await fetch(`${WATCHDOG_URL}/stats`);
      if (resp.ok) {
        setStats(await resp.json());
      }
    } catch {
      // Not available yet
    }
  }, []);

  // Trigger a poll cycle
  const triggerPoll = useCallback(async () => {
    setIsPolling(true);
    try {
      await fetch(`${WATCHDOG_URL}/poll`, { method: 'POST' });
      await new Promise(r => setTimeout(r, 2000));
      await fetchEvents();
    } catch {
      // Not deployed
    }
    setIsPolling(false);
  }, [fetchEvents]);

  // Demo: submit an image directly
  const submitDemo = useCallback(async (file) => {
    setDemoMode(true);
    const formData = new FormData();
    formData.append('image', file);
    formData.append('username', 'artiswagallery');
    formData.append('tweet_text', `New drop: ${file.name}`);

    try {
      const resp = await fetch(`${WATCHDOG_URL}/demo`, {
        method: 'POST',
        body: formData,
      });
      if (resp.ok) {
        const result = await resp.json();
        // Add to local events immediately
        setEvents(prev => [result, ...prev]);
        setExpandedEvent(result.job_id);
      }
    } catch {
      // Generate local demo event
      const demoEvent = generateLocalDemoEvent(file.name);
      setEvents(prev => [demoEvent, ...prev]);
      setExpandedEvent(demoEvent.job_id);
      // Animate steps
      animateDemoEvent(demoEvent.job_id);
    }
    setDemoMode(false);
  }, []);

  // Local demo animation (when watchdog isn't deployed)
  const animateDemoEvent = useCallback((jobId) => {
    const steps = [
      { name: 'image_download', status: 'complete', delay: 500, details: { size_bytes: 2457600, sha256: 'a1b2c3d4e5f6...' } },
      { name: 'verification_fee', status: 'simulated', delay: 1500, details: { amount: '$0.02', to: 'Metavolve Labs', tx_hash: '0x' + 'a'.repeat(64) } },
      { name: 'aegis_verification', status: 'complete', delay: 3000, details: { c2pa_valid: true, gcx_registered: true, artwork_id: 'GCX-AA-00055', confidence: 98.7 } },
      { name: 'content_preview', status: 'complete', delay: 3800, details: { alt_text: 'Sacred geometry ascending through flame — golden ratios spiral upward as light and shadow negotiate the boundary between mathematical precision and divine chaos.' } },
      { name: 'claude_evaluation', status: 'complete', delay: 5000, details: { decision: 'APPROVED', reasoning: 'High-quality sacred geometry with verified C2PA provenance and CC-BY-4.0 training terms. Strong addition to the geometric abstraction corpus.' } },
      { name: 'artist_payment', status: 'simulated', delay: 6500, details: { amount: '$0.95', to: 'Artist 0xFE14...063B', tx_hash: '0x' + 'b'.repeat(64) } },
      { name: 'platform_fee', status: 'simulated', delay: 7200, details: { amount: '$0.05', to: 'Metavolve Labs (5%)', tx_hash: '0x' + 'c'.repeat(64) } },
    ];

    steps.forEach(({ name, status, delay, details }) => {
      setTimeout(() => {
        setEvents(prev => prev.map(e => {
          if (e.job_id !== jobId) return e;
          const newSteps = [...(e.steps || []), {
            name, status, details,
            timestamp: new Date().toISOString(),
          }];

          const updates = { steps: newSteps, status: name };

          if (name === 'aegis_verification') {
            updates.verification = {
              c2pa_valid: true,
              gcx_registered: true,
              artwork_id: 'GCX-AA-00055',
              confidence: 0.987,
              training_terms: 'CC-BY-4.0 + x402 training license',
            };
          }

          if (name === 'verification_fee') {
            updates.payments = [{
              service: 'gcx_verification_fee → Metavolve',
              amount_usd: 0.02,
              status: 'simulated',
              tx_hash: details.tx_hash,
            }];
          }

          if (name === 'platform_fee') {
            updates.payments = [
              ...(e.payments || []),
              {
                service: 'artist_share (95%)',
                amount_usd: 0.95,
                status: 'simulated',
                tx_hash: '0x' + 'b'.repeat(64),
              },
              {
                service: 'platform_fee (5%) → Metavolve',
                amount_usd: 0.05,
                status: 'simulated',
                tx_hash: details.tx_hash,
              },
            ];
            updates.status = 'complete';
            updates.license_acquired = true;
            updates.total_paid_usd = 1.02;
            updates.fee_breakdown = {
              verification_fee: '$0.02 → Metavolve',
              artist_share: '$0.95 → Artist',
              platform_fee: '$0.05 → Metavolve',
              total_metavolve: '$0.07',
              total_artist: '$0.95',
              total_buyer: '$1.02',
            };
          }

          return { ...e, ...updates };
        }));
      }, delay);
    });
  }, []);

  // Auto-refresh
  useEffect(() => {
    fetchEvents();
    fetchStats();
    const interval = setInterval(() => {
      fetchEvents();
      fetchStats();
    }, 5000);
    return () => clearInterval(interval);
  }, [fetchEvents, fetchStats]);

  return (
    <section className="py-16 md:py-24 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-[#0066cc]/10 border border-[#0066cc]/20 rounded-full mb-4">
            <Eye className="w-4 h-4 text-[#3399ff]" />
            <span className="text-sm text-[#3399ff] font-semibold">Provenance Watchdog</span>
          </div>
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-3">
            Real-Time Image Drop Monitor
          </h2>
          <p className="text-gray-400 max-w-2xl mx-auto">
            Autonomous agent watches artist X accounts for new image drops. Each drop triggers
            verification, C2PA inspection, and training data licensing — with x402 payments settled on Kite.
          </p>
        </div>

        {/* Controls */}
        <div className="flex items-center justify-center gap-3 mb-6">
          <button
            onClick={triggerPoll}
            disabled={isPolling}
            className="flex items-center gap-2 px-4 py-2 bg-blue-500/20 text-blue-400 border border-blue-500/30 rounded-lg text-sm font-semibold disabled:opacity-50 hover:bg-blue-500/30 transition-all"
          >
            {isPolling ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
            Poll X Now
          </button>
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={demoMode}
            className="flex items-center gap-2 px-4 py-2 bg-[#0066cc]/20 text-[#3399ff] border border-[#0066cc]/30 rounded-lg text-sm font-semibold disabled:opacity-50 hover:bg-[#0066cc]/30 transition-all"
          >
            <Upload className="w-4 h-4" />
            Demo Drop
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) submitDemo(file);
              e.target.value = '';
            }}
          />
        </div>

        {/* Stats bar */}
        {stats && (
          <div className="grid grid-cols-4 gap-3 mb-6">
            {[
              { label: 'Drops Detected', value: stats.total_drops_detected, color: 'text-white' },
              { label: 'Licenses Acquired', value: stats.total_licenses_acquired, color: 'text-green-400' },
              { label: 'USD Settled', value: `$${stats.total_usd_settled?.toFixed(3)}`, color: 'text-[#3399ff]' },
              { label: 'x402 Payments', value: stats.total_payments, color: 'text-blue-400' },
            ].map((s, i) => (
              <div key={i} className="bg-black/40 border border-gray-800 rounded-lg p-3 text-center">
                <div className={`text-lg font-bold ${s.color}`}>{s.value}</div>
                <div className="text-[10px] text-gray-600">{s.label}</div>
              </div>
            ))}
          </div>
        )}

        {/* Split screen: X Feed | Agent Pipeline */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left: X Feed */}
          <div className="bg-black/40 border border-gray-800 rounded-xl p-4 max-h-[700px] overflow-y-auto">
            <XFeedPanel events={events} />
          </div>

          {/* Right: Agent Pipeline Detail */}
          <div className="bg-black/40 border border-gray-800 rounded-xl p-4 max-h-[700px] overflow-y-auto">
            <div className="flex items-center gap-2 mb-4">
              <Shield className="w-5 h-5 text-[#3399ff]" />
              <h3 className="text-sm font-semibold text-white uppercase tracking-wider">
                Agent Pipeline
              </h3>
              <div className="ml-auto flex items-center gap-1.5 px-2 py-0.5 bg-[#0066cc]/10 border border-[#0066cc]/20 rounded text-[10px] text-[#3399ff] font-mono">
                Kite {KITE_CHAIN.x402Scheme}
              </div>
            </div>

            {events.length === 0 ? (
              <div className="text-center py-12 text-gray-600">
                <Shield className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">Waiting for drops to process...</p>
                <p className="text-xs mt-1">Click "Demo Drop" to simulate</p>
              </div>
            ) : (
              <div className="space-y-3">
                {events.map((event) => (
                  <EventCard
                    key={event.job_id}
                    event={event}
                    isExpanded={expandedEvent === event.job_id}
                    onToggle={() => setExpandedEvent(
                      expandedEvent === event.job_id ? null : event.job_id
                    )}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatStepName(name) {
  return (name || '')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, c => c.toUpperCase());
}

function formatKey(key) {
  return key
    .replace(/_/g, ' ')
    .replace(/\b\w/g, c => c.toUpperCase());
}

function generateLocalDemoEvent(filename) {
  const id = `demo-${Date.now()}`;
  return {
    job_id: id,
    agent_id: 'watchdog-agent-01',
    tweet_id: id,
    tweet_text: `New drop: ${filename}`,
    image_url: '',
    username: 'artiswagallery',
    artist_display_name: 'Artiswa Creatio',
    detected_at: new Date().toISOString(),
    status: 'detected',
    steps: [],
    payments: [],
    verification: null,
    license_acquired: false,
    total_paid_usd: 0,
  };
}
