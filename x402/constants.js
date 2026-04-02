// Kite AI Chain Constants (from docs.gokite.ai)
export const KITE_CHAIN = {
  // Testnet (for hackathon demo)
  testnet: {
    chainId: 2368,
    name: 'KiteAI Testnet',
    rpcUrl: 'https://rpc-testnet.gokite.ai/',
    explorerUrl: 'https://testnet.kitescan.ai',
    faucetUrl: 'https://faucet.gokite.ai',
    chainListUrl: 'https://chainlist.org/chain/2368',
  },
  // Mainnet (for production)
  mainnet: {
    chainId: 2366,
    name: 'KiteAI Mainnet',
    rpcUrl: 'https://rpc.gokite.ai/',
    rpcFallback: 'https://rpc-virginia.gokite.ai',
    wsUrl: 'wss://rpc.gokite.ai/ws',
    explorerUrl: 'https://kitescan.ai',
    chainListUrl: 'https://chainlist.org/chain/2366',
  },
  currency: 'KITE',
  // Settlement token on Kite testnet (Test USDT — NOT USDC)
  settlementToken: '0x0fF5393387ad2f9f691FD6Fd28e07E3969e27e63',
  // Pieverse x402 Facilitator (recommended by Kite docs)
  facilitatorUrl: 'https://facilitator.pieverse.io',
  facilitatorAddress: '0x12343e649e6b2b2b77649DFAb88f103c02F3C78b',
  // Kite Passport MCP endpoint
  passportMcpUrl: 'https://neo.dev.gokite.ai/v1/mcp',
  // Kite Portal (session management UI)
  portalUrl: 'https://x402-portal-eight.vercel.app/',
  // AA SDK deployed contracts (testnet)
  contracts: {
    settlementContract: '0x8d9FaD78d5Ce247aA01C140798B9558fd64a63E3',
    clientAgentVaultImpl: '0xB5AAFCC6DD4DFc2B80fb8BCcf406E1a2Fd559e23',
    gokiteAccount: '0x93F5310eFd0f09db0666CA5146E63CA6Cdc6FC21',
    gokiteAccountFactory: '0xF0Fc19F0dc393867F19351d25EDfc5E099561cb7',
    serviceRegistry: '0xc67a4AbcD8853221F241a041ACb1117b38DA587F',
  },
  // Ash multisig wallet tool
  walletUrl: 'https://wallet.ash.center/?network=kite',
  // x402 scheme for Kite AA payments
  x402Scheme: 'gokite-aa',
  x402Network: 'kite-testnet',
};

// Shorthand for demo display
export const KITE_TESTNET = KITE_CHAIN.testnet;

