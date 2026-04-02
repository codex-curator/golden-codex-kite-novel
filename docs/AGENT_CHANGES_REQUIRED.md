# Agent Changes Required — Kite AI x402 Integration

> **APPROVED** — Tad confirmed these changes are non-disruptive to existing pipeline (2026-03-30).
> Additive-only: x402 middleware activates only when `X-Agent-Network: kite` header is present.
> Existing GCP processing flow is completely untouched.

**Approach**: Additive Shadow Mode — Kite integration is opt-in via `X-Agent-Network: kite` header.
No changes to existing GCP logic. Agents that receive the header additionally settle payments on Kite.

---

## Global Changes (All Agents)

### New Environment Variables
```bash
KITE_CHAIN_ID=2368                                                 # Testnet (mainnet: 2366)
KITE_RPC_URL=https://rpc-testnet.gokite.ai/                       # Testnet RPC
KITE_FACILITATOR_URL=https://facilitator.pieverse.io               # Pieverse x402 facilitator
KITE_FACILITATOR_ADDRESS=0x12343e649e6b2b2b77649DFAb88f103c02F3C78b  # On-chain facilitator
KITE_SETTLEMENT_TOKEN=0x0fF5393387ad2f9f691FD6Fd28e07E3969e27e63   # Test USDT on Kite
KITE_SETTLEMENT_CONTRACT=0x8d9FaD78d5Ce247aA01C140798B9558fd64a63E3
KITE_PASSPORT_MCP_URL=https://neo.dev.gokite.ai/v1/mcp            # Kite Passport MCP
KITE_PASSPORT_ID=                                                  # Per-agent, from Kite Portal
KITE_VAULT_ADDRESS=                                                # Per-agent ClientAgentVault
```

### New Python Dependencies
```
gokite-aa-sdk         # npm package — for JS agents, or use REST API for Python
eth-account>=0.10.0   # For wallet management
web3>=6.0.0           # Kite RPC interaction
httpx>=0.25.0         # For Pieverse facilitator API calls
```

### x402 Middleware Pattern
Every agent needs a middleware function that:
1. Checks for `X-Agent-Network: kite` header on incoming `/process_job` requests
2. If present, returns HTTP 402 with payment requirement before processing
3. After processing, records payment settlement to AgentPaymentLedger contract
4. If header absent, processes normally (existing behavior unchanged)

```python
# Pseudocode for x402 middleware
def x402_middleware(request):
    if request.headers.get('X-Agent-Network') == 'kite':
        payment_header = request.headers.get('X-PAYMENT')
        if not payment_header:
            return Response(status=402, json=payment_requirement())
        if not verify_payment(payment_header):
            return Response(status=402, json={"error": "Payment verification failed"})
    # Proceed with normal processing
    return process_job(request)
```

### HTTP 402 Response Format (Kite gokite-aa scheme)
```json
{
  "x402Version": 1,
  "accepts": [{
    "scheme": "gokite-aa",
    "network": "kite-testnet",
    "maxAmountRequired": "50000000000000000",
    "resource": "agent:nova/process_job",
    "description": "Nova AI Enrichment — Gemini 3.1 Pro analysis",
    "payTo": "0x...",
    "maxTimeoutSeconds": 300,
    "asset": "0x0fF5393387ad2f9f691FD6Fd28e07E3969e27e63"
  }]
}
```

### x402 Payment Flow (from Kite docs)
```
1. Agent calls /process_job without X-PAYMENT header
2. Agent receives 402 with payment requirement (above)
3. Agent calls Kite Passport MCP: get_payer_addr → gets AA wallet
4. Agent calls Kite Passport MCP: approve_payment → gets X-Payment payload
5. Agent retries /process_job with X-Payment header
6. Agent's middleware calls Pieverse /v2/verify to validate
7. Agent processes the job
8. Agent calls Pieverse /v2/settle to finalize on-chain
9. Agent returns result
```

---

## Per-Agent Changes

### Aurora Agent (`agents/aurora-agent/`)
- **Payment Scheme**: `exact`
- **Cost**: $0.05 USDC (50000 in 6-decimal)
- **Endpoint Changes**: Add x402 middleware to `/process_job`
- **Additional**: Register intake attestation on EAS after archiving. Sign EIP-712 receipt for A2 batch.
- **Estimated Effort**: 2 hours

### Nova Agent (`agents/nova-agent/`)
- **Payment Scheme**: `exact`
- **Cost**: $0.10 USDC (100000 in 6-decimal)
- **Endpoint Changes**: Add x402 middleware to `/process_job`
- **Additional**: Include Gemini token usage in payment metadata for PoAI. Sign EIP-712 receipt.
- **Estimated Effort**: 2 hours

