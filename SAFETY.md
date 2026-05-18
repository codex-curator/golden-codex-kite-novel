# SAFETY.md — Agent Safety Envelope

The Maestra autonomous purchasing agent operates inside an explicit
defense-in-depth envelope. Every layer below is enforced in code, not in prose.

## Spend ceilings

| Boundary | Value | Enforced where |
|---|---|---|
| Per-transaction max | **$2.00 USDC** | Kite Passport spending session — declared at session creation; the Passport facilitator refuses to sign any TransferWithAuthorization above this. |
| Per-session total | **$10.00 USDC** | Kite Passport spending session — cumulative cap across all txs in the 30-day session. |
| Session TTL | **30 days** | Kite Passport — session keys expire automatically; renewal requires re-auth. |
| Treasury floor | balance check before each settle | `agents/maestra/x402_settlement.py:settle_payment()` — refuses to spend if agent wallet falls below configured floor. |

## Identity isolation

- **Two-wallet routing.** The agent operates an *ephemeral session key* (BIP-32-derived) on the agent_wallet, never the treasury_wallet. The treasury holds funds; the session key only ever sees what's allocated to its session ceiling.
- **EIP-712 TransferWithAuthorization.** Every settlement is a signed message — there is no `eth_sendTransaction` in the agent. The facilitator must verify the signature before broadcasting.
- **No private key in process memory beyond session lifetime.** `x402_settlement.py` loads the session key from `KITE_PASSPORT_JWT` and never persists it.

## Purchase preconditions

Before any settlement above $0.01, Maestra:
1. **Verifies provenance** — Aegis hash-check against the registry. No registry hit, no purchase.
2. **Reads the C2PA manifest** — confirms artist signature + claim generator + active manifest, not an unsigned rip.
3. **Logs a structured decision** to stdout (JSON) + Firestore, recording inputs, outputs, and rationale.

Stub-mode behavior (`GCX_BAR_FACILITATOR_URL` unset): the bar accepts any well-formed envelope so cold-start judges can reproduce the flow without a Coinbase CDP / Pieverse account. In production, the facilitator is required.

## Trap-hardening (the agent-trap taxonomy)

We map our boundaries to the six trap classes catalogued in *AI Agent Traps* (SSRN 6372438):

| Trap class | Our defense |
|---|---|
| Runaway spend loop | Per-tx + per-session caps enforced at Passport facilitator |
| Provenance forgery | Aegis hash-check + C2PA manifest verification before settlement |
| Wrong-chain settlement | Bar advertises both Kite mainnet 2366 and Base mainnet 8453 in `accepts`; Passport routes whichever the session holds funds on |
| Replay | EIP-712 nonce in every TransferWithAuthorization; facilitator rejects duplicates |
| Allowlist capture | Bar verifies signatures **locally** via ecrecover (see `kite_passport_verify.py`) — no Kite catalog gatekeeper |
| Prompt injection of payload | Cocktail recipe content is served only AFTER settlement clears; payload cannot influence the pricing decision |

## Audit trail

Every Maestra decision emits a structured JSON line to stdout. Pipe to any
SIEM (Splunk, Datadog, Azure Monitor, CloudWatch). The same record is dual-written
to Firestore for the live demo replay. No Google-stack lock-in: stdout is the
canonical source.

## Reporting

Found a safety gap? Open a GitHub issue with the `safety` label, or email
research@iaeternum.ai.
