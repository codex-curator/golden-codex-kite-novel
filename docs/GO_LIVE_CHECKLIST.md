# Go Live Checklist — KITE x402 Payments

> Step-by-step guide to make the Watchdog Agent settle real payments on Kite chain.

---

## Phase 1: Get KITE (5 minutes)

### Option A: Buy on Coinbase (simplest)
1. Open Coinbase app (phone — you're doing ID verification there)
2. Search "KITE" → Buy → $10–20 worth (~60–120 KITE at $0.17)
3. KITE lands in your Coinbase wallet as ERC-20 on Ethereum

### Option B: Buy on Binance
1. Binance → KITE/USDT → Market Buy
2. Higher liquidity, lower fees

### What you need:
- **~$5 of KITE** on Kite chain for gas (covers thousands of transactions)
- **~$5 of USDC** on Kite chain for x402 settlements (covers ~40 full pipeline runs)

---

## Phase 2: Bridge to Kite Chain (10 minutes)

KITE bought on Coinbase is ERC-20 on Ethereum. Need to get it to Kite L1 (chain 2366).

### For USDC → Kite:
Kite uses **Lucid** (LayerZero bridge) for canonical USDC:
- USDC on Kite: `0x7aB6f3ed87C42eF0aDb67Ed95090f8bF5240149e`
- Bridged from Avalanche via LayerZero OFT
- Route: Coinbase → Avalanche → Lucid bridge → Kite

### For KITE gas:
- Check if Kite has a native bridge at `https://wallet.ash.center/?network=kite`
- Or use LayerZero if available (Kite endpoint ID: 30406)
- Testnet alternative: faucet at `https://faucet.gokite.ai` (free testnet KITE)

### MetaMask Setup:
Add Kite to MetaMask:
```
Network Name: KiteAI Mainnet
RPC URL: https://rpc.gokite.ai/
Chain ID: 2366
Token: KITE
Explorer: https://kitescan.ai/
```

For testnet:
```
Network Name: KiteAI Testnet
RPC URL: https://rpc-testnet.gokite.ai/
Chain ID: 2368
Token: KITE
Explorer: https://testnet.kitescan.ai/
```

---

## Phase 3: Create Agent Wallets (15 minutes)

Each agent needs a **ClientAgentVault** (ERC-4337 smart account).

### Quick path: Use gokite-aa-sdk
```bash
npm install gokite-aa-sdk
```

```javascript
import { GokiteAASDK } from 'gokite-aa-sdk';

const sdk = new GokiteAASDK(
  'kite_testnet',
  'https://rpc-testnet.gokite.ai',
  'https://bundler-service.staging.gokite.ai/rpc/'
);

// Get AA wallet for Watchdog agent
const watchdogVault = sdk.getAccountAddress('0xYourEOA');
console.log('Watchdog vault:', watchdogVault);
```

### Or: Use existing EOA wallets
For the hackathon demo, regular wallets work fine. AA vaults are needed for production spending rules.

### Wallets needed:
| Agent | Purpose | Fund with |
|-------|---------|-----------|
| Watchdog | Pays for verifications + licenses | ~$2 USDC |
| Aegis | Receives verification payments | Already deployed |
| Artist wallets | Receive training data license fees | Already in metadata |

---

## Phase 4: Configure Secrets (10 minutes)

### X API Bearer Token
The Watchdog needs a bearer token to read tweets. Your AntiGravity swarm already has this.

```bash
# Store in GCP Secret Manager
gcloud secrets create X_BEARER_TOKEN --project=the-golden-codex-1111
echo -n "YOUR_BEARER_TOKEN" | gcloud secrets versions add X_BEARER_TOKEN --data-file=-

# Or set as env var on Cloud Run
gcloud run services update watchdog-agent \
  --set-env-vars="X_BEARER_TOKEN=YOUR_TOKEN" \
  --region=us-west1
```

### X User IDs
Need the numeric user IDs for @artiswagallery, @0x_b1ank, @Golden_Codex.
These are in your AntiGravity credential files.

```bash
# Set on Cloud Run
gcloud run services update watchdog-agent \
  --set-env-vars="ARTISWA_USER_ID=2019690975011172361,ARTISWA_WALLET=0x...,B1ANK_USER_ID=...,B1ANK_WALLET=...,GOLDEN_CODEX_USER_ID=...,GOLDEN_CODEX_WALLET=..." \
  --region=us-west1
```

### Kite Wallet
```bash
gcloud run services update watchdog-agent \
  --set-env-vars="WATCHDOG_VAULT_ADDRESS=0xYourWatchdogWallet" \
  --region=us-west1
```

---

## Phase 5: Deploy Watchdog (5 minutes)

```bash
cd agents/watchdog-agent
./deploy.sh
```

Then set up Cloud Scheduler to poll every 60 seconds:
```bash
gcloud scheduler jobs create http watchdog-poll \
  --schedule="* * * * *" \
  --uri="https://watchdog-agent-XXXXX.us-west1.run.app/poll" \
  --http-method=POST \
  --project=the-golden-codex-1111 \
  --location=us-west1
```

---

## Phase 6: Test (5 minutes)

### Manual test (no X API needed):
```bash
# Upload an image directly to the demo endpoint
curl -X POST https://watchdog-agent-XXXXX.us-west1.run.app/demo \
  -F "image=@test_artwork.jpg" \
  -F "username=artiswagallery" \
  -F "tweet_text=New drop test"
```

### Check dashboard:
```bash
curl https://watchdog-agent-XXXXX.us-west1.run.app/events?limit=5
curl https://watchdog-agent-XXXXX.us-west1.run.app/stats
```

### View on website:
Open `https://golden-codex.com/kite-demo` and scroll to the Watchdog Dashboard.

---

## Phase 7: Deploy Website (2 minutes)

```bash
cd golden-codex-website
rm -rf .firebase/hosting.*.cache
npm run build
ls dist/site_images/ | wc -l  # Should be 29+
npx firebase deploy --only hosting:golden-codex
```

---

## Decision Points for Tad

| Question | Options |
|----------|---------|
| **Testnet or mainnet?** | Testnet = free (faucet), but "simulation" badges. Mainnet = real money, impressive to judges. |
| **How much to fund?** | $5-10 total is plenty. $2 USDC in watchdog wallet, rest as KITE gas. |
| **X API tier?** | Free tier can read tweets. Basic ($100/mo) needed for filtered stream (real-time). Polling works on free tier. |
| **When to deploy?** | Website is ready to deploy now. Watchdog needs bearer token + wallet address first. |
| **Artist wallets?** | Use the Metavolve Coinbase wallet for all three artists initially. Split later. |

---

## Cost Breakdown

| Item | Cost | Notes |
|------|------|-------|
| KITE gas | ~$0.001/tx | Thousands of txs for pennies |
| Aegis verification | $0.02/image | Paid by Watchdog |
| Training data license | $0.10/image | Paid to artist wallet |
| Full pipeline demo | $0.12/image | Total per drop |
| X API (free tier) | $0/mo | Polling, not streaming |
| Cloud Run (watchdog) | ~$0/mo | min-instances=0, pay per use |

**To run 50 demo drops: ~$6 total.**

---

## What's Already Done (No Action Needed)

- [x] Watchdog Agent code (agents/watchdog-agent/)
- [x] Real-time dashboard (golden-codex-website /kite-demo)
- [x] Aegis verification endpoint (deployed, working)
- [x] Firestore events collection (watchdog_events)
- [x] Demo mode (works without X API or wallet — simulates locally)
- [x] Kite chain constants (real contract addresses from docs)
- [x] StudioMCPHub x402 Kite support
- [x] Solidity contract stubs
- [x] Website builds clean, route works

---

*Last Updated: 2026-03-31*