### Flux Agent (`agents/flux-agent/`)
- **Payment Scheme**: `upto`
- **Cost**: Up to $0.10 USDC (100000 in 6-decimal)
- **Endpoint Changes**: Add x402 middleware with variable pricing based on image dimensions
- **Additional**: GPU compute time should be reported for PoAI rewards. Sign EIP-712 receipt.
- **Note**: `upto` scheme means agent returns actual cost after processing (may be less than max)
- **Estimated Effort**: 3 hours (variable pricing logic)

### Atlas Agent (`agents/atlas-agent/`)
- **Payment Scheme**: `exact`
- **Cost**: $0.05 USDC (50000 in 6-decimal)
- **Endpoint Changes**: Add x402 middleware to `/process_job`
- **Additional**:
  - After metadata infusion, call `AeternumProvenanceSchema.registerProvenance()` on Kite
  - Include soulmark (SHA-256), arweave CID, agent swarm addresses, total cost
  - Record EAS attestation UID in job provenance log
- **Estimated Effort**: 4 hours (EAS integration is the most complex)

### Archivus Agent (`agents/archivus-agent/`)
- **Payment Scheme**: `exact`
- **Cost**: $0.03 USDC (30000 in 6-decimal)
- **Endpoint Changes**: Add x402 middleware to `/process_job`
- **Additional**: Include Arweave CID in Kite attestation data
- **Estimated Effort**: 2 hours

### Mintra Agent (`agents/mintra-agent/`)
- **Payment Scheme**: `exact`
- **Cost**: $0.10 USDC (100000 in 6-decimal)
- **Endpoint Changes**: Add x402 middleware to `/process_job`
- **Additional**: Bridge NFT metadata hash to Kite for cross-chain verification
- **Estimated Effort**: 3 hours

### Aegis Agent (`agents/aegis-agent/`)
- **Payment Scheme**: `exact`
- **Cost**: $0.008 USDC (8000 in 6-decimal)
- **Endpoint Changes**: Add x402 middleware to `/aegis/verify`
- **Additional**:
  - This is the **external provision** endpoint — third-party agents pay to verify provenance
  - Add `/aegis/license` endpoint for training data licensing (future)
  - CORS should remain restrictive; external agents use server-to-server calls with x402 headers
- **Estimated Effort**: 3 hours

---

## Thalos Orchestrator (`thalos-agent/`)

### Changes Required
1. **Session Key Management**: Before dispatching a job, create a Kite Session Key scoped to that job's budget
2. **x402 Payment Signing**: Sign x402 payment proofs before calling each worker agent
3. **Payment Ledger Recording**: After each agent completes, call `AgentPaymentLedger.recordPayment()`
4. **Job Completion**: Call `AgentPaymentLedger.recordJobCompletion()` when pipeline finishes
5. **MCP Discovery**: Add header `X-Agent-Network: kite` when calling StudioMCPHub tools
6. **Standing Intent**: Read daily budget from on-chain Standing Intent contract

### New Endpoints
- `POST /jobs` — Add optional `kite_settlement: true` flag in job parameters
- `GET /jobs/{id}/payments` — Return x402 payment history for a job

### Estimated Effort: 6-8 hours (most complex agent)

---

## StudioMCPHub Changes (COMPLETED)

Already implemented in `studiomcphub.com/src/payment/`:
- `kite_config.py` — Chain configuration, passport stubs, session key stubs
- `x402.py` — Updated `create_payment_requirement()` and `verify_payment()` to support `network="kite"` parameter
- Routing via `X-Agent-Network: kite` header

---

## Smart Contracts (COMPLETED — Stubs)

Created in `contracts/kite/`:
- `AeternumProvenanceSchema.sol` — EAS schema registration + attestation creation
- `AgentPaymentLedger.sol` — On-chain payment audit trail with view functions for dashboard

### Deployment Steps (When Ready)
1. Deploy `AeternumProvenanceSchema` to Kite Ozone Testnet
2. Call `registerSchema()` to create the EAS schema
3. Deploy `AgentPaymentLedger` to Kite Ozone Testnet
4. Update all agent environment variables with contract addresses
5. Fund agent wallets with testnet KITE for gas

---

## Total Estimated Effort

| Component | Hours |
|-----------|-------|
| Aurora | 2 |
| Nova | 2 |
| Flux | 3 |
| Atlas | 4 |
| Archivus | 2 |
| Mintra | 3 |
| Aegis | 3 |
| Thalos | 7 |
| Contract deployment | 2 |
| Integration testing | 4 |
| **Total** | **32 hours** |

---

## Blockers

1. **Kite AA SDK**: Not yet publicly available. Session key management and ClientAgentVault deployment require SDK.
2. **Kite EAS deployment**: Need EAS contract addresses on Kite Ozone Testnet.
3. **USDC on Kite**: Need USDC contract address or faucet for testnet.
4. **AP2 Facilitator URL**: Need official Kite x402 facilitator endpoint.
5. **Agent wallet funding**: Each agent needs KITE tokens for gas on testnet.

---

*Last Updated: 2026-03-30*
*Status: Documentation complete. Awaiting human review before implementation.*
