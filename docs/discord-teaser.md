# Pre-Submission Discord Teaser — Kite `#builders` (drop ~24h before deadline)

**Per pass-2 decision #3:** *"Share the Coinbase CDP / Base L2 workaround in Discord BEFORE submission. Establishes ecosystem-savior posture rather than hoard a fragile competitive advantage."*

**When:** Sun 2026-05-17, ~9-11 AM PT (24-30 hours before the 04:59 AM Mon deadline). Lands in mid-day for US/EU builders; Kite team (Henry Lee, Scott Shi) typically active in Discord around this window.

**Where:** Kite Discord `#builders` channel — https://discord.com/invite/Gqvh6hv9gt

**Tone:** Helpful peer · "we noticed this, here's the fix" · NO product-name in the teaser · earn the savior posture first; the submission references Metavolve afterwards.

---

## Draft

> Hey team — we noticed a fair number of builders hitting HTTP 500s on the Pieverse v2 testnet facilitator over the past week. We mapped the undocumented cross-chain abstraction in Kite Passport (`agent_wallet` on Kite chain 2366 + `treasury_wallet` auto-provisioned on Base mainnet) and built a clean Coinbase CDP bypass that goes direct on Base L2.
>
> Sharing the gist here so other teams aren't blocked overnight:
>
> ```
> # The Passport silently provisions two wallets per user.
> # `kpass wallet balance` shows the agent_wallet (Kite identity).
> # x402 settlements actually come from the treasury_wallet on Base.
> # The Passport SDK handles cross-chain routing transparently —
> # set X402_NETWORK=base + supply a treasury_wallet vault address
> # and your existing x402 service hits Base USDC without Pieverse.
>
> export X402_NETWORK=base
> export OPERATOR_VAULT=<your treasury_wallet from `kpass agent info`>
> # If on testnet, your treasury_wallet is auto-funded via the Base Sepolia faucet
> ```
>
> Proof tx (live, $0.01 weather call): https://basescan.org/tx/0x09deffc164a15d69a1095e132ab851791e4ba595af42f0257b9c2cca85847623
>
> Anyone else seeing the same? Happy to compare notes on routing edge cases. 🙏

---

## Why this works

1. **Helpful, not boastful.** Frames the discovery as community-shared infrastructure knowledge, not "we solved it first."
2. **Builds credibility with Henry + Scott.** They'll read this as a team that dug deeper than anyone else into Passport internals — validates their cross-chain design even when their testnet facilitator was flakey.
3. **No product name.** The submission references Metavolve afterwards; this teaser is pure-tech-sharing. Earns the savior posture before the brand reveal.
4. **Anchor tx is real.** The 0x09deffc1… settlement is on Base mainnet — anyone can verify.

## Follow-up if the teaser lands

If Henry, Scott, Stephen A, or any Kite team member replies with thanks, follow up with a brief mention of the submission:

> Glad it helps! Our submission goes in Sun PM — it's an autonomous Frontier Lab procurement agent that uses the Passport routing exactly this way. Two-agent + Cognitive Nutrition Bar bridge into Arweave/AO. Repo + writeup will be linked in the submission thread tomorrow. 🍸