// Agent definitions for the RAMS pipeline
export const AGENTS = [
  {
    id: 'thalos-prime',
    name: 'Thalos Prime',
    role: 'Architect Agent',
    description: 'Root orchestrator of the Recursive Agent Market Swarm. Deploys Standing Intents, creates Delegations, manages Sessions via Kite Passport.',
    color: '#3399ff',
    icon: 'Crown',
    passportId: '0xTHALOS...PRIME',
    serviceUrl: 'https://thalos-agent-172867820131.us-west1.run.app',
    healthEndpoint: '/health',
    paymentScheme: null,
    cost: null,
  },
  {
    id: 'aurora',
    name: 'Aurora',
    role: 'Intake & Archiving',
    description: 'Reserves sequential artwork IDs, creates archive folder structure, copies originals to permanent storage.',
    color: '#FF6B6B',
    icon: 'Sunrise',
    passportId: '0xAURO...RA01',
    serviceUrl: 'https://aurora-agent-172867820131.us-west1.run.app',
    healthEndpoint: '/health',
    paymentScheme: 'exact',
    cost: 0.05,
  },
  {
    id: 'nova',
    name: 'Nova',
    role: 'AI Enrichment',
    description: 'Gemini 3.1 Pro deep analytical enrichment. Generates 8-section Golden Codex JSON with artistic and technical metadata.',
    color: '#4ECDC4',
    icon: 'Sparkles',
    passportId: '0xNOVA...0001',
    serviceUrl: 'https://nova-agent-172867820131.us-west1.run.app',
    healthEndpoint: '/health',
    paymentScheme: 'exact',
    cost: 0.10,
  },
  {
    id: 'flux',
    name: 'Flux',
    role: 'ESRGAN Upscaling',
    description: 'NVIDIA L4 GPU-powered 4x image upscaling using RealESRGAN. Variable compute cost based on image dimensions.',
    color: '#45B7D1',
    icon: 'Maximize2',
    passportId: '0xFLUX...0001',
    serviceUrl: 'https://flux-agent-172867820131.us-west1.run.app',
    healthEndpoint: '/health',
    paymentScheme: 'upto',
    cost: 0.10,
  },
  {
    id: 'atlas',
    name: 'Atlas',
    role: 'Metadata Infusion',
    description: 'ExifTool XMP/IPTC metadata embedding + SHA-256 Soulmark hash registration. Creates strip-proof provenance.',
    color: '#96CEB4',
    icon: 'FileCode',
    passportId: '0xATLA...S001',
    serviceUrl: 'https://atlas-agent-172867820131.us-west1.run.app',
    healthEndpoint: '/health',
    paymentScheme: 'exact',
    cost: 0.05,
  },
  {
    id: 'archivus',
    name: 'Archivus',
    role: 'Permanent Storage',
    description: 'Arweave L1 permanent storage via native AR SDK. Creates immutable CID-addressable archive of final artifacts.',
    color: '#FFEAA7',
    icon: 'Archive',
    passportId: '0xARCH...V001',
    serviceUrl: 'https://archivus-agent-172867820131.us-west1.run.app',
    healthEndpoint: '/health',
    paymentScheme: 'exact',
    cost: 0.03,
  },
  {
    id: 'mintra',
    name: 'Mintra',
    role: 'NFT Minting',
    description: 'ERC-721 minting on Polygon + Ethereum. Bridges provenance attestations to destination chain.',
    color: '#DDA0DD',
    icon: 'Gem',
    passportId: '0xMINT...RA01',
    serviceUrl: 'https://mintra-agent-172867820131.us-west1.run.app',
    healthEndpoint: '/health',
    paymentScheme: 'exact',
    cost: 0.10,
  },
  {
    id: 'aegis',

    name: 'Aegis',
    role: 'Provenance Verification',
    description: 'Perceptual hash verification ("Shazam for Art"). LSH 16x4 band indexing for O(candidates) lookup at 100K+ scale.',
    color: '#74B9FF',
    icon: 'Shield',
    passportId: '0xAEGI...S001',
    serviceUrl: 'https://aegis-agent-172867820131.us-west1.run.app',
    healthEndpoint: '/health',
    paymentScheme: 'exact',
    cost: 0.008,
  },
];

// StudioMCPHub as external service node
export const STUDIO_MCP_HUB = {
  id: 'studio-mcp-hub',
  name: 'StudioMCPHub',
  role: 'External MCP Service',
  description: 'Open MCP tool marketplace. 32 tools for AI art processing, discoverable via Streamable HTTP transport.',
  color: '#E17055',
  icon: 'Globe',
  url: 'https://studiomcphub.com/mcp',
};

// Pipeline flow order (edges in the labor graph)
export const PIPELINE_EDGES = [
  { from: 'thalos-prime', to: 'aurora', label: 'Assign Job' },
  { from: 'aurora', to: 'nova', label: '$0.05' },
  { from: 'nova', to: 'flux', label: '$0.10' },
  { from: 'flux', to: 'atlas', label: '$0.10' },
  { from: 'atlas', to: 'archivus', label: '$0.05' },
  { from: 'archivus', to: 'mintra', label: '$0.03' },
  { from: 'mintra', to: 'aegis', label: '$0.10' },
  { from: 'thalos-prime', to: 'studio-mcp-hub', label: 'MCP Discovery' },
];

// Simulated Kite testnet transaction hashes
export function generateTxHash() {
  const chars = '0123456789abcdef';
  let hash = '0x';
  for (let i = 0; i < 64; i++) {
    hash += chars[Math.floor(Math.random() * chars.length)];
  }
  return hash;
}

// Total pipeline cost for one artwork
export const TOTAL_PIPELINE_COST_USDC = 0.438;
